#!/bin/bash
# Custom file suggestion script for Claude Code
# Uses rg + fzf for fuzzy matching and symlink support

# Parse JSON input to get query
QUERY=$(jq -r '.query // ""')

# Use project dir from env, fallback to pwd
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# cd into project dir so rg outputs relative paths
cd "$PROJECT_DIR" || exit 1

{
  # Directories - include folders so @ can match them too
  find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.svelte-kit/*' -not -path '*/.turbo/*' -not -path '*/dist/*' -not -path '*/.next/*' 2>/dev/null | sed 's|$|/|'

  # Files - respects .gitignore, includes hidden files, follows symlinks
  rg --files --follow --hidden . 2>/dev/null

  # Additional paths - include even if gitignored (uncomment and customize)
  # [ -e .notes ] && rg --files --follow --hidden --no-ignore-vcs .notes 2>/dev/null
} | sort -u | fzf --filter "$QUERY" | awk '{print (/\/$/ ? "0" : "1"), $0}' | sort -s -k1,1 | cut -d' ' -f2- | head -15
