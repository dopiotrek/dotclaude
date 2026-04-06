#!/usr/bin/env python3
"""
Merged Stop hook: verification checks + ship-log lesson writing.

Replaces the old stop-verification.py and ship-log-writer.py which redundantly
ran the same expensive checks (tsc, svelte-check) independently.

This hook forks to background so the Stop event returns in <50ms.
Results are written to /tmp/claude-verify-<pid>.txt and lessons are
appended to .claude/logs/ship-log.md on failure.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ── Project detection ────────────────────────────────────────────────


def find_project_root() -> Path | None:
    """Find the project root via git, fall back to cwd."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback: walk up looking for project markers
    cwd = Path.cwd()
    for directory in [cwd] + list(cwd.parents):
        if any((directory / m).exists() for m in ["package.json", "pyproject.toml", "Cargo.toml"]):
            return directory
        if directory == Path.home():
            break
    return None


def detect_checks(project_root: Path) -> list[tuple[str, list[str], int]]:
    """Return (name, command, timeout) tuples for applicable checks."""
    checks: list[tuple[str, list[str], int]] = []

    if (project_root / "tsconfig.json").exists():
        checks.append(("TypeScript", ["pnpm", "tsc", "--noEmit"], 90))

    if (project_root / "svelte.config.js").exists() or (project_root / "svelte.config.ts").exists():
        checks.append(("Svelte", ["pnpm", "svelte-check", "--threshold", "error"], 90))

    if (project_root / "pyproject.toml").exists() or (project_root / "setup.py").exists():
        checks.append(("Python (mypy)", ["mypy", "."], 60))

    if (project_root / "Cargo.toml").exists():
        checks.append(("Rust", ["cargo", "check"], 120))

    return checks


# ── Running checks ───────────────────────────────────────────────────


def run_check(name: str, command: list[str], cwd: Path, timeout: int = 60) -> dict:
    """Run a single verification check."""
    try:
        result = subprocess.run(
            command, cwd=cwd,
            capture_output=True, text=True, timeout=timeout,
        )
        return {
            "name": name,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"name": name, "success": False, "error": f"Timeout after {timeout}s"}
    except FileNotFoundError:
        return {"name": name, "success": False, "error": "Command not found"}
    except Exception as e:
        return {"name": name, "success": False, "error": str(e)}


# ── Verification output ─────────────────────────────────────────────


def format_results(results: list[dict]) -> str:
    """Format verification results for display."""
    if not results:
        return ""

    lines = ["", "📋 Verification Results:"]
    all_passed = True

    for r in results:
        if r["success"]:
            lines.append(f"  ✅ {r['name']}: passed")
        else:
            all_passed = False
            error = r.get("error", "")
            stderr = r.get("stderr", "")
            if error:
                lines.append(f"  ❌ {r['name']}: {error}")
            elif stderr:
                first_line = stderr.strip().split("\n")[0][:80]
                lines.append(f"  ❌ {r['name']}: {first_line}")
            else:
                lines.append(f"  ❌ {r['name']}: failed (exit {r.get('returncode', '?')})")

    if all_passed:
        lines.insert(1, "✨ All checks passed!")
    else:
        lines.insert(1, "⚠️  Some checks failed - review before committing")

    return "\n".join(lines)


# ── Ship-log lesson writing ─────────────────────────────────────────


