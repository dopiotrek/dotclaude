# Agents

Agents are specialized task handlers that Claude Code can spawn for complex, domain-specific work. Each agent has its own system prompt, model preference, and expertise area.

## How Agents Work

When Claude Code encounters a task matching an agent's expertise, it spawns a sub-agent with:

- The agent's specialized system prompt
- The specified model (sonnet, opus, etc.)
- Full access to relevant tools
- Context about the current task

Agents are defined as Markdown files with YAML frontmatter.

## Included Agents

### Frontend Development

#### `frontend-engineer.md`

**Model:** sonnet | **Color:** blue

Expert in Svelte 5 components with runes mode exclusively:

- `$state()`, `$derived()`, `$effect()`, `$props()`
- shadcn-svelte component integration
- Responsive design with TailwindCSS
- Accessibility (WCAG 2.1 AA)
- Performance optimization

**Triggers:** Component creation, responsive design, frontend issues

### Backend Development

#### `backend-engineer.md`

**Model:** sonnet | **Color:** orange

SvelteKit server-side expert:

- File-based routing (+page.server.ts, +server.ts)
- Load functions with streaming SSR
- Form actions with validation
- Hooks and middleware
- Authentication flows

**Triggers:** Server-side data fetching, form handling, API endpoints

### Quality & Review

#### `code-reviewer.md`

**Model:** opus | **Effort:** high | **Isolation:** worktree | **Color:** purple

Security and quality review, ordered by what actually matters:

- Security — injection, auth bypasses, RLS gaps, exposed secrets
- Data safety — error handling, race conditions, data loss
- Performance — N+1 queries, missing indexes, bundle size
- Code quality — duplication, complexity, naming
- Writes a dated report to `.docs/reviews/`

Reports everything it finds and ranks it, rather than pre-filtering to
high-severity only — see the note under [Writing an agent](#writing-an-agent).

**Triggers:** Code review, security audit, quality check

## Agent Properties

| Property      | Description                                                                     |
| ------------- | ------------------------------------------------------------------------------- |
| `name`        | Unique identifier used to reference the agent. May differ from the filename     |
| `description` | When and how the agent should be used (with examples)                           |
| `model`       | Preferred model: `sonnet`, `opus`, or `haiku`                                   |
| `effort`      | Reasoning effort: `low`, `medium`, `high`, `xhigh`. Omit to inherit the session |
| `tools`       | Comma-separated allowlist. **Omit and the agent gets everything**               |
| `isolation`   | `worktree` runs the agent in its own git worktree                               |
| `color`       | Terminal color for agent output                                                 |

`tools:` is an allowlist, not a hint — an MCP tool the prompt talks about but the
frontmatter doesn't list simply cannot be called. Keep the two in sync.

## Writing an agent

### File Structure

Create a Markdown file in `agents/` with this structure:

```markdown
---
name: my-agent
description: Use this agent when... Examples: <example>user: "..." assistant: "I'll use my-agent..."</example>
model: sonnet
tools: Read, Glob, Grep, Edit, Write, Bash
color: blue
---

You are an expert in [domain].

## What you know that the model doesn't

Project conventions, the gotcha that bit us last time, which library we picked
and why. Not general best practice.

## Definition of done

The one external check worth running, and what to report from it.

## Reporting back

Lead with the outcome. What I need to decide on, if anything.
```

### Writing for Claude 5-generation models

These models follow instructions literally and need less scaffolding than
earlier ones. What that changes:

1. **Encode what's specific to us.** A prompt that explains good engineering to
   a model that already knows it is wasted context. Write down the project
   conventions, the past incident, the non-obvious choice
2. **Cut generic methodology.** "First analyze, then investigate, then
   verify" is behavior these models already have. Numbered reasoning steps
   don't add rigor, they add tokens
3. **Don't add self-verification.** The model checks and corrects its own work
   unprompted. "Double-check your answer" and "verify before reporting"
   compound with that and cost tokens for nothing. Name the _external_ check
   instead — the type-checker, the failing test — because that's the signal the
   model can't produce by thinking harder
4. **Never cap what a review reports.** "Only flag high-severity issues", "be
   conservative", "keep it under 50 lines" get followed literally and real bugs
   go unreported. Ask for everything, ranked, and filter when you read it
5. **State the reporting shape.** These models narrate more by default. If you
   want terse, say so — and say what a good update looks like rather than
   listing what to avoid. Positive examples land better than prohibitions
6. **Scope the deliverable's length.** Agents that write files to disk will
   write long ones unless told to match length to substance
7. **Keep `tools:` honest.** Scope it to what the agent needs, and make sure
   every tool the prompt mentions is actually in the list

### Model and effort selection

- **opus**: Complex analysis, comprehensive reviews, critical decisions
- **sonnet**: Standard development tasks, good balance of speed/quality
- **haiku**: Simple, quick tasks with minimal complexity

`effort` is the cheaper lever. On Claude 5-generation models `low` and `medium`
hold up well for a fraction of the tokens and latency, so treat them as the
default control for cost and reserve `high` / `xhigh` for demanding coding and
review work. Effort settings carried over from an older model are worth
re-checking against your own results rather than trusting.

## Agent Invocation

Agents are automatically invoked by Claude Code based on:

1. Task description matching the agent's expertise
2. Explicit user request ("use the code-reviewer agent")
3. Proactive detection of relevant scenarios

Example triggers:

```
"Build a profile card component" → frontend-engineer
"Add a form action for this endpoint" → backend-engineer
"Review this code for security" → code-reviewer
```
