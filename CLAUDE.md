# Global Claude Preferences

## About Me

- Primary stack: SvelteKit, Svelte 5 (runes), TypeScript, Supabase, Drizzle ORM
- All projects use pnpm (never npm or yarn)
- Always use Svelte 5 runes syntax ($state, $derived, $effect) — never Svelte 4 stores or reactive declarations ($:, writable, derived)

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
- Consider mobile-first for any UI work
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

All agents write documentation to `.docs/` in the project root. Two directories:

- `.docs/specs/` — what to build. Feature specs, implementation plans. Written before coding.
- `.docs/reviews/` — what was found. Code reviews, SEO audits, security checks. Written after coding.

Name files descriptively: `auth-flow.md`, `homepage-seo-audit.md`. No metadata files, no progress tracking.

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
