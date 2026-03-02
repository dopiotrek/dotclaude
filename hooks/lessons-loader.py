#!/usr/bin/env python3
"""
UserPromptSubmit hook that injects relevant lessons into Claude's context.

Reads .claude/lessons.md, matches lesson tags against keywords in the
user's prompt, and outputs the top matches to stdout. Claude sees these
before processing the message — fresh context every time, immune to
context window eviction.

Keeps output compact: max 5 lessons, truncated to avoid bloating tokens.
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def find_project_root() -> Path | None:
    """Find the project root using git or fallback to cwd."""
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


def parse_lessons(content: str) -> list[dict]:
    """Parse lessons.md into structured entries."""
    lessons: list[dict] = []
    entries = re.split(r'\n## ', content)

    for entry in entries[1:]:  # skip the file header
        lines = entry.strip().split("\n")
        if not lines:
            continue

        header = lines[0]
        parts = header.split("|", 1)
        tags = [t.strip().lower() for t in parts[1].split(",")] if len(parts) > 1 else []
        body = "\n".join(lines[1:]).strip()

        # Skip lessons with unfilled rules (they're noise until reviewed)
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
            # Exact tag match in prompt
            if tag in prompt_lower:
                score += 2.0
            # Tag appears as a word boundary match
            elif tag in prompt_words:
                score += 1.5
            # Stem match (first 4+ chars) — catches migrate/migration, etc.
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

    lessons_file = project_root / ".claude" / "lessons.md"
    if not lessons_file.exists():
        sys.exit(0)

    try:
        content = lessons_file.read_text()
    except (IOError, OSError):
        sys.exit(0)

    lessons = parse_lessons(content)
    if not lessons:
        sys.exit(0)

    matched = match_lessons(prompt, lessons)
    if not matched:
        sys.exit(0)

    # Output to stdout — Claude sees this as pre-prompt context
    lines: list[str] = [
        "<past-lessons>",
        f"Relevant lessons from past sessions ({len(matched)} matched):",
        "",
    ]
    for lesson in matched:
        lines.append(f"## {lesson['header']}")
        # Truncate body to keep token usage reasonable
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
