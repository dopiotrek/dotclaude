# Coding Sessions — Recurring Corrections

Last mined: 2026-06-10 · 50 sessions scanned (2026-05-10 → 2026-06-10) · 88 correction signals

## Recurring corrections

### 1. Agent declares a fix done without verifying it in the running app (seen 4× across 4 sessions · projects: tma)

- **What happens:** Agent edits code, reports the fix as complete, and the user immediately disproves it by looking at the actual app — screenshot, blank window, or unchanged behavior.
- **Examples:**
  > [Image #1] still visible
  > if i play with the numbers, nothing changes, not even the chart
  > the tauri app is blank, does not start
  > i have 193 mapping rules in the database but see only the one for Spotify
- **Candidate CLAUDE.md rule:** Already covered by: "Verify claims against the running app (screenshot/observe), not solely against your own DB/file reads or theory." **Rule exists but isn't holding** — all 4 sessions postdate the rule. The correction loop only closes when verification is forced (browse/screenshot step), not requested.

### 2. Agent claims "applied everywhere" but instances remain (seen 3× across 3 sessions · projects: tma)

- **What happens:** On sweep tasks (replace all inputs, fix all scrollbars, show all rules), the agent finishes the cases it touched and stops; the user pastes screenshots of the ones it missed, often over multiple rounds in one session.
- **Examples:**
  > we have a lot more [Image #1], and on scenarios route [Image #2]
  > what about these fields [Image #4]
  > portfolio value, annual savings, spending in retirement as well
  > but thge scrollbar is still visible on the sidebar
- **Candidate CLAUDE.md rule:** Already covered by: "For 'apply X everywhere' tasks… grep for ALL occurrences first, list them, change each, then re-grep to prove zero remain." **Rule exists but isn't holding.** Contrast: the one time coverage was actually achieved (tma 300-line decompose arc, ~12 commits), it was a `/goal` stop hook blocking session exit — a gate, not a rule.

### 3. Agent works from a stale spec/skill file the user just updated (seen 3× across 3 sessions · projects: deep-dives)

- **What happens:** The user edits the source-of-truth file (skill definition, design rules) between or during sessions; the agent keeps generating artifacts to the old version until explicitly told to re-read.
- **Examples:**
  > the design was updated for how the html should look like
  > the skill also says we should have only one html, not multiple
  > I updated the skill again, with style guidlines for the charrs, read and redo
  > check the skill, we have updated the namings as well
- **Candidate CLAUDE.md rule:** "Before regenerating any artifact governed by a spec/skill/rules file, re-read that file first — treat specs as mutable, never trust the in-context copy across user edits."

### 4. Agent leaves worktrees/branches dangling after merging (seen 3× across 3 sessions · projects: tma, khira, dronelist)

- **What happens:** Agent completes the merge/commit and stops; the user has to ask about the leftover worktree or branch every time.
- **Examples:**
  > what about the worktrees?
  > but there is a branch : claude/pedantic-shaw-b0e8e6
  > ok merge now with dev, cleanup branch and worktree
- **Candidate CLAUDE.md rule:** "After merging work from a worktree or feature branch, remove the worktree and delete the branch in the same step — cleanup is part of the merge, not a follow-up."

### 5. Agent asserts code is absent based on a single grep (false negative) (seen 2× across 2 sessions · projects: dronelist, tma)

- **What happens:** A single (RTK-proxied) grep returns zero results and the agent confidently asserts the pattern doesn't exist — wrong both times, once corrupting an audit conclusion, once nearly removing a `use:enhance` that was actually in use.
- **Examples:**
  > you say svelte superforms is not used, but it is
  > (agent self-correction, tma): "The `use:enhance` is still in the save form template — the RTK grep gave a false negative."
- **Candidate CLAUDE.md rule:** "Never assert something is absent from the codebase on the strength of one grep — confirm absence with a second search using different terms or an unproxied tool. RTK grep has produced false negatives."

### 6. Calculated numbers contradict the user's authoritative real-world figures (seen 2× across 2 sessions · projects: tma)

- **What happens:** Financial outputs (portfolio total, retirement age) disagree with the user's ground truth from their broker or basic arithmetic; the user supplies the real numbers and the agent has to trace the discrepancy (stale prices, missing EUR conversion, off-by-years).
- **Examples:**
  > what i dont understand is the discrepancy between my traderepublic actual portfolio value (today 348,862EUR) but the app shows 364,185
  > Retiring in 2026 at age 50 - this cannot be tru when i am 43 at 20206,
- **Candidate CLAUDE.md rule:** Already covered by: "Treat the user's domain knowledge as authoritative" + "restate exactly which inputs feed a metric before coding." **Partially holding** — corrections still recur on multi-currency/stale-price paths specifically.

### 7. Artifact claimed ready but broken or invisible on the user's end (seen 2× across 2 sessions · projects: dotclaude, yoda)

- **What happens:** Agent hands off a generated artifact (HTML report, state.json-driven map) that the user can't open or that fails to parse — delivery was claimed, not verified.
- **Examples:**
  > i dont see the report
  > Could not parse state.json.
- **Candidate CLAUDE.md rule:** "After generating an artifact the user must open (report, HTML, JSON state), verify it opens/parses before reporting it ready." (Cousin of pattern 1 — same verification gap, different surface.)

## Observed once

- `.env` files staged in a commit despite the user believing they were gitignored (dronelist) — surfaced during pre-commit; user caught it, not the agent.
- User manually inserts dry-run gates before DB deploys (`pnpm db:deploy:dry`, `supabase migration list` typed as bash-input mid-session) — the user is building verification checkpoints the agent doesn't offer.
