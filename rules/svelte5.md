---
paths:
  - "**/*.svelte"
  - "**/*.svelte.ts"
  - "**/*.svelte.js"
---

# Svelte 5 + UI

Loads when working in Svelte files. The runes-only rule also lives in `CLAUDE.md` (always-on) so it still applies when creating a brand-new component from scratch.

- Svelte 5 runes only: `$state`, `$derived`, `$effect`, `$props`. Never Svelte 4 patterns — no `writable` / `derived` stores, no `$:` reactive statements, no `export let`.
- Prefer `$derived` for computed values; use `$effect` only for genuine side effects (DOM, subscriptions, logging), not for deriving state.
- Use `$app/state` (not the deprecated `$app/stores`).
- Mobile-first: build the small-screen layout first, then scale up.
