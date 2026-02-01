#!/usr/bin/env python3
"""
PreToolUse hook: Log all Claude Code tool usage for audit and debugging.
Logs: timestamp, tool name, file path, and key parameters.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "command-log.txt"


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "Unknown")
    tool_input = input_data.get("tool_input", {})

    # Extract relevant info based on tool type
    details = []

    # File path (for Edit, Write, Read, etc.)
    file_path = tool_input.get("file_path") or tool_input.get("path", "")
    if file_path:
        # Shorten path for readability
        path = Path(file_path)
        short_path = f".../{path.parent.name}/{path.name}" if len(str(path)) > 50 else str(path)
        details.append(f"file={short_path}")

    # Command (for Bash)
    command = tool_input.get("command", "")
    if command:
        # Truncate long commands
        short_cmd = command[:80] + "..." if len(command) > 80 else command
        short_cmd = short_cmd.replace("\n", " ")
        details.append(f"cmd={short_cmd}")

    # Pattern (for Grep, Glob)
    pattern = tool_input.get("pattern", "")
    if pattern:
        details.append(f"pattern={pattern[:40]}")

    # URL (for WebFetch)
    url = tool_input.get("url", "")
    if url:
        details.append(f"url={url[:60]}")

    # Build log line
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    details_str = " | ".join(details) if details else "no details"
    log_line = f"[{timestamp}] {tool_name}: {details_str}\n"

    # Append to log
    with open(LOG_FILE, "a") as f:
        f.write(log_line)

    # PreToolUse: exit 0 to allow the tool to proceed
    sys.exit(0)


if __name__ == "__main__":
    main()
