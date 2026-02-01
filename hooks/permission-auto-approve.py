#!/usr/bin/env python3
"""
PermissionRequest hook for auto-approving safe operations.

Based on Boris Cherny's tip #8c: Route permission requests through a hook
to auto-approve safe operations while maintaining security.

Exit behavior:
- Output JSON with "decision": "allow" to auto-approve
- Output JSON with "decision": "deny" + "message" to block
- Output nothing (exit 0) to prompt user normally
"""

import json
import re
import sys


# Safe tools that should always be approved
SAFE_TOOLS = frozenset([
    "Read",
    "Glob",
    "Grep",
    "LS",
    "Task",
    "WebSearch",
    "WebFetch",
    "mcp__svelte__list-sections",
    "mcp__svelte__get-documentation",
    "mcp__svelte__svelte-autofixer",
])

# Safe Bash command prefixes (read-only or low-risk)
SAFE_BASH_PREFIXES = [
    "git status",
    "git diff",
    "git log",
    "git branch",
    "git show",
    "git remote",
    "git fetch",
    "git rev-parse",
    "ls ",
    "ls\n",
    "tree ",
    "tree\n",
    "cat ",
    "head ",
    "tail ",
    "wc ",
    "file ",
    "which ",
    "whereis ",
    "type ",
    "pwd",
    "echo ",
    "printenv",
    "env ",
    "pnpm list",
    "pnpm why",
    "pnpm view",
    "pnpm outdated",
    "npm list",
    "npm why",
    "npm view",
    "node --version",
    "node -v",
    "pnpm --version",
    "npm --version",
    "python3 --version",
    "rg ",  # ripgrep
    "fd ",  # fd-find
    "jq ",  # json query
    "gh pr view",
    "gh issue view",
    "gh repo view",
    "gh api",
]

# Dangerous patterns that should ALWAYS be denied or require explicit approval
DANGEROUS_PATTERNS = [
    (r"rm\s+-rf\s+/(?!\S)", "Dangerous: rm -rf on root"),
    (r"rm\s+-rf\s+~", "Dangerous: rm -rf on home directory"),
    (r"sudo\s+rm", "Dangerous: sudo rm"),
    (r"sudo\s+chmod", "Dangerous: sudo chmod"),
    (r"chmod\s+777", "Dangerous: chmod 777 is insecure"),
    (r">\s*/dev/sd[a-z]", "Dangerous: writing to disk device"),
    (r">\s*/dev/null\s*2>&1\s*&", "Suspicious: silent background process"),
    (r"curl\s+[^|]*\|\s*(ba)?sh", "Dangerous: piping curl to shell"),
    (r"wget\s+[^|]*\|\s*(ba)?sh", "Dangerous: piping wget to shell"),
    (r"DROP\s+TABLE", "Dangerous: SQL DROP TABLE"),
    (r"DROP\s+DATABASE", "Dangerous: SQL DROP DATABASE"),
    (r"DELETE\s+FROM\s+\S+\s*(;|$)", "Dangerous: DELETE without WHERE clause"),
    (r"TRUNCATE\s+TABLE", "Dangerous: TRUNCATE TABLE"),
    (r":\(\)\s*\{\s*:\|:&\s*\}", "Dangerous: fork bomb"),
    (r"mkfs\.", "Dangerous: filesystem formatting"),
    (r"dd\s+if=", "Dangerous: dd can destroy data"),
    (r">\s*/etc/", "Dangerous: overwriting system config"),
    (r"--no-preserve-root", "Dangerous: bypassing root protection"),
]


def is_safe_tool(tool_name: str) -> bool:
    """Check if the tool is in the safe list."""
    return tool_name in SAFE_TOOLS


def is_safe_bash_command(command: str) -> bool:
    """Check if a Bash command matches safe prefixes."""
    command_stripped = command.strip()
    for prefix in SAFE_BASH_PREFIXES:
        if command_stripped.startswith(prefix) or command_stripped == prefix.strip():
            return True
    return False


def check_dangerous_patterns(command: str) -> str | None:
    """Check if command matches any dangerous patterns. Returns message if dangerous."""
    for pattern, message in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return message
    return None


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Always approve safe tools
    if is_safe_tool(tool_name):
        print(json.dumps({"decision": "allow"}))
        return

    # Handle Bash commands specifically
    if tool_name == "Bash":
        command = tool_input.get("command", "")

        # Check for dangerous patterns first
        danger_message = check_dangerous_patterns(command)
        if danger_message:
            print(json.dumps({
                "decision": "deny",
                "message": f"🚫 {danger_message}"
            }))
            return

        # Auto-approve safe Bash commands
        if is_safe_bash_command(command):
            print(json.dumps({"decision": "allow"}))
            return

    # For everything else, let the normal permission flow handle it
    # (output nothing, exit 0)
    pass


if __name__ == "__main__":
    main()