def get_changed_files(project_root: Path) -> list[str]:
    files: list[str] = []
    for cmd in [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    ]:
        try:
            result = subprocess.run(
                cmd, cwd=project_root,
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                files.extend(result.stdout.strip().split("\n"))
        except Exception:
            pass
    return list(dict.fromkeys(files))


def infer_tags(files: list[str], error_output: str) -> list[str]:
    tags: set[str] = set()
    tag_patterns: dict[str, list[str]] = {
        "drizzle": ["drizzle", "migration", ".sql", "schema.ts"],
        "svelte": [".svelte", "svelte-check", "+page", "+layout"],
        "typescript": [".ts", "tsc", "TS2", "TS18"],
        "supabase": ["supabase", "rls", "policy"],
        "api": ["+server.ts", "+server.js", "api/"],
        "auth": ["auth", "session", "login", "signup"],
        "runes": ["$state", "$derived", "$effect", "$props"],
        "sveltekit": ["routes/", "+page", "+layout", "+error", "hooks.server"],
        "css": [".css", ".scss", "tailwind", "styles"],
        "testing": ["test", "vitest", "spec"],
        "types": ["type ", "interface ", "TS2", "TS18", "as const"],
    }
    combined = " ".join(files) + " " + error_output.lower()
    for tag, patterns in tag_patterns.items():
        if any(p.lower() in combined for p in patterns):
            tags.add(tag)
    return sorted(tags)


def extract_meaningful_errors(raw_output: str, max_errors: int = 3) -> list[str]:
    lines = [l.strip() for l in raw_output.split("\n") if l.strip()]

    noise_patterns = [
        r"^\d+ error", r"^Found \d+", r"^\s*$",
        r"^ELIFECYCLE", r"^ERR!", r"^npm ", r"^pnpm ",
    ]

    error_pattern = re.compile(r".+\(\d+,\d+\):\s*error\s+TS\d+:.+")
    errors: list[str] = []

    for line in lines:
        if any(re.match(p, line) for p in noise_patterns):
            continue
        if error_pattern.match(line):
            errors.append(line[:200])
            if len(errors) >= max_errors:
                break
        elif not errors and len(line) > 20:
            errors.append(line[:200])

    return errors if errors else ([lines[0][:200]] if lines else [])


def infer_rule(check_name: str, errors: list[str], tags: list[str]) -> str:
    combined = " ".join(errors).lower()

    rules = {
        "ts1005": "Check for syntax errors (missing semicolons, commas, brackets) before committing.",
        "ts2322": "Verify type assignments match expected types — don't use `as` to silence, fix the source.",
        "ts2345": "Verify type assignments match expected types — don't use `as` to silence, fix the source.",
        "ts2304": "Check that all referenced names are imported and spelled correctly.",
        "ts2552": "Check that all referenced names are imported and spelled correctly.",
        "ts2339": "Verify the property exists on the type — check the type definition, not just the runtime shape.",
        "ts18": "Check for top-level await, missing async, or module resolution issues.",
        "ts2307": "Fix import paths — check for typos, missing extensions, or incorrect aliases.",
    }

    for code, rule in rules.items():
        if code in combined:
            return rule

    if "svelte" in check_name.lower():
        return f"Run svelte-check before committing changes to {', '.join(tags[:3])} files."

    return f"Run `pnpm {check_name.lower()}` check before committing to catch these errors early."


def is_duplicate(ship_log: Path, error_key: str) -> bool:
    if not ship_log.exists():
        return False
    today = datetime.now().strftime("%Y-%m-%d")
    content = ship_log.read_text()
    return today in content and error_key[:50] in content


def append_lesson(project_root: Path, tags: list[str], check_name: str,
                  errors: list[str], changed_files: list[str]):
    ship_log = project_root / ".claude" / "logs" / "ship-log.md"

    if not ship_log.exists():
        ship_log.parent.mkdir(parents=True, exist_ok=True)
        ship_log.write_text(
            "# Ship Log\n\n"
            "<!-- 🚀 = shipped. 💡 = learned. Auto-maintained by hooks + CLAUDE.md. -->\n\n"
        )

    if is_duplicate(ship_log, errors[0]):
        return

    date = datetime.now().strftime("%Y-%m-%d")
    tag_str = ", ".join(tags) if tags else "general"
    files_str = ", ".join(changed_files[:3])
    if len(changed_files) > 3:
        files_str += f" (+{len(changed_files) - 3} more)"

    if len(errors) == 1:
        errors_str = errors[0]
    else:
        errors_str = "\n".join(f"  - `{e}`" for e in errors)

    rule = infer_rule(check_name, errors, tags)

    entry = (
        f"## {date} | 💡 Lesson: {check_name} failure in {files_str}\n\n"
        f"**What broke:** {errors_str}\n\n"
        f"**Rule:** {rule}\n\n"
        f"**Tags:** {tag_str}\n\n"
        f"---\n\n"
    )

    with open(ship_log, "a") as f:
        f.write(entry)


# ── Main ─────────────────────────────────────────────────────────────


def do_work():
    """Run checks, write results file, and append lessons on failure."""
    project_root = find_project_root()
    if not project_root:
        return

    checks = detect_checks(project_root)
    if not checks:
        return

    # Run all checks (once, shared results)
    results = [run_check(name, cmd, project_root, timeout) for name, cmd, timeout in checks]

    # Write verification results to temp file
    output = format_results(results)
    if output:
        results_file = Path(f"/tmp/claude-verify-{os.getpid()}.txt")
        results_file.write_text(output)

    # Write lessons for any failures
    failed = [r for r in results if not r["success"] and r.get("error") != "Command not found"]
    if failed:
        changed_files = get_changed_files(project_root)
        for check in failed:
            raw_output = (check.get("stderr") or check.get("stdout", "")).strip()
            errors = extract_meaningful_errors(raw_output)
            if not errors:
                continue
            tags = infer_tags(changed_files, raw_output)
            append_lesson(project_root, tags, check["name"], errors, changed_files)


def main():
    # Consume stdin (required by hook protocol)
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        pass

    # Fork to background — parent exits immediately, child does the work
    pid = os.fork()
    if pid > 0:
        # Parent: exit immediately so Stop event is not blocked
        sys.exit(0)

    # Child: detach and do the work
    os.setsid()
    try:
        do_work()
    except Exception:
        pass  # Background — don't crash noisily


if __name__ == "__main__":
    main()
