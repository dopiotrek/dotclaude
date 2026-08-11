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

## Response Shape

- Keep responses focused, brief, and concise. Spend most of the response on the main answer; keep caveats and disclaimers short. When asked to explain something, give a high-level summary unless I ask for depth
- Narration while working: one sentence before the first tool call saying what you're about to do, then a brief update only when you find something important or change direction. When you finish, lead with the outcome — the first sentence answers "what happened" or "what did you find", supporting detail after
- Match the length of files you write to disk (specs, ADRs, reviews, handoffs, `TODO.md` entries) to what the task needs. Cover the substance; no padding, no redundant summary sections, no boilerplate
- Don't add self-review passes on top of your own. Skip "let me double-check" rounds and don't spawn a subagent to verify your own work — the type-checker and the hooks are the verification

## Working Habits

- Run the type checker before considering work complete. It's an external signal you can't get by re-reading the diff — run it and report what it actually said
- For "apply X everywhere" tasks (layout, padding, token, component pattern), grep for ALL occurrences first, list them, change each, then re-grep to prove zero of the old pattern remain. Never claim full coverage based only on the cases you happened to edit
- Treat my domain knowledge as authoritative: if I say the data is correct, don't build heuristics that flag it as suspicious. Verify claims against the running app (screenshot/observe), not only against your own file reads or theory
- For pixel-level UI/alignment work, don't rely on screenshot judgment alone — read `getBoundingClientRect()`/`getComputedStyle()` for the changed element (and the reference element, if matching one) and compare actual values. Screenshots miss 1px offsets, dropped borders, and small vertical shifts that measurements catch immediately
- Before implementing a metric/stat/calculation, restate which inputs feed it and confirm the definition before coding — don't assume (passive income ≠ total investment return). One line, then proceed
- Before a multi-file refactor or schema change where scope could plausibly expand (adjacent features, extra abstractions, "while I'm here" additions), restate what you'll build and 2-3 things you'll deliberately not build, and wait for a go-ahead. Skip this when the ask and its boundaries are already unambiguous
- When porting from another codebase, copy the intent, not every detail. If you carry over a heavy behavior from the reference, call it out so it can be opted out of
- Delegate to a subagent only for large, genuinely independent work — a wide multi-file investigation, a migration that splits cleanly. Don't delegate what you can finish in a handful of tool calls, and don't use a subagent to double-check your own work. If one agent can do it, use one
- When you do fan out, scope each agent to one self-contained slice with a clear contract, and require a passing type-check on that slice before integrating — never merge a slice you haven't seen compile
- Never re-derive a fact a source already carries authoritatively (e.g. an `asset_class` column) with name/keyword heuristics — use the existing column
- Never delete a file/module during cleanup without first grepping for imports of it — over-deletion of still-referenced modules has broken pages before
- Never assert "the page is stale" or "should be empty" without confirming it in the live app first
- When a reported error can't be reproduced, or before declaring a browser-verified UI change done, check for a stale dev server, build cache, stale HMR state, or a pending Drizzle migration — restart/reapply first, before deep-diving the code
- When multiple related repos exist on this machine, confirm `pwd` resolves inside the intended repo (and use absolute paths in Bash — cwd carries over between calls) before exploring or spawning subagents

## Browser Automation

Default to the **claude-in-chrome** MCP server for anything touching a browser. It drives my real Chrome, so I stay logged in to the apps under test.

- Start with `tabs_context_mcp({ createIfEmpty: true })` — that opens a **new window** with its own tab group. Keep the work inside that group.
- Do NOT reach for `gstack-browse`, `agent-browser`, `playwright-cli`, or the `playwright` / `chrome-devtools` MCP servers for normal browsing, QA, or dogfooding. Each launches a separate browser with a blank profile, so I am logged out and the run is useless for authenticated pages.
- Use a headless or standalone browser only when I ask for it by name, or when the task genuinely needs a clean unauthenticated session (e.g. checking a logged-out landing page).

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
