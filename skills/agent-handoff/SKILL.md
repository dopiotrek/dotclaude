---
name: handoff
description: Write or update a handoff document so the next agent with fresh context can continue this work.
---

# Agent Handoff Skill

Write or update a handoff document so the next agent with fresh context can continue this work. The handoff should be concise but complete enough that a fresh agent can pick up immediately without asking clarifying questions.

## Steps

1. Check if HANDOFF.md already exists in the project root
2. If it exists, read it first to understand prior context before updating
3. Review recent work: check `git diff`, `git log --oneline -10`, and any open files to capture the full picture
4. Create or update HANDOFF.md using the template below — skip any sections that don't apply

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

- Be specific over comprehensive. "Fixed the auth redirect in `+page.server.ts` line 42" beats "Made progress on auth."
- If a decision was contentious or non-obvious, explain the reasoning. The next agent will otherwise second-guess it.
- Keep Recent Changes to files actually touched this session, not a full project history.
- If the task is complete, say so and note any follow-up items or things to monitor.

## Output

Save as `HANDOFF.md` in the project root. Tell the user:
- The file path
- A one-line summary of where things stand
- That they can start a fresh session with: `claude "Read HANDOFF.md and continue where we left off"`
