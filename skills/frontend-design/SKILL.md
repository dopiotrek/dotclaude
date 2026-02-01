---
name: ui-skills
description: Opinionated constraints for building better interfaces with agents.
---

# UI Skills

When invoked, apply these opinionated constraints for building better interfaces.

## How to use

- `/ui-skills`  
  Apply these constraints to any UI work in this conversation.

- `/ui-skills <file>`  
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

- MUST use Tailwind CSS defaults unless custom values already exist or are explicitly requested
- SHOULD use `tw-animate-css` for entrance and micro-animations in Tailwind CSS
- MUST use `cn` utility (`clsx` + `tailwind-merge`) for class logic

## Components

- MUST use accessible component primitives for anything with keyboard or focus behavior (`shadcn-svelte`)
- MUST use the project’s existing component primitives first
- NEVER mix primitive systems within the same interaction surface
- MUST add an `aria-label` to icon-only buttons
- NEVER rebuild keyboard or focus behavior by hand unless explicitly requested

## Interaction

- MUST use an `AlertDialog` for destructive or irreversible actions
- SHOULD use structural skeletons for loading states
- NEVER use `h-screen`, use `h-dvh`
- MUST respect `safe-area-inset` for fixed elements
- MUST show errors next to where the action happens
- NEVER block paste in `input` or `textarea` elements

## Animation

- NEVER add animation unless it is explicitly requested
- MUST animate only compositor props (`transform`, `opacity`)
- NEVER animate layout properties (`width`, `height`, `top`, `left`, `margin`, `padding`)
- SHOULD avoid animating paint properties (`background`, `color`) except for small, local UI (text, icons)
- SHOULD use `ease-out` on entrance
- NEVER exceed `200ms` for interaction feedback
- MUST pause looping animations when off-screen
- SHOULD respect `prefers-reduced-motion`
- NEVER introduce custom easing curves unless explicitly requested
- SHOULD avoid animating large images or full-screen surfaces

## Typography

- MUST use `text-balance` for headings and `text-pretty` for body/paragraphs
- MUST use `tabular-nums` for data
- SHOULD use `truncate` or `line-clamp` for dense UI
- NEVER modify `letter-spacing` (`tracking-*`) unless explicitly requested

## Layout

- MUST use a fixed `z-index` scale (no arbitrary `z-*`)
- SHOULD use `size-*` for square elements instead of `w-*` + `h-*`

## Performance

- NEVER animate large `blur()` or `backdrop-filter` surfaces
- NEVER apply `will-change` outside an active animation
- NEVER use `useEffect` for anything that can be expressed as render logic

## Design

- NEVER use gradients unless explicitly requested
- NEVER use purple or multicolor gradients
- NEVER use glow effects as primary affordances
- SHOULD use Tailwind CSS default shadow scale unless explicitly requested
- MUST give empty states one clear next action
- SHOULD limit accent color usage to one per view
- SHOULD use existing theme or Tailwind CSS color tokens before introducing new ones
