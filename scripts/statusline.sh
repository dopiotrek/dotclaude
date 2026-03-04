#!/bin/bash
input=$(cat)

if [ -z "$input" ]; then
    printf "Claude"
    exit 0
fi

# ANSI colors matching oh-my-posh theme
blue=$'\033[38;2;0;153;255m'
orange=$'\033[38;2;255;176;85m'
green=$'\033[38;2;0;160;0m'
cyan=$'\033[38;2;46;149;153m'
red=$'\033[38;2;255;85;85m'
yellow=$'\033[38;2;230;200;0m'
dim=$'\033[2m'
rst=$'\033[0m'
SEP="${dim} | ${rst}"

# --- model ---
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')

# --- git branch ---
dir=$(echo "$input" | jq -r '.cwd // ""')
branch=""
if [ -n "$dir" ] && [ -d "${dir}/.git" ]; then
    branch=$(git -C "$dir" symbolic-ref --short HEAD 2>/dev/null || git -C "$dir" rev-parse --short HEAD 2>/dev/null)
fi

# --- context window ---
ctx_str=""
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
if [ -n "$used_pct" ]; then
    used_int=$(printf "%.0f" "$used_pct")
    ctx_used=$(echo "$input" | jq -r '(.context_window.current_usage.cache_read_input_tokens + .context_window.current_usage.cache_creation_input_tokens + .context_window.current_usage.input_tokens + .context_window.current_usage.output_tokens) // empty' 2>/dev/null)
    ctx_total=$(echo "$input" | jq -r '.context_window.context_window_size // empty' 2>/dev/null)

    # Color based on usage
    ctx_color="$green"
    [ "$used_int" -ge 50 ] 2>/dev/null && ctx_color="$orange"
    [ "$used_int" -ge 70 ] 2>/dev/null && ctx_color="$yellow"
    [ "$used_int" -ge 90 ] 2>/dev/null && ctx_color="$red"

    if [ -n "$ctx_used" ] && [ -n "$ctx_total" ]; then
        ctx_used_k=$(( ctx_used / 1000 ))
        ctx_total_k=$(( ctx_total / 1000 ))
        ctx_str="${ctx_color}${used_int}%${rst} ${dim}(${ctx_used_k}k/${ctx_total_k}k)${rst}"
    else
        ctx_str="${ctx_color}${used_int}%${rst}"
    fi
fi

# --- thinking status ---
thinking=""
settings_path="$HOME/.claude/settings.json"
if [ -f "$settings_path" ]; then
    thinking_val=$(jq -r '.alwaysThinkingEnabled // false' "$settings_path" 2>/dev/null)
    if [ "$thinking_val" = "true" ]; then
        thinking="${orange}think${rst}"
    fi
fi

# ===== model | branch | ctx | thinking =====
printf "%s" "${blue}${model}${rst}"
[ -n "$branch" ] && printf "%s" "${SEP}${cyan}${branch}${rst}"
[ -n "$ctx_str" ] && printf "%s" "${SEP}${ctx_str}"
[ -n "$thinking" ] && printf "%s" "${SEP}${thinking}"
