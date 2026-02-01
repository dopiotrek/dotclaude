# Hooks

Hooks are Python scripts that run before/after Claude Code tool invocations. They provide automated guardrails for security, code quality, and developer experience.

## Hook Types

| Event               | When it Runs                     | Can Block?   | Use Case                    |
| ------------------- | -------------------------------- | ------------ | --------------------------- |
| `PreToolUse`        | Before tool execution            | Yes (exit 2) | Validation, transformation  |
| `PostToolUse`       | After successful tool execution  | No           | Formatting, auditing        |
| `PermissionRequest` | When permission is requested     | Yes          | Auto-approve/deny           |
| `Stop`              | When Claude completes work       | No           | Verification, notifications |
| `Notification`      | When Claude needs user attention | No           | Desktop notifications       |

## Exit Codes

- `0` - Success, continue normally
- `1` - Warning, show stderr to user (doesn't block)
- `2` - Block the operation, show stderr to Claude

## Included Hooks

### Security & Safety

#### `no-secrets.py`

**Event:** PreToolUse (Write, Edit)

Blocks hardcoded secrets from being written to files:

- Stripe live keys (`sk_live_*`)
- OpenAI API keys (`sk-*`)
- Supabase service role keys
- JWT tokens
- Hardcoded passwords

```python
# Patterns detected:
"sk_live_xxxx"           # Stripe
"sk-xxxxxxxxxxxxxxxx"    # OpenAI
"password = 'secret'"    # Hardcoded password
```

#### `permission-auto-approve.py`

**Event:** PermissionRequest

Auto-approves safe, read-only operations to reduce permission prompts:

- Read, Glob, Grep, LS tools
- Safe git commands (status, diff, log)
- Package info commands (pnpm list, npm view)

Also blocks dangerous patterns like:

- `rm -rf /` or `rm -rf ~`
- `sudo rm`, `sudo chmod`
- `curl | sh` (piped execution)
- SQL injection patterns

#### `bash-command-validator.py`

**Event:** PreToolUse (Bash)

Enforces use of modern, faster CLI tools:

- Suggests `rg` (ripgrep) instead of `grep`
- Suggests `rg --files` instead of `find -name`

### Code Quality

#### `auto-format.py`

**Event:** PostToolUse (Write, Edit, MultiEdit)

Auto-formats code after edits using appropriate formatters:

- **Prettier** - JS, TS, JSX, TSX, JSON, CSS, SCSS, HTML, MD, YAML, Svelte
- **Black** - Python
- **gofmt** - Go
- **rustfmt** - Rust
- **php-cs-fixer** - PHP

Skips: node_modules, .svelte-kit, build, dist, lock files

#### `import-path-validator.py`

**Event:** PreToolUse (Write, Edit, MultiEdit)

Enforces import conventions for monorepo projects:

- Blocks cross-package relative imports (use `@package/*` instead)
- Warns about deep relative imports (use `$lib/` in SvelteKit)
- Blocks imports from node_modules via relative path
- Warns about wildcard imports (tree-shaking issues)
- Warns about deprecated `$app/stores` (use `$app/state` in Svelte 5)

#### `sveltekit-route-validator.py`

**Event:** PreToolUse (Write, Edit, MultiEdit)

Validates SvelteKit routing conventions:

- Ensures `+` prefix on route files (+page.svelte, +server.ts)
- Detects Svelte 3 syntax (\_\_layout.svelte, index.svelte)
- Catches common typos (+pages.svelte, +layouts.svelte)
- Warns about load functions in wrong files
- Blocks server-only imports in client files

#### `sveltekit-perf-guard.py`

**Event:** PostToolUse (Write, Edit, MultiEdit, Bash)

Monitors bundle size and performance:

- Checks total JS bundle size against budget (default 1000KB)
- Warns about individual chunks exceeding 100KB
- Detects anti-patterns:
  - Wildcard imports (`import * as`)
  - Full lodash import (use lodash-es)
  - moment.js (use date-fns)
  - Barrel imports from @tabler/icons-svelte

### Database & Migrations

#### `drizzle-migration-guard.py`

**Event:** PreToolUse (Write, Edit, MultiEdit)

Prevents dangerous schema changes in Drizzle migrations:

**Blocks (exit 2):**

- DROP TABLE, DROP SCHEMA
- TRUNCATE
- DELETE without WHERE

**Warns (exit 0):**

- DROP COLUMN
- ALTER COLUMN TYPE
- SET NOT NULL without DEFAULT

Also validates migration file naming (NNNN_name.sql format).

#### `supabase-rls-reminder.py`

**Event:** PreToolUse (Write, Edit, MultiEdit)

Reminds to add Row Level Security when creating tables:

- Detects new table definitions in Drizzle schema files
- Checks for tables with tenant columns (organizationId, userId)
- Suggests RLS policy patterns
- Provides documentation links

### Utilities

#### `command-logger.py`

**Event:** PreToolUse (Bash, Write, Edit)

Logs all Claude Code operations for audit:

- Timestamp
- Tool name
- File path (for file operations)
- Command (for Bash, truncated to 80 chars)
- Pattern (for Grep/Glob)

Logs to `~/.claude/logs/command-log.txt`

#### `dependency-audit.py`

**Event:** PostToolUse (Write, Edit)

Runs security audits when dependency files are modified:

- `package.json` / `pnpm-lock.yaml` → `pnpm audit`
- `requirements.txt` → `safety check`
- `Cargo.toml` → `cargo audit`
- `Gemfile` → `bundle audit`

#### `stop-verification.py`

**Event:** Stop

Runs verification checks when Claude completes work:

- TypeScript: `pnpm tsc --noEmit`
- Svelte: `pnpm svelte-check --threshold error`
- Python: `mypy .`
- Rust: `cargo check`

Reports pass/fail status with helpful output.

#### `web-search-enhancer.py`

**Event:** PreToolUse (WebSearch)

Enhances web searches for documentation:

- Adds current year to tech documentation queries
- Only modifies queries about docs, tutorials, APIs
- Skips queries that already have temporal context

## Creating Your Own Hooks

### Basic Template

```python
#!/usr/bin/env python3
"""
Description of what this hook does.
"""

import json
import sys

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # PreToolUse: Check input before execution
    # PostToolUse: Also has tool_response

    # Your logic here...

    # Exit codes:
    # 0 = allow/success
    # 1 = warning (show stderr to user)
    # 2 = block (show stderr to Claude)
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Input Data Structure

```python
{
    "tool_name": "Write",  # or Edit, Bash, etc.
    "tool_input": {
        "file_path": "/path/to/file",
        "content": "file content",
        # ... tool-specific fields
    },
    # PostToolUse only:
    "tool_response": {
        "success": True,
        # ... response data
    }
}
```

### Modifying Tool Input (PreToolUse)

```python
# Return modified input via stdout
output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "modifiedToolInput": {
            "query": "modified query"
        }
    }
}
print(json.dumps(output))
```

### Adding to Settings

After creating a hook, add it to `settings/settings.template.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/.claude/hooks/my-hook.py"
          }
        ]
      }
    ]
  }
}
```

## Logs

Hook logs are stored in `~/.claude/logs/`:

- `command-log.txt` - All tool operations
- `auto-format.log` - Formatting operations
- `drizzle-guard.log` - Migration checks
- `route-validator.log` - SvelteKit route validation
- `import-validator.log` - Import path checks
- `rls-reminder.log` - RLS policy reminders
- `web-search.log` - Search query modifications
