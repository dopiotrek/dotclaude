#!/bin/bash
set -f  # disable globbing

input=$(cat)

if [ -z "$input" ]; then
    printf "Claude"
    exit 0
fi

# ANSI colors matching oh-my-posh theme
blue='\033[38;2;0;153;255m'
orange='\033[38;2;255;176;85m'
green='\033[38;2;0;160;0m'
cyan='\033[38;2;46;149;153m'
red='\033[38;2;255;85;85m'
yellow='\033[38;2;230;200;0m'
dim='\033[2m'
reset='\033[0m'

# ===== Extract data from JSON =====
model_name=$(echo "$input" | jq -r '.model.display_name // "Claude"')

# Context window
size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
[ "$size" -eq 0 ] 2>/dev/null && size=200000

# Token usage (input + cache)
input_tokens=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
cache_create=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
cache_read=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
current=$(( input_tokens + cache_create + cache_read ))

if [ "$size" -gt 0 ]; then
    pct_used=$(( current * 100 / size ))
else
    pct_used=0
fi

# Format token counts (e.g., 50k / 200k)
format_tokens() {
    local num=$1
    if [ "$num" -ge 1000000 ]; then
        awk "BEGIN {printf \"%.1fm\", $num / 1000000}"
    elif [ "$num" -ge 1000 ]; then
        awk "BEGIN {printf \"%.0fk\", $num / 1000}"
    else
        printf "%d" "$num"
    fi
}

used_tokens=$(format_tokens $current)
total_tokens=$(format_tokens $size)

# Context color
ctx_color="$green"
[ "$pct_used" -ge 50 ] 2>/dev/null && ctx_color="$orange"
[ "$pct_used" -ge 70 ] 2>/dev/null && ctx_color="$yellow"
[ "$pct_used" -ge 90 ] 2>/dev/null && ctx_color="$red"

# Git branch from cwd
dir=$(echo "$input" | jq -r '.cwd // ""')
branch=""
if [ -n "$dir" ] && [ -d "${dir}/.git" ]; then
    branch=$(git -C "$dir" symbolic-ref --short HEAD 2>/dev/null || git -C "$dir" rev-parse --short HEAD 2>/dev/null)
fi

# Thinking status
thinking_on=false
settings_path="$HOME/.claude/settings.json"
if [ -f "$settings_path" ]; then
    thinking_val=$(jq -r '.alwaysThinkingEnabled // false' "$settings_path" 2>/dev/null)
    [ "$thinking_val" = "true" ] && thinking_on=true
fi

# ===== Build line =====
# Model | branch | ctx used/total (%) | thinking
line="${blue}${model_name}${reset}"
[ -n "$branch" ] && line+=" ${dim}|${reset} ${cyan}${branch}${reset}"
line+=" ${dim}|${reset} ${ctx_color}${used_tokens} / ${total_tokens}${reset} ${dim}(${pct_used}%)${reset}"
if $thinking_on; then
    line+=" ${dim}|${reset} ${orange}think${reset}"
fi

printf "%b" "$line"
exit 0
