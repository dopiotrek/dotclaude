# dotclaude v2 — System Blueprint

## What Changed

Four new systems that make Claude Code context-aware, compaction-proof, and content-ready.

---

## 1. Task System (compaction-proof continuity)

**Files:**
- `.claude/tasks/active/` — current work
- `.claude/tasks/completed/` — done
- `.claude/tasks/backlog/` — planned
- `hooks/task-snapshot.py` — precompact hook, saves state before compression
- `hooks/task-restore.py` — postcompact + SessionStart hook, restores context

**How it works:**
- CLAUDE.md tells Claude to create task files when starting non-trivial work
- Each task has: Goal, Plan (checkboxes), Notes, and an auto-managed Context Snapshot
- Before compaction: `task-snapshot.py` writes git state + timestamp to the task file
- After compaction: `task-restore.py` injects the full task file back into context
- On session start/resume: same restore hook fires, giving Claude immediate context

**The old `session-context-loader.py` and `current-task.md` pattern is replaced** by this system. The task-restore hook serves both purposes (session start + post-compaction).

---

## 2. Ship Log (merged build-log + lessons)

**Files:**
- `.claude/logs/ship-log.md` — the unified log
- `hooks/ship-log-writer.py` — replaces `lessons-writer.py`
- `hooks/lessons-loader.py` — updated to read from ship-log

**Two entry types:**
- 🚀 Ship entries — features, fixes, DX wins. Include a tweet draft.
- 💡 Lesson entries — failures, rules. Auto-logged by hook, manually fillable.

**What's different from before:**
- Build-log and lessons are now one file (easier to scan, one source of truth)
- Every ship entry includes a `Tweet draft:` field for build-in-public content
- lessons-loader.py reads from ship-log (with legacy lessons.md fallback)
- Higher quality bar: no more "ran pnpm check" entries

**Migration:** The old `build-log.md` has been preserved. The single existing entry was ported to ship-log format. The old `lessons-writer.py` can be removed once you confirm ship-log-writer works.

---

## 3. Features Registry

**Files:**
- `.claude/features.json` — the feature map

**Structure:** Each feature has: id, name, status, category, route, description, dependencies, dates, notes.

**Statuses:** `shipped` | `in-progress` | `planned` | `paused` | `deprecated`

**How it's used:**
- CLAUDE.md tells Claude to update it when features change
- task-restore.py injects a summary of in-progress features after compaction
- You can query it yourself ("what features are planned?") or build an admin page from it

**Action needed:** You need to populate this with your actual dronelist.io features.

---

## 4. Product Concept

**Files:**
- `.claude/concept.md` — business context template

**What it provides:** Who, what, why, business model, competitive edge, product principles, tone. Claude reads this when making product decisions, naming things, or writing user-facing copy.

**Action needed:** Fill in the template with your actual product details. This is a human-authored document — Claude references it but shouldn't generate it.

---

## Settings Changes (`settings.template.json`)

**Added:**
- `PostToolUse` → `precompact` matcher → `task-snapshot.py`
- `PostToolUse` → `postcompact` matcher → `task-restore.py`

**Changed:**
- `SessionStart` → now runs `task-restore.py` instead of `session-context-loader.py`
- `Stop` → now runs `ship-log-writer.py` instead of `lessons-writer.py`

**To apply:** Run `install.sh` or manually copy settings to `~/.claude/settings.json`.

---

## File Tree (new/changed files)

```
.claude/
├── concept.md                    # NEW — product context (fill in manually)
├── features.json                 # NEW — feature registry (fill in manually)
├── logs/
│   ├── build-log.md              # KEPT — old entries preserved
│   └── ship-log.md               # NEW — merged build-log + lessons
├── tasks/
│   ├── active/                   # NEW — current task files
│   ├── completed/                # NEW — done tasks
│   └── backlog/                  # NEW — planned tasks
hooks/
├── task-snapshot.py              # NEW — precompact state saver
├── task-restore.py               # NEW — postcompact + session start restorer
├── ship-log-writer.py            # NEW — replaces lessons-writer.py
├── lessons-loader.py             # UPDATED — reads from ship-log + legacy fallback
├── lessons-writer.py             # DEPRECATED — kept for reference, replaced by ship-log-writer
├── session-context-loader.py     # DEPRECATED — replaced by task-restore.py
CLAUDE.md                         # UPDATED — new sections for tasks, ship-log, features, concept
settings/settings.template.json   # UPDATED — new hook wiring
```

---

## What You Need To Do

1. **Fill in `.claude/concept.md`** — your product's business context
2. **Populate `.claude/features.json`** — your existing features
3. **Run `install.sh`** or copy settings to apply new hooks
4. **Test the flow:** start a task in Claude Code, let it create a task file, verify precompact/postcompact hooks fire
5. **Optional cleanup:** remove `lessons-writer.py`, `session-context-loader.py`, and `current-task.md` once you're confident the new system works
