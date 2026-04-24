#!/usr/bin/env bash
# tmux-task.sh — Spawn, check, and collect background CLI tasks.
#
# Usage:
#   tmux-task.sh run <name> <command...>   — Run command in background session
#   tmux-task.sh status <name>             — Check if session is still running
#   tmux-task.sh read <name> [lines]       — Read last N lines of output (default: 50)
#   tmux-task.sh wait <name> [timeout]     — Block until done (default: 300s)
#   tmux-task.sh kill <name>               — Kill a session
#   tmux-task.sh list                      — List active task sessions
#
# Sessions are prefixed with "task-" to avoid collisions.

set -euo pipefail

PREFIX="task-"

cmd="${1:-help}"
shift || true

case "$cmd" in
  run)
    name="${1:?Usage: tmux-task.sh run <name> <command...>}"
    shift
    session="${PREFIX}${name}"

    # Kill existing session with same name
    tmux kill-session -t "$session" 2>/dev/null || true

    # Create detached session running the command
    # Tee output to a log file so `read` works even after the session exits
    marker="/tmp/tmux-task-${name}.done"
    log="/tmp/tmux-task-${name}.log"
    rm -f "$marker" "$log"
    tmux new-session -d -s "$session" -x 200 -y 50 \
      "( $* ) 2>&1 | tee $log; echo \${PIPESTATUS[0]} > $marker"

    echo "✅ Started: $session"
    echo "   Command: $*"
    echo "   Check:   ~/.claude/scripts/tmux-task.sh status $name"
    echo "   Read:    ~/.claude/scripts/tmux-task.sh read $name"
    ;;

  status)
    name="${1:?Usage: tmux-task.sh status <name>}"
    session="${PREFIX}${name}"
    marker="/tmp/tmux-task-${name}.done"

    if [ -f "$marker" ]; then
      code=$(cat "$marker")
      if [ "$code" = "0" ]; then
        echo "✅ Completed (exit 0)"
      else
        echo "❌ Failed (exit $code)"
      fi
    elif tmux has-session -t "$session" 2>/dev/null; then
      echo "⏳ Running"
    else
      echo "❓ No such task"
    fi
    ;;

  read)
    name="${1:?Usage: tmux-task.sh read <name> [lines]}"
    lines="${2:-50}"
    session="${PREFIX}${name}"
    log="/tmp/tmux-task-${name}.log"

    if tmux has-session -t "$session" 2>/dev/null; then
      # Still running — capture live pane
      tmux capture-pane -t "$session" -p -S "-${lines}"
    elif [ -f "$log" ]; then
      # Session exited but log persists — tail it
      tail -n "$lines" "$log"
    else
      echo "No output found for task: $name"
      exit 1
    fi
    ;;

  wait)
    name="${1:?Usage: tmux-task.sh wait <name> [timeout_seconds]}"
    timeout="${2:-300}"
    marker="/tmp/tmux-task-${name}.done"
    session="${PREFIX}${name}"
    elapsed=0

    while [ ! -f "$marker" ] && [ "$elapsed" -lt "$timeout" ]; do
      sleep 2
      elapsed=$((elapsed + 2))
    done

    if [ -f "$marker" ]; then
      code=$(cat "$marker")
      # Print final output from log (works even if session already exited)
      log="/tmp/tmux-task-${name}.log"
      [ -f "$log" ] && tail -n 100 "$log" || tmux capture-pane -t "$session" -p -S -100 2>/dev/null || true
      exit "$code"
    else
      echo "⏰ Timeout after ${timeout}s"
      exit 124
    fi
    ;;

  kill)
    name="${1:?Usage: tmux-task.sh kill <name>}"
    session="${PREFIX}${name}"
    tmux kill-session -t "$session" 2>/dev/null && echo "Killed: $session" || echo "No such session"
    rm -f "/tmp/tmux-task-${name}.done" "/tmp/tmux-task-${name}.log"
    ;;

  list)
    tmux list-sessions -F '#{session_name} #{session_created_string}' 2>/dev/null \
      | grep "^${PREFIX}" \
      | sed "s/^${PREFIX}//" \
      || echo "No active tasks"
    ;;

  *)
    echo "Usage: tmux-task.sh {run|status|read|wait|kill|list} [args...]"
    exit 1
    ;;
esac
