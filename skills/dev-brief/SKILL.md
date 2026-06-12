---
name: dev-brief
description: >
  Morning command-center sweep: checks Vercel deployments, PostHog errors, Supabase advisors,
  and open Linear issues across all projects, then pushes actionable findings to Linear.
  Use when asked for a "dev brief", "morning brief", "what's broken", or "project status".
  Also triggered by the daily scheduled task. Requires Vercel, PostHog, and Linear MCPs connected.
---

# Dev Brief — Command Center Sweep

You are running a cross-project health check. Check every source, filter ruthlessly, push only
what requires a developer's focused attention to Linear. Silent if everything is clean.

## Projects in scope

| Project       | Vercel ID                              | GitHub repo (dopiotrek/)  |
|---------------|----------------------------------------|---------------------------|
| dronelist-app | prj_acB8Iq85UZ1dDvrrBbPOmyaoYLtt      | dronelist                 |
| dronelist-mkt | prj_wT5yn33hH3k0vSn0TShGFe2NYwCq      | dronelist                 |
| swissCRM      | —                                      | swisscrm                  |
| piotrek-cc    | —                                      | piotrek-cc                |
| thatmoneyapp  | —                                      | that-money-app            |

- **Vercel team**: `team_vD1RgxbpbCqxBBYEWJGkskNL` (build-ship)
- **PostHog project**: 88549 (build/ship, EU region: eu.posthog.com)
- **Linear team**: "Make now"

---

## Phase 1 — Vercel: deployment failures

List recent deployments for both Vercel projects. Filter to the last 24 hours. Flag any with
`state: ERROR` or `state: CANCELED` on the `main` or `production` branch.

For each failure, note: project name, branch, deployment URL, timestamp.

**Threshold**: create a Linear issue for any production branch failure. Skip preview branch failures.

---

## Phase 2 — PostHog: active errors

Check the PostHog error tracking for active issues. Filter to issues with at least 5 occurrences
OR first seen in the last 48 hours. Check health issues for anything with severity `critical` or
`warning`.

For each finding: exception type, occurrence count, first/last seen, affected users.

**Threshold**: create a Linear issue for any error with 10+ occurrences or 5+ affected users.
For new errors (< 48h), threshold is 3+ occurrences.

---

## Phase 3 — Supabase: advisors (if connected)

If the Supabase MCP is available and authenticated, list security and performance advisors for
all projects. If the MCP returns an auth error, skip this phase and note it in the summary.

**Threshold**: security advisors → always create a Linear issue (Urgent). Performance advisors
with a HIGH impact → Medium priority Linear issue.

---

## Phase 4 — Linear: deduplication

Before creating any issue, fetch open issues in team "Make now" with status not in
[Done, Canceled, Duplicate]. For each finding from phases 1–3, check for an existing issue
with a matching title keyword. Skip creation if a near-duplicate exists.

---

## Phase 5 — Issue creation

For each qualifying finding with no duplicate, create a Linear issue:

```
title:  [Source/Project] Short description ≤ 60 chars
team:   Make now
assignee: me
priority: per threshold table below
description:
  **Source**: Vercel / PostHog / Supabase
  **Project**: [name]
  **Detail**: [specific error, deployment URL, advisor text]
  **First seen / detected**: [timestamp]
  **Link**: [direct URL to the finding]
  **Auto-created**: dev-brief — [YYYY-MM-DD]
```

Priority table:

| Finding | Priority |
|---|---|
| Vercel production deploy failed | High (2) |
| PostHog error 50+ occurrences | Urgent (1) |
| PostHog error 10–49 occurrences | High (2) |
| PostHog error < 10 occurrences, new | Medium (3) |
| Supabase security advisory | Urgent (1) |
| Supabase performance advisory | Low (4) |
| PostHog health warning | Medium (3) |
| PostHog health critical | High (2) |

---

## Phase 6 — Output

After all phases complete, output a compact summary (≤ 20 lines):

```
## Dev Brief — [YYYY-MM-DD HH:MM]

### Created
- MAK-XX: [title] (Priority: High)

### Skipped (duplicate of MAK-YY)
- [title]

### Clean
- Vercel: ✅  PostHog: ✅  Supabase: ⚠️ (not connected)

### GitHub (via Actions)
Staleness + CI covered separately — check Linear for [CI] and [PR] prefixed issues.
```

If nothing was created: output only `✅ All clear — [date]`. No noise.
