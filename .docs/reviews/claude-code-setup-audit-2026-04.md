# Claude Code Setup Audit — April 2026

Comprehensive review of hooks, scripts, agents, skills, and settings against the latest Claude Code features (v2.1.90+).

---

## Executive Summary

Your setup is mature and well-architected — 14 hooks, 9 agents, 47+ skills, custom file suggestion, and RTK integration. But it was largely built around Claude Code v2.0–v2.1.50 patterns. Since then, Claude Code has shipped **conditional hooks (`if` field)**, **hook type: agent**, **hook type: http**, **auto-memory**, **worktree isolation**, **tool search**, **1M context windows**, and **new hook events** (`FileChanged`, `CwdChanged`, `TaskCreated`, `PostCompact`). Several of your hooks are now doing work that the settings system handles natively, and some patterns are outdated.

**Impact categories:**
- 🔴 **Fix now** — broken, deprecated, or causing real perf/token waste
- 🟡 **Upgrade** — working but superseded by better native features
- 🟢 **Adopt** — new features you're not using yet

---

## 🔴 Fix Now

### 1. `permission-auto-approve.py` is redundant with your settings.json

Your `settings.template.json` already has 60+ `allow` rules covering every command this hook auto-approves (git status, git diff, ls, rg, etc.). The hook fires on **every** permission request, spawns Python, parses JSON, runs regex — all to duplicate what the native permissions engine does in microseconds.

**Action:** Delete `permission-auto-approve.py` entirely. Your `permissions.allow` list already covers it. Move any DANGEROUS_PATTERNS checks to `permissions.deny`:

```json
"deny": [
  "Bash(rm -rf /)",
  "Bash(rm -rf ~*)",
  "Bash(sudo rm*)",
  "Bash(curl * | sh)",
  "Bash(curl * | bash)",
  "Bash(wget * | sh)"
]
```

**Token savings:** ~50ms per tool call × hundreds of calls per session.

### 2. `bash-command-validator.py` fights your own CLAUDE.md

This PostToolUse hook blocks `grep` and `find` with exit code 2 — but your CLAUDE.md already says "Use Grep instead of grep/rg. Use Read instead of cat." Claude follows CLAUDE.md instructions reliably. This hook fires *after* execution (PostToolUse), meaning it blocks the *result* from reaching Claude after the command already ran. That's wasteful.

**Action:** Either delete it (CLAUDE.md handles this) or move it to `PreToolUse:Bash` so it blocks *before* execution. But honestly, between CLAUDE.md + RTK rewrite hook, this is triple-coverage for the same thing.

### 3. `stop-verify-and-log.py` uses `os.fork()` — POSIX only

This breaks on Windows and in some containerized environments. More importantly, the forked child process's results go to `/tmp/claude-verify-{pid}.txt` — but nothing ever reads that file. The verification results are written but never surfaced to Claude or to you.

**Action:** The background fork pattern was clever for v2.0, but now you can use the **`if` conditional field** on hooks + the Stop event directly. The real question: do you actually want type-checking on every Stop? If yes, consider a lighter approach — use `tmux-task.sh` to run checks in background and surface via the `SessionStart` hook on next session.

### 4. Settings template isn't your actual settings

Your `settings/settings.template.json` is a template, not the live config. Claude Code reads from `~/.claude/settings.json` or `.claude/settings.json`. If you're symlinking, fine — but verify this is actually loaded.

**Action:** Confirm with `claude /config` that hooks and permissions from this file are active.

---

## 🟡 Upgrade — Replace With Native Features

### 5. Replace hook duplication with `if` conditionals

Your Write/Edit/MultiEdit PreToolUse hooks each run the same 5 scripts:
- no-secrets.py
- drizzle-migration-guard.py
- import-path-validator.py
- sveltekit-route-validator.py
- supabase-rls-reminder.py

That's **15 hook invocations** (5 × 3 matchers) that could be 5 with modern syntax:

