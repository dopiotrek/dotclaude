# AGENTS.md

Machine-wide rules for coding agents that read `AGENTS.md` (Codex, Cursor, Gemini CLI, opencode, and others).

Claude Code reads `CLAUDE.md` in this repo instead. That file is the full set of rules — stack, communication style, git conventions, hard limits. Read it too: `~/.claude/CLAUDE.md`.

Only rules that agents get wrong without being told are repeated here.

## Browser Automation

Use the **agent-browser** CLI (`agent-browser.dev`). It runs its own Chrome with a dedicated profile that stays logged in. It never touches the Chrome window I am working in.

**Headless by default. Do not open a window.** Always pass the profile so my logins are there:

```bash
agent-browser --profile ~/.agent-browser/profiles/main open <url>
agent-browser --profile ~/.agent-browser/profiles/main snapshot -i -c
agent-browser --profile ~/.agent-browser/profiles/main screenshot shot.png
agent-browser --profile ~/.agent-browser/profiles/main close   # always, when done
```

- Read the page with `snapshot -i -c` and click `@ref` ids. Do not guess CSS selectors.
- Show me a screenshot instead of describing the page.
- Run `agent-browser skills get core --full` when you do not know a command.
- Add `--headed` only when I ask to watch, or when a site needs a first login. Say so before you do it, and close the window straight after — the login stays in the profile.
- Drop `--profile` when the task needs a clean logged-out session (e.g. a public landing page).
- Do NOT use `gstack-browse`, `playwright-cli`, or Playwright MCP. They start a blank profile, so I am logged out.

## Tooling

- pnpm only. Never npm or yarn.
- Svelte 5 runes only (`$state`, `$derived`, `$effect`, `$props`). Never Svelte 4 stores or `$:`.
- Run the type checker before you call work complete, and report what it said.
