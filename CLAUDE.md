# Global Claude Preferences

## About Me

- Primary stack: SvelteKit, Svelte 5 (runes only), TypeScript, Supabase, Drizzle ORM, Turborepo
- All projects use pnpm (never npm or yarn)
- Svelte 5 runes only — never Svelte 4 stores or `$:` reactive declarations. (This always-on guard covers new files; the full Svelte and Drizzle/Supabase code rules are path-scoped in `rules/` and load when you touch matching files.)

## Communication Style

- Use plain, simple English. I'm not a native speaker: prefer short sentences and common words. Avoid idioms, slang, wordplay, and rare vocabulary
- Technical terms are fine, but explain an uncommon one in a short plain clause the first time it appears
- Don't overcomplicate explanations — one clear idea per sentence beats a dense paragraph
- Be concise but thorough
- Explain "why" not just "what"
- Don't apologize for mistakes, just fix them
- Ask clarifying questions for genuinely ambiguous product decisions — but when the obvious next step is to apply the same treatment as adjacent/existing items, just do it instead of asking where to put it or offering to hand it back. Ask at most one focused question, never a multi-part menu
- If something is plausibly owned by another agent or out of scope, note it in one line and proceed with your part rather than blocking

## Things to Always Do

- Run type checks before considering work complete
- Preserve existing code style in files being edited
- Use existing patterns from the codebase, don't invent new ones
- After reading a file, reference it from context. Only re-read if the file was modified since last read.
- Use Glob instead of find/ls commands. Use Grep instead of grep/rg. Use Read instead of cat.
- For "apply X everywhere" tasks (layout, padding, token, weight, component pattern), grep/glob for ALL occurrences first, list them, change each, then re-grep to prove zero of the old pattern remain. Never claim full coverage based only on the cases you happened to edit.
- Treat the user's domain knowledge as authoritative: if they say the numbers/data are correct, don't build heuristics that flag them as suspicious. Verify claims against the running app (screenshot/observe), not solely against your own DB/file reads or theory.
- When following an example or porting from another codebase, copy the intent, not every detail. Default to the simplest interaction that meets the need; if you carry over a heavy behavior from a reference, call it out so it can be opted out of.
- Before implementing a metric/stat/calculation, restate exactly which inputs feed it and confirm the definition before coding — don't assume (e.g. passive income ≠ total investment return). One line, then proceed.
- When fanning out work to multiple subagents (design-system ports, audits, migrations), scope each to one self-contained slice with a clear contract, and require a passing type-check on that slice before integrating it — never merge a slice you haven't seen compile.

## Things to Never Do

- Never commit secrets or credentials
- Never use `any` type without explicit justification
- Never delete data without explicit confirmation
- Never run destructive commands without asking first
- Never add dependencies without checking for existing alternatives
- Never generate fake/placeholder data in production code
- Never assert "the page is stale" or "should be empty" without confirming it in the live app first
- Never re-derive a fact a source already carries authoritatively (e.g. an `asset_class` column) with name/keyword heuristics — use the existing column
- Never delete a file/module during cleanup without first grepping the repo for imports/usages of it — over-deletion of still-referenced modules has broken pages before
- When a reported error can't be reproduced, suspect a stale dev server, build cache, or stale HMR state before deep-diving the code — restart/hard-reload first, then investigate

## Security Boundaries

- Never read or display contents of .env files
- Never include API keys in code
- Always use parameterized queries for database operations
- Assume all user input is untrusted

## Git Conventions

- Conventional commits: feat:, fix:, refactor:, docs:, chore:
- Keep commits atomic and focused

## Project Docs (`.docs/`)

All agents write documentation to `.docs/` in the project root, organized by **knowledge domain** — not project phase. Where a fact lives depends on what _kind_ of knowledge it is, so its location stays stable as a project matures (MVP or mature product, the database spec and the business rules are always in the same place). Not every repo needs every folder; this is the superset, create what the project uses. Start a project's docs with `ai/context-map.md`.

- `.docs/ai/` — agent context: `context-map.md` (read first, routes a task to the right doc) + reusable prompts. **Coding rules live in `.claude/rules/` (auto-loaded by Claude Code), NOT here — do not duplicate them.**
- `.docs/decisions/` — **WHY**: Architecture Decision Records, `NNNN-short-desc.md`, one decision per file (context → decision → consequences → source). **Write an ADR for every non-obvious technical choice** so it isn't silently reverted later.
- `.docs/engineering/` — **HOW**: technical & operational reality. The architecture map (`architecture.json` / `.html`), feature specs/implementation plans, and ops runbooks (deployment, env strategy, local setup). **Write new specs here.**
- `.docs/business/` — **WHAT**: product, requirements, domain context. `concept.md` is the canonical "what is this app"; discovery lives in `requirements.md` + `discovery.json`; `_input/` = raw client source. Internal commercial (pricing, strategy) lives here too — not for client eyes.
- `.docs/reviews/` — post-coding audits, code reviews, SEO/security checks. **Write new reviews here.**
- `.docs/archive/` — superseded artifacts kept for the record; never write new work here.
- `.docs/mining/` — session-mining bank (`coding-sessions.md`, `content-ideas.md`); gitignored, private working state.
- `.docs/handoff.md` — session handoff notes (current state and decisions); stays at the root.

**Frontmatter.** Current/long-lived docs carry YAML frontmatter: `title`, `status` (`draft | accepted | living | superseded`), `last_updated`, and `context_for_ai` (one line on when an agent should read it). Agents parse this well; it routes context cheaply.

**Per-domain current-state JSON.** A domain may keep a machine-readable snapshot mirroring `engineering/architecture.json`'s `meta` block — e.g. `engineering/architecture.json` (the system) and `business/discovery.json` (requirements). Keep them current alongside the prose.

**File naming.** Lowercase kebab-case. **The date goes in front only in `reviews/`** — point-in-time audits are `YYYY-MM-DD-descriptive-name.md` (ISO date first, so repeat audits of an area sort chronologically and never collide). Everywhere else, plain descriptive names with no date. ADRs are `decisions/NNNN-short-desc.md`. No progress-tracking files.

A project may document its own extensions in its repo `CLAUDE.md`, but the knowledge-domain folders, frontmatter, and date-in-front-only-for-reviews rule are the shared baseline.

## Deferred Work (`TODO.md`)

Every project keeps a `TODO.md` in the root. When you defer, skip, or cannot finish something, append it there as a checkbox item with a short tag (`[DB]`, `[HOOKS]`, `[TEST]`...), what to do, and why it was deferred. Check items off only after verifying the fix in this session. Never delete or rewrite items from other sessions.

## Token Optimization

# requires @RTK.md to be loaded — if missing, skip rtk prefix and use commands directly

- Always prefix CLI commands with `rtk` when available: `rtk git log`, `rtk ls`, `rtk read file`, `rtk grep pattern`
- Use `rtk` for: git, gh, cat, ls, grep, rg, curl, docker, pnpm, vitest, tsc, svelte-check, eslint, prettier, playwright, cargo, pytest
- RTK compresses verbose output before it enters context — 60-90% token savings

## Systems

@RTK.md

## Workflow

@workflow/tmux-tasks.md
