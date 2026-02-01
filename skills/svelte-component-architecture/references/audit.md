# Component Architecture Audit

Systematic checklist for reviewing and improving component structure.

## Quick Health Check

Run through these for a rapid assessment:

| Check | Command/Action | Red Flag |
|-------|---------------|----------|
| Depth | Count levels from page to leaf | >4 custom component levels |
| Size | Check file line counts | Any component >300 lines |
| Names | Read component names only | Can't guess purpose from name |
| Props | Trace a prop through tree | Same prop passes through 3+ files |
| Reuse | Search for component imports | Component imported exactly once |

## Detailed Audit Process

### Step 1: Map the Component Tree

For each major page/route:

1. Open `+page.svelte`
2. List direct component imports
3. For each component, list its imports
4. Continue until reaching leaf components
5. Draw or note the hierarchy

```
Example output:
+page.svelte
├── DashboardHeader (ui)
├── ProposalSection (feature)
│   ├── ProposalList (feature)
│   │   ├── ProposalCard (ui)
│   │   │   ├── StatusBadge (ui)        ← 4 levels, acceptable
│   │   │   └── PriceDisplay (ui)
│   │   └── EmptyState (ui)
│   └── ProposalFilters (ui)
└── DroneGrid (feature)
    └── DroneCard (ui)
```

### Step 2: Identify Issues

**Depth violations**
- Mark any branch exceeding 4 levels
- Question: Is each level adding value or just organizing?

**Wrapper detection**
- Find components under 50 lines
- Check: Do they add logic, or just wrap markup?
- If only wrapping: candidate for removal

**Prop drilling**
- Pick 3-5 important props (user, config, theme)
- Trace each from source to usage
- Count intermediate components that just pass through

**State confusion**
- Find components with local state
- Check: Is same state managed in parent too?
- Look for `bind:` chains through multiple levels

**Naming audit**
- List all component names
- Can you categorize each as Feature or UI from name alone?
- Flag generic names: `Container`, `Wrapper`, `Layout`, `Component`

### Step 3: Categorize Findings

Sort issues by type:

| Category | Issue | Severity | Fix |
|----------|-------|----------|-----|
| **Structure** | Too deep | Medium | Flatten or merge |
| **Structure** | Wrappers | Low | Inline |
| **Data** | Prop drilling | High | Context or restructure |
| **Data** | State duplication | High | Single source of truth |
| **Naming** | Generic names | Low | Rename for clarity |
| **Size** | God component | High | Split by concern |

### Step 4: Prioritize Fixes

**Fix first (high impact, usually quick):**
1. State duplication — causes bugs
2. God components — blocks all other work
3. Prop drilling — makes changes painful

**Fix second (medium impact):**
4. Deep nesting — cognitive overhead
5. Generic names — discoverability

**Fix last (low impact):**
6. Unnecessary wrappers — minor cleanup

## Audit Questions by Component Type

### For Pages (+page.svelte)

- [ ] Does it primarily import and compose, or contain lots of logic?
- [ ] Is inline markup under 50 lines?
- [ ] Are feature components clearly named?
- [ ] Could someone understand the page structure from imports alone?

### For Feature Components

- [ ] Is it self-contained? (Could move to another project?)
- [ ] Does it own its state, or receive too much from parent?
- [ ] Is the prop interface small? (<7 props is healthy)
- [ ] Are internal UI pieces reusable or specific?

### For UI Components

- [ ] Is it pure? (No API calls, no business logic)
- [ ] Is it controlled? (All state via props)
- [ ] Does it handle one concern? (Display OR interaction, not both)
- [ ] Would it work in a different feature context?

## Refactoring Recipes

### Recipe: Flatten Deep Nesting

Before:
```
Page → Container → Layout → Section → Card → Content
```

After:
```
Page → FeatureSection → Card
```

Steps:
1. Identify the "meaningful" components (Card, FeatureSection)
2. Inline the structural wrappers (Container, Layout, Section)
3. Move layout CSS to parent or use Tailwind directly

### Recipe: Fix Prop Drilling

Before:
```
Page (user) → Dashboard (user) → Sidebar (user) → Menu (user)
```

Options:
1. **Context** — if truly global (user, theme, config)
2. **Restructure** — move Menu to be direct child of component that has user
3. **Feature component** — let Menu fetch user itself

### Recipe: Split God Component

Before: `Dashboard.svelte` (600 lines, handles stats, charts, filters, modals)

After:
```
Dashboard.svelte (80 lines, orchestrates)
├── DashboardStats.svelte (100 lines, feature)
├── DashboardCharts.svelte (150 lines, feature)
├── DashboardFilters.svelte (80 lines, feature)
└── DashboardModal.svelte (120 lines, feature)
```

Steps:
1. List all concerns in the file
2. Group related state and markup
3. Extract each group as feature component
4. Wire together in original file

### Recipe: Remove Wrapper

Before:
```svelte
<!-- CardContainer.svelte -->
<div class="p-4 border rounded">
  {@render children()}
</div>
```

After:
```svelte
<!-- Inline in parent -->
<div class="p-4 border rounded">
  <ActualContent />
</div>
```

Or create a real Card component with semantic value if reused.

## Audit Report Template

```markdown
# Component Audit: [Feature/Page Name]

## Summary
- Total components: X
- Max depth: X levels
- Issues found: X

## Tree Structure
[paste hierarchy]

## Issues

### Critical
- [ ] Issue description → Recommended fix

### Medium  
- [ ] Issue description → Recommended fix

### Low
- [ ] Issue description → Recommended fix

## Recommended Order
1. Fix X first because...
2. Then fix Y...
3. Finally clean up Z...
```