#!/usr/bin/env python3
"""
PostToolUse hook (matcher: precompact) — saves task state before context compaction.

When Claude's context window is about to be compressed, this hook captures
the current git state and appends it to .claude/current-task.md so nothing
is lost across the compaction boundary.

This is the WRITE side of the compaction bridge.
The READ side is task-restore.py (postcompact).
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


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


def get_recent_changes(project_root: Path) -> str:
    """Get a compact summary of recent git activity."""
    lines = []

    # Recent commits (last 5)
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--no-decorate"],
            cwd=project_root, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines.append("Recent commits:")
            for line in result.stdout.strip().split("\n"):
                lines.append(f"  {line}")
    except Exception:
        pass

    # Uncommitted changes
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "--no-color"],
            cwd=project_root, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines.append("Uncommitted changes:")
            for line in result.stdout.strip().split("\n")[-5:]:
                lines.append(f"  {line}")
    except Exception:
        pass

    # Staged changes
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--stat", "--no-color"],
            cwd=project_root, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines.append("Staged changes:")
            for line in result.stdout.strip().split("\n")[-5:]:
                lines.append(f"  {line}")
    except Exception:
        pass

    return "\n".join(lines) if lines else "No recent git activity."


def get_current_branch(project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_root, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def update_task_snapshot(task_file: Path, project_root: Path):
    """Write or update the Context Snapshot section in the task file."""
    content = task_file.read_text()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    branch = get_current_branch(project_root)
    changes = get_recent_changes(project_root)

    snapshot = (
        f"## Context Snapshot\n"
        f"<!-- Auto-written by precompact hook at {now} -->\n"
        f"Branch: {branch}\n"
        f"Snapshot at: {now}\n\n"
        f"{changes}\n"
    )

    # Replace existing snapshot or append
    snapshot_pattern = r"## Context Snapshot\n.*?(?=\n## |\Z)"
    if "## Context Snapshot" in content:
        content = re.sub(snapshot_pattern, snapshot, content, flags=re.DOTALL)
    else:
        content = content.rstrip() + "\n\n" + snapshot

    # Update the Updated: field
    updated_pattern = r"Updated: .*"
    if re.search(updated_pattern, content):
        content = re.sub(updated_pattern, f"Updated: {now}", content)

    task_file.write_text(content)


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    project_root = find_project_root()
    if not project_root:
        sys.exit(0)

    task_file = project_root / ".claude" / "current-task.md"

    if not task_file.exists():
        sys.exit(0)

    try:
        update_task_snapshot(task_file, project_root)
    except Exception:
        # Never block compaction
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
