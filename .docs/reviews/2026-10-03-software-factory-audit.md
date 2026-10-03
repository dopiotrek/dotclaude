# Software factory audit (2026-10-03)

Scope: `dotclaude/` (the `~/.claude` source) and the 8 repos in `repos/apps`.
Not readable from the audit session: `dotclaude/CLAUDE.md`, `agents/`, `skills/`
(the file bridge protects them) and the live `~/.claude/settings.json`.
Earlier audits (`2026-10-02-prompt-audit.md`, `2026-10-02-config-cleanup.md`)
covered prompt wording and skill cuts. This one covers the **work system**: how
an agent gets a task, works on it, proves it is done, and lands it.

## What already works

- One source of truth for global config (`dotclaude` → `~/.claude` symlinks).
- Real guardrail hooks: secrets, lockfiles, `.env`, migrations, auto-format,
  type check after edit and on Stop (`asyncRewake`, wakes Claude on errors).
- Path-scoped rules in every app repo, so most rules cost nothing until needed.
- A shared `.docs/` standard with `handoff.md`, `specs/`, `decisions/`.
- Auto mode as default. CI with real gates in frontq (tenancy + RLS tests).
- Agents already do most of the work: frontq had 801 commits in 30 days,
  786 co-authored by Claude. swissCRM 113 of 120.

## The main gap

**Agents work directly on `main`, in the main checkout.** frontq: 801 commits,
1 merge in 30 days. There is no branch → PR → CI → review → merge path for
agent work. This blocks the two things a factory needs:

1. **Parallel work.** Two sessions in one checkout fight over files and the
   dev server. Worktrees exist (`.claude/worktrees/`) but are unused.
2. **A gate you trust.** CI runs after the code is already on `main`. Review
   (dronelist only) runs on PRs that agents do not open.

## Findings

| # | Sev | Where | Finding | Fix |
|---|-----|-------|---------|-----|
| F1 | High | all repos | Agent work lands on `main` directly. No PR path. | Worktree per task → PR → CI → merge. `ship` skill opens the PR. |
| F2 | High | `settings.template.json` | `allow: gh pr merge *`, `vercel --prod *`. Narrow allow rules run **before** the auto-mode classifier, so they switch off its two most useful blocks: merging unreviewed PRs and production deploys. With F1 this means an agent can merge and deploy its own work with no human or CI check. | Move both to `ask`, or allow merge only through a gate (CI green). Decision needed. |
| F3 | High | `settings.template.json` `autoMode.environment` | Written by `/auto-mode-setup` inside frontq. It tells the classifier, in **every** repo, that the trusted repo is `dopiotrek/frontq` and that the main use is FrontQ. In the other 7 repos pushes may be misjudged. | Generalize: source control = `github.com/dopiotrek/*`; keep frontq-only lines labeled "in frontq". |
| F4 | High | 5 repos | Same-name rules drift: `svelte-patterns`, `tailwind-patterns`, `motion`, `forms`, `ux-*`, `design` exist in 3–5 repos, **every copy different** (md5). A fix in one repo never reaches the others. | Move the shared core to `dotclaude/rules/` (user-level, path-scoped). Keep only project deltas in repos. Plugins cannot ship rules, so user rules are the right channel. |
| F5 | Med | swissCRM, tma, dronelist | Context cost. Opening one `.svelte` file in swissCRM loads ~1,900 rule lines (`design.md` alone is 932). tma loads ~700 lines in **every** session (5 rules without `paths`). | Split big rules into a short rule + skill `references/`. Add `paths` to tma's always-on rules. |
| F6 | Med | dronelist + frontq | 5 identical project skills copied in both (`brandkit-gen`, `imagegen-frontend`, `pixel-perfect`, `product-description`, `visual-redesign`). | Private plugin `studio-design` in a marketplace inside `dotclaude`; enable per repo in `.claude/settings.json`. |
| F7 | Med | tma, loom | Instruction files drift. tma has CLAUDE.md, AGENTS.md, GEMINI.md: three versions (GEMINI says superforms, CLAUDE says Zod; AGENTS imports a misspelled `code-guidlines.md`). loom CLAUDE.md/AGENTS.md differ in ~10 places. compass and swissCRM already solve this with a symlink. | One file + symlinks (compass pattern). |
| F8 | Med | all repos | No single "done" command. Only swissCRM has `pnpm verify`. Stop hook, CI and agents each guess what to run. | Add `pnpm verify` to every repo = the factory contract. Stop hook, `ship` and CI all call it. |
| F9 | Med | `hooks/protect-files.sh` | Tells the agent to run `supabase migration new`. The repos use Drizzle (`pnpm db:generate`) and hand-numbered `NNNN_*.sql`. The hook teaches the wrong command. | Point to the repo's own migration command. |
| F10 | Med | 6 repos | `.claude/worktrees/` not gitignored (6 repos), `.claude/settings.local.json` not ignored (6), `CLAUDE.local.md` not ignored (8). Worktree use would show the worktree as untracked files. | Add to `.gitignore`. |
| F11 | Low | compass, swissCRM, piotrek-cc, loom, ui-registry | No committed `.claude/settings.json`. Nothing repo-level is shared (deny rules, plugins, verify allow). | Small baseline settings per repo. |
| F12 | Low | tma `settings.local.json` | Permission sprawl: 13 one-off `sed` lines from a past refactor. | Clean. |
| F13 | Low | dronelist CI | `claude-code-review.yml` runs a hand prompt; the `code-review` plugin is now the documented path. `claude.yml` has `contents: read`, so `@claude` cannot push a fix. Only dronelist has these workflows. | Decide if PR review runs in CI or locally (`/code-review`). |
| F14 | Low | install | Template and live settings differ; `install.sh` not re-run (open TODO). Every settings fix here is blocked on that sync. | Sync live → template once, then always edit the template. |
| F15 | Low | tools | Session tooling differs per repo: `entire` only in tma, `.gstack/` folders left in dronelist, loom, swissCRM after the gstack cut, `.cursor`/`.gemini` configs. | Remove leftovers; pick one session-capture tool or none. |

