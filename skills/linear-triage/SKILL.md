---
name: linear-triage
description: >
  Scan the current repo for actionable issues (TODOs, type errors, CI signals, tech debt) and
  push them to Linear as triaged issues. Use when you want to run a repo health sweep, when
  prompted by a schedule, or when asked to "triage this repo" / "push issues to Linear". Requires
  the Linear MCP to be connected. Team: "Make now".
  Scans src/**/*.ts, src/**/*.svelte, src/**/*.js, and .github/workflows/*.yml.
---

# Linear Triage Skill

You are running a structured repo health scan. Your job is to find real, actionable problems —
not style preferences — and push them to Linear as clean, well-scoped issues. Be a strict filter:
if it's not worth a developer's focused attention, skip it.

## Team + Project

- **Team**: "Make now"
- **Default project**: derive from the repo name (e.g. `swissCRM`, `dronelist`, `khira`). If
  uncertain, leave project unset and note it in the issue description.
- **Assignee**: "me" (Piotrek)

## Phase 1 — Discovery (run these in sequence)

### 1a. TODO / FIXME / HACK scan

```bash
git grep -n "TODO\|FIXME\|HACK\|REVIEW\|XXX\|TEMP\|@deprecated" -- \
  '*.ts' '*.svelte' '*.js' '*.tsx' | head -80
```

Capture file, line, comment text. Skip auto-generated files (`node_modules`, `.next`, `dist`,
`build`, `.svelte-kit`).

### 1b. Type-check

```bash
pnpm typecheck 2>&1 | head -100
```

or, for SvelteKit:

```bash
pnpm svelte-check 2>&1 | grep -E "Error|error" | head -60
```

Capture each error: file, line, message. Cluster errors that stem from the same root cause — open
one issue for the root, not one per symptom.

### 1c. Recent git signals

```bash
git log --since="7 days ago" --oneline | grep -iE "fix fix|revert|hotfix|broken|oops|temp" | head -20
```

Each hit is a signal of churn worth reviewing. Don't create issues automatically — flag it and
decide if there's an open problem underneath.

### 1d. Dead code / orphaned exports (optional, run if repo is < 200 files)

```bash
pnpm knip 2>&1 | head -40
```

If `knip` isn't installed, skip silently.

## Phase 2 — Deduplication

Before creating any issue, fetch open Linear issues to avoid duplicates:

Use the Linear MCP tool to list open issues in team "Make now" — look for issues with `state`
not in `[Done, Canceled, Duplicate]`. For each finding, check if a similar issue already exists
by title keyword match. If a near-duplicate exists, skip creation and note it.

## Phase 3 — Triage & Priority

Map findings to priorities:

| Finding type | Priority |
|---|---|
| Type error blocking build | Urgent (1) |
| Type error (non-blocking) | High (2) |
| FIXME or HACK with context | Medium (3) |
| TODO with clear scope | Low (4) |
| TODO vague / aspirational | Backlog — skip or Low |
| Git churn signal | Medium (3) |
| Dead code cluster | Low (4) |

**Quality gate**: before creating an issue, verify:
- Title is ≤ 60 chars and describes the problem, not the symptom
- Description includes: file:line, current behaviour, why it matters, one-line suggested fix
- Skip anything you'd close immediately as "won't fix"

## Phase 4 — Issue Creation

For each qualifying finding, create a Linear issue with:

```
title: [Type] Short description of the problem
description:
  **File**: `path/to/file.ts:42`
  **Found by**: linear-triage scan / type-check / git signal
  **Context**: [what the code does and why this is a problem]
  **Suggested fix**: [one concrete sentence]
  **Triage date**: YYYY-MM-DD
```

Use the Linear MCP `save_issue` tool. Set `team: "Make now"`, `assignee: "me"`, and the
appropriate `priority` value.

## Phase 5 — Summary

After all issues are created (or skipped), output a compact triage report:

```
## Triage Summary — [repo] — [date]

Created: N issues
Skipped (duplicate): N
Skipped (too vague): N

### Created
- MAK-XX: [title] (Priority: High)
- ...

### Skipped (existing)
- [title] — already tracked as MAK-YY

### Skipped (below threshold)
- [file:line] — [reason]
```

Write this summary to `.docs/reviews/linear-triage-YYYY-MM-DD.md`.

## Guard Rails

- Never create more than 10 issues per run. If you find more, create the top 10 by priority and
  note the rest in the summary doc.
- Never create an issue for a line you haven't read. If the TODO is inside commented-out code,
  skip it.
- Never create duplicate issues — always check Phase 2 first.
- If the Linear MCP is not available, write all findings to `.docs/reviews/linear-triage-YYYY-MM-DD.md`
  and tell the user to connect the Linear MCP.
