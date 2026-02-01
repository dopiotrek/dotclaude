# Skills

Skills are reusable task definitions that provide Claude Code with domain-specific knowledge, workflows, and reference materials. Unlike agents (which spawn sub-processes), skills inject their content directly into the conversation context.

## How Skills Work

Skills are invoked via slash commands (e.g., `/clean-comments`) and provide:

- Task-specific instructions and workflows
- Reference documentation
- Code examples and patterns
- Optional automation scripts

## Included Skills

### clean-comments

**Command:** `/clean-comments`

Removes unnecessary, redundant, or obvious code comments while preserving valuable explanations.

**When to use:**

- Cleaning up verbose documentation
- Removing obvious comments (e.g., `// increment counter`)
- Preparing code for review
- Simplifying inline comments

**Principles:**

- Remove comments that merely restate what code does
- Keep complexity explanations at decision points
- Preserve comments that explain "why" not "what"
- Trust readable code to communicate intent

### code-reviewer

**Command:** `/code-reviewer`

Comprehensive code review toolkit with automated analysis and checklists.

**Structure:**

```
code-reviewer/
├── SKILL.md                    # Main skill definition
├── references/
│   ├── code_review_checklist.md   # Review checklist
│   ├── coding_standards.md        # Standards reference
│   └── common_antipatterns.md     # Anti-patterns to avoid
└── scripts/
    ├── pr_analyzer.py             # PR analysis tool
    ├── code_quality_checker.py    # Quality metrics
    └── review_report_generator.py # Report generation
```

**Capabilities:**

- PR analysis and diff review
- Quality metrics checking
- Report generation
- Standards compliance

### frontend-design

**Command:** `/frontend-design`

Opinionated UI constraints for building consistent interfaces.

**Design Philosophy: "Technical Swiss"**

- Grid is law (4px base unit)
- Typography does the work
- One accent color, used sparingly
- Monospace for data
- No decoration

**Constraints include:**

- Component primitives (shadcn-svelte)
- Animation rules (compositor props only)
- Typography (`text-balance`, `tabular-nums`)
- Layout (fixed z-index scale)
- Performance (no large blur effects)

### svelte-component-architecture

**Command:** `/svelte-architect`

Component decomposition guidelines for SvelteKit/Svelte 5 applications.

**Core Model: Three-Tier Hierarchy**

```
+page.svelte       → Orchestrator (data wiring, layout)
  └─ Feature       → Self-contained capability (owns logic)
       └─ UI       → Pure presentation (props in, events out)
```

**Includes:**

- Extraction decision tree
- File structure recommendations
- Naming conventions
- Anti-patterns to avoid
- Audit workflow checklist

**References:**

- `references/patterns.md` - Good/bad code examples
- `references/audit.md` - Component structure audit checklist

## Skill Structure

A skill consists of:

```
skill-name/
├── SKILL.md           # Required: Main skill definition
├── references/        # Optional: Supporting documentation
│   ├── guide.md
│   └── patterns.md
└── scripts/           # Optional: Automation scripts
    └── tool.py
```

### SKILL.md Format

```markdown
---
name: skill-name
description: When and why to use this skill. Trigger phrases.
---

# Skill Title

Main content with:

- Instructions
- Workflows
- Code examples
- Best practices
```

### Frontmatter Properties

| Property      | Required | Description                               |
| ------------- | -------- | ----------------------------------------- |
| `name`        | Yes      | Unique identifier (used in slash command) |
| `description` | Yes      | When to use, trigger phrases              |

## Creating Your Own Skill

### 1. Create the directory structure

```bash
mkdir -p skills/my-skill/references
```

### 2. Create SKILL.md

```markdown
---
name: my-skill
description: Use when [scenario]. Triggers on [phrases].
---

# My Skill

## Overview

What this skill does and when to use it.

## Workflow

1. Step one
2. Step two
3. Step three

## Examples

### Good Example

\`\`\`typescript
// Code showing correct approach
\`\`\`

### Bad Example

\`\`\`typescript
// Code showing what to avoid
\`\`\`

## References

See [references/guide.md](references/guide.md) for detailed patterns.
```

### 3. Add reference materials (optional)

Create files in `references/` for:

- Detailed documentation
- Code pattern libraries
- Checklists
- External resource links

### 4. Add automation scripts (optional)

Create Python scripts in `scripts/` for:

- Automated analysis
- Report generation
- Code transformations

## Best Practices

1. **Clear Triggers**: Define specific phrases that invoke the skill
2. **Focused Scope**: Keep skills single-purpose
3. **Actionable Content**: Provide specific, implementable guidance
4. **Examples**: Include both good and bad code examples
5. **References**: Link to external documentation when helpful

## Using Skills

Skills are invoked via slash commands in Claude Code:

```
/clean-comments
/code-reviewer
/frontend-design
/svelte-architect
```

Some skills can accept arguments:

```
/code-reviewer path/to/file.ts
```
