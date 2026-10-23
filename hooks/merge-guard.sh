#!/usr/bin/env bash
# PreToolUse(Bash): agents merge only through safe-merge. A raw `gh pr merge`
# would hit the ask rule and prompt; a deny makes the agent switch instead.
# safe-merge calls gh itself, outside Claude, so it is not affected.
command -v jq &>/dev/null || exit 0
CMD=$(jq -r '.tool_input.command // empty')
[[ "$CMD" =~ (^|[\;\&\|\(]|\$\(|[[:space:]](then|do)[[:space:]])[[:space:]]*(rtk[[:space:]]+)?gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$) ]] || exit 0
jq -n '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: "Blocked: agents do not run `gh pr merge`. Use `safe-merge <pr> <head-sha> [owner/repo]`: it checks the head SHA, that main has not moved and that checks are green, then merges with no prompt. If it refuses, fix what it names (rebase, re-run verify, wait for checks); if the PR has no checks, leave it open for Piotrek. Do not cd first."
  }
}'
