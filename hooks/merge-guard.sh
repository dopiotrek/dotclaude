#!/usr/bin/env bash
# PreToolUse(Bash): agents land PRs with GitHub auto-merge (`gh pr merge --auto`),
# which waits for the base branch's required checks. An immediate merge or
# `--admin` would skip them, so those are denied; a deny makes the agent switch.
# safe-merge calls gh itself, outside Claude, so it is not affected.
command -v jq &>/dev/null || exit 0
CMD=$(jq -r '.tool_input.command // empty')
MERGE='(^|[\;\&\|\(]|\$\(|[[:space:]](then|do)[[:space:]])[[:space:]]*(rtk[[:space:]]+)?gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$)'
[[ "$CMD" =~ $MERGE ]] || exit 0

deny() {
  jq -n --arg r "$1" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  exit 0
}
# Every merge in a compound command must be an auto-merge, not just the first.
while IFS= read -r seg; do
  [[ "$seg" =~ (^|[[:space:]])gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$) ]] || continue
  [[ "$seg" =~ (^|[[:space:]])--admin([[:space:]=]|$) ]] && deny "Blocked: never use \`gh pr merge --admin\`. It skips the required checks."
  [[ "$seg" =~ (^|[[:space:]])--(auto|disable-auto)([[:space:]]|$) ]] && continue
  deny "Blocked: agents do not merge a PR right away. Run \`gh pr merge <pr> --auto --squash [-R owner/repo]\`: GitHub merges it when the required checks pass. If the base branch has no required checks, use \`safe-merge --verified <pr> <head-sha>\` after \`pnpm verify\` passed on that head. Do not cd first."
done < <(sed -E 's/(&&|\|\||[;&|]|\$\(|\))/\n/g' <<<"$CMD")
exit 0
