#!/usr/bin/env python3
"""
UserPromptSubmit hook that injects relevant lessons into Claude's context.

Reads .claude/logs/ship-log.md, finds 💡 Lesson entries, matches their tags
against keywords in the user's prompt, and outputs the top matches to stdout.

Claude sees these before processing the message — fresh context every time,
immune to context window eviction.

Also supports legacy .claude/lessons.md for backward compatibility.

Keeps output compact: max 5 lessons, truncated to avoid bloating tokens.
"""

import json
import re
import subprocess
import sys
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


def parse_ship_log_lessons(content: str) -> list[dict]:
    """Parse 💡 lesson entries from ship-log.md."""
    lessons: list[dict] = []
    entries = re.split(r'\n## ', content)

    for entry in entries[1:]:
        lines = entry.strip().split("\n")
        if not lines:
            continue

        header = lines[0]

        # Only parse 💡 Lesson entries
        if "💡" not in header:
            continue

        # Extract tags from **Tags:** line
        tags: list[str] = []
        body_lines: list[str] = []
        for line in lines[1:]:
            if line.startswith("**Tags:**"):
                tag_str = line.replace("**Tags:**", "").strip()
                tags = [t.strip().lower() for t in tag_str.split(",")]
            elif line.strip() != "---":
                body_lines.append(line)

        body = "\n".join(body_lines).strip()

        # Skip lessons with unfilled rules
        if "TODO - fill in" in body:
            continue

        lessons.append({"header": header.strip(), "tags": tags, "body": body})

    return lessons


def parse_legacy_lessons(content: str) -> list[dict]:
    """Parse lessons from old-format lessons.md for backward compatibility."""
    lessons: list[dict] = []
    entries = re.split(r'\n## ', content)

    for entry in entries[1:]:
        lines = entry.strip().split("\n")
        if not lines:
            continue

        header = lines[0]
        parts = header.split("|", 1)
        tags = [t.strip().lower() for t in parts[1].split(",")] if len(parts) > 1 else []
        body = "\n".join(lines[1:]).strip()

        if "TODO - fill in" in body:
            continue

        lessons.append({"header": header.strip(), "tags": tags, "body": body})

    return lessons


def match_lessons(prompt: str, lessons: list[dict], max_results: int = 5) -> list[dict]:
    """Find lessons relevant to the current prompt using tag matching."""
    prompt_lower = prompt.lower()
    prompt_words = set(re.findall(r'\b\w+\b', prompt_lower))
    scored: list[tuple[float, dict]] = []

    for lesson in lessons:
        score = 0.0
        for tag in lesson["tags"]:
            if tag in prompt_lower:
                score += 2.0
            elif tag in prompt_words:
                score += 1.5
            elif len(tag) > 3:
                stem = tag[:4]
                if any(w.startswith(stem) for w in prompt_words):
                    score += 0.5

        if score > 0:
            scored.append((score, lesson))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:max_results]]


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = input_data.get("prompt", "")
    if not prompt or len(prompt) < 5:
        sys.exit(0)

    project_root = find_project_root()
    if not project_root:
        sys.exit(0)

    # Collect lessons from both sources
    all_lessons: list[dict] = []

    # Primary: ship-log.md
    ship_log = project_root / ".claude" / "logs" / "ship-log.md"
    if ship_log.exists():
        try:
            all_lessons.extend(parse_ship_log_lessons(ship_log.read_text()))
        except (IOError, OSError):
            pass

    # Legacy fallback: lessons.md
    legacy_file = project_root / ".claude" / "lessons.md"
    if legacy_file.exists():
        try:
            all_lessons.extend(parse_legacy_lessons(legacy_file.read_text()))
        except (IOError, OSError):
            pass

    if not all_lessons:
        sys.exit(0)

    matched = match_lessons(prompt, all_lessons)
    if not matched:
        sys.exit(0)

    lines: list[str] = [
        "<past-lessons>",
        f"Relevant lessons from past sessions ({len(matched)} matched):",
        "",
    ]
    for lesson in matched:
        lines.append(f"## {lesson['header']}")
        body = lesson["body"]
        if len(body) > 300:
            body = body[:300] + "..."
        lines.append(body)
        lines.append("")

    lines.append("Apply these lessons to avoid repeating past mistakes.")
    lines.append("</past-lessons>")

    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
