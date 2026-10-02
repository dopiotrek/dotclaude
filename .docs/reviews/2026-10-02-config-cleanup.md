---
title: Global config cleanup audit
status: approved — hard cut
last_updated: 2026-10-02
context_for_ai: Keep/cut plan for the global Claude Code setup (dotclaude → ~/.claude). Inputs - the 2026-10-02 /insights report (174 sessions, 2026-09-11 → 10-02) and a read of the repo at HEAD 40448c3. Plugins, MCP servers and per-skill usage counts are NOT yet known (see "Missing data").
---

# Global config cleanup — 2026-10-02

## Decision

2026-10-02: **hard cut** chosen. Global keeps only what most repos use; the rest moves to the project that needs it or is cut. Rules for each item are in "Execution brief" below.

## Inputs

- `/insights` report, 2026-09-11 → 2026-10-02: 174 sessions, 485 commits, 48/49 sessions fully or mostly achieved.
- Top friction: buggy code (33), wrong approach (23), misunderstood request (10), tool permission blocked (4).
- Main causes named by the report: UI built from a guess instead of options; shared components not reused (SettingList, combobox); "done" before checking the running app and the right database (local vs prod Supabase); deploy steps rediscovered each session; deploys blocked by permissions, expired tokens and empty GitHub Actions minutes; small uncommitted leftovers at session end.
- Repo at HEAD: ~98 skill folders (~2,000 tracked files), 9 agents, 13 hooks, 3 rules, 11 KB `CLAUDE.md`.

## Missing data

Cowork cannot read `~/.claude/`. Before the final cut, collect:

1. Per-skill and per-agent use counts from session transcripts.
2. Installed plugins and marketplaces.
3. User-level MCP servers.

Command (run on the Mac, writes into this repo):

```bash
cd ~/repos/dotclaude && {
  echo "## skills (Skill tool)"; grep -ho '"skill":"[^"]*"' ~/.claude/projects/*/*.jsonl | sort | uniq -c | sort -rn
  echo "## slash commands"; grep -ho '<command-name>/[^<]*' ~/.claude/projects/*/*.jsonl | sort | uniq -c | sort -rn | head -80
  echo "## agents"; grep -ho '"subagent_type":"[^"]*"' ~/.claude/projects/*/*.jsonl | sort | uniq -c | sort -rn
  echo "## plugins"; ls ~/.claude/plugins 2>&1; cat ~/.claude/plugins/installed_plugins.json 2>/dev/null | head -80
  echo "## mcp"; claude mcp list 2>&1
} > .docs/reviews/usage-raw.txt
```

## Skills — proposed decisions

Rule: global = used across most repos. Niche or project-bound → move into that project's `.claude/skills/`.

| Group | Skills | Proposal | Why |
| --- | --- | --- | --- |
| gstack (vendored) | `gstack/` (1,161 files) + ~50 `gstack-*` link folders | **Cut** (keep at most 2–3 used ones as own copies) | `CLAUDE.md` already bans `gstack-browse`; `ship`, `review`, `qa`, `design-review` overlap own skills/agents; ~50 entries eat the skill listing budget |
| App sync copy | `synced/` (docx, pdf, pptx, xlsx, docs, morning, skill-creator, import-memory) | **Untrack + .gitignore** | Managed by the Claude app, not by this repo |
| Banned tool | `playwright-cli` | **Cut** | `CLAUDE.md` forbids it |
| Video | `hyperframes*` (10), `media-use`, `motion-graphics` (~400 files) | **Move to the site/video repo** | Used for the explainer video and logo sting only |
| UI taste | `frontend-design`, `emil-design-eng`, `make-interfaces-feel-better`, `review-animations`, `web-design-guidelines`, `awwwards-hero/sections/motion`, `oklch-skill` | **Merge to 2**: one "build UI" skill, one "review UI" skill. Keep `oklch-skill` only if used | 9 skills with overlapping triggers; the model picks one at random |
| SEO / marketing | `ai-seo`, `seo-audit`, `programmatic-seo`, `free-tool-strategy`, `find-keywords`, `google-search-console` | **Keep**, check usage | Active work (dronelist, front/q) |
| Writing | `humanizer`, `latent-economy` | **Keep**; consider moving `latent-economy` to its content repo | |
| Stack reference | `supabase`, `supabase-postgres-best-practices`, `turborepo`, `ai-sdk`, `svelte-component-architecture`, `superforms-reference` | **Keep** | Core stack |
| Quality | `uiverify`, `test-audit`, `tdd-workflow`, `clean-comments`, `thermo-nuclear-code-review`, `agent-handoff` | **Keep**, check `tdd-workflow` usage | |
| Browser | `agent-browser` | **Keep** | The chosen browser tool |
| New | `ship` | **Add** (global steps + per-project deploy command in project `CLAUDE.md`) | Report: deploy/commit in ≥14 sessions, rediscovered each time |

Target: ~100 → ~30 global skills.

## Agents — proposed decisions

