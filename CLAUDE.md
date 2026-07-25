# Global Claude Preferences

## About Me

- Primary stack: SvelteKit, Svelte 5 (runes only), TypeScript, Supabase, Drizzle ORM, Turborepo
- All projects use pnpm (never npm or yarn)
- Svelte 5 runes only — never Svelte 4 stores or `$:`. (Always-on guard for new files; full Svelte and Drizzle/Supabase rules are path-scoped in `rules/`.)

## Communication Style

- Use plain, simple English. I'm not a native speaker: prefer short sentences and common words. Avoid idioms, slang, wordplay, and rare vocabulary
- Technical terms are fine, but explain an uncommon one in a short plain clause the first time it appears
- Ask clarifying questions for genuinely ambiguous product decisions — but when the obvious next step is to apply the same treatment as adjacent/existing items, just do it instead of asking where to put it. Ask at most one focused question, never a multi-part menu
- If something is plausibly owned by another agent or out of scope, note it in one line and proceed with your part rather than blocking

## Working Habits

- Run type checks before considering work complete
- For "apply X everywhere" tasks (layout, padding, token, component pattern), grep for ALL occurrences first, list them, change each, then re-grep to prove zero of the old pattern remain. Never claim full coverage based only on the cases you happened to edit
- Treat my domain knowledge as authoritative: if I say the data is correct, don't build heuristics that flag it as suspicious. Verify claims against the running app (screenshot/observe), not only against your own file reads or theory
- Before implementing a metric/stat/calculation, restate which inputs feed it and confirm the definition before coding — don't assume (passive income ≠ total investment return). One line, then proceed
- When porting from another codebase, copy the intent, not every detail. If you carry over a heavy behavior from the reference, call it out so it can be opted out of
- When fanning out to subagents, scope each to one self-contained slice with a clear contract, and require a passing type-check on that slice before integrating — never merge a slice you haven't seen compile
- Never re-derive a fact a source already carries authoritatively (e.g. an `asset_class` column) with name/keyword heuristics — use the existing column
- Never delete a file/module during cleanup without first grepping for imports of it — over-deletion of still-referenced modules has broken pages before
- Never assert "the page is stale" or "should be empty" without confirming it in the live app first
- When a reported error can't be reproduced, suspect a stale dev server, build cache, or stale HMR state before deep-diving the code — restart/hard-reload first

## Hard Limits

- Never read or display the contents of `.env` files
- Never use `any` without explicit justification
- Never delete data without explicit confirmation
- Never generate fake/placeholder data in production code
- Never add a dependency without checking for an existing alternative

## Git Conventions

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- Keep commits atomic and focused

## Project Docs (`.docs/`)

Internal docs go in `.docs/`, filed by **knowledge domain** so a fact's location stays stable as the project matures. Read `.docs/README.md` (or `.docs/ai/context-map.md`) in a repo for its full conventions.

| Folder              | Holds                                                                                |
| ------------------- | ------------------------------------------------------------------------------------ |
| `ai/` (or `agent/`) | `context-map.md` — read first, routes a task to the right doc                        |
| `decisions/`        | **WHY** — one ADR per non-obvious technical choice, named by topic, no number prefix |
| `engineering/`      | **HOW** — architecture map, feature specs, ops runbooks                              |
| `product/`          | **WHAT** — `concept.md` is canonical; requirements, internal commercial              |
| `research/`         | Investigations and evidence; conclusions graduate to an ADR or spec                  |
| `reviews/`          | Point-in-time audits, `YYYY-MM-DD-short-name.md`                                     |
| `archive/`          | Superseded; never write new work here                                                |

Coding rules live in `.claude/rules/`, never in `.docs/`. Names are kebab-case, two words max — the date goes in front **only** in `reviews/`. Long-lived docs carry frontmatter: `title`, `status`, `last_updated`, `context_for_ai`.

## Deferred Work (`TODO.md`)

Every project keeps a root `TODO.md`. When you defer or cannot finish something, append a checkbox item with a short tag (`[DB]`, `[TEST]`…), what to do, and why it was deferred. Check items off only after verifying the fix in this session. Never rewrite items from other sessions.

## Systems

@RTK.md
