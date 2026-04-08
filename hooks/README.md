# Hooks

Hooks are scripts that run before/after Claude Code tool invocations. They provide automated guardrails for security, code quality, and developer experience.

## Hook Types

| Event              | When it Runs                     | Can Block?   | Use Case                    |
| ------------------ | -------------------------------- | ------------ | --------------------------- |
| `PreToolUse`       | Before tool execution            | Yes (exit 2) | Validation, transformation  |
| `PostToolUse`      | After successful tool execution  | No           | Formatting, auditing        |
| `UserPromptSubmit` | Before Claude processes a prompt | No           | Context injection           |
| `Stop`             | When Claude completes work       | No           | Verification, notifications |
| `Notification`     | When Claude needs user attention | No           | Desktop notifications       |
| `SessionStart`     | On startup or resume             | No           | State restoration           |

## Exit Codes

- `0` - Success, continue normally
- `1` - Warning, show stderr to user (doesn't block)
- `2` - Block the operation, show stderr to Claude

## Performance Notes

Hooks spawn a process on every matching event. To minimize overhead:

- **Use `if` conditionals** in settings to skip hooks when the file path doesn't match (e.g., only run drizzle-migration-guard on `.sql` files)
- **Use pipe matchers** like `Write|Edit|MultiEdit` instead of duplicating hooks per tool
- **Dangerous pattern blocking** is handled by `permissions.deny` in settings (native, zero overhead) — don't duplicate it in hooks

## Included Hooks

### Security

#### `no-secrets.py`

**Event:** PreToolUse (Write|Edit|MultiEdit)

Blocks hardcoded secrets from being written to files:

- Stripe live keys (`sk_live_*`)
- OpenAI API keys (`sk-*`)
- Supabase service role keys
- JWT tokens
- Hardcoded passwords

### Code Quality

#### `auto-format.py`

**Event:** PostToolUse (Write|Edit|MultiEdit)

Auto-formats code after edits using appropriate formatters:

- **Prettier** - JS, TS, JSX, TSX, JSON, CSS, SCSS, HTML, MD, YAML, Svelte
- **Black** - Python
- **gofmt** - Go
- **rustfmt** - Rust
- **php-cs-fixer** - PHP

Skips: node_modules, .svelte-kit, build, dist, lock files

#### `import-path-validator.py`

**Event:** PreToolUse (Write|Edit|MultiEdit)
**Conditional:** Only runs on `.ts`, `.js`, `.svelte` files

Enforces import conventions for monorepo projects:

- Blocks cross-package relative imports (use `@package/*` instead)
- Warns about deep relative imports (use `$lib/` in SvelteKit)
- Warns about wildcard imports (tree-shaking issues)
- Warns about deprecated `$app/stores` (use `$app/state` in Svelte 5)

#### `sveltekit-route-validator.py`

**Event:** PreToolUse (Write|Edit|MultiEdit)
**Conditional:** Only runs on files in `routes/` directories

Validates SvelteKit routing conventions:

- Ensures `+` prefix on route files (+page.svelte, +server.ts)
- Detects Svelte 3 syntax (\_\_layout.svelte, index.svelte)
- Catches common typos (+pages.svelte, +layouts.svelte)

#### `sveltekit-perf-guard.py`

**Event:** PostToolUse (Bash)
**Conditional:** Only runs on build commands (pnpm build, vite build)

Monitors bundle size and performance:

- Checks total JS bundle size against budget (default 1000KB)
- Warns about individual chunks exceeding 100KB
- Detects anti-patterns: wildcard imports, full lodash, moment.js

### Database & Migrations

#### `drizzle-migration-guard.py`

**Event:** PreToolUse (Write|Edit|MultiEdit)
**Conditional:** Only runs on `.sql` files, `migrations/`, and `schema*` files

Prevents dangerous schema changes:

- **Blocks:** DROP TABLE, DROP SCHEMA, TRUNCATE, DELETE without WHERE
- **Warns:** DROP COLUMN, ALTER COLUMN TYPE, SET NOT NULL without DEFAULT

#### `supabase-rls-reminder.py`

**Event:** PreToolUse (Write|Edit|MultiEdit)
**Conditional:** Only runs on `.sql` files, `migrations/`, and `schema*` files

Reminds to add Row Level Security when creating tables:

- Detects new table definitions in Drizzle schema files
- Checks for tables with tenant columns (organizationId, userId)
- Suggests RLS policy patterns

### Token Optimization

#### `rtk-rewrite.sh`

**Event:** PreToolUse (Bash)

Transparently rewrites CLI commands to RTK equivalents for 60-90% token savings:

- git, gh, cargo, pnpm, vitest, tsc, eslint, prettier, docker, kubectl, curl, pytest, ruff

Skips silently if `rtk` or `jq` are not installed.

### Context & Learning

#### `lessons-loader.py`

**Event:** UserPromptSubmit

Injects relevant past lessons into every prompt:

- Reads `.claude/logs/ship-log.md` for lesson entries
- Matches tags against current prompt keywords
- Returns top 5 relevant lessons (max 300 chars each)

#### `stop-verify-and-log.py`

**Event:** Stop

Runs verification checks in background when Claude completes work:

- TypeScript: `pnpm tsc --noEmit`
- Svelte: `pnpm svelte-check --threshold error`
- Python: `mypy .`
- Rust: `cargo check`

Results saved to `.claude/logs/last-verify.txt`. Failures auto-append lessons to `.claude/logs/ship-log.md`.

### Dependencies

#### `dependency-audit.py`

**Event:** PostToolUse (Write|Edit|MultiEdit)
**Conditional:** Only runs when package.json, requirements.txt, Cargo.toml, or Gemfile are modified

Runs security audits on dependency file changes.

## Removed Hooks (April 2026 cleanup)

The following hooks were removed as they're now handled by native Claude Code features:

- **`permission-auto-approve.py`** — Replaced by `permissions.allow` and `permissions.deny` rules in settings.json (native, zero overhead)
- **`bash-command-validator.py`** — Triple coverage with CLAUDE.md instructions + RTK rewrite hook
- **`web-search-enhancer.py`** — Low value, search engines already bias toward recent results

## Creating Your Own Hooks

### Basic Template

```python
#!/usr/bin/env python3
import json
import sys

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Your logic here...

    # Exit codes: 0 = allow, 1 = warn user, 2 = block + tell Claude
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Using `if` Conditionals (v2.1.85+)

In settings.json, use `if` to skip hooks when irrelevant:

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "if": "Write(*.sql)|Edit(*.sql)|MultiEdit(*.sql)",
  "hooks": [{ "type": "command", "command": "python3 $HOME/.claude/hooks/drizzle-migration-guard.py" }]
}
```
