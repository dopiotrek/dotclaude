# dotclaude

> Claude Code configuration framework — hooks, agents, skills, settings.

My personal, shareable [Claude Code](https://claude.ai/download) setup: automated guardrails for a SvelteKit / Svelte 5 / Supabase / Drizzle / Turborepo stack, specialized subagents, a library of skills, and sensible defaults. The repo is the single source of truth; `install.sh` symlinks it into `~/.claude`.

> Component counts below are intentionally approximate — run `./install.sh` and read its summary for the exact numbers on your checkout, so this README can't drift out of date.

## What's included

| Component     | Roughly | What it is                                                       |
| ------------- | ------- | ---------------------------------------------------------------- |
| **Hooks**     | ~10     | PreToolUse / PostToolUse / Stop guardrails (security, format, DB) |
| **Agents**    | ~9      | Specialized subagents (frontend, backend, debug, review, …)      |
| **Skills**    | ~20 + vendored | Reusable procedures; plus a vendored `gstack/` skill set    |
| **Settings**  | 1       | `settings/settings.template.json` (`$HOME` is expanded on install) |
| **CLAUDE.md** | 1       | Global preferences and instructions                              |

## Quick start

```bash
git clone https://github.com/dopiotrek/dotclaude.git ~/repos/dotclaude
cd ~/repos/dotclaude
./install.sh        # symlinks ~/.claude → this repo, generates settings.json
claude              # start a new session
```

### Install options

```bash
./install.sh             # symlink mode (recommended): edits here apply live
./install.sh --copy      # copy instead of symlink
./install.sh --uninstall # remove symlinks, optionally restore backup
```

The installer symlinks `CLAUDE.md`, `RTK.md`, `hooks/`, `agents/`, `skills/`, `scripts/`, and `mining/` into `~/.claude`, generates `~/.claude/settings.json` from the template (expanding `$HOME`), marks hook scripts executable, and adds `~/.claude/scripts` to your shell `PATH`.

## Hooks

Python (and one shell) scripts that run around tool calls. Each path-sensitive hook self-checks the file path and exits early when irrelevant, so they're registered under a broad `matcher` with no `if` filter. Exit codes: `0` allow, `1` warn (stderr to you), `2` block (stderr to Claude).

**Security**

- `no-secrets.py` — blocks hardcoded keys/tokens/passwords on write (`sk_live_*`, `sk-*`, Supabase service-role keys, JWTs).

**Code quality**

- `auto-format.py` — formats after edits (Prettier, Black, gofmt, rustfmt, php-cs-fixer).
- `import-path-validator.py` — enforces monorepo import conventions (`@pkg/*`, `$lib/`, `$app/state` over `$app/stores`).
- `sveltekit-route-validator.py` — checks SvelteKit route file naming (`+page.svelte`, `+server.ts`, …).
- `sveltekit-perf-guard.py` — after a build command, checks bundle/chunk budgets and import anti-patterns.

**Database & migrations**

- `drizzle-migration-guard.py` — blocks destructive schema changes (DROP/TRUNCATE/DELETE-without-WHERE), warns on risky ones.
- `supabase-rls-reminder.py` — reminds you to add Row Level Security on new tables.

**Tooling**

- `rtk-rewrite.sh` — transparently rewrites Bash commands to `rtk` equivalents for token savings (no-op if `rtk`/`jq` absent).
- `dependency-audit.py` — runs a security audit when a manifest (`package.json`, `requirements.txt`, `Cargo.toml`, …) changes.
- `stop-verify-and-log.py` — on Stop, runs type checks in the background (`tsc`, `svelte-check`, `mypy`, `cargo check`).

See [hooks/README.md](hooks/README.md) for the full reference and how to write your own.

## Agents

Subagents in `agents/`, each a markdown file with YAML frontmatter. Tools are scoped with the `tools:` field (comma-separated), so a subagent only gets what it needs.

| Agent                        | Model  | Purpose                                               |
| ---------------------------- | ------ | ----------------------------------------------------- |
| **frontend-engineer**        | sonnet | Svelte 5 runes, shadcn-svelte, responsive UI          |
| **backend-engineer**         | sonnet | SvelteKit server: load functions, actions, hooks      |
| **superforms-expert**        | sonnet | sveltekit-superforms + Zod                            |
| **mobile-ui-designer**       | sonnet | Mobile-first UI with TailwindCSS                      |
| **debug-expert**             | opus   | Error diagnosis, test failures, perf issues (worktree)|
| **code-reviewer**            | opus   | Security & quality review (worktree)                  |
| **discovery-agent**          | sonnet | Lightweight feature specs in `.docs/`                 |
| **vercel-deployment-expert** | sonnet | Vercel deploys and configuration                      |
| **seo-expert**               | sonnet | Content structure and on-page SEO                     |

> Filenames may differ from the agent `name` (e.g. `debug-specialist.md` defines `debug-expert`). See [agents/README.md](agents/README.md).

## Skills

Reusable procedures in `skills/`, each `skill-name/SKILL.md`. Invoke with `/skill-name` (the **directory** name) or let Claude load one when its `description` matches. Roughly grouped:

- **Stack / dev** — `ai-sdk`, `superforms-reference`, `svelte-component-architecture`, `tapforce-shadcn-svelte`, `tdd-workflow`, `turborepo`, `frontend-design`, `clean-comments`, `playwright-cli`
- **SEO / growth** — `ai-seo`, `seo-audit`, `programmatic-seo`, `find-keywords`, `free-tool-strategy`, `google-search-console`, `web-design-guidelines`
- **Writing / content** — `deep-dive-burst`, `humanizer`, `writing-linkedin-posts`, `twitter-algorithm-optimizer`, `session-mining`
- **Workflow** — `agent-handoff`, `tutor`

A vendored `gstack/` skill set (the `gstack-*` directories) ships alongside these; treat it as third-party and prune what you don't use.

## Configuration

### settings/settings.template.json

`install.sh` expands `$HOME` and writes the result to `~/.claude/settings.json`. The template sets:

- **`hooks`** — the PreToolUse / PostToolUse / Stop wiring above.
- **`permissions.deny`** — native blocks for `.env` / `secrets/` reads and `rm -rf` of root/home.
- **`statusLine`** — a command status line (`scripts/statusline.sh`).
- **`skillListingBudgetFraction`** — caps how much context the skill listing consumes.
- **`skipDangerousModePermissionPrompt`** — skips the confirmation before bypass-permissions mode. Lands in your **user** settings, so it's honored. Remove it if you don't want that default (especially before sharing).

### Adding a hook

1. Drop a script in `hooks/` (template below).
2. Register it under the right event in `settings/settings.template.json`.
3. Re-run `./install.sh`.

```python
#!/usr/bin/env python3
import json, sys

def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    # Self-check the path here and return early if irrelevant.
    sys.exit(0)  # 0=allow, 1=warn, 2=block

if __name__ == "__main__":
    main()
```

### Adding an agent

Create `agents/<name>.md`:

```markdown
---
name: my-agent
description: When Claude should delegate to this agent.
model: sonnet
color: blue
tools: Read, Glob, Grep, Edit, Write, Bash
---

You are an expert in…
```

Use `tools:` (comma-separated) to scope tools — not `allowed-tools` (that's a **skills** field and is ignored on subagents, which silently grants all tools).

### Adding a skill

```
skills/<skill-name>/
├── SKILL.md          # frontmatter (name, description, optional paths/allowed-tools) + body
├── references/       # optional supporting docs
└── scripts/          # optional helper scripts
```

## Requirements

- [Claude Code CLI](https://claude.ai/download)
- Python 3.10+ (hooks)
- Bash (install)

Optional, for full hook functionality: `prettier`, `black`, `rtk`, `jq`, `terminal-notifier` (macOS).

## License

MIT. Use, modify, and share. If you fork it, review `skipDangerousModePermissionPrompt` and the `permissions.deny` list before installing.
