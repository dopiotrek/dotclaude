# TODOS

Unfinished or deferred work items from agent sessions in this repo. Agents: append here when you defer something; check items off only after verifying the fix. Never delete another session's items.

## Hooks

- [x] **[HOOKS]** `hooks/supabase-rls-reminder.py` line 272 used a backslash
      inside an f-string expression (SyntaxError on Python < 3.12). Fixed
      2026-06-17: the `"org_isolation"` literal is now hoisted into
      `policy_name` before the f-string. Verified with `py_compile`.

## Install / local machine

- [ ] **[INSTALL]** Re-run `./install.sh` after the 2026-06-12 `mining/` move
      so `~/.claude/mining` gets symlinked. Until then the session-mining
      skill writes to paths that no longer exist. The installer also removes
      the old per-file symlinks (`coding-sessions.md`, `content-ideas.md`,
      `.session-mining-ledger.json`) from `~/.claude/`.
- [ ] **[GIT]** A zero-byte `.git/index.lock` was stranded by a sandbox mount
      on 2026-06-12. Git operations still worked, but if git ever refuses to
      run with an "index.lock exists" error, delete the file.

## From the June 2026 config audit (.docs/reviews/2026-06-17-dotclaude-config-audit.md)

Done 2026-06-17:

- [x] **[AGENTS]** All agents used `allowed-tools` (a skills field subagents
      ignore), so tool restrictions never applied. Renamed to `tools:`
      (comma-string). C1.
- [x] **[SETTINGS]** Every `if` filter packed multiple permission rules with
      `|`, which `if` does not support (one rule only). Removed all `if`
      filters; the path-sensitive hooks already self-check the path. C2.
- [x] **[SETTINGS]** Added a `permissions.deny` block (env/secrets reads,
      `rm -rf` of root/home). The old hooks/README claimed this existed; it
      didn't. H2.
- [x] **[AGENTS]** Deleted orphaned `agents/linear-reporter.md` (pointed at the
      removed linear-triage loop). H3.

Still open (High/Medium from the June audit):

- [ ] **[DOCS]** Rewrite `README.md` — counts wrong (13/9/4 vs 10/9/78), lists
      5 deleted hooks, calls the `code-reviewer` agent a skill, documents
      settings keys that don't exist. H1.
- [x] **[DOCS]** ~~CLAUDE.md claims `.claude/rules/` is auto-loaded; it isn't.~~
      RETRACTED 2026-06-17 — `.claude/rules/` IS a real Claude Code feature
      (recursive `.md` discovery, `paths`-scoped loading, symlinks, user-level
      `~/.claude/rules/`). The CLAUDE.md claim is correct. Wired `install.sh` to
      symlink `rules/ → ~/.claude/rules` and added `rules/README.md`.
- [ ] **[RULES]** PROPOSED: split stack-specific blocks out of the global
      `CLAUDE.md` into `~/.claude/rules/*.md` with `paths` scoping (svelte5 →
      `**/*.svelte`, drizzle/rls → schema+migrations, pnpm/monorepo →
      `package.json`) so they don't sit in context every session. Awaiting
      sign-off before moving content.
- [x] **[SKILLS]** Skill `name`s now match their directories (done 2026-06-17:
      handoff→agent-handoff, ui-skills→frontend-design,
      svelte-architect→svelte-component-architecture). Fixed the stale
      `/svelte-architect` command refs in skills/README.md too. M5.
- [x] **[RULES]** Split done 2026-06-17: `rules/svelte5.md` (paths `**/*.svelte`)
      and `rules/drizzle-supabase.md` (paths schema/migrations/sql). Kept an
      always-on runes guard + all security/pnpm rules in CLAUDE.md, because
      path-scoped rules trigger on _reading_ a matching file and would miss
      greenfield file creation / command choice.
- [x] **[SKILLS]** Removed every dangling cross-ref (description, inline, and
      Related-Skills bullets) to non-installed skills across all custom skills;
      kept refs to installed ones. Done 2026-06-17.
