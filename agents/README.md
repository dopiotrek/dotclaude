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

#### `mobile-ui-designer.md`

**Model:** sonnet | **Color:** purple

Mobile-first UI specialist:

- Touch-friendly interfaces (44px+ touch targets)
- Mobile navigation patterns (drawers, bottom tabs)
- Responsive TailwindCSS layouts
- Visual feedback for touch interactions

**Triggers:** Mobile UI design, responsive layouts

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

#### `superforms-expert.md`

**Model:** sonnet | **Color:** cyan

Form handling specialist with sveltekit-superforms and Zod:

- Comprehensive Zod schema design
- Server-side form validation
- Multi-step forms with state management
- File uploads and nested data
- Real-time validation feedback

**Triggers:** Form creation, validation, complex form patterns

### Quality & Review

#### `code-reviewer.md`

**Model:** opus | **Color:** purple

Elite code review expert with 2025 methodologies:

- Security analysis (OWASP Top 10)
- Performance optimization
- Production reliability assessment
- Code quality and maintainability
- Detailed audit reports

**Triggers:** Code review, security audit, quality check

#### `debug-specialist.md`

**Model:** sonnet | **Color:** red

Systematic debugging expert:

- Runtime errors and exceptions
- Build and compilation errors
- Test failures
- Performance bottlenecks
- Memory leaks

**Triggers:** Errors, test failures, unexpected behavior

### Planning & Discovery

#### `discovery-agent.md`

**Model:** sonnet | **Color:** cyan

Feature discovery and requirements specialist:

- Six-phase discovery workflow
- Codebase analysis with repomix/Gemini
- Stakeholder interview facilitation
- Detailed specification creation
- Roadmap integration

**Triggers:** New features, requirements gathering, feature planning

#### `seo-expert.md`

**Model:** sonnet | **Color:** cyan

Content structure and SEO specialist:

- Header hierarchy analysis (H1-H6)
- Schema markup (JSON-LD)
- Internal linking optimization
- Featured snippet optimization

**Triggers:** SEO optimization, content structure

### DevOps

#### `vercel-deployment-expert.md`

**Model:** sonnet | **Color:** green

Vercel deployment specialist:

- Deployment configuration
- Environment variable management
- Build troubleshooting
- Domain configuration
- Performance optimization

**Triggers:** Vercel deployment, build failures, domain setup

## Agent Properties

| Property      | Description                                           |
| ------------- | ----------------------------------------------------- |
| `name`        | Unique identifier used to reference the agent         |
| `description` | When and how the agent should be used (with examples) |
| `model`       | Preferred model: `sonnet`, `opus`, or `haiku`         |
| `color`       | Terminal color for agent output                       |

## Creating Your Own Agent

### File Structure

Create a Markdown file in `agents/` with this structure:

```markdown
---
name: my-agent
description: Use this agent when... Examples: <example>user: "..." assistant: "I'll use my-agent..."</example>
model: sonnet
color: blue
---

You are an expert in [domain]. Your core responsibilities include...

## Expertise Areas

- Area 1
- Area 2

## Approach

When handling tasks, you will:

1. First...
2. Then...

## Code Patterns

\`\`\`typescript
// Example patterns you follow
\`\`\`

## Quality Standards

- Standard 1
- Standard 2
```

### Best Practices

1. **Clear Scope**: Define exactly what the agent handles
2. **Examples**: Include trigger examples in the description
3. **Structured Approach**: Outline step-by-step methodology
4. **Code Patterns**: Show preferred coding patterns
5. **Quality Checks**: Include verification steps

### Model Selection

- **opus**: Complex analysis, comprehensive reviews, critical decisions
- **sonnet**: Standard development tasks, good balance of speed/quality
- **haiku**: Simple, quick tasks with minimal complexity

## Agent Invocation

Agents are automatically invoked by Claude Code based on:

1. Task description matching the agent's expertise
2. Explicit user request ("use the debug agent")
3. Proactive detection of relevant scenarios

Example triggers:

```
"Create a form with validation" → superforms-expert
"Deploy to Vercel" → vercel-deployment-expert
"I'm getting a TypeError" → debug-specialist
"Review this code for security" → code-reviewer
```
