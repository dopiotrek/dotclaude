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


def extract_meaningful_error(raw_output: str) -> str | None:
    """Extract a meaningful error message, skipping noise."""
    lines = [l.strip() for l in raw_output.split("\n") if l.strip()]

    # Skip lines that are just file paths or counts
    noise_patterns = [
        r"^\d+ error",
        r"^Found \d+",
        r"^\s*$",
        r"^ELIFECYCLE",
        r"^ERR!",
    ]

    for line in lines:
        if any(re.match(p, line) for p in noise_patterns):
            continue
        if len(line) > 20:  # Skip very short lines
            return line[:150]

    return lines[0][:150] if lines else None


def is_duplicate(ship_log: Path, error_key: str) -> bool:
    """Check if we already logged a similar lesson today."""
    if not ship_log.exists():
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    content = ship_log.read_text()

    # Same date + same error signature = duplicate
    return today in content and error_key[:50] in content


def append_lesson(project_root: Path, tags: list[str], check_name: str,
                  error_preview: str, changed_files: list[str]):
    """Append a 💡 lesson entry to the ship-log."""
    ship_log = project_root / ".claude" / "logs" / "ship-log.md"

    if not ship_log.exists():
        ship_log.parent.mkdir(parents=True, exist_ok=True)
        ship_log.write_text(
            "# Ship Log — dronelist.io\n\n"
            "<!-- 🚀 = shipped. 💡 = learned. Auto-maintained by hooks + CLAUDE.md. -->\n\n"
        )

    if is_duplicate(ship_log, error_preview):
        return

    date = datetime.now().strftime("%Y-%m-%d")
    tag_str = ", ".join(tags) if tags else "general"
    files_str = ", ".join(changed_files[:3])
    if len(changed_files) > 3:
        files_str += f" (+{len(changed_files) - 3} more)"

    entry = (
        f"## {date} | 💡 Lesson: {check_name} failure in {files_str}\n\n"
        f"**What broke:** {error_preview}\n\n"
        f"**Rule:** TODO - fill in after reviewing the root cause\n\n"
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
                    "stderr": result.stderr[-500:] if result.stderr else "",
                    "stdout": result.stdout[-500:] if result.stdout else "",
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
        error_preview = extract_meaningful_error(raw_output)
        if not error_preview:
            continue

        tags = infer_tags(changed_files, raw_output)
        append_lesson(project_root, tags, check["name"], error_preview, changed_files)

    sys.exit(0)


if __name__ == "__main__":
    main()