## Target setup (one recommendation)

Simple. Built from what exists. No new services.

```
dotclaude/                      control plane — applies to every repo
  CLAUDE.md                     who I am, how I work, hard limits
  rules/                        shared stack rules (svelte, tailwind, drizzle, forms, motion, ux) — path-scoped
  hooks/                        guardrails + Stop gate (calls `pnpm verify` when it exists)
  plugins/studio-design/        skills shared by some repos (marketplace in .claude-plugin/)
  settings/settings.template.json

<repo>/                         one product
  AGENTS.md  (CLAUDE.md → AGENTS.md)   repo facts only; <150 lines
  .claude/settings.json         deny rules, enabled plugins, verify allow
  .claude/rules/                project-only deltas
  .docs/specs/                  the work queue's "ready" items (status: approved)
  .docs/handoff.md              last session only
  TODO.md                       backlog
  package.json  "verify"        the definition of done
```

### The work loop

1. **Spec.** A task becomes `.docs/specs/<slug>.md` (`status: approved`). Small
   fixes can skip this and use a TODO line.
2. **Isolate.** `claude -w <slug>` → own worktree + branch `worktree-<slug>`.
   Many tasks can run at once.
3. **Build.** Agent works in auto mode. Hooks guard secrets, lockfiles, migrations.
4. **Prove.** Stop hook runs `pnpm verify`; exit 2 wakes the agent until green.
5. **Land.** `ship` skill pushes and opens a PR. CI runs `pnpm verify` +
   repo-specific gates. Review: `/code-review` subagent (fresh context).
6. **Merge.** You merge — or auto-merge on green CI for low-risk labels later,
   once the gate has earned trust.
7. **Unattended (later).** Routines or `@claude` on GitHub issues take
   `[agent]`-tagged backlog items and end at step 5, never step 6.

## Decisions needed

- D1: Who merges and deploys (F2)?
- D2: Consolidate shared rules into `dotclaude/rules/` (F4)? Which repo's copy
  is the base when copies disagree?
- D3: Shared design skills as a private plugin (F6)?
- D4: Is the PR path (F1) for all repos, or only the active products?
