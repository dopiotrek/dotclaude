---
name: agent-handoff
description: Write a fresh handoff document (overwriting the previous one) so the next agent with fresh context can continue this work.
---

# Agent Handoff Skill

Write or update a handoff document so the next agent with fresh context can continue this work. The handoff should be concise but complete enough that a fresh agent can pick up immediately without asking clarifying questions.

## Steps

1. Read `.docs/handoff.md` if it exists — only to find anything that must outlive this session.
2. Move that lasting content out before you overwrite, then drop it from the handoff:
   - product truth → `.docs/product/standing-context.md`
   - tooling gotchas that keep costing time → `.docs/engineering/working-notes.md`
   - a decision with reasoning → a new ADR in `.docs/decisions/`
   - deferred work → root `TODO.md`
3. Review this session's work: `git diff`, `git log --oneline -10`, and the files you touched.
4. **Overwrite** `.docs/handoff.md` with the template below. Never append, and never keep older sessions in the file. The previous handoff stays in git history (`git log -p -- .docs/handoff.md`).

## Template

```markdown
# Handoff

## Goal

What we're trying to accomplish (the why, not just the what).

## Current State

Where we left off. Be specific: which file, which function, what's working vs broken.

## Key Decisions Made

Important choices, tradeoffs, or conclusions reached during this session. Include the reasoning so the next agent doesn't relitigate them.

## What Worked

Approaches that succeeded — keep doing these.

## What Didn't Work

Approaches that failed or were abandoned. Include why, so they're not retried.

## Recent Changes

Files modified, commands run, dependencies added. Keep it factual.

- `path/to/file.ts` — what changed
- `path/to/other.ts` — what changed

## Important Context

Technical constraints, environment details, gotchas, or user preferences that aren't obvious from the code alone.

## Next Steps

Ordered action items for the next session. First item should be immediately actionable.

1. ...
2. ...
```

## Guidelines

- One session only. If the file holds more than one `## Goal`, it was appended — that is a bug, not history.
- Max ~8 KB. If it is longer, lasting content belongs in step 2's destinations, not here.
- Be specific over comprehensive. "Fixed the auth redirect in `+page.server.ts` line 42" beats "Made progress on auth."
- Length follows the work. A session that touched three files gets a short handoff. Drop template sections that have nothing to say rather than filling them with restatements — a padded handoff buries the parts that matter.
- If a decision was contentious or non-obvious, explain the reasoning. The next agent will otherwise second-guess it.
- Keep Recent Changes to files actually touched this session, not a full project history.
- If the task is complete, say so and note any follow-up items or things to monitor.

## Output

Save as `.docs/handoff.md`. Tell the user:

- The file path
- A one-line summary of where things stand
- That they can start a fresh session with: `claude "Read .docs/handoff.md and continue where we left off"`
