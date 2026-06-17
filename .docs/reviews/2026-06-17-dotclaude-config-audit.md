---
title: dotclaude config audit (vs current Claude Code docs)
status: accepted
last_updated: 2026-06-17
context_for_ai: Read before changing settings.template.json, agents/, hooks/, or README.md. Lists verified-against-docs defects and exact fixes. Supersedes the open items in TODO.md tagged from the April 2026 audit.
---

# dotclaude config audit — 2026-06-17

Scope: the whole repo (`CLAUDE.md`, `settings/`, `hooks/`, `agents/`, `skills/`, `README.md`, `install.sh`, `.claude/`). Every schema claim below was checked against the live docs at code.claude.com (settings, hooks, sub-agents, skills) on 2026-06-17, not from memory.

Headline: the framework is mostly current — `if` hook conditionals, `color`/`effort`/`isolation`/`background` agent fields, `skillListingBudgetFraction`, `skipDangerousModePermissionPrompt`, `maxSkillDescriptionChars`, `user-invocable`, `paths`, `disable-model-invocation`, and the `statusLine` command form are all real, current keys. But three defects cause **silent functional failure** (tool restrictions, path filters, and one hook don't actually work), and the public-facing docs (`README.md`) describe a repo that no longer exists.

---

## Critical — silent functional failure

### C1. Every subagent uses `allowed-tools`, which subagents ignore → all agents inherit *all* tools
All 10 files in `agents/` declare tools as:
```yaml
allowed-tools: ["Read", "Glob", "Grep", "Edit", "Write", "Bash"]
```
`allowed-tools` is the **skills** frontmatter field. The sub-agents doc lists the recognized fields explicitly: `name, description, tools, disallowedTools, model, permissionMode, mcpServers, hooks, maxTurns, skills, initialPrompt, memory, effort, background, isolation, color`. There is no `allowed-tools`. Unrecognized keys are dropped, and the doc states: *"[tools] Inherits all tools if omitted."*

Consequence: the restriction is a no-op. `code-reviewer` (which you scoped to read-only-ish: no `Edit`) and every other agent actually run with the full toolset. Your maker/checker separation and least-privilege intent are not enforced.

Fix — rename the field and use the comma-separated **string** form the docs show (not a YAML array):
```yaml
# code-reviewer.md
tools: Read, Glob, Grep, Bash
```
Do this for all 10 agents. Where you want "everything except writes," prefer `disallowedTools: Write, Edit` instead of re-listing the allowlist.

### C2. Every `if` hook conditional packs multiple permission rules into one field — unsupported
`settings/settings.template.json` uses values like:
```json
"if": "Write(*.ts)|Write(*.js)|Write(*.svelte)|Edit(*.ts)|Edit(*.js)|..."
```
The hooks doc is explicit: *"The `if` field holds exactly one permission rule. There is no `&&`, `||`, or list syntax for combining rules."* The pipe is valid in `matcher` (tool names), **not** in `if` (permission rules). Every `if` in the file is malformed this way, including the destructive-SQL guard:
```json
"if": "Write(*.sql)|Edit(*.sql)|MultiEdit(*.sql)|Write(*migrations*)|..."
```
`if` is documented as "best-effort": an unparseable rule means the filter does not narrow as intended, so these guards (`drizzle-migration-guard`, `supabase-rls-reminder`, `sveltekit-route-validator`, `import-path-validator`, `dependency-audit`) either over-fire on every edit or do not fire on the files you care about. You cannot rely on them as written.

Fix — one matcher group per rule, one rule per `if`, and use nested globs so paths in `packages/db/migrations/…` actually match:
```json
{ "matcher": "Write|Edit", "if": "Edit(**/*.sql)",
  "hooks": [ { "type": "command", "command": "python3 $HOME/.claude/hooks/drizzle-migration-guard.py" } ] },
{ "matcher": "Write|Edit", "if": "Edit(**/migrations/**)",
  "hooks": [ { "type": "command", "command": "python3 $HOME/.claude/hooks/drizzle-migration-guard.py" } ] }
```
Simpler and more robust: drop `if` entirely and let each hook self-check the path on stdin (they already inspect `tool_input`). `if` is only a spawn-overhead optimization, not an enforcement layer. Also fix the same pattern documented in `hooks/README.md` ("Using `if` Conditionals") so it stops teaching the broken form.

### C3. `supabase-rls-reminder.py` crashes on Python < 3.12
Line 272 puts backslash-escaped quotes inside an f-string expression:
```python
lines.append(f"   {pipe} {styled('CREATE POLICY', Colors.MAGENTA)} {styled('\"org_isolation\"', Colors.GREEN)} ...")
```
Backslashes inside an f-string replacement field are a `SyntaxError` before Python 3.12, so the whole module fails to import — the RLS reminder never runs on a 3.10/3.11 interpreter, silently. Already logged in `TODO.md` (2026-06-12) and still unfixed.

Fix — hoist the literal out of the f-string:
```python
policy_name = styled('"org_isolation"', Colors.GREEN)
lines.append(f"   {pipe} {styled('CREATE POLICY', Colors.MAGENTA)} {policy_name} ...")
```

---

## High — stale docs and a real safety gap

### H1. `README.md` describes a repo that no longer exists
It is the most out-of-date file and directly contradicts reality and `hooks/README.md`:

- **Counts are wrong:** claims Hooks 13 / Agents 9 / Skills 4. Actual: 10 hook scripts (9 `.py` + `rtk-rewrite.sh`), 10 agents, 78 skill directories (23 custom + 55 under `gstack/`).
- **Lists 5 deleted hooks** as if present: `permission-auto-approve.py`, `bash-command-validator.py`, `command-logger.py`, `web-search-enhancer.py`, `stop-verification.py` (the real one is `stop-verify-and-log.py`). `hooks/README.md` documents these as removed in the April 2026 cleanup — straight contradiction.
- **Calls `code-reviewer` a skill** in the Skills section; it is an agent.
- **Settings section is fiction:** claims the template has "Permissions — allow/deny/ask", "Model — default model preference", and "Plugins — enabled marketplace plugins". `settings.template.json` has **none** of these keys.

Fix: regenerate the README from the actual tree, or generate the counts/lists in `install.sh` so they can't drift again.

### H2. No `permissions` block at all, but the docs claim one guards dangerous commands
`hooks/README.md` states: *"Dangerous pattern blocking is handled by `permissions.deny` in settings (native, zero overhead) — don't duplicate it in hooks."* There is no `permissions` block in `settings.template.json`. So nothing native blocks `rm -rf`, `curl | sh`, secret reads, etc. — only the `no-secrets.py` hook (writes only) and CLAUDE.md prose. This is a safety gap, not just doc drift.

Fix — add an explicit deny list, e.g.:
```json
"permissions": {
  "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)", "Bash(rm -rf *)", "Bash(curl * | sh)"]
}
```

### H3. `linear-reporter.md` is orphaned
The agent's own description says it is *"the checker subagent for the linear-triage loop … spawned by the orchestrating agent after the discovery phase."* The `linear-triage` skill was deleted today. The agent also depends on `mcp__linear__save_issue` / `mcp__linear__list_issues`. It now points at nothing.

Fix: delete `agents/linear-reporter.md`, or, if you still want Linear triage, restore a thin orchestrator skill and confirm the Linear MCP server is connected.

---

## Medium

### M1. ~~CLAUDE.md asserts `.claude/rules/` is "auto-loaded"~~ — RETRACTED 2026-06-17, I was wrong
My original claim here said `.claude/rules/` was a Cursor-only convention and not a real Claude Code feature. **That is false.** `.claude/rules/` is a current Claude Code feature: every `.md` is discovered recursively and loaded into context — unconditionally if it has no `paths` frontmatter (same priority as `.claude/CLAUDE.md`), or only when Claude touches matching files if it has a `paths` glob. It supports symlinks and a user-level `~/.claude/rules/` that applies to every project. The CLAUDE.md claim is **correct**; no change needed there.

This turns into an opportunity instead. The global `CLAUDE.md` (~8 KB) loads every session in full. Stack-specific blocks could move to `~/.claude/rules/*.md` with `paths` scoping so they only cost context when relevant — e.g. Svelte-5-runes rules scoped to `**/*.svelte`, Drizzle/RLS rules scoped to `**/schema/**` and `**/migrations/**`, pnpm/monorepo rules to `**/package.json`. This repo installs into `~/.claude`, so a `rules/` dir here becomes user-level rules. Wiring added 2026-06-17: `install.sh` now symlinks `rules/ → ~/.claude/rules` when the dir exists, and a `rules/README.md` documents the convention. The actual CLAUDE.md → rules content split is still a proposal (see TODO) — not done yet, to avoid carving up hand-written global prefs without sign-off.

### M2. Real `paths` field is unused; path scoping lives in prose that does nothing
Many skills bake `"Applies to src/**/*.svelte, …"` into the **description text**. That string is not functional — it is just words Claude reads. The skills schema has a real `paths` field: *"Glob patterns that limit when this skill is activated."* (This is open audit item 13 in `TODO.md`.)

Fix — promote the prose to frontmatter on the editor-facing skills (`frontend-design`, `tdd-workflow`, `clean-comments`, `superforms-reference`, `svelte-component-architecture`, `tapforce-shadcn-svelte`):
```yaml
paths:
  - src/**/*.svelte
  - src/lib/components/**
```

### M3. Skill-listing bloat: 78 skills, 55 of them `gstack/`
Claude sees the skill listing every turn. `skillListingBudgetFraction: 0.02` + `maxSkillDescriptionChars` cap it, but 78 entries means real skills get truncated or crowded out. `TODO.md` already flags archiving unused `gstack/` skills.

Fix: move `gstack/` out of the loaded path or set `disable-model-invocation: true` on the ones you never auto-trigger, so they stay `/`-invocable without sitting in context.

### M4. `autoMemoryDirectory` still unset
Open audit item 15 in `TODO.md`. `.claude/memory/` exists but is empty and nothing points auto-memory at it. Add `"autoMemoryDirectory": ".claude/memory"` to the template if you want auto-memory persisted there.

---

## Low / cosmetic

- ~~**Skill `name` ≠ directory**~~ — FIXED 2026-06-17. Aligned `name` to the directory for `frontend-design`, `svelte-component-architecture`, and `agent-handoff`; also corrected the stale `/svelte-architect` command references in `skills/README.md`.
- ~~**Dangling skill cross-references**~~ — FIXED 2026-06-17. Swept all custom skills: removed every "see X" / `**X**` / Related-Skills pointer to a non-installed skill (schema-markup, content-strategy, brief, build-clusters, lead-magnets, competitor-alternatives, page-cro, site-architecture, analytics-tracking, xml-sitemap, indexing, core-web-vitals, mobile-friendly, backlink-analysis, seo-monitoring, copywriting, email-sequence). Kept refs to installed skills (seo-audit, programmatic-seo, ai-seo). google-search-console's all-dangling Related Skills section was dropped. Also rewrote the stale `skills/README.md` (it documented 4 skills, one of which — `code-reviewer` — is an agent).
- **`debug-specialist.md` has `name: debug-expert`** — filename ≠ agent name. Harmless, but pick one.
- ~~**Literal `\n` in agent descriptions**~~ — FIXED 2026-06-17. Rewrote `backend-engineer`, `debug-specialist`, and `discovery-agent` descriptions to crisp trigger text, dropping the embedded `\n…<example>…` dumps. (The other agents use inline `<example>` text with no literal `\n` — left as-is.)
- **`skipDangerousModePermissionPrompt: true`** is valid and lands in `~/.claude/settings.json` (so it is honored, not stripped). It removes the confirmation before bypass-permissions mode. Fine for your own machine; reconsider shipping it as a default in a "shareable, MIT" repo — anyone who runs `install.sh` inherits auto-bypass with no prompt.

---

## Confirmed current (no action — listed so they don't get "fixed" by mistake)
`if` hook field; `matcher` + nested `hooks` array; `statusLine` `{type:"command"}`; agent fields `color`, `effort`, `isolation: worktree`, `background`, `model: inherit`; model aliases `sonnet`/`opus`; settings keys `skillListingBudgetFraction`, `skipDangerousModePermissionPrompt`, `maxSkillDescriptionChars`, `autoMemoryDirectory`; skill fields `paths`, `user-invocable`, `disable-model-invocation`, `allowed-tools` (skills only); hook exit-code semantics (0/1/2) in `hooks/README.md`.

---

## Suggested order of work
1. C1 (rename `allowed-tools`→`tools` in all agents) — restores least-privilege.
2. C3 (one-line f-string fix) — trivial, unblocks the RLS hook.
3. C2 + H2 (rework `if` blocks; add `permissions.deny`) — same file, do together.
4. H1 + H3 (rewrite README; remove/repoint `linear-reporter`).
5. Medium items as a batch; Low items opportunistically.
