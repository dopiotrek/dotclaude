---
name: next-task
description: Take the next agent-ready item from this repo's TODO.md (tagged [agent]), build it on a branch, prove it with `pnpm verify`, and open a PR with auto-merge. Use when asked for "the next task", or when a scheduled run starts with /next-task.
---

# Next task

One item per run. The output is a PR, or a clear note on why there is none.

## 1. Pick

- Read `TODO.md` with `grep -n '\[agent\]' TODO.md`. Never read the whole file.
- Take the first open item (`- [ ]`) tagged `[agent]` that has no `(PR #…)` or
  `(blocked: …)` note.
- If no item qualifies, stop and say so. Do not pick an untagged item.

## 2. Check it is ready

An item is ready when it says what to change and how to tell it is done.
If it is not ready, or it needs a product decision, a new dependency, a
schema change on shared data, or a production action:
- add ` (blocked: <one line why>)` to the item, commit that on a branch, open
  a PR for it, and stop.

## 3. Build

- Work on a branch `agent/<short-slug>` (in a cloud session the clone is
  already isolated; locally use a worktree — see `factory-workflow.md`).
- Keep the change to what the item asks. Note anything else you find as a new
  `TODO.md` item, not as extra code.

## 4. Prove

- Run `pnpm verify`. Fix failures the change caused. Never weaken a check.
- If a step cannot run here (no database, no `.env`), name it in the PR.

## 5. Land

- In `TODO.md`, mark the item `- [x]` and add ` (PR #<n>)` after you open the
  PR (amend the branch with that one-line change).
- `gh pr create --fill`; the body says: the item, what changed, how it was
  verified, what could not run.
- `gh pr merge --auto --squash`. CI decides; never merge by hand, never `--admin`.

## Writing good [agent] items (for Piotrek)

`- [ ] [agent] [UI] Rename "Bidders" to "Suppliers" on the tender page — done
when no "Bidders" string is left in apps/web/src/routes/(app)/tenders/**.`
One change, one place, one check.
