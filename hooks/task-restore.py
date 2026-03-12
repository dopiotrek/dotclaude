#!/usr/bin/env python3
"""
PostToolUse hook (matcher: postcompact) — restores task context after compaction.

After Claude's context is compressed, most project-specific context is lost.
This hook reads the active task file (which was just updated by task-snapshot.py
during precompact) and injects it into Claude's context as a system message.

This is the READ side of the compaction bridge.
The WRITE side is task-snapshot.py (precompact).

Also fires on SessionStart (startup|resume) for session continuity.
"""

import json
import sys
import subprocess
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


def get_active_task(tasks_dir: Path) -> Path | None:
    """Find the most recently modified active task file."""
    active_dir = tasks_dir / "active"
    if not active_dir.exists():
        return None

    task_files = sorted(active_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    return task_files[0] if task_files else None


def get_features_summary(project_root: Path) -> str:
    """Get a compact summary of in-progress features."""
    features_file = project_root / ".claude" / "features.json"
    if not features_file.exists():
        return ""

    try:
        import json as json_mod
        data = json_mod.loads(features_file.read_text())
        in_progress = [f for f in data.get("features", []) if f.get("status") == "in-progress"]
        if not in_progress:
            return ""
        lines = ["Active features:"]
        for f in in_progress[:5]:
            lines.append(f"  - {f['name']} ({f.get('route', 'no route')}): {f.get('description', '')[:80]}")
        return "\n".join(lines)
    except Exception:
        return ""


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    project_root = find_project_root()
    if not project_root:
        sys.exit(0)

    tasks_dir = project_root / ".claude" / "tasks"
    task_file = get_active_task(tasks_dir)

    if not task_file:
        sys.exit(0)

    try:
        content = task_file.read_text().strip()
    except (IOError, OSError):
        sys.exit(0)

    if not content:
        sys.exit(0)

    # Build the context injection
    lines = [
        "=" * 60,
        "TASK CONTEXT RESTORED (post-compaction)",
        "=" * 60,
        "",
        content,
    ]

    # Also inject features context if available
    features = get_features_summary(project_root)
    if features:
        lines.extend(["", features])

    # Inject concept summary if available
    concept_file = project_root / ".claude" / "concept.md"
    if concept_file.exists():
        try:
            concept = concept_file.read_text().strip()
            # Only inject if it's been filled in (not just template comments)
            if concept and not all(line.startswith("<!--") or line.startswith("#") or not line.strip()
                                   for line in concept.split("\n")):
                lines.extend([
                    "",
                    "Product context: see .claude/concept.md",
                ])
        except Exception:
            pass

    lines.extend([
        "",
        "=" * 60,
        "Resume work on this task. Check the Plan section for next steps.",
        "Update the task file as you make progress.",
        "=" * 60,
    ])

    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
