#!/bin/bash
# Claude Code SessionStart + CwdChanged hook: load the mise env (Node/Python version) of the current dir.
cat >/dev/null   # ignore hook input
[ -n "${CLAUDE_ENV_FILE:-}" ] || exit 0
/opt/homebrew/bin/mise env -s bash > "$CLAUDE_ENV_FILE" 2>/dev/null || true
exit 0
