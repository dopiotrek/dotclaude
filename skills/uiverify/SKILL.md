---
name: uiverify
description: Verify a pixel-level UI change in the live browser with computed-style measurements instead of screenshot judgment. Use when matching a design reference, checking alignment/spacing/borders, or before declaring any visual UI change "done".
paths:
  - "**/*.svelte"
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.css"
---

# UI Verify

Screenshots catch gross layout breaks but miss the details that actually get flagged in review: a 1px underline offset, a dropped `border-bottom`, a 6px vertical shift between two tabs that should align. Don't eyeball a screenshot and call it matched — measure it.

## Steps

1. Confirm the dev server is running and fresh (not stale/crashed) before verifying anything. If unsure, restart it.
2. Navigate to the affected route(s) with `agent-browser` (see the Browser Automation section of `~/.claude/CLAUDE.md`).
3. Take a before/after screenshot for a sanity check — but treat it as a first pass, not the verdict.
4. Evaluate JavaScript in the page to read `getBoundingClientRect()` and `getComputedStyle()` for the changed element, and for the reference element if matching one. Pull at least: `x`, `y`, `width`, `height`, `padding`, `border`, `font-size`, `font-weight`, `color`.
5. Explicitly check the things that tend to go unnoticed in a screenshot:
   - Borders, especially `border-bottom` on toolbars/tabs
   - Vertical alignment between sibling tabs/panels
   - Left gutter / padding consistency with adjacent elements
   - Underline or divider extent (does it span the full element or fall short?)
6. Report a diff table: expected vs. actual for each measured property. Only report the change as matching when every value lines up — not "looks close."

## When there's no reference element

If there's no existing element to diff against (a genuinely new design), state the target values explicitly before measuring (e.g. "border-bottom: 1px solid var(--border-subtle)") and confirm the computed style matches those values, not just that something visually resembling a border is present.
