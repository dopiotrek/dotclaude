#!/usr/bin/env python3
"""
PostToolUse hook: Auto-format code files after edits.
Supports: Prettier (JS/TS/CSS/HTML/JSON/Svelte), Black (Python), gofmt, rustfmt, php-cs-fixer
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

# Map file extensions to formatters
# Each entry: extension -> (formatter_cmd, check_cmd, description)
FORMATTERS = {
    # JavaScript/TypeScript ecosystem (Prettier)
    ".js": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".jsx": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".ts": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".tsx": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".json": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".css": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".scss": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".html": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".md": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".yaml": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".yml": (["npx", "prettier", "--write"], "prettier", "Prettier"),
    ".svelte": (["npx", "prettier", "--write", "--plugin", "prettier-plugin-svelte"], "prettier", "Prettier"),

    # Python (Black)
    ".py": (["black", "--quiet"], "black", "Black"),

    # Go (gofmt)
    ".go": (["gofmt", "-w"], "gofmt", "gofmt"),

    # Rust (rustfmt)
    ".rs": (["rustfmt"], "rustfmt", "rustfmt"),

    # PHP (php-cs-fixer)
    ".php": (["php-cs-fixer", "fix", "--quiet"], "php-cs-fixer", "php-cs-fixer"),
}

# Files/directories to skip
SKIP_PATTERNS = [
    "node_modules",
    ".svelte-kit",
    "build",
    "dist",
    ".vercel",
    "vendor",
    "__pycache__",
    ".git",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
]


def should_skip(file_path: str) -> bool:
    """Check if file should be skipped."""
    for pattern in SKIP_PATTERNS:
        if pattern in file_path:
            return True
    return False


def format_file(file_path: str) -> None:
    """Format a file using the appropriate formatter."""
    path = Path(file_path)

    if not path.exists():
        return

    if should_skip(file_path):
        return

    suffix = path.suffix.lower()
    if suffix not in FORMATTERS:
        return

    cmd_parts, check_cmd, formatter_name = FORMATTERS[suffix]

    # Check if formatter is available
    if not shutil.which(check_cmd) and check_cmd != "prettier":
        return

    # Build full command
    cmd = cmd_parts + [str(path)]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=path.parent
        )

        pass  # Silent success/failure

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")

    if tool_name not in ("Edit", "MultiEdit", "Write"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})

    # Check if operation was successful
    success = tool_response.get("success", True)
    if not success:
        sys.exit(0)

    # Get file path
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")

    if file_path:
        format_file(file_path)

    # PostToolUse hooks should not block
    sys.exit(0)


if __name__ == "__main__":
    main()
