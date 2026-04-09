# Global Claude Preferences

## About Me

- Primary stack: SvelteKit, Svelte 5 (runes), TypeScript, Supabase, Drizzle ORM
- All projects use pnpm (never npm or yarn)
- Always use Svelte 5 runes syntax ($state, $derived, $effect) — never Svelte 4 stores or reactive declarations ($:, writable, derived)

## Communication Style

- Be concise but thorough
- Explain "why" not just "what"
- Don't apologize for mistakes, just fix them
- Ask clarifying questions rather than making assumptions

## Things to Always Do

- Run type checks before considering work complete
- Preserve existing code style in files being edited
- Use existing patterns from the codebase, don't invent new ones
- Consider mobile-first for any UI work
- After reading a file, reference it from context. Only re-read if the file was modified since last read.
- Use Glob instead of find/ls commands. Use Grep instead of grep/rg. Use Read instead of cat.

## Things to Never Do

- Never commit secrets or credentials
- Never use `any` type without explicit justification
- Never delete data without explicit confirmation
- Never run destructive commands without asking first
- Never add dependencies without checking for existing alternatives
- Never generate fake/placeholder data in production code

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

## Token Optimization

# requires @RTK.md to be loaded — if missing, skip rtk prefix and use commands directly
- Always prefix CLI commands with `rtk` when available: `rtk git log`, `rtk ls`, `rtk read file`, `rtk grep pattern`
- Use `rtk` for: git, gh, cat, ls, grep, rg, curl, docker, pnpm, vitest, tsc, svelte-check, eslint, prettier, playwright, cargo, pytest
- RTK compresses verbose output before it enters context — 60-90% token savings

## Systems

@RTK.md

## Workflow

@workflow/ship-log.md
@workflow/tmux-tasks.md
