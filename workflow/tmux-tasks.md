# Tmux Background Tasks

Use `~/.claude/scripts/tmux-task.sh` to run CLI tasks in background tmux sessions.

> **Always use the full path** `~/.claude/scripts/tmux-task.sh` — Claude Code subshells do not source `.zshrc` and won't have `~/.claude/scripts` on PATH.

## When to Use

- **Parallel work**: Run build/check/test while continuing to edit code
- **Long processes**: Dev servers, large builds, migrations
- **CLI delegation**: Send work to `gemini`, `gh`, `vercel`, or any CLI tool
- **Multi-step pipelines**: Chain tasks that don't need interactivity

## When NOT to Use

- Quick commands that finish in <5 seconds — just run them inline
- Interactive CLIs that need back-and-forth input
- Anything requiring real-time streaming output in conversation

## Commands

```bash
~/.claude/scripts/tmux-task.sh run <name> <command...>   # Spawn background task
~/.claude/scripts/tmux-task.sh status <name>             # Check: running/done/failed
~/.claude/scripts/tmux-task.sh read <name> [lines]       # Read output (default: last 50 lines)
~/.claude/scripts/tmux-task.sh wait <name> [timeout]     # Block until done (default: 300s)
~/.claude/scripts/tmux-task.sh kill <name>               # Kill a task
~/.claude/scripts/tmux-task.sh list                      # List active tasks
```

## Patterns

### Parallel build + lint
```bash
~/.claude/scripts/tmux-task.sh run build "cd $PROJECT && pnpm build"
~/.claude/scripts/tmux-task.sh run check "cd $PROJECT && pnpm check"
# ... do other work ...
~/.claude/scripts/tmux-task.sh wait build && ~/.claude/scripts/tmux-task.sh read build
~/.claude/scripts/tmux-task.sh wait check && ~/.claude/scripts/tmux-task.sh read check
```

### Delegate to Gemini CLI
```bash
~/.claude/scripts/tmux-task.sh run gemini-review "gemini -m flash 'Review this file for bugs' < src/lib/auth.ts"
# ... continue working ...
~/.claude/scripts/tmux-task.sh read gemini-review
```

### Persistent dev server
```bash
~/.claude/scripts/tmux-task.sh run dev "cd $PROJECT && pnpm dev"
# Server stays alive across tool calls
~/.claude/scripts/tmux-task.sh read dev  # Check for errors
~/.claude/scripts/tmux-task.sh kill dev  # When done
```

### GitHub operations
```bash
~/.claude/scripts/tmux-task.sh run pr "gh pr create --fill --draft"
~/.claude/scripts/tmux-task.sh wait pr && ~/.claude/scripts/tmux-task.sh read pr
```

## Rules

- Always give tasks descriptive names (`build`, `typecheck`, `gemini-security-review`)
- Check `status` before `read` — if still running, output may be incomplete
- Use `wait` when the next step depends on the result
- Kill dev servers and long-running tasks when no longer needed
- Output is captured in the tmux pane — `read` gets the last N lines from the scrollback buffer
