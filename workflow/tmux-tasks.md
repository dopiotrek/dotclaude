# Tmux Background Tasks

Use `tmux-task.sh` to run CLI tasks in background tmux sessions.

> **PATH requirement**: `~/.claude/scripts` must be on your PATH. `install.sh` adds this automatically. If the command isn't found, run `source ~/.zshrc` (or `~/.bashrc`) or re-run `install.sh`.

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
tmux-task.sh run <name> <command...>   # Spawn background task
tmux-task.sh status <name>             # Check: running/done/failed
tmux-task.sh read <name> [lines]       # Read output (default: last 50 lines)
tmux-task.sh wait <name> [timeout]     # Block until done (default: 300s)
tmux-task.sh kill <name>               # Kill a task
tmux-task.sh list                      # List active tasks
```

## Patterns

### Parallel build + lint
```bash
tmux-task.sh run build "cd $PROJECT && pnpm build"
tmux-task.sh run check "cd $PROJECT && pnpm check"
# ... do other work ...
tmux-task.sh wait build && tmux-task.sh read build
tmux-task.sh wait check && tmux-task.sh read check
```

### Delegate to Gemini CLI
```bash
tmux-task.sh run gemini-review "gemini -m flash 'Review this file for bugs' < src/lib/auth.ts"
# ... continue working ...
tmux-task.sh read gemini-review
```

### Persistent dev server
```bash
tmux-task.sh run dev "cd $PROJECT && pnpm dev"
# Server stays alive across tool calls
tmux-task.sh read dev  # Check for errors
tmux-task.sh kill dev  # When done
```

### GitHub operations
```bash
tmux-task.sh run pr "gh pr create --fill --draft"
tmux-task.sh wait pr && tmux-task.sh read pr
```

## Rules

- Always give tasks descriptive names (`build`, `typecheck`, `gemini-security-review`)
- Check `status` before `read` — if still running, output may be incomplete
- Use `wait` when the next step depends on the result
- Kill dev servers and long-running tasks when no longer needed
- Output is captured in the tmux pane — `read` gets the last N lines from the scrollback buffer
