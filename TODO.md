# TODOS

Unfinished or deferred work items from agent sessions in this repo. Agents: append here when you defer something; check items off only after verifying the fix. Never delete another session's items.

## Hooks

- [ ] **[HOOKS]** `hooks/supabase-rls-reminder.py` line 272 uses a backslash
      inside an f-string expression. That is a SyntaxError on Python < 3.12,
      so the hook dies silently wherever `python3` is 3.10/3.11. Fix: move the
      escaped quote into a variable before the f-string. (Found 2026-06-12
      maintenance pass.)

## Install / local machine

- [ ] **[INSTALL]** Re-run `./install.sh` after the 2026-06-12 `mining/` move
      so `~/.claude/mining` gets symlinked. Until then the session-mining
      skill writes to paths that no longer exist. The installer also removes
      the old per-file symlinks (`coding-sessions.md`, `content-ideas.md`,
      `.session-mining-ledger.json`) from `~/.claude/`.
- [ ] **[GIT]** A zero-byte `.git/index.lock` was stranded by a sandbox mount
      on 2026-06-12. Git operations still worked, but if git ever refuses to
      run with an "index.lock exists" error, delete the file.

## Open items from the April 2026 setup audit (.docs/reviews/claude-code-setup-audit-2026-04.md)

Items 1–3 of the audit are done (redundant hooks deleted, `os.fork` gone).
`if` conditionals are adopted in `settings/settings.template.json`. Still open:

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