| Agent | Proposal | Why |
| --- | --- | --- |
| `code-reviewer`, `debug-specialist`, `discovery-agent`, `seo-expert` | Keep (check usage) | Distinct jobs |
| `backend-engineer`, `frontend-engineer` | Cut unless usage says otherwise | Same job as the main session; `CLAUDE.md` says delegate rarely |
| `superforms-expert` | Cut | Duplicates `superforms-reference` skill |
| `vercel-deployment-expert` | Replace with `ship` skill | Deploy is Vercel CLI or Coolify per project |
| `mobile-ui-designer` | Cut unless used | |

## Settings and hooks

- `skillListingBudgetFraction: 0.02` with ~100 skills cuts descriptions short, so skills trigger badly. Re-check after the skill cut; it should then be enough.
- Permissions: add `allow` rules for the deploy commands you approve (Vercel CLI, Coolify, `gh pr merge`). Report: 4 sessions blocked here. Decide which production actions Claude may run.
- `typecheck-after-edit` already exists, yet "buggy code" is still the top friction. Check that it fires in the procurement and dronelist repos (20 s debounce, package detection). Fix before adding anything new.
- `dependency-audit`, `sveltekit-perf-guard`, `import-path-validator`, `sveltekit-route-validator`: check that each one has blocked or warned at least once; cut the silent ones.
- Delete `hooks/rtk-rewrite.sh.bak` (tracked in git).

## CLAUDE.md

- 11 KB, loaded in every session. Move the long "Browser Automation" block into the `agent-browser` skill; keep 2 lines in `CLAUDE.md`. Same block is copied in `AGENTS.md`.
- Add from the report, short: (1) reuse an existing shared component before you build a new one, and check all its users when you change it; (2) before "done", confirm which database the app points to; (3) end every session with: uncommitted, not verified, local vs live.
- Already covered, leave as is: "verify in the running app", "restate scope before multi-file refactor".

## Repo hygiene

- `README.md` rewrite (open since June audit).
- Re-run `./install.sh` (open since June).
- `mining/` not touched since June — keep or archive.
- `workflow/templates` (Linear CI) and empty `.cursor/`, `.agents/` — check, likely archive.

## Order of work

1. Collect missing data (command above).
2. Cut and move skills/agents (one commit per group).
3. Settings: permissions + budget; fix typecheck hook.
4. `CLAUDE.md` trim + 3 additions; add `ship` skill.
5. Re-run `install.sh`, start a fresh session, check `/skills` and `/agents` lists.
6. Then: local repos, one by one.

Apply steps 2–5 in Claude Code on the Mac. Cowork cannot write `skills/`, `agents/`, `CLAUDE.md` or `~/.claude/`.

## Execution brief (paste into Claude Code, in ~/repos/dotclaude)

```text
Read .docs/reviews/2026-10-02-config-cleanup.md. Do the "hard cut" it describes. Work in ~/repos/dotclaude on a new branch `chore/hard-cut`.

1. Usage data. For every skill folder in skills/ and every agent in agents/, count uses in ~/.claude/projects/*/*.jsonl over the last 60 days: Skill tool calls ("skill":"<name>"), slash commands (<command-name>/<name>) and subagent_type. Record the count AND the list of project folders it was used in. Also list installed plugins (~/.claude/plugins) and `claude mcp list`. Write the result to .docs/reviews/usage-raw.txt.

2. Classify each skill and agent with these rules, in this order:
   - KEEP global: core stack reference (supabase, supabase-postgres-best-practices, turborepo, ai-sdk, svelte-component-architecture, superforms-reference), agent-browser, uiverify, test-audit, agent-handoff, or used in 2+ projects.
   - MOVE: used in exactly 1 project → that project's .claude/skills/ (or .claude/agents/). Do not commit in the target repo; list the move.
   - MERGE: the 9 UI taste skills (frontend-design, emil-design-eng, make-interfaces-feel-better, review-animations, web-design-guidelines, awwwards-hero, awwwards-sections, awwwards-motion, oklch-skill) → `ui-build` and `ui-review`. Keep only the rules that are not generic advice. Max ~150 lines each.
   - CUT: everything else with 0 uses. Always cut: gstack/ and all gstack-* links, playwright-cli, superforms-expert agent, vercel-deployment-expert agent, hooks/rtk-rewrite.sh.bak.
   - skills/synced/: `git rm --cached` and add to .gitignore. Do not delete the folder.
   Show me the table (name | uses | projects | decision) and WAIT for my OK before you change files.

3. After my OK: one commit per group (cut, move, merge, synced, agents). Before you cut a skill, grep the repo, CLAUDE.md, AGENTS.md, rules/ and hooks/ for its name and fix the references.

4. Plugins and MCP: list each with uses. Propose disable/remove. Wait for my OK. Do not uninstall on your own.

5. Settings template: add permissions.allow for `vercel deploy*`, `vercel --prod*` and `gh pr merge*` (ask me for the Coolify command). Keep skillListingBudgetFraction for now.

6. Hook check: in ~/repos/<procurement app> and ~/repos/<dronelist>, edit one .ts file with a type error and confirm typecheck-after-edit blocks it (exit 2). If it does not fire, find why and fix it. Revert the test edit.

7. CLAUDE.md: move the long Browser Automation block into skills/agent-browser (keep a 2-line pointer). Add the 3 lines from the appendix below. Add skills/ship/SKILL.md from the appendix.

8. Run ./install.sh. Report: skills before/after, agents before/after, what moved where, what is not done. Update TODO.md (close the README and install.sh items only if done in this session).
```