```json
"PreToolUse": [
  {
    "matcher": "Write|Edit|MultiEdit",
    "hooks": [
      { "type": "command", "command": "python3 $HOME/.claude/hooks/no-secrets.py" },
      { "type": "command", "command": "python3 $HOME/.claude/hooks/drizzle-migration-guard.py" },
      ...
    ]
  }
]
```

Same for PostToolUse (auto-format, dependency-audit, sveltekit-perf-guard × 3 matchers → 1).

**Action:** Consolidate matchers using pipe syntax. Check if your Claude Code version supports `Write|Edit|MultiEdit` matcher syntax (v2.1.63+).

### 6. `web-search-enhancer.py` — minor value, token cost every search

Appending "2026" to tech queries is a micro-optimization. Search engines already bias toward recent results. Every WebSearch call spawns Python for this.

**Action:** Consider removing. If you want this, a one-liner in CLAUDE.md ("When searching for documentation, include the current year") achieves the same.

### 7. `lessons-loader.py` — consider auto-memory instead

Claude Code v2.1.59+ has **auto-memory** (`/memory` command). It automatically saves useful context and loads it every session. Your lessons-loader does keyword matching against ship-log entries, which is clever — but auto-memory does contextual retrieval natively.

**Action:** Migrate high-value lessons from `ship-log.md` into `/memory` entries. Keep the hook if you want the tag-matching precision, but know that auto-memory handles the "don't forget this" use case natively now.

### 8. RTK rewrite hook — consider `if` field for efficiency

`rtk-rewrite.sh` runs on every Bash PreToolUse, even when RTK isn't installed (it checks `command -v rtk` each time). With the `if` conditional:

```json
{
  "matcher": "Bash",
  "if": "Bash(git *)|Bash(cargo *)|Bash(pnpm *)|Bash(gh *)",
  "hooks": [{ "type": "command", "command": "$HOME/.claude/hooks/rtk-rewrite.sh" }]
}
```

This skips the hook entirely for non-rewritable commands (echo, mkdir, chmod, etc.).

---

## 🟢 Adopt — New Features You're Missing

### 9. Worktree isolation for agents

Your agent team setup uses `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` but your agents don't use `isolation: "worktree"`. For code-reviewer, debug-specialist, and especially frontend-engineer working in parallel — worktrees prevent file conflicts:

```yaml
# In agent definition frontmatter
isolation: worktree
```

### 10. `FileChanged` and `CwdChanged` hook events

New hook events that fire when files change or working directory changes. You could replace the sveltekit-perf-guard PostToolUse hook (which fires on every edit) with a `FileChanged` hook that only fires when `.svelte-kit/output/` changes.

### 11. `PostCompact` hook event — restore context after compaction

Your `task-snapshot.py` / `task-restore.py` hooks use `precompact` / `postcompact` matchers. These are now proper events (`PreCompact` / `PostCompact`) — verify your matchers work with the current event names.

### 12. Hook type: `agent` — replace complex Python with prompts

Some of your hooks (supabase-rls-reminder, import-path-validator) are essentially "look at this code and give advice." The new `agent` hook type lets you write these as prompts instead of Python regex parsers:

```json
{
  "type": "agent",
  "prompt": "Check if this SQL migration creates tables without RLS policies. If so, warn about missing Row Level Security.",
  "model": "haiku"
}
```

Cheaper, more flexible, handles edge cases regex can't.

### 13. Skill `paths` field for auto-activation

Your skills don't use the `paths` field. This means Claude has to decide which skills are relevant from descriptions alone. With paths:

```yaml
# In svelte-component-architecture/SKILL.md
paths: "src/**/*.svelte, src/lib/components/**"
```

Skills auto-activate when working on matching files.

### 14. `/loop` for dev server monitoring

Instead of `tmux-task.sh run dev "pnpm dev"` + manual `tmux-task.sh read dev`, you can now use:

```
/loop 30s check dev server health at localhost:5173
```

### 15. Auto-memory directory

Set `autoMemoryDirectory` in settings to keep auto-memory in your dotclaude repo:

