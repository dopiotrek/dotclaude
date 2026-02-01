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