## Appendix A — CLAUDE.md additions (Working Habits)

- Before you build UI, search for an existing shared component (lists, tables, pickers, dialogs) and reuse it. When you change a shared component, check every place that uses it.
- Before you say "done", confirm which database and environment the running app points to (local or production).
- At the end of a session, list: uncommitted changes, items not verified in the browser, and what is live versus only local. Then commit what is finished.

## Appendix B — skills/ship/SKILL.md

```markdown
---
name: ship
description: Commit, push and deploy the current project to production, then verify it is live. Use when the user says ship, deploy, release, push to prod, or commit and deploy.
---

1. Read the project's CLAUDE.md for its deploy command (Vercel CLI or Coolify). If none is written, ask once and add it there.
2. Run `git status`. List uncommitted and unpushed changes. Group them into atomic conventional commits. Ask once about anything that looks unrelated.
3. Confirm which environment and database the app points to.
4. Run the type check, lint and tests. Stop on failure and report the output.
5. Commit and push.
6. Deploy with the project's direct command. Do not wait on GitHub Actions.
7. Check the live site: key pages return 200 and the changed feature renders.
8. Report: commits shipped, deploy URL, checks passed or failed, anything not done, and the rollback command.
```

## Docs check — 2026-10-02 (Claude Code v2.1.285)

Verified on live pages: code.claude.com/docs/en/{skills,sub-agents,hooks,memory,permission-modes,plugins-reference}.md and the GitHub CHANGELOG. These items change the execution brief above; where they conflict, this section wins.

1. **Use the built-in audits first.** `/skill-doctor` shows cost and use per skill (in `/plugin` → Stats). `/doctor prompt-audit` (v2.1.283+) checks CLAUDE.md, rules, skills, agents and commands for stale or conflicting text and proposes edits. Run both before step 2 and add their findings to the table.
2. **Skill listing budget.** The default is 1% of the context window. On overflow, Claude Code drops descriptions of the least-used skills first. Description + `when_to_use` are cut at 1,536 chars. Our `skillListingBudgetFraction: 0.02` doubles the default; after the cut, remove the key and use the default.
3. **`skillOverrides`** (settings): `"off"` / `"name-only"` / `"user-invocable-only"` per skill name. Use it to switch off the unused skills inside the plugins we keep (we cannot delete those files).
4. **`syncClaudeAiSkills: false`** (user settings) stops the claude.ai skill sync. This is why `skills/synced/` is in git: `~/.claude/skills` links to this repo. When turned off, Claude Code moves synced skills to `~/.claude/skills/.trash/`, so add `skills/.trash/` to `.gitignore` too.
5. **Auto mode is now the default start mode** (v2.1.283+), and its classifier **blocks production deploys and migrations by default**. This explains the deploy blocks in the insights report. Allow rules resolve before the classifier, so step 5 (exact `permissions.allow` rules for the deploy commands) is the fix. Alternative: `autoMode.allow` / `autoMode.environment`. Keep the rules narrow.
6. **Hooks.** PostToolUse exit 2 does not block; it only shows stderr to Claude (our type-check hook works this way). New: `async: true` and `asyncRewake: true` (runs in the background, wakes Claude on exit 2). Use `asyncRewake` for the Stop-hook verify, so its result reaches Claude instead of a log file. Check if the new `PostToolBatch` event can replace the 20 s debounce of the type-check hook (not yet verified). `if` takes one rule only — our June fix was correct.
7. **Auto memory is built in and on by default** (`~/.claude/projects/<repo>/memory/`). The `claude-memory` plugin and `mining/` overlap with it. Uninstalling a plugin deletes its `${CLAUDE_PLUGIN_DATA}` folder unless you pass `--keep-data`: back up first.
8. **Agent frontmatter** now has `omitClaudeMd`, `effort`, `isolation` (worktree), `background`, `memory`, `skills`, `mcpServers`, `hooks`, `maxTurns`. For the agents that move to frontq, consider `model`/`effort` and `omitClaudeMd: true` when the prompt carries all context.
9. **CLAUDE.md size**: target under 200 lines; imports still load at launch. Ours (~120 lines) is fine after the planned trims.
10. **AGENTS.md** is read only when no CLAUDE.md exists on the path (v2.1.277+). No double load with our setup.
11. **Models**: Opus 5.5 and Sonnet 5.5 are the defaults, both 1M context. Sonnet 5.5 costs half of Opus 5.5 per token — consider it for the code-reviewer agent.

Not verified, do not act on: an `/agent <name>` command; a "Not used recently" filter in `/plugin`; using `claude plugin eval` to measure plugin cost (it tests plugin behavior, it does not measure cost — use `/skill-doctor`).