- [x] **[DOCS]** Rewrote stale `skills/README.md` (was 4 skills incl. the
      `code-reviewer` agent); now an accurate grouped index + frontmatter table.
      Cleaned literal `\n` from 3 agent descriptions. Done 2026-06-17.

## Open items from the April 2026 setup audit (.docs/reviews/claude-code-setup-audit-2026-04.md)

Items 1–3 of the audit are done (redundant hooks deleted, `os.fork` gone). Still open:

- [ ] **[SETTINGS]** Set `autoMemoryDirectory: ".claude/memory"` in settings
      (audit item 15). Not present in `settings.template.json` as of
      2026-06-12.
- [ ] **[SKILLS]** Add the `paths` field to the most-used custom skills for
      auto-activation (audit item 13). Zero skills use it as of 2026-06-12.
- [ ] **[SETTINGS]** Verify `settings.template.json` matches the live
      `~/.claude/settings.json` (audit item 4). Needs a check on the local
      machine; cannot be verified from the repo.
- [x] **[AGENTS]** Trim `agents/superforms-expert.md` — move reference docs
      into a skill (audit). Not verified whether already done.
      (2026-10-02: agent cut; `superforms-reference` skill covers it.)
- [x] **[SKILLS]** Archive unused `skills/gstack/` skills (audit). Not
      verified whether already done.
      (2026-10-02: all gstack skills cut.)

## Claude 5-generation model alignment (2026-08-04)

Done this session: `CLAUDE.md` response-shape + delegation caps, `code-reviewer`
report-everything principles, removed self-verification scaffolding from
`frontend-engineer` / `debug-expert` / `backend-engineer`, fixed the broken code
fence in `backend-engineer.md`, aligned `.docs/` paths, fixed
`vercel-deployment-expert` tool grant, refreshed `agents/README.md`,
`skills/README.md`, `rules/README.md`, root `README.md`.

Deferred:

- [ ] **[SKILLS]** Apply progressive disclosure to the oversized custom skills:
      `turborepo` (914 lines), `tdd-workflow` (449), `seo-audit` (408). Each
      pays its full context cost on every trigger. Split the decision path into
      `SKILL.md` and push detail into `references/`. Deferred: each is a
      content restructure that needs a read-through, not a mechanical edit.
- [ ] **[AGENTS]** Re-check `effort` on the agents against real runs. All the
      sonnet agents inherit session effort and both opus agents are pinned
      `high`; Claude 5-generation docs say `low`/`medium` often hold quality at
      a fraction of the cost. Deferred: needs eval on actual tasks, can't be
      settled from the repo.
- [ ] **[AGENTS]** `backend-engineer.md` and `frontend-engineer.md` still carry
      long inline code examples. Candidates for moving into a skill's
      `references/` rather than sitting in every spawn's context. Deferred:
      scope call — the examples do encode real project conventions.

## Hard cut (2026-10-02, .docs/reviews/2026-10-02-config-cleanup.md)

Done on branch `chore/hard-cut`: cut gstack (56 folders), `playwright-cli`,
`hooks/rtk-rewrite.sh.bak` and six agents; untracked `skills/synced/`; fixed
`typecheck-after-edit` (it could not find pnpm, so it never fired); moved the
browser rules into the `agent-browser` skill; added the `ship` skill. Usage
data is in `.docs/reviews/usage-raw.txt`.

Deferred:

- [ ] **[SETTINGS]** Add `permissions.allow` for `Bash(vercel deploy*)`,
      `Bash(vercel --prod*)` and the Coolify deploy command
      to `settings/settings.template.json`. Deferred: auto mode blocks Claude
      from widening its own permissions, so this needs a manual edit; the
      Coolify command is not known yet. (2026-10-03: `Bash(gh pr merge*)`
      dropped from this item; agents never run `gh pr merge` now, see
      `rules/factory-workflow.md`.)