```json
"autoMemoryDirectory": ".claude/memory"
```

This way memories are version-controlled and shared across machines.

---

## Hook Performance Summary

| Hook | Event | Fires on | Spawns | Verdict |
|------|-------|----------|--------|---------|
| permission-auto-approve.py | PermissionRequest | Every tool | Python | 🔴 Delete (native covers it) |
| bash-command-validator.py | PostToolUse:Bash | Every bash | Python | 🔴 Delete or move to Pre |
| rtk-rewrite.sh | PreToolUse:Bash | Every bash | Bash+jq | 🟡 Add `if` conditional |
| no-secrets.py | PreToolUse:W/E/M | Every write | Python | ✅ Keep (security) |
| drizzle-migration-guard.py | PreToolUse:W/E/M | Every write | Python | 🟡 Add `if` for .sql only |
| import-path-validator.py | PreToolUse:W/E/M | Every write | Python | 🟡 Add `if` for .ts/.svelte |
| sveltekit-route-validator.py | PreToolUse:W/E/M | Every write | Python | 🟡 Add `if` for routes/ |
| supabase-rls-reminder.py | PreToolUse:W/E/M | Every write | Python | 🟡 Consider type:agent |
| web-search-enhancer.py | PreToolUse:WebSearch | Every search | Python | 🟡 Low value, consider removing |
| auto-format.py | PostToolUse:W/E/M | Every write | Python+formatter | ✅ Keep |
| dependency-audit.py | PostToolUse:W/E/M | Every write | Python | 🟡 Add `if` for package.json |
| sveltekit-perf-guard.py | PostToolUse:W/E/M/B | Every write+bash | Python | 🟡 Add `if` for build commands |
| lessons-loader.py | UserPromptSubmit | Every prompt | Python+git | ✅ Keep (unique value) |
| stop-verify-and-log.py | Stop | Every stop | Python+fork+tsc | 🔴 Fix fork, surface results |

**Current overhead per Write/Edit:** 5 PreToolUse hooks + 3 PostToolUse hooks = 8 Python spawns.
**After cleanup:** 3-4 conditional hooks that only fire when relevant.

---

## Agent Definitions Review

All 9 agents use `model: sonnet` — which is good for speed/cost. Consider:

- **code-reviewer.md** and **debug-specialist.md** — these benefit from deeper reasoning. Consider `model: opus` + `effort: high` for these two.
- **superforms-expert.md** (24KB) — this is huge. Much of it is reference docs that could be a skill reference file instead, loaded on demand. As an agent prompt, it eats context every spawn.
- **discovery-agent.md** — references repomix/Gemini. Verify these tools are still in your workflow.
- All agents lack `allowed-tools` — they inherit the session's permissions. For security, scope them: a code-reviewer shouldn't need Write access.

---

## Skills Review

47 skills is a lot. With tool search enabled (`ENABLE_TOOL_SEARCH=true`), Claude lazy-loads tool definitions — but skill descriptions are always loaded. Each skill's description consumes prompt tokens every turn.

**Action:** Audit which skills you've actually used in the last 30 days. Archive unused ones to a `skills-archive/` directory. The `gstack/` symlinked skills (68 sub-skills) are particularly suspect — do you use all of them?

---

## Quick Wins Checklist

- [ ] Delete `permission-auto-approve.py` (replaced by native permissions)
- [ ] Delete or move `bash-command-validator.py` to PreToolUse
- [ ] Consolidate Write|Edit|MultiEdit matchers (15 → 5 hook invocations)
- [ ] Add `if` conditionals to drizzle/import/route/rls hooks
- [ ] Fix `stop-verify-and-log.py` — either surface results or replace with tmux-task pattern
- [ ] Set `autoMemoryDirectory: ".claude/memory"` in settings
- [ ] Add `paths` field to top custom skills
- [ ] Trim superforms-expert.md agent — move reference docs to a skill
- [ ] Archive unused skills from gstack/
- [ ] Verify settings.template.json is actually symlinked to live config
