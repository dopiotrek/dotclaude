---
name: svelte-architect
description: Component decomposition and architecture guidelines for SvelteKit/Svelte 5 apps. Use when creating new components, deciding how to split code, reviewing component structure, refactoring nested components, or when unsure whether to extract a component. Triggers on phrases like "where should this go", "too many components", "too nested", "extract component", "component structure", "file organization", "props drilling", "refactor components", "review architecture", or questions about component boundaries.
---

# Svelte Component Architecture

Guidelines for decomposing SvelteKit applications into maintainable component hierarchies.

## Core Model: Three-Tier Hierarchy

```
+page.svelte       → Orchestrator (data wiring, layout, minimal UI)
  └─ Feature       → Self-contained capability (owns its logic + state)
       └─ UI       → Pure presentation (props in, events out)
```

**Target: Maximum 3 levels of custom components.** Not a hard rule, but exceeding 4-5 levels signals structural problems.

## Component Categories

| Type | Responsibility | Owns State? | Location |
|------|----------------|-------------|----------|
| **Page** | Data orchestration, layout composition | Receives from `load` | `routes/**/+page.svelte` |
| **Feature** | Encapsulates complete capability | Yes, local state | `lib/components/features/` |
| **UI** | Pure presentation, fully controlled | No | `lib/components/ui/` |

**Feature components are the main abstraction boundary.** They should be understandable in isolation.

## When to Extract a Component

Extract when ANY of these apply:

1. **Reuse** — needed in 2+ places
2. **Complexity** — file exceeds ~250 lines with clear seams
3. **Testing** — want to test a piece in isolation
4. **Cognitive chunking** — a name would clarify intent
5. **State isolation** — local state that shouldn't leak upward

## When NOT to Extract

Avoid creating components that:

- Exist purely for "organization" without adding logic
- Pass props straight through without transformation
- Are used exactly once and are under ~50 lines
- Replace simple markup that's clearer inline

**A `<div class="grid grid-cols-2">` in the parent is clearer than a `<TwoColumnLayout>` wrapper.**

## Decision Tree

```
Is this reused elsewhere?
  └─ Yes → Extract
  └─ No → Is it complex (>250 lines or multiple concerns)?
            └─ Yes → Extract as Feature
            └─ No → Does it have independent state?
                      └─ Yes → Consider extracting
                      └─ No → Keep inline
```

## File Structure

```
src/lib/components/
├── ui/                    # Design system primitives
│   ├── Button.svelte
│   ├── Input.svelte
│   ├── Card.svelte
│   └── Badge.svelte
├── features/              # Self-contained feature blocks
│   ├── auth/
│   │   ├── LoginForm.svelte
│   │   └── UserMenu.svelte
│   └── dashboard/
│       ├── StatsCard.svelte
│       └── ActivityFeed.svelte
└── layout/                # App-wide layout components (optional)
    ├── Navbar.svelte
    └── Footer.svelte
```

## Naming Conventions

- **PascalCase** for all component files: `ProposalBuilder.svelte`
- **Feature-based names** over generic: `DroneSpecsTable` not `DataTable`
- **Suffix patterns** (optional): `*Form`, `*Card`, `*List`, `*Modal`
- **Folder = feature domain**: `features/billing/`, `features/onboarding/`

## Props & State Guidelines

- **UI components**: All data via props, all interactions via events
- **Feature components**: May fetch/manage own data, expose minimal API
- **Prop drilling limit**: If passing through 3+ levels, consider context or restructuring

```svelte
<!-- Feature: owns its logic -->
<script>
  let { projectId } = $props();
  let data = $state(null);
  // fetches and manages its own state
</script>

<!-- UI: pure presentation -->
<script>
  let { label, variant = 'primary', onclick } = $props();
</script>
```

## Anti-Patterns to Avoid

| Pattern | Problem | Fix |
|---------|---------|-----|
| **Wrapper-only components** | Adds indirection without value | Inline the markup |
| **Prop tunneling** | Passing same prop through 4+ levels | Use context or flatten |
| **God components** | 500+ lines, multiple responsibilities | Split by concern |
| **Premature extraction** | Single-use 30-line component | Keep inline until reused |
| **Layout-as-component** | `<TwoColumn>` for one-time use | Use CSS classes directly |
| **Nested state sync** | Child and parent both manage same state | Single source of truth |

## Audit Workflow

When reviewing existing component structure:

1. **Map the tree** — sketch component hierarchy for a complex page
2. **Count depth** — flag anything beyond 4 levels
3. **Check names** — can you understand purpose without opening the file?
4. **Find tunneling** — trace props through the tree, flag 3+ hops
5. **Spot wrappers** — components under 50 lines used once
6. **Review features** — are they self-contained or leaking concerns?

See [references/audit.md](references/audit.md) for detailed checklist.

## Refactoring Strategies

**Flattening deep nesting:**
- Merge parent-child when child is trivial
- Promote deeply nested component to feature level
- Replace intermediate wrappers with slots

**Splitting god components:**
- Identify distinct concerns (data, display, interaction)
- Extract each concern as feature or UI component
- Page becomes thin orchestrator

**Fixing prop drilling:**
- Use Svelte context for truly global data (theme, user, config)
- Restructure so data owner is closer to consumers
- Consider feature components that fetch their own data

## References

- **Code Examples**: See [references/patterns.md](references/patterns.md) for good/bad examples
- **Audit Checklist**: See [references/audit.md](references/audit.md) for systematic review