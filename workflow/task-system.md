# Task System

Active work is tracked in `.claude/current-task.md` — a single file, always the current thing.

**When to write it:**
- When exiting plan mode (write the full plan)
- When starting non-trivial work
- When switching to a different task

**Format:**

```
# Task: Short descriptive title
Status: in-progress | blocked | done
Branch: feature-branch-name
Updated: YYYY-MM-DD HH:MM

## Goal
One sentence — what "done" looks like.

## Plan
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Notes
Key decisions, context, blockers. Free-form.
```

**Keep it current:**
- Check off steps as you complete them
- Add new steps if scope changes
- Update Notes with key decisions — especially things that would be lost during compaction
- Set Status to `done` when finished

**Critical:** The precompact hook snapshots git state into this file. The postcompact hook restores it. Keep it accurate — it's your lifeline across compaction boundaries.

**After compaction:** If you notice context was just compressed, immediately read `.claude/current-task.md` to restore your working state.