- [ ] **[INSTALL]** `./install.sh` not re-run. It replaces the live
      `~/.claude/settings.json` with the template, and the template lacks keys
      the live file has (`model`, `enabledPlugins`, `extraKnownMarketplaces`,
      `autoMode`). All other items are already symlinked, so nothing else was
      pending. Sync the template with the live file first.
- [x] **[HOOKS]** `stop-verify-and-log.py` and `dependency-audit.py` call bare
      `pnpm`, same as `typecheck-after-edit` did before the fix. Likely silent
      for the same reason (pnpm lives under mise, not on the hook PATH).
      (2026-10-02: both now find pnpm through mise; tested in frontq and
      dronelist.)
- [x] **[HOOKS]** `stop-verify-and-log.py` only looks for `tsconfig.json` and
      `svelte.config.*` at the repo root. frontq has neither there, so the Stop
      hook runs no check in that repo. Deferred: outside the pnpm fix.
      (2026-10-02: in a pnpm workspace it now runs one check per changed
      package; tested in frontq and dronelist.)
- [x] **[DOCS]** `hooks/README.md` still describes the Stop hook as root-only
      `pnpm tsc` / `svelte-check`. Deferred: another agent had uncommitted
      edits in that file. (2026-10-02: Stop hook section rewritten.)
- [ ] **[HOOKS]** `asyncRewake` on `typecheck-after-edit` and
      `stop-verify-and-log` is tested by hand only (scripts exit 2 with the
      errors). Confirm in a live session that a type error wakes Claude.
      Deferred: flags load only in a new session.
- [ ] **[HOOKS]** Check that `dependency-audit`, `sveltekit-perf-guard`,
      `import-path-validator` and `sveltekit-route-validator` have each fired at
      least once; cut the silent ones. Deferred: not in the execution brief.
- [x] **[PLUGINS]** Uninstalled 30 unused plugins (kept `cloudflare` and
      `next-steps`) and removed the `playwright`, `stripe` and `gemini-cli` MCP
      servers.
- [ ] **[SKILLS]** `skills/agent-browser/SKILL.md` now holds a "My setup"
      section. A vendor update of that skill would overwrite it; re-add after
      updating.
- [ ] **[DOCS]** `README.md` still lists skills that do not exist
      (`tapforce-shadcn-svelte`, `tutor`, `deep-dive-burst`, …). Only the cut
      items were removed this session; the full rewrite is still open.
- [ ] **[SKILLS]** Hard cut is not finished: 45 skill folders remain (target
      ~8). Still to do from the review: cut the 0-use skills (ai-sdk,
      clean-comments, find-keywords, free-tool-strategy, frontend-design,
      latent-economy, make-interfaces-feel-better, oklch-skill,
      programmatic-seo, review-animations, supabase,
      supabase-postgres-best-practices, superforms-reference,
      svelte-component-architecture, tdd-workflow, thermo-nuclear-code-review,
      turborepo, web-design-guidelines); move the video set (hyperframes*,
      media-use, motion-graphics, general-video) and google-search-console to
      dronelist, emil-design-eng to frontq; merge awwwards-motion into
      awwwards-hero; merge ai-seo + seo-audit. Found missing in the 2026-10-02
      final check (Cowork session).
- [ ] **[SETTINGS]** Template still has `skillListingBudgetFraction: 0.02` and
      no `syncClaudeAiSkills: false`; `.gitignore` lacks `skills/.trash/`. Do
      together with the template/live sync before `./install.sh`.

## Agent factory (2026-10-03, .docs/reviews/2026-10-03-software-factory-audit.md)

- [ ] **[CI]** Run `Claude outputs/factory-runner.sh` on the Mac first: GitHub-hosted
      minutes are used up, so all jobs in the four factory repos now run on a
      self-hosted runner in an OrbStack VM (`runs-on: [self-hosted, linux]`).
      compass and tma are included now; tma's macOS release build stays on
      GitHub's runner (needs macOS).
- [ ] **[GIT]** Run `Claude outputs/factory-land.sh` on the Mac: settings sync +
      `install.sh`, push dotclaude, push the four `chore/agent-factory` branches,
      open the PRs and leave them open (free plan: no branch protection, so the
      script skips the merge; Piotrek merges when CI is green). Deferred: the
      Cowork session has no GitHub credentials.
