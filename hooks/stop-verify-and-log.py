#!/usr/bin/env python3
"""
Stop hook: runs type/lint verification checks in the background.

Launches a background subprocess so the Stop event returns immediately.
Results are written to .claude/logs/last-verify.txt.
"""

import json
import subprocess
import sys
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
            # Keep the HEAD of the output: tsc/svelte-check print the first
            # (most relevant) errors first, then a "Found N errors" trailer.
            # Tailing the output would drop the errors we actually want.
            "stdout": (result.stdout or "")[:16000],
            "stderr": (result.stderr or "")[:16000],
        }
    except subprocess.TimeoutExpired:
        return {"name": name, "success": False, "error": f"Timeout after {timeout}s"}
    except FileNotFoundError:
        return {"name": name, "success": False, "error": "Command not found"}
    except Exception as e:
        return {"name": name, "success": False, "error": str(e)}


# ── Verification output ─────────────────────────────────────────────


def check_detail(r: dict) -> str:
    """Human-useful error text for a failed check.

    tsc, svelte-check, and mypy write their diagnostics to stdout, so prefer
    stdout and fall back to stderr (where cargo and the pnpm wrapper write).
    The old code only ever read stderr, which is empty for the TS toolchain —
    that's why failures showed up as a bare "failed (exit 2)".
    """
    if r.get("error"):
        return r["error"].strip()
    return (r.get("stdout") or "").strip() or (r.get("stderr") or "").strip()


SUMMARY_LINES = 15


def format_results(results: list[dict]) -> str:
    """Compact summary: the verdict plus the first error lines per failed check."""
    if not results:
        return ""

    lines = ["", "📋 Verification Results:"]
    all_passed = True

    for r in results:
        if r["success"]:
            lines.append(f"  ✅ {r['name']}: passed")
            continue

        all_passed = False
        lines.append(f"  ❌ {r['name']}: failed (exit {r.get('returncode', '?')})")
        detail = check_detail(r)
        if not detail:
            continue
        detail_lines = detail.split("\n")
        lines.extend(f"       {dl}" for dl in detail_lines[:SUMMARY_LINES])
        if len(detail_lines) > SUMMARY_LINES:
            lines.append(f"       … ({len(detail_lines) - SUMMARY_LINES} more lines — see log)")

    if all_passed:
        lines.insert(1, "✨ All checks passed!")
    else:
        lines.insert(1, "⚠️  Some checks failed - review before committing")

    return "\n".join(lines)


def format_log(results: list[dict]) -> str:
    """Full detail for the persisted log: compact summary, then complete output."""
    if not results:
        return ""

    blocks = [format_results(results), "", "─" * 60, "FULL OUTPUT", "─" * 60]
    for r in results:
        status = "passed" if r["success"] else f"FAILED (exit {r.get('returncode', '?')})"
        blocks.append(f"\n## {r['name']} — {status}")
        if r.get("error"):
            blocks.append(r["error"].strip())
        out = (r.get("stdout") or "").strip()
        err = (r.get("stderr") or "").strip()
        if out:
            blocks.append(out)
        if err:
            blocks.append("[stderr]")
            blocks.append(err)
        if not (r.get("error") or out or err):
            blocks.append("(no output)")
    return "\n".join(blocks)


# ── Background worker ───────────────────────────────────────────────


def send_notification(title: str, message: str) -> None:
    """Send a macOS notification via osascript."""
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            timeout=5, capture_output=True,
        )
    except Exception:
        pass


def write_log(project_root: Path, output: str) -> Path | None:
    """Persist verification output so it can be read after the turn ends.

    Returns the absolute log path (or None if writing failed) so the
    notification can point at the real file instead of a relative string.
    """
    try:
        log_dir = project_root / ".claude" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "last-verify.txt"
        log_path.write_text(output.strip() + "\n")
        return log_path
    except Exception:
        return None  # Background — never crash on logging


# Extensions whose changes warrant a type/lint pass.
CHECK_EXTENSIONS = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".svelte", ".py", ".rs")


def changed_files_need_checks(project_root: Path) -> bool:
    """True if uncommitted changes touch a checkable file.

    Avoids running a full monorepo typecheck after turns that changed nothing
    relevant (a Q&A turn, a markdown edit). Considers staged, unstaged, and
    untracked files. Fails open: if git is unavailable or errors, run the
    checks rather than silently skip them.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root, capture_output=True, text=True, timeout=5,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return True
    if result.returncode != 0:
        return True  # not a git repo — don't suppress checks

    changed = result.stdout.strip()
    if not changed:
        return False  # nothing changed — nothing to verify
    for line in changed.splitlines():
        path = line[3:]  # strip the "XY " porcelain status prefix
        if " -> " in path:  # rename: "old -> new"
            path = path.split(" -> ", 1)[1]
        if path.strip().rstrip('"').endswith(CHECK_EXTENSIONS):
            return True
    return False


def do_work():
    """Run checks, persist results, and notify with pass/fail status."""
    project_root = find_project_root()

    # No project, no relevant edits, or no applicable checks — just confirm Claude stopped.
    if not project_root:
        send_notification("Claude", "Done ✓")
        return

    if not changed_files_need_checks(project_root):
        send_notification("Claude", "Done ✓")
        return

    checks = detect_checks(project_root)
    if not checks:
        send_notification("Claude", "Done ✓")
        return

    results = [run_check(name, cmd, project_root, timeout) for name, cmd, timeout in checks]

    # The log file gets the FULL output; the printed summary is the short form.
    log_path = write_log(project_root, format_log(results))

    # Notification reflects the actual check status, not just "stopped".
    failed = [r for r in results if not r["success"]]
    if failed:
        names = ", ".join(r["name"] for r in failed)
        where = f" — see {log_path}" if log_path else ""
        send_notification("Claude", f"❌ {names} failed{where}")
    else:
        send_notification("Claude", "Done ✓ — all checks passed")

    summary = format_results(results)
    if summary:
        print(summary)


# ── Main ─────────────────────────────────────────────────────────────


def main():
    # Consume stdin (required by hook protocol)
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        pass

    # Launch background subprocess so Stop event is not blocked
    subprocess.Popen(
        [sys.executable, __file__, "--background"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    sys.exit(0)


if __name__ == "__main__":
    if "--background" in sys.argv:
        try:
            do_work()
        except Exception:
            pass  # Background — don't crash noisily
    else:
        main()
