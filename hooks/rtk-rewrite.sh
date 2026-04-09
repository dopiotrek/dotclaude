#!/bin/bash
# RTK auto-rewrite hook for Claude Code PreToolUse:Bash
# Transparently rewrites raw commands to their rtk equivalents.
# Outputs JSON with updatedInput to modify the command before execution.

# Guards: skip silently if dependencies missing
if ! command -v rtk &>/dev/null || ! command -v jq &>/dev/null; then
  exit 0
fi

set -euo pipefail

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$CMD" ]; then
  exit 0
fi

# Strip leading "cd ... && " prefix that Claude Code often prepends
CD_PREFIX=""
CD_REGEX='^(cd[[:space:]]+[^&]*&&[[:space:]]+)'
if [[ "$CMD" =~ $CD_REGEX ]]; then
  CD_PREFIX="${BASH_REMATCH[1]}"
  CMD="${CMD:${#CD_PREFIX}}"
fi

# Strip leading env var assignments (e.g., NODE_OPTIONS='...' pnpm check)
ENV_PREFIX=""
ENV_REGEX='^([A-Z_]+=[^ ]+ )+'
if [[ "$CMD" =~ $ENV_REGEX ]]; then
  ENV_PREFIX="${BASH_REMATCH[0]}"
  CMD="${CMD:${#ENV_PREFIX}}"
fi

FIRST_CMD="$CMD"

# Skip if already using rtk
case "$FIRST_CMD" in
  rtk\ *|*/rtk\ *) exit 0 ;;
esac

# Skip commands with heredocs
case "$FIRST_CMD" in
  *'<<'*) exit 0 ;;
esac

REWRITTEN=""

# --- Git commands ---
if echo "$FIRST_CMD" | grep -qE '^git\s+(status|diff|log|add|commit|push|pull|branch|fetch|stash|show)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^git /rtk git /')

# --- GitHub CLI ---
elif echo "$FIRST_CMD" | grep -qE '^gh\s+(pr|issue|run)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^gh /rtk gh /')

# --- Cargo ---
elif echo "$FIRST_CMD" | grep -qE '^cargo\s+(test|build|clippy|check)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^cargo /rtk cargo /')

# --- File operations ---
elif echo "$FIRST_CMD" | grep -qE '^cat(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^cat/rtk read/')
elif echo "$FIRST_CMD" | grep -qE '^(rg|grep)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(rg|grep)/rtk grep/')
elif echo "$FIRST_CMD" | grep -qE '^ls(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^ls/rtk ls/')

# --- JS/TS tooling (npx, pnpm, bare) ---
elif echo "$FIRST_CMD" | grep -qE '^(npx\s+|pnpm\s+)?vitest(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(npx |pnpm )?vitest/rtk vitest run/')
elif echo "$FIRST_CMD" | grep -qE '^pnpm\s+test(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^pnpm test/rtk vitest run/')
elif echo "$FIRST_CMD" | grep -qE '^(npx\s+|pnpm\s+)?tsc(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(npx |pnpm )?tsc/rtk tsc/')
elif echo "$FIRST_CMD" | grep -qE '^(npx\s+|pnpm\s+)?svelte-check(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(npx |pnpm )?svelte-check/rtk svelte-check/')
elif echo "$FIRST_CMD" | grep -qE '^(pnpm\s+)?lint(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(pnpm )?lint/rtk lint/')
elif echo "$FIRST_CMD" | grep -qE '^(npx\s+|pnpm\s+)?eslint(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(npx |pnpm )?eslint/rtk lint/')
elif echo "$FIRST_CMD" | grep -qE '^(npx\s+|pnpm\s+)?prettier(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(npx |pnpm )?prettier/rtk prettier/')
elif echo "$FIRST_CMD" | grep -qE '^(npx\s+|pnpm\s+)?playwright(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(npx |pnpm )?playwright/rtk playwright/')
elif echo "$FIRST_CMD" | grep -qE '^(npx\s+)?prisma(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(npx )?prisma/rtk prisma/')
elif echo "$FIRST_CMD" | grep -qE '^pnpm\s+install(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^pnpm install/rtk pnpm install/')

# --- Containers ---
elif echo "$FIRST_CMD" | grep -qE '^docker\s+(ps|images|logs)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^docker /rtk docker /')
elif echo "$FIRST_CMD" | grep -qE '^kubectl\s+(get|logs)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^kubectl /rtk kubectl /')

# --- Network ---
elif echo "$FIRST_CMD" | grep -qE '^curl\s+'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^curl /rtk curl /')

# --- pnpm package management ---
elif echo "$FIRST_CMD" | grep -qE '^pnpm\s+(list|ls|outdated)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^pnpm /rtk pnpm /')

# --- Python tooling ---
elif echo "$FIRST_CMD" | grep -qE '^(python\s+-m\s+)?pytest(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed -E 's/^(python -m )?pytest/rtk pytest/')
elif echo "$FIRST_CMD" | grep -qE '^ruff\s+(check|format)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^ruff /rtk ruff /')
elif echo "$FIRST_CMD" | grep -qE '^pip\s+(list|outdated|install|show)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^pip /rtk pip /')
elif echo "$FIRST_CMD" | grep -qE '^uv\s+pip\s+(list|outdated|install|show)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^uv pip /rtk pip /')

# --- Go tooling ---
elif echo "$FIRST_CMD" | grep -qE '^go\s+(test|build|vet)(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^go /rtk go /')
elif echo "$FIRST_CMD" | grep -qE '^golangci-lint(\s|$)'; then
  REWRITTEN=$(echo "$CMD" | sed 's/^golangci-lint/rtk golangci-lint/')
fi

# Prepend env vars and cd prefix if they were stripped
if [ -n "$ENV_PREFIX" ] && [ -n "$REWRITTEN" ]; then
  REWRITTEN="${ENV_PREFIX}${REWRITTEN}"
fi
if [ -n "$CD_PREFIX" ] && [ -n "$REWRITTEN" ]; then
  REWRITTEN="${CD_PREFIX}${REWRITTEN}"
fi

# If no rewrite needed, approve as-is
if [ -z "$REWRITTEN" ]; then
  exit 0
fi

# Build the updated tool_input with all original fields preserved, only command changed
ORIGINAL_INPUT=$(echo "$INPUT" | jq -c '.tool_input')
UPDATED_INPUT=$(echo "$ORIGINAL_INPUT" | jq --arg cmd "$REWRITTEN" '.command = $cmd')

# Output the rewrite instruction
jq -n \
  --argjson updated "$UPDATED_INPUT" \
  '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "allow",
      "permissionDecisionReason": "RTK auto-rewrite",
      "updatedInput": $updated
    }
  }'
