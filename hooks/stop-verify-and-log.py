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


def do_work():
    """Run checks and write results file."""
    project_root = find_project_root()

    # Always notify when Claude stops, regardless of checks
    send_notification("Claude", "Done ✓")

    if not project_root:
        return

    checks = detect_checks(project_root)
    if not checks:
        return

    results = [run_check(name, cmd, project_root, timeout) for name, cmd, timeout in checks]

    output = format_results(results)
    if output:
        print(output)


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
