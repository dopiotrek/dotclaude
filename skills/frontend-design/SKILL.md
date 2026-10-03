---
name: frontend-design
description: Opinionated constraints for building better interfaces with agents. Use when working on UI in src/**/*.svelte, src/lib/components/**, or src/routes/**/+page.svelte.
---

# UI Skills

When invoked, apply these opinionated constraints for building better interfaces.

## How to use

- `/frontend-design`  
  Apply these constraints to any UI work in this conversation.

- `/frontend-design <file>`  
  Review the file against all constraints below and output:
  - violations (quote the exact line/snippet)
  - why it matters (1 short sentence)
  - a concrete fix (code-level suggestion)

## Design Philosophy

### Technical Swiss

Rooted in Swiss Style's grid discipline, typographic hierarchy, and functional restraint — but inflected with the precision of professional instrumentation. The interface feels like well-designed equipment: dense but legible, technical but humane, precise but not cold.

The aesthetic connection to drones comes not from imagery, but from the values we share with aerospace: precision, reliability, efficiency, and professional-grade clarity.

### Core Principles

1. **Grid is law** — 4px base unit, everything aligns
2. **Typography does the work** — hierarchy through size/weight, not color
3. **One accent, used sparingly** — lime for primary actions only (never text)
4. **Monospace for data** — numbers, IDs, timestamps get Geist Mono
5. **Whitespace is intentional** — dense but never cramped
6. **No decoration** — every element is functional
7. **Contrast is non-negotiable** — accessibility over aesthetics

### Reference Touchstones

- Attio (direct inspiration)
- Linear (dense, clean, Swiss)
- Vercel dashboard (technical precision)
- Dieter Rams / Braun (industrial design principles)

### What We Don't Do

- No decorative elements that don't serve function
- No softness or playfulness — everything is purposeful
- No gradients, heavy shadows, or depth effects

## Stack

- Use Tailwind CSS defaults unless custom values already exist or are explicitly requested
- Prefer `tw-animate-css` for entrance and micro-animations in Tailwind CSS
- Use the `cn` utility (`clsx` + `tailwind-merge`) for class logic

## Components

- Use accessible component primitives for anything with keyboard or focus behavior (`shadcn-svelte`)
- Use the project’s existing component primitives first
- Don't mix primitive systems within the same interaction surface
- Add an `aria-label` to icon-only buttons
- Don't rebuild keyboard or focus behavior by hand unless explicitly requested

## Interaction

- Use an `AlertDialog` for destructive or irreversible actions
- Prefer structural skeletons for loading states
- Use `h-dvh`, not `h-screen`
- Respect `safe-area-inset` for fixed elements
- Show errors next to where the action happens
- Don't block paste in `input` or `textarea` elements

## Animation

- Don't add animation unless it is explicitly requested
- Animate only compositor props (`transform`, `opacity`)
- Don't animate layout properties (`width`, `height`, `top`, `left`, `margin`, `padding`)
- Avoid animating paint properties (`background`, `color`) except for small, local UI (text, icons)
- Prefer `ease-out` on entrance
- Keep interaction feedback at `200ms` or less
- Pause looping animations when off-screen
- Respect `prefers-reduced-motion`
- Don't introduce custom easing curves unless explicitly requested
- Avoid animating large images or full-screen surfaces

## Typography

- Use `text-balance` for headings and `text-pretty` for body/paragraphs
- Use `tabular-nums` for data
- Prefer `truncate` or `line-clamp` for dense UI
- Don't modify `letter-spacing` (`tracking-*`) unless explicitly requested

## Layout

- Use a fixed `z-index` scale (no arbitrary `z-*`)
- Prefer `size-*` for square elements instead of `w-*` + `h-*`

## Performance

- Don't animate large `blur()` or `backdrop-filter` surfaces
- Don't apply `will-change` outside an active animation
- Don't use `$effect` for anything `$derived` can express

## Design

- Don't use gradients unless explicitly requested
- Don't use purple or multicolor gradients
- Don't use glow effects as primary affordances
- Prefer the Tailwind CSS default shadow scale unless explicitly requested
- Give empty states one clear next action
- Limit accent color usage to one per view
- Prefer existing theme or Tailwind CSS color tokens before introducing new ones
