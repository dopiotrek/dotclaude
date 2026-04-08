#!/bin/bash
# Custom file suggestion script for Claude Code
# Uses rg + fzf for fuzzy matching
#
# Optimized: removed --follow (symlink recursion), replaced find with rg,
# added timeout, expanded exclusions, removed redundant sort.

# Parse JSON input to get query
QUERY=$(jq -r '.query // ""')

# Use project dir from env, fallback to pwd
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# cd into project dir so rg outputs relative paths
cd "$PROJECT_DIR" || exit 1

# macOS-compatible timeout wrapper (GNU timeout may not exist)
_timeout() {
  local secs=$1; shift
  if command -v gtimeout &>/dev/null; then
    gtimeout "$secs" "$@"
  elif command -v timeout &>/dev/null; then
    timeout "$secs" "$@"
  else
    # Fallback: run without timeout
    "$@"
  fi
}

# Common dirs to exclude (beyond .gitignore)
EXCLUDES=(
  --glob '!.git'
  --glob '!node_modules'
  --glob '!.svelte-kit'
  --glob '!.turbo'
  --glob '!.next'
  --glob '!.nuxt'
  --glob '!.vercel'
  --glob '!.cache'
  --glob '!.tmp'
  --glob '!dist'
  --glob '!build'
  --glob '!target'
  --glob '!coverage'
  --glob '!__pycache__'
  --glob '!.DS_Store'
)

{
  # Directories — extract unique dirs from rg file list
  # Much faster than `find` since rg already respects .gitignore
  _timeout 3 rg --files --hidden "${EXCLUDES[@]}" . 2>/dev/null \
    | sed 's|/[^/]*$||' | sort -u | sed 's|$|/|'

  # Files — no --follow (avoids symlink recursion), respects .gitignore
  _timeout 3 rg --files --hidden "${EXCLUDES[@]}" . 2>/dev/null
} | fzf --filter "$QUERY" | awk '!seen[$0]++ {print (/\/$/ ? "0" : "1"), $0}' | sort -s -k1,1 | cut -d' ' -f2- | head -15
