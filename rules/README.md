# rules/

User-level Claude Code rules. `install.sh` symlinks this directory to
`~/.claude/rules/`, so every `.md` here loads into **every** project on this
machine.

## How loading works

- Every `.md` is discovered recursively (subdirectories like `frontend/` are
  fine).
- A rule **without** `paths` frontmatter loads unconditionally, at the same
  priority as `~/.claude/CLAUDE.md`.
- A rule **with** a `paths` glob loads only when Claude works with a matching
  file — so stack-specific guidance costs no context until it's relevant.
- User-level rules load **before** a project's `.claude/rules/`, so project
  rules win on conflicts.

## Path-scoped rule

```markdown
---
paths:
  - "**/*.svelte"
  - "src/**/*.{ts,tsx}"
---

# Svelte 5 rules
- Use runes ($state, $derived, $effect) — never Svelte 4 stores or `$:`.
```

| Pattern                 | Matches                                  |
| ----------------------- | ---------------------------------------- |
| `**/*.svelte`           | all Svelte files, any directory          |
| `**/schema/**`          | anything under a `schema/` directory     |
| `**/package.json`       | every package manifest                   |
| `src/**/*.{ts,tsx}`     | TS/TSX under `src/`                       |

## Convention here

Keep one topic per file with a descriptive name (`svelte5.md`, `drizzle.md`,
`security.md`). Put always-on machine-wide preferences in an unscoped file;
scope anything stack-specific with `paths` so it stays out of context until it
matters.

> Note: `~/.claude/CLAUDE.md` and these rules are both global. Don't duplicate a
> rule in both places — pick one home for each fact.
