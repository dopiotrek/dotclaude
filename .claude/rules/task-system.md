# Task System

Tasks live in `.claude/tasks/` with subdirectories: `active/`, `completed/`, `backlog/`.

**When starting non-trivial work:**
1. Create a task file: `.claude/tasks/active/YYYY-MM-DD-task-name.md`
2. Use this format:

```
# Task: Short descriptive title
Status: in-progress
Created: YYYY-MM-DD
Updated: YYYY-MM-DD HH:MM
Priority: high | medium | low
Feature: feature-id (from features.json, if applicable)

## Goal
One sentence — what "done" looks like.

## Plan
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Notes
Key decisions, context, blockers. Free-form.
```

3. **Update the Plan section** as you complete steps (check boxes, add new ones)
4. **Update Notes** with key decisions and context — especially things that would be lost during compaction
5. When done, move the file to `completed/`

**Critical:** The precompact hook automatically snapshots git state into the task file. The postcompact hook restores it. Keep the task file accurate — it's your lifeline across compaction boundaries.

**After compaction:** If you notice context was just compressed, immediately read the active task file to restore your working state.
