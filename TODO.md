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
      path-scoped rules trigger on *reading* a matching file and would miss
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
- [ ] **[AGENTS]** Trim `agents/superforms-expert.md` — move reference docs
      into a skill (audit). Not verified whether already done.
- [ ] **[SKILLS]** Archive unused `skills/gstack/` skills (audit). Not
      verified whether already done.
