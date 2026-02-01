#!/usr/bin/env python3
"""
PostToolUse hook: Run security audits when dependency files are modified.
Triggers on: package.json, requirements.txt, Cargo.toml, pom.xml, Gemfile
"""

import json
import subprocess
import sys
from pathlib import Path

DEPENDENCY_FILES = {
    "package.json": {
        "name": "pnpm/npm",
        "commands": [
            # Try pnpm first (if pnpm-lock.yaml exists), fallback to npm
            ["pnpm", "audit"],
        ]
    },
    "pnpm-lock.yaml": {
        "name": "pnpm",
        "commands": [
            ["pnpm", "audit"],
        ]
    },
    "requirements.txt": {
        "name": "pip",
        "commands": [
            ["safety", "check", "-r"],  # file path appended
        ]
    },
    "Cargo.toml": {
        "name": "cargo",
        "commands": [
            ["cargo", "audit"],
        ]
    },
    "Gemfile": {
        "name": "bundler",
        "commands": [
            ["bundle", "audit", "check", "--update"],
        ]
    },
}


LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "dependency-audit.log"


def log(message: str) -> None:
    """Log to both stdout and file."""
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")


def run_audit(file_path: str) -> None:
    """Run appropriate audit command for the dependency file."""
    path = Path(file_path)
    filename = path.name

    if filename not in DEPENDENCY_FILES:
        return

    config = DEPENDENCY_FILES[filename]
    log(f"\n📦 Dependency file modified: {file_path}")
    log(f"🔍 Running {config['name']} security audit...\n")

    for cmd in config["commands"]:
        # Append file path for commands that need it
        if cmd[0] == "safety":
            cmd = cmd + [file_path]

        try:
            # Check if command exists
            if subprocess.run(["which", cmd[0]], capture_output=True).returncode != 0:
                print(f"⚠️  {cmd[0]} not installed, skipping audit")
                continue

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=path.parent,
                timeout=60
            )

            if result.stdout:
                log(result.stdout)
            if result.stderr:
                log(result.stderr)

            if result.returncode != 0:
                log(f"⚠️  Audit found issues (exit code {result.returncode})")
            else:
                log(f"✅ No vulnerabilities found")

        except FileNotFoundError:
            log(f"⚠️  {cmd[0]} not found, skipping")
        except subprocess.TimeoutExpired:
            log(f"⚠️  {cmd[0]} audit timed out")
        except Exception as e:
            log(f"⚠️  Error running {cmd[0]}: {e}")


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")

    if not file_path:
        sys.exit(0)

    # Check if this is a dependency file
    filename = Path(file_path).name
    if filename in DEPENDENCY_FILES:
        run_audit(file_path)

    # PostToolUse hooks should not block, always exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()
