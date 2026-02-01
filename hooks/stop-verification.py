#!/usr/bin/env python3
"""
Stop hook for running verification checks when Claude completes work.

Based on Boris Cherny's tips #5 and #6a: Give Claude a way to verify its work
for 2-3x quality improvement.

This hook runs when Claude stops to provide feedback on code quality.
Since Stop hooks are informational (not blocking), failures are reported
but don't prevent completion.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def find_project_root() -> Path | None:
    """Find the project root by looking for package.json or pyproject.toml."""
    cwd = Path.cwd()

    # Walk up the directory tree looking for project markers
    for directory in [cwd] + list(cwd.parents):
        if (directory / "package.json").exists():
            return directory
        if (directory / "pyproject.toml").exists():
            return directory
        if (directory / "Cargo.toml").exists():
            return directory
        # Stop at home directory
        if directory == Path.home():
            break

    return None


def detect_project_type(project_root: Path) -> dict:
    """Detect project type and available checks."""
    checks = {
        "typescript": False,
        "svelte": False,
        "eslint": False,
        "python": False,
        "rust": False,
    }

    if (project_root / "tsconfig.json").exists():
        checks["typescript"] = True

    if (project_root / "svelte.config.js").exists() or (project_root / "svelte.config.ts").exists():
        checks["svelte"] = True

    if (project_root / ".eslintrc.js").exists() or (project_root / ".eslintrc.json").exists() or (project_root / "eslint.config.js").exists():
        checks["eslint"] = True

    if (project_root / "pyproject.toml").exists() or (project_root / "setup.py").exists():
        checks["python"] = True

    if (project_root / "Cargo.toml").exists():
        checks["rust"] = True

    return checks


def run_check(name: str, command: list[str], cwd: Path, timeout: int = 60) -> dict:
    """Run a verification check and return results."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "name": name,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-1000:] if result.stdout else "",  # Last 1000 chars
            "stderr": result.stderr[-500:] if result.stderr else "",   # Last 500 chars
        }
    except subprocess.TimeoutExpired:
        return {
            "name": name,
            "success": False,
            "error": f"Timeout after {timeout}s",
        }
    except FileNotFoundError:
        return {
            "name": name,
            "success": False,
            "error": "Command not found",
        }
    except Exception as e:
        return {
            "name": name,
            "success": False,
            "error": str(e),
        }


def run_verifications(project_root: Path, project_checks: dict) -> list[dict]:
    """Run all applicable verification checks."""
    results = []

    # TypeScript type checking
    if project_checks["typescript"]:
        # Check if pnpm is available (preferred) or fall back to npm/npx
        result = run_check(
            "TypeScript",
            ["pnpm", "tsc", "--noEmit"],
            project_root,
            timeout=90,
        )
        results.append(result)

    # Svelte check
    if project_checks["svelte"]:
        result = run_check(
            "Svelte",
            ["pnpm", "svelte-check", "--threshold", "error"],
            project_root,
            timeout=90,
        )
        results.append(result)

    # Python type checking with mypy (if available)
    if project_checks["python"]:
        # Try mypy first
        result = run_check(
            "Python (mypy)",
            ["mypy", "."],
            project_root,
            timeout=60,
        )
        if result.get("error") != "Command not found":
            results.append(result)

    # Rust cargo check
    if project_checks["rust"]:
        result = run_check(
            "Rust",
            ["cargo", "check"],
            project_root,
            timeout=120,
        )
        results.append(result)

    return results


def format_results(results: list[dict]) -> str:
    """Format verification results for display."""
    if not results:
        return ""

    lines = ["", "📋 Verification Results:"]

    all_passed = True
    for result in results:
        if result["success"]:
            lines.append(f"  ✅ {result['name']}: passed")
        else:
            all_passed = False
            error = result.get("error", "")
            stderr = result.get("stderr", "")
            if error:
                lines.append(f"  ❌ {result['name']}: {error}")
            elif stderr:
                # Get first line of stderr for summary
                first_line = stderr.strip().split('\n')[0][:80]
                lines.append(f"  ❌ {result['name']}: {first_line}")
            else:
                lines.append(f"  ❌ {result['name']}: failed (exit {result.get('returncode', '?')})")

    if all_passed:
        lines.insert(1, "✨ All checks passed!")
    else:
        lines.insert(1, "⚠️  Some checks failed - review before committing")

    return "\n".join(lines)


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Stop hooks might not always receive JSON
        input_data = {}

    # Find project root
    project_root = find_project_root()
    if not project_root:
        # Not in a project directory, nothing to verify
        sys.exit(0)

    # Detect project type
    project_checks = detect_project_type(project_root)

    # Skip if no checks available
    if not any(project_checks.values()):
        sys.exit(0)

    # Run verifications
    results = run_verifications(project_root, project_checks)

    # Format and output results
    output = format_results(results)
    if output:
        # Print to stderr so it's visible to user (exit 1 = show to user)
        print(output, file=sys.stderr)

        # Check if any failed
        any_failed = any(not r["success"] for r in results)
        if any_failed:
            # Exit 1 shows stderr to user but doesn't block
            sys.exit(1)

    # All passed or no checks run
    sys.exit(0)


if __name__ == "__main__":
    main()
