#!/usr/bin/env python3
"""
SessionStart hook for loading current task context.

Reads the project's current task file and outputs it to stdout for context injection.
This helps maintain task continuity across session restarts and resumes.

Note: The `compact` matcher is bugged (https://github.com/anthropics/claude-code/issues/15174)
so this only triggers on startup|resume. CLAUDE.md contains a reference to remind
Claude to check the task file after compaction.
"""

import subprocess
import sys
from pathlib import Path


def find_project_root() -> Path | None:
    """Find the project root using git or fallback to cwd."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback to current working directory
    return Path.cwd()


def get_task_file_path() -> Path | None:
    """Get the path to the current task file in the project."""
    project_root = find_project_root()
    if not project_root:
        return None
    return project_root / ".claude" / "current-task.md"


def main():
    task_file = get_task_file_path()

    if not task_file or not task_file.exists():
        # No task file - nothing to inject
        sys.exit(0)

    try:
        content = task_file.read_text().strip()
    except (IOError, OSError):
        # Can't read file - silently skip
        sys.exit(0)

    if not content:
        # Empty file - nothing to inject
        sys.exit(0)

    # Output task context to stdout for injection into session
    print("=" * 60)
    print(f"CURRENT TASK CONTEXT (from .claude/current-task.md)")
    print("=" * 60)
    print()
    print(content)
    print()
    print("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
