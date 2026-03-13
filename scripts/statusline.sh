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
dir=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
dir_name="${dir##*/}"

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

used_str=$(format_tokens $current)
total_str=$(format_tokens $size)

# Context color based on usage
if [ "$pct_used" -ge 90 ]; then
    ctx_color="$red"
elif [ "$pct_used" -ge 70 ]; then
    ctx_color="$yellow"
elif [ "$pct_used" -ge 50 ]; then
    ctx_color="$orange"
else
    ctx_color="$green"
fi

# # Progress bar (uncomment to enable)
# BAR_WIDTH=20
# FILLED=$((pct_used * BAR_WIDTH / 100))
# [ "$FILLED" -gt "$BAR_WIDTH" ] && FILLED=$BAR_WIDTH
# EMPTY=$((BAR_WIDTH - FILLED))
# BAR=""
# [ "$FILLED" -gt 0 ] && BAR=$(printf "%${FILLED}s" | tr ' ' '█')
# [ "$EMPTY" -gt 0 ] && BAR="${BAR}$(printf "%${EMPTY}s" | tr ' ' '░')"

# # Cost & duration (uncomment to enable for API usage)
# cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
# cost_fmt=$(printf '$%.2f' "$cost")
# duration_ms=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')
# mins=$((duration_ms / 60000))
# secs=$(( (duration_ms % 60000) / 1000 ))

# Git branch (cached for performance)
CACHE_FILE="/tmp/statusline-git-cache-$$"
branch=""
if [ -n "$dir" ]; then
    # Use a stable cache key based on directory
    CACHE_FILE="/tmp/statusline-git-cache"
    CACHE_MAX_AGE=5
    cache_stale=true
    if [ -f "$CACHE_FILE" ]; then
        # Portable age check: create a reference file N seconds old, compare
        ref_file="/tmp/statusline-ref-$$"
        touch -d "$(date -d "${CACHE_MAX_AGE} seconds ago" 2>/dev/null || date -v-${CACHE_MAX_AGE}S 2>/dev/null)" "$ref_file" 2>/dev/null
        if [ -f "$ref_file" ] && [ "$CACHE_FILE" -nt "$ref_file" ]; then
            cache_stale=false
        fi
        rm -f "$ref_file"
    fi
    if $cache_stale; then
        if [ -d "${dir}/.git" ] || git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
            branch=$(git -C "$dir" symbolic-ref --short HEAD 2>/dev/null || git -C "$dir" rev-parse --short HEAD 2>/dev/null)
        fi
        echo "$branch" > "$CACHE_FILE"
    else
        branch=$(cat "$CACHE_FILE")
    fi
fi

# Thinking status
thinking=""
settings_path="$HOME/.claude/settings.json"
if [ -f "$settings_path" ]; then
    thinking_val=$(jq -r '.alwaysThinkingEnabled // false' "$settings_path" 2>/dev/null)
    [ "$thinking_val" = "true" ] && thinking=" ${dim}|${reset} ${orange}think${reset}"
fi

# ===== Output: Model | Branch | Context (%) | Thinking =====
line="${blue}${model_name}${reset}"
# [ -n "$dir_name" ] && line+=" ${dim}|${reset} 📁 ${dim}${dir_name}${reset}"  # uncomment to show repo name
[ -n "$branch" ] && line+=" ${dim}|${reset} ${cyan}${branch}${reset}"
line+=" ${dim}|${reset} ${ctx_color}${used_str}/${total_str} ${dim}(${pct_used}%)${reset}"
# line+=" ${dim}|${reset} ${yellow}${cost_fmt}${reset}"  # uncomment for cost
# line+=" ${dim}|${reset} ⏱ ${dim}${mins}m ${secs}s${reset}"  # uncomment for duration
line+="${thinking}"

printf "%b" "$line"
exit 0
