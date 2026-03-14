#!/usr/bin/env python3
"""
Stop hook that writes lessons to the ship-log when verification checks fail.

Replaces the old lessons-writer.py. Now writes to .claude/logs/ship-log.md
using the 💡 Lesson format instead of a separate lessons.md file.

Key differences from the old system:
- Writes to ship-log.md (merged format) instead of lessons.md
- Uses 💡 prefix for visual scanning
- Includes tags for the lessons-loader to match against
- Skips low-level noise (same error repeated, trivial failures)
- Deduplication window: same error type = once per day max
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _trim_output(text: str, max_chars: int = 2000) -> str:
    """Take the tail of output but align to a line boundary so we don't slice mid-message."""
    if len(text) <= max_chars:
        return text
    trimmed = text[-max_chars:]
    nl = trimmed.find("\n")
    if nl >= 0:
        trimmed = trimmed[nl + 1:]
    return trimmed


def find_project_root() -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return Path.cwd()


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
    """Extract meaningful error messages, skipping noise. Returns up to max_errors."""
    lines = [l.strip() for l in raw_output.split("\n") if l.strip()]

    noise_patterns = [
        r"^\d+ error",
        r"^Found \d+",
        r"^\s*$",
        r"^ELIFECYCLE",
        r"^ERR!",
        r"^npm ",
        r"^pnpm ",
    ]

    # Match actual TS/Svelte error lines: file(line,col): error TSXXXX: message
    error_pattern = re.compile(r".+\(\d+,\d+\):\s*error\s+TS\d+:.+")

    errors: list[str] = []
    for line in lines:
        if any(re.match(p, line) for p in noise_patterns):
            continue
        # Prefer actual error lines
        if error_pattern.match(line):
            errors.append(line[:200])
            if len(errors) >= max_errors:
                break
        elif not errors and len(line) > 20:
            # Fallback: first non-noise line if no TS errors found yet
            errors.append(line[:200])

    return errors if errors else ([lines[0][:200]] if lines else [])


def is_duplicate(ship_log: Path, error_key: str) -> bool:
    """Check if we already logged a similar lesson today."""
    if not ship_log.exists():
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    content = ship_log.read_text()

    # Same date + same error signature = duplicate
    return today in content and error_key[:50] in content


def infer_rule(check_name: str, errors: list[str], tags: list[str]) -> str:
    """Auto-generate a useful rule from the error pattern."""
    combined = " ".join(errors).lower()

    if "ts1005" in combined:
        return "Check for syntax errors (missing semicolons, commas, brackets) before committing."
    if "ts2322" in combined or "ts2345" in combined:
        return "Verify type assignments match expected types — don't use `as` to silence, fix the source."
    if "ts2304" in combined or "ts2552" in combined:
        return "Check that all referenced names are imported and spelled correctly."
    if "ts2339" in combined:
        return "Verify the property exists on the type — check the type definition, not just the runtime shape."
    if "ts18" in combined:
        return "Check for top-level await, missing async, or module resolution issues."
    if "ts2307" in combined:
        return "Fix import paths — check for typos, missing extensions, or incorrect aliases."
    if "svelte" in check_name.lower():
        return f"Run svelte-check before committing changes to {', '.join(tags[:3])} files."

    return f"Run `pnpm {check_name.lower()}` check before committing to catch these errors early."


def append_lesson(project_root: Path, tags: list[str], check_name: str,
                  errors: list[str], changed_files: list[str]):
    """Append a 💡 lesson entry to the ship-log."""
    ship_log = project_root / ".claude" / "logs" / "ship-log.md"

    if not ship_log.exists():
        ship_log.parent.mkdir(parents=True, exist_ok=True)
        ship_log.write_text(
            "# Ship Log\n\n"
            "<!-- 🚀 = shipped. 💡 = learned. Auto-maintained by hooks + CLAUDE.md. -->\n\n"
        )

    # Deduplicate against first error
    if is_duplicate(ship_log, errors[0]):
        return

    date = datetime.now().strftime("%Y-%m-%d")
    tag_str = ", ".join(tags) if tags else "general"
    files_str = ", ".join(changed_files[:3])
    if len(changed_files) > 3:
        files_str += f" (+{len(changed_files) - 3} more)"

    # Format errors as a list if multiple
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


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    project_root = find_project_root()
    if not project_root:
        sys.exit(0)

    has_ts = (project_root / "tsconfig.json").exists()
    has_svelte = (
        (project_root / "svelte.config.js").exists()
        or (project_root / "svelte.config.ts").exists()
    )

    if not has_ts and not has_svelte:
        sys.exit(0)

    checks_to_run: list[tuple[str, list[str]]] = []
    if has_ts:
        checks_to_run.append(("TypeScript", ["pnpm", "tsc", "--noEmit"]))
    if has_svelte:
        checks_to_run.append(("Svelte", ["pnpm", "svelte-check", "--threshold", "error"]))

    checks_failed: list[dict] = []
    for name, cmd in checks_to_run:
        try:
            result = subprocess.run(
                cmd, cwd=project_root,
                capture_output=True, text=True, timeout=90,
            )
            if result.returncode != 0:
                checks_failed.append({
                    "name": name,
                    "stderr": _trim_output(result.stderr or ""),
                    "stdout": _trim_output(result.stdout or ""),
                })
        except subprocess.TimeoutExpired:
            pass
        except FileNotFoundError:
            pass

    if not checks_failed:
        sys.exit(0)

    changed_files = get_changed_files(project_root)

    for check in checks_failed:
        raw_output = (check["stderr"] or check["stdout"]).strip()
        errors = extract_meaningful_errors(raw_output)
        if not errors:
            continue

        tags = infer_tags(changed_files, raw_output)
        append_lesson(project_root, tags, check["name"], errors, changed_files)

    sys.exit(0)


if __name__ == "__main__":
    main()