- [x] **[SKILLS]** (2026-10-03: done; the skill leaves the PR open and never runs
      `gh pr merge`.) Align `skills/ship` with `rules/factory-workflow.md` (branch,
      PR left open for Piotrek to merge, never push to `main`). Deferred: the
      Cowork bridge cannot read `skills/`.
- [x] **[RULES]** (2026-10-03: trimmed on the `chore/agent-factory` branches of frontq,
      dronelist, swissCRM; lands with factory-land.sh. compass/tma copies untouched.)
      Shared rules are live, but the repo copies of svelte, forms,
      tailwind, motion, ux-* still load too. Trim each repo copy to its delta
      ("stays in repo" lists in `.docs/reviews/2026-10-03-shared-rules-conflicts.md`).
- [x] **[RULES]** (2026-10-03: `factory-land.sh` step 1 runs `fix-claude-md-docs.py`;
      the docs rule wins.) `CLAUDE.md` "Project Docs" table (`ai/`, `archive/`, no
      `handoff.md`/`specs/`) contradicts `rules/docs-conventions.md` (`_archive/`,
      `handoff.md`, `specs/`). Pick one.
- [x] **[SKILLS]** (2026-10-03: done as `factory/skills` + factory-sync instead of a
      plugin, so cloud agents get them too.) Move the 5 design skills copied in
      dronelist + frontq into one private plugin (audit F6).
- [x] **[RULES]** (2026-10-03: 169-line rule + `design-system` skill with 7 reference
      files, on swissCRM's factory branch.) swissCRM `design.md` is 932 lines and loads on every `.svelte`
      edit; split into rule + skill references (audit F5).
- [x] **[SYNC]** (2026-10-03: a SessionStart hook in the settings template runs
      `factory-sync --check --quiet` and tells the agent when a repo is behind.)
      After editing anything in `rules/`, `factory/` or the four guard
      hooks, run `factory-sync` and commit in each factory repo. A `--check`
      step in CI would catch a forgotten sync; not added yet.
- [ ] **[CLOUD]** Cloud sessions have no `.env` and no local Postgres. Add the
      env vars each repo needs in the cloud environment settings on claude.ai;
      `test:db` steps stay CI-only.
- [ ] **[RULES]** `factory/core.md` repeats the stack and hard limits from
      `CLAUDE.md` (cloud agents never see `CLAUDE.md`). Locally both load; keep
      them in step, or move "Hard Limits" out of `CLAUDE.md` into a rule.
- [x] **[RULES]** (2026-10-03: decided — see the "Resolved" section of the conflicts
      review.) Repo rule copies still disagree with the shared rules in places
      (each kept its own side): compass + tma import Tabler from the barrel,
      compass forms say "superforms always", compass ux-* carry swissCRM's aviation
      text (copy drift?), `duration-slow-1100` = 1000ms in compass and tma. See
      `.docs/reviews/2026-10-03-shared-rules-conflicts.md`.
- [ ] **[QUEUE]** After the factory PRs merge and CI is green: tag 1–2 small
      `TODO.md` items `[agent]` in one repo, run `/next-task` by hand once, then
      schedule it (`/schedule` in Claude Code, a cloud routine, e.g. weekdays
      03:00, prompt `/next-task`). Merge its PRs with `factory-prs`. Add the repo's env vars to the cloud
      environment first.
- [ ] **[GIT]** Free GitHub plan (decided 2026-10-03): no branch protection, no
      auto-merge on private repos. Agents open PRs; Piotrek merges green ones with
      `factory-prs`. piotrek-cc#3 was merged before CI by `gh pr merge --auto`.
- [x] **[SKILLS]** (2026-10-03: it did say `gh pr merge --auto --squash`; changed to
      "leave the PR open".) Check `skills/ship` (changed 2026-10-03 in fa9e7da): it
      must not run `gh pr merge`. The Cowork bridge cannot read it.
