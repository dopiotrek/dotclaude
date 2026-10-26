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

- **Every path-sensitive hook self-checks the file path** (extension + directory) and exits early on irrelevant files, so it is safe to register them under a broad `matcher` without an `if` filter. This is the approach in `settings.template.json`.
- **Use pipe matchers** like `Write|Edit|MultiEdit` instead of duplicating hooks per tool. Note: the pipe (`|`) is only valid in `matcher` (tool names). The `if` field holds **exactly one** permission rule — no `|`, `&&`, or list syntax. If you need to narrow to several path patterns, use one matcher group per rule, or let the hook self-check (preferred).
- **Dangerous pattern blocking** is handled by the `permissions.deny` block in settings (native, zero overhead) — don't duplicate it in hooks.

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

#### `typecheck-after-edit.py`

**Event:** PostToolUse (Write|Edit|MultiEdit)
**Conditional:** Only runs on `.ts`, `.tsx`, `.svelte` files

Type-checks the **single package** the edited file belongs to, right after the
edit, and feeds any errors back to Claude (exit 2) so it self-corrects in the
same turn instead of declaring "done" with broken types. `pnpm verify` stays the
full check.

- Walks up to the nearest `package.json` and runs that package's own `check`
  script (so `svelte-kit sync`, tsconfig, and thresholds are respected),
  falling back to `tsc --noEmit` if there's no `check` script. Scoped with
  `pnpm -C <pkg>` so it never triggers the root `turbo check` graph.
- **Runs in the background** (`asyncRewake` in `settings.json`): svelte-check on
  an app package takes ~24s, so edits do not wait. Exit 2 wakes Claude with the
  errors.
- **One check per package at a time**: an edit that lands mid-check marks the
  package dirty and the running hook re-checks when it finishes.
- Silent on success; never crashes the turn (any error → exit 0).

Tuning via env vars:

- `CLAUDE_SKIP_TYPECHECK=1` — disable entirely
- `CLAUDE_TYPECHECK_TIMEOUT` — max seconds per check run (default 60)

### Database & Migrations

#### `drizzle-migration-guard.py`

**Event:** PreToolUse (Write|Edit|MultiEdit)
**Conditional:** Only runs on `.sql` files, `migrations/`, and `schema*` files

Prevents dangerous schema changes:

- **Blocks:** DROP TABLE, DROP SCHEMA, TRUNCATE, DELETE without WHERE in migrations; `dropTable()` in schema files
- Block only: warn-only checks were removed because Claude never sees them

### Token Optimization

#### `rtk-rewrite.sh`

**Event:** PreToolUse (Bash)

Transparently rewrites CLI commands to RTK equivalents for 60-90% token savings:

- git, gh, cargo, pnpm, vitest, tsc, eslint, prettier, docker, kubectl, curl, pytest, ruff

Skips silently if `rtk` or `jq` are not installed.

## Removed Hooks (April 2026 cleanup)

The following hooks were removed as they're now handled by native Claude Code features:

- **`permission-auto-approve.py`** — Replaced by `permissions.allow` and `permissions.deny` rules in settings.json (native, zero overhead)
- **`bash-command-validator.py`** — Triple coverage with CLAUDE.md instructions + RTK rewrite hook
- **`web-search-enhancer.py`** — Low value, search engines already bias toward recent results

October 2026:

- **`import-path-validator.py`**, **`sveltekit-route-validator.py`** — Hardcoded dronelist paths; a wrong route name fails the build anyway
- **`supabase-rls-reminder.py`** — Never blocked, and PreToolUse stderr on exit 0 never reaches Claude, so it had no effect. The RLS rule lives in `rules/drizzle-supabase.md`
- **`sveltekit-perf-guard.py`** — Fixed bundle budgets that fit no single project
- **`stop-verify-and-log.py`** — Third copy of the same check, next to `typecheck-after-edit.py` and `pnpm verify`
- **`dependency-audit.py`** — GitHub already reports vulnerable dependencies

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

`if` skips a hook when the call doesn't match, avoiding the process spawn. It holds **exactly one** permission rule — there is no `|`, `&&`, or list syntax (that is `matcher`-only). To cover several patterns, register one matcher group per rule:

```json
{
  "matcher": "Write|Edit",
  "if": "Edit(**/*.sql)",
  "hooks": [{ "type": "command", "command": "python3 $HOME/.claude/hooks/drizzle-migration-guard.py" }]
},
{
  "matcher": "Write|Edit",
  "if": "Edit(**/migrations/**)",
  "hooks": [{ "type": "command", "command": "python3 $HOME/.claude/hooks/drizzle-migration-guard.py" }]
}
```

Because `if` is best-effort and can't express OR in one field, the hooks in this repo skip it and self-check the path instead (see Performance Notes). Use `permissions.deny` — not a hook — to enforce a hard block.
