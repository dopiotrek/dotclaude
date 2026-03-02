#!/usr/bin/env python3
"""
Stop hook that appends lessons when verification checks fail.

Runs alongside stop-verification.py. When tsc or svelte-check fails,
it logs what broke, which files were involved, and auto-tags the entry
so the lessons-loader can match it to future prompts.

The 'Rule:' line is left as a placeholder — Claude will fill it in
on the next interaction when it sees the lesson in context.
"""

import json
import subprocess
import sys
from datetime import datetime
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


def get_changed_files(project_root: Path) -> list[str]:
    """Get files changed since last commit (staged + unstaged + untracked)."""
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
    return list(dict.fromkeys(files))  # dedupe, preserve order


def infer_tags(files: list[str], error_output: str) -> list[str]:
    """Infer lesson tags from changed files and error output."""
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


def is_duplicate(lessons_file: Path, error_first_line: str) -> bool:
    """Check if we already logged a very similar lesson today."""
    if not lessons_file.exists():
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    content = lessons_file.read_text()

    # Simple dedup: same date + same first error line
    return today in content and error_first_line[:60] in content


def append_lesson(project_root: Path, tags: list[str], check_name: str,
                  error_preview: str, changed_files: list[str]):
    """Append a lesson entry to .claude/lessons.md."""
    lessons_dir = project_root / ".claude"
    lessons_dir.mkdir(parents=True, exist_ok=True)
    lessons_file = lessons_dir / "lessons.md"

    if not lessons_file.exists():
        lessons_file.write_text("# Lessons Learned\n\n"
                                "<!-- Auto-populated by lessons-writer.py stop hook. -->\n"
                                "<!-- Edit freely: fix Rules, add context, remove noise. -->\n\n")

    if is_duplicate(lessons_file, error_preview):
        return

    date = datetime.now().strftime("%Y-%m-%d")
    tag_str = ", ".join(tags) if tags else "general"
    files_str = ", ".join(changed_files[:5])
    if len(changed_files) > 5:
        files_str += f" (+{len(changed_files) - 5} more)"

    entry = (
        f"## {date} | {tag_str}\n"
        f"{check_name} check failed after editing: {files_str}\n"
        f"Error: {error_preview}\n"
        f"Rule: TODO - fill in after reviewing the root cause\n\n"
    )

    with open(lessons_file, "a") as f:
        f.write(entry)


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    project_root = find_project_root()
    if not project_root:
        sys.exit(0)

    # Only run checks if this is a SvelteKit/TS project
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
        # Grab a meaningful error line (skip blank lines)
        error_lines = [l for l in raw_output.split("\n") if l.strip()]
        error_preview = error_lines[0][:150] if error_lines else "Unknown error"

        tags = infer_tags(changed_files, raw_output)
        append_lesson(project_root, tags, check["name"], error_preview, changed_files)

    sys.exit(0)


if __name__ == "__main__":
    main()
