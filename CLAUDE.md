# Global Claude Preferences

## About Me

- Primary stack: SvelteKit, Svelte 5 (runes only), TypeScript, Supabase, Drizzle ORM, Turborepo
- All projects use pnpm (never npm or yarn). Exception: HyperFrames video projects, whose generated scripts are pinned `npx hyperframes` calls — run them as their own `CLAUDE.md` says
- Svelte 5 runes only — never Svelte 4 stores or `$:`. (Always-on guard for new files; full Svelte and Drizzle/Supabase rules are path-scoped in `rules/`.)

## Communication Style

- Use plain, simple English. I'm not a native speaker: prefer short sentences and common words. Avoid idioms, slang, wordplay, and rare vocabulary
- Technical terms are fine, but explain an uncommon one in a short plain clause the first time it appears
- Ask clarifying questions for genuinely ambiguous product decisions — but when the obvious next step is to apply the same treatment as adjacent/existing items, just do it instead of asking where to put it. Ask at most one focused question, never a multi-part menu
- If something is plausibly owned by another agent or out of scope, note it in one line and proceed with your part rather than blocking

## Response Shape

- Keep responses focused, brief, and concise. Spend most of the response on the main answer; keep caveats and disclaimers short. When asked to explain something, give a high-level summary unless I ask for depth
- Narration while working: at most one short sentence before the first tool call, then stay quiet until done — no play-by-play of each action, no walls of text. Break the silence only for something important or a change of direction. On a long task, write one short line when you move to a new part (for example, the next repo). When you finish, lead with the outcome — the first sentence answers "what happened" or "what did you find", supporting detail after. I want a clean terminal, not a novella
- Match the length of files you write to disk (specs, ADRs, reviews, handoffs, `TODO.md` entries) to what the task needs. Cover the substance; no padding, no redundant summary sections, no boilerplate
- Don't add self-review passes on top of your own. Skip "let me double-check" rounds and don't spawn a subagent to verify your own work — the type-checker and the hooks are the verification

### Explaining a plan or a choice

This is the shape I want, every time.

- Plain words. No file paths, no function names, no internal jargon, unless I ask for them
- Short sentences. Bold headers of two or three words, a line or two under each
- The whole explanation fits on one screen. If it does not, I will not read it
- Say what the problem is, what you would do, what you will not do — then stop
- When you ask me to decide, give me two options with one line each, say which you prefer, and ask one question. Never a menu of four
- Save the detail for the code, the docs and `TODO.md`. Those can be as long as they need to be. My terminal cannot

## Text in the Product

Text is allowed, but it must earn its place. Every string I add to a screen or a code file has to tell the reader something the surrounding context does not already say.

- UI copy: write the label, not the label plus an explanation of the label. Add helper text, an empty-state sentence, or a tooltip only when a user would otherwise get it wrong or not know what happens next — then keep it to one short line. No reassurance text, no restating the heading in smaller grey type, no descriptions under every field by default
- Code comments: minimal by default. Explain a non-obvious _why_ — a constraint, a workaround, a decision that looks wrong until you know the reason — and nothing else. Never narrate what the next line does, never section-header a short function, never add JSDoc that only repeats the parameter names, never banner the top of a file. When editing, match the file's existing comment density instead of adding your own. (Full rule, path-scoped to code files: `rules/comments.md`.)
- If I ask for more explanation on a specific screen or function, give it. This is about the default, not a ban

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
- Before you build UI, search for an existing shared component (lists, tables, pickers, dialogs) and reuse it. When you change a shared component, check every place that uses it
- Before you say "done", confirm which database and environment the running app points to (local or production)
- At the end of a session, list: uncommitted changes, items not verified in the browser, and what is live versus only local. Then commit what is finished

## Browser Automation

- Use the **agent-browser** CLI, headless, always with `--profile ~/.agent-browser/profiles/main`. Load the `agent-browser` skill before the first browser command — it holds my rules and the exceptions.
- Use my real Chrome (claude-in-chrome) only when I ask for it by name. Do NOT use `playwright-cli` or Playwright MCP.

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

Internal docs go in `.docs/`. The full layout, front matter and life cycle are in `rules/docs-conventions.md`, which loads when you work in `.docs/`. In short: `README.md` routes a task to the right doc, `handoff.md` holds the last session only, then `product/` (what), `decisions/` (why), `engineering/` (how), `specs/` (plan), `research/` (evidence), `reviews/` (`YYYY-MM-DD-slug.md` audits) and `_archive/`. Coding rules live in `.claude/rules/`, never in `.docs/`.

## Deferred Work (`TODO.md`)

Every project keeps a root `TODO.md`. If the project already has `TODOS.md`, use that file instead of creating a second one. When you defer or cannot finish something, append a checkbox item with a short tag (`[DB]`, `[TEST]`…), what to do, and why it was deferred. Check items off only after verifying the fix in this session. Never rewrite items from other sessions.

## Systems

@RTK.md
