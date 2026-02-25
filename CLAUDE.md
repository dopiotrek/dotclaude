# Global Claude Preferences

## About Me

- Primary stack: SvelteKit, TypeScript, Supabase
- All projects use pnpm (never npm or yarn)

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

## Build Log

Before finishing any non-trivial task (not typos, not quick questions), append an entry to `.claude/logs/build-log.md`. This is used for content creation — blog posts, social media, changelogs.

Format each entry like this:

```
## YYYY-MM-DD | Category: Short title

**What:** One sentence — what was built/fixed/changed.
**Why:** The problem or motivation. What was broken, missing, or needed.
**How:** The approach taken, key decisions, tradeoffs considered.
**Outcome:** What's different now. Concrete result.
**Takeaway:** One reusable insight — the kind of thing worth sharing in a post.
```

Categories: Feature, Fix, Refactor, Infrastructure, Performance, DX, Design.
Keep entries concise (5-8 lines max). Write for an audience of devs building SaaS with AI tools.
Skip entries for trivial changes (renaming, comment updates, formatting).

## Current Task

If working on a task, check `.claude/current-task.md` in the project root for context.

@RTK.md
