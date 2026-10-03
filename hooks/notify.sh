#!/bin/bash
# Claude Code Notification hook: macOS notification, click opens Ghostty.
in=$(cat)
proj=$(basename "$(jq -r '.cwd // "?"' <<<"$in")")
msg=$(jq -r '.message // "Needs your input"' <<<"$in")
/opt/homebrew/bin/terminal-notifier -title "Claude · $proj" -message "$msg" -sound Glass \
  -activate com.mitchellh.ghostty -group "claude-$proj" >/dev/null 2>&1
exit 0
