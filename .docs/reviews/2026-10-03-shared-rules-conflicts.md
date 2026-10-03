# Shared rules — conflicts to decide (2026-10-03)

## Resolved 2026-10-03 (Piotrek)

- **Design system is repo-owned.** Icon set, icon sizing, button API and
  default variant, colour aliases, grey ramp, elevation, radius, durations,
  easing, when to animate: each product keeps its own. The shared rules stay
  neutral; the rows below on these topics are closed.
- **Forms: the repo decides.** Each repo's `forms.md` names its library. A new
  repo starts with plain `formData` + Zod. Closed: library, error return,
  showing the result, field components, pending state, Zod adapters.
- **Action order: permission first, everywhere.** Now in the shared
  `forms.md`; the swissCRM and compass examples were changed.
- **Icon imports: deep imports everywhere.** The shared rule stands; the
  compass and tma rule copies now say so too. Code moves when touched.

Still open: nothing that needs a decision. Leftovers to fix when touched:
`duration-slow-1100` = 1000ms in compass and tma; compass ux-* text copied
from swissCRM (aviation).

The shared core in `rules/` holds only what frontq, dronelist and swissCRM agree on. Every disagreement below was left OUT of the shared rule. Decide each one; then the winning position goes into the shared rule or stays as a repo delta. The "stays in repo" lists say what each repo copy keeps after the old copies are trimmed.

---

# Topic: svelte5

## svelte5.md — conflicts and leftovers

Sources: frontq `svelte.md`, dronelist / swissCRM / compass / tma `svelte-patterns.md`, dotclaude `svelte5.md`.

## Conflicts

"—" means the copy does not speak. "In rule?" says what the shared file does.

| Rule | frontq | dronelist | swissCRM | compass / tma | In rule? |
| --- | --- | --- | --- | --- | --- |
| Icon library | Tabler | Tabler, "not lucide" | Phosphor only | Tabler (compass: Lucide only inside `packages/ui`) | No — repo |
| Icon import style | one deep import per icon, never barrel | — (example only) | one deep import per icon, never barrel (lint-enforced) | barrel import `{ IconTrash } from '@tabler/icons-svelte'` | Yes — in-scope agree; compass/tma differ |
| Icon size / stroke | never pass `size`/`stroke`; tokens set it; override with `size-*` class | `class="size-4"` on each icon | never pass `weight`; set once by root `IconContext` | tma: `class="size-4"` per icon | No |
| Icon-only button API | `shape="square"`/`"circle"`; there is no `size="icon"` | `size="icon-sm"` | `size="icon"` | `size="icon"` | No — repo |
| Button default variant | `secondary` is default; `primary` once per view | default = primary; `variant="outline"` for secondary | default = primary; `outline` for secondary | same as swissCRM | No — repo |
| Single-component import path | from `$ui` barrel | `$lib/components/ui/<name>/index.js` | `$ui/components/ui/<name>` (no barrel) | compass `$ui/...`; tma `$lib/components/ui/...` | No (namespace-for-compound kept, paths dropped) |
| Resync after `use:enhance` | — (uses its `reported()` helper) | — | mandatory re-copy from `data`, or rely on invalidation | mandatory (tma: re-copy only) | Yes — generic form; others silent |
| `state_referenced_locally` suppression | — | only for editable form `$state` | — (snapshot pattern without the warning rule) | — | Yes |
| Motion | `svelte/transition` / `svelte/motion` unused on purpose; CSS only | — | — (own `motion.md`) | — (own `motion.md`) | No — repo `motion.md` |
| Variant helper | `tailwind-variants` (`tv()`), no `cva` | — | — | — | No — repo dependency |
| Readability over cleverness / pure `$lib/utils` | — | — | yes | yes | No — dropped as generic advice |
| `$app/state` vs `$app/stores` | `$app/state` (via dotclaude) | — | — | — | Yes — no copy disagrees |

## Stays in the repo file

Once the shared core lands, each repo keeps only these sections.

**frontq `svelte.md`**
- Props: the `packages/ui` library shape (`WithElementRef`, bindable `ref`, `class`, rest props).
- Importing from `$ui`: barrel vs sub-path, the list of non-barrel components.
- Controls: `secondary` default, `shape` + size tiers from `$ui/config/sizes.ts`, card actions in the header as links, `PanelSection` in the side panel, "a button never creates a record" + `ActionDialog`, `LayerDialog`, `tv()` not `cva`.
- Icons: `@tabler/icons-svelte/icons/<name>`, `--icon-size` / `--icon-stroke` tokens, `IconComponent` type.
- Snippets and motion: no `svelte/transition`, see `motion.md`.
- Smaller things: pointer to `apps/admin/src/lib/shell/session.svelte.ts` as the pattern.
- Incident names only (the general rule is shared): `Field` `registerLabel`, `setPageActions`, the supplier-portal `notes` case, the questionnaire builder `reported({ payload })` fix.
- Remove: runes, Props shape, `svelte/reactivity`, `{@const}`, `onSelectedChange`, kebab-case, and the general text of the three gotchas.

**dronelist `svelte-patterns.md`**
- Select / Button examples with `$lib/components/ui/...` paths and `size="icon-sm"`.
- Icons: `@tabler/icons-svelte`, not `lucide-svelte`.
- Superforms detail of the effect-loop example (`$form.pricing.*`), if kept as a local example.
- Fix the frontmatter: `paths: **/*.svelte, **/*.svelte.ts` is not a YAML list.
- Remove: Props, derived examples, `state_referenced_locally`, `{@const}`, `onSelectedChange`, `import * as`, effect-loop rule, plain `use:enhance` example.

**swissCRM `svelte-patterns.md`**
- UI component imports from `$ui/components/ui/...`, `Chip` and its `onToggle`.
- Button patterns with `size="icon"`.
- Icons: Phosphor only, `phosphor-svelte/lib/<Name>`, `swisscrm/no-legacy-icon-import`, no `weight`, root `IconContext`, `$ui/icons` limited to status and Excel marks.
- `persistedCookieState()` / `persistedState()` helper names from `$lib/state/table-prefs.svelte`.
- Resync note naming the `accounts` / `contacts` list pages.
- Optional: "Readability over cleverness" and pure `$lib/utils` (dropped from shared as generic).
- Remove: Props, state/derived, snapshot, generic resync rule, Select, `{@const}`, kebab-case, `$:`/stores.

**compass / tma (reference only)** — same split as swissCRM; their icon rules (Tabler barrel, `apps/studio`, design-system inline SVGs) stay local.

---

# Topic: forms

## forms.md — conflicts and leftovers

Sources: frontq, swissCRM, compass `forms.md`. dronelist has no `forms.md`; its `svelte-patterns.md` shows a plain `use:enhance` form and an effect over "Superforms state".

## Conflicts

| Rule | frontq | dronelist | swissCRM | compass / tma | In rule? |
| --- | --- | --- | --- | --- | --- |
| Form library | plain `formData` + Zod + `fail()`; superforms installed but "not adopted" | uses Superforms (`$form` in an effect) and plain `use:enhance` | superforms + formsnap default for multi-field forms; `formData` + Zod for one-shot posts | compass: superforms always, "never raw forms"; tma: — | No — repo `forms.md` decides |
| Action error return | `fail(400, { message })`, one sentence | — | `message(form, …)`; "never raw `fail` with a plain string" | compass: same as swissCRM | No |
| Showing the result | toast via `reported()`; page never renders `form.message`; banner only for lasting state | — | renders `$message` inline under the form | compass: inline `$message` | No |
| Field components | `Field` / `FieldLabel` / `Input` from `$ui` | — | formsnap `Form.Field` / `Form.Control` / `Form.FieldErrors` for every field | compass: formsnap | No |
| Order inside an action | permission → parse → tenant → write | — | parse (`superValidate`) → `requireAuth` → write | compass: same as swissCRM | No |
| Zod version / adapters | not stated | — | Zod 4; `zod4 as zod` server, `zod4Client` client | compass: same | No — repo |
| Pending state | `reported()` holds a pending flag | — | `$submitting` disables submit | compass: same | No — mechanism differs |
| Partial updates: `formData.has` | yes | — | yes (and why `superValidate` breaks it) | — | Yes |
| `reset: false` | when fields mirror server state | — | when you want to keep form state | compass: same | Yes |
| Comment when breaking the pattern | comment why if you use superforms | — | comment why if you skip superforms | — | Yes (both directions) |
| Zod message = user sentence | yes | — | — | — | Yes |
| Glob | `apps/*/src/routes/**/+page.server.ts` | — | `**/*.svelte` + `apps/web/.../*.server.ts` | `**/*.svelte` + `apps/studio/...` | Shared uses generic globs |

## Stays in the repo file

**frontq `forms.md`**
- Intro line: plain `formData` + Zod, no superforms.
- The full action example and the order permission → parse → tenant → write (`can`, `currentTenantId`, `asTenant`, `auditContext`).
- Mutation and audit row in one `asTenant` transaction.
- `codeSchema` / `escalation_rule.owner_group_code` example.
- Client: `reported()` from `$lib/forms/reported`, its options (`quiet`), `Field` from `$ui`.
- Banner vs toast; never render `form.message`.
- "Superforms" section (available in `@frontq/ui`, not adopted).
- Remove: Zod-message rule, `formData.has`, generic module-scope schema rule, `reset: false`.

**dronelist** — nothing to keep (no `forms.md`). It should add a short `forms.md` that states its form library, since it is the one in-scope repo that does not say.

**swissCRM `forms.md`**
- Stack line (superforms + formsnap + Zod 4) and adapter naming (`zod4 as zod`, `zod4Client`).
- Load and action examples, `message(form, …)` rule, `DomainError` → 422, `requireAuth`.
- Client example and formsnap `Form.*` usage from `$ui/components/ui/form`.
- Rules: `$submitting`, `fieldProxy` / `arrayProxy`, adapter per side.
- "When NOT to use superforms" — keep the scoring-popover case and the pointers to `tenders/[id]/bidders/compare` and `updateMemberRole`; the one-shot and partial-update reasons are now shared.
- Narrow the glob: `**/*.svelte` loads forms rules on every component.

**compass (reference only)** — keep as is; it predates the "when not to use superforms" exceptions that swissCRM added.

---

# Topic: tailwind

## tailwind — conflicts and leftovers

Sources: frontq `tailwind.md` (Sep 2026), dronelist `tailwind-patterns.md`
(Oct 3), swissCRM `tailwind-patterns.md` (Oct 3), compass (Oct 3, near-copy of
swissCRM), tma (Jun 2026). "—" = silent.

## Conflicts (left out of the shared rule)

| Rule | frontq | dronelist | swissCRM | compass / tma |
| --- | --- | --- | --- | --- |
| shadcn colour aliases (`bg-muted`, `bg-primary`, `text-muted-foreground`, `border-border`) | Deleted; all 26 had zero consumers. Rewrite shadcn output to role names | Uses `bg-muted` as the preferred example | Preferred over raw tokens | Both use them |
| Grey ramp `system-gray-*` | Dead pre-Kumo leftover; no `gray` role | — | Live; Apollo sand values (`#f4f4f2` / `#535347`) | compass: live, Apple values (`#F2F2F7` / `#8E8E93`); tma: live, `ring-system-gray-5` for card depth |
| Elevation utilities | `shadow-elevate-*`, `material-menu`, `material-modal` are dead leftovers; edges are rings | `material-*` only; never `shadow-*` | `shadow-elevate-1..3` + `material-menu` / `material-modal` | compass adds `material-small`; tma also `shadow-button` |
| Edges: ring or border | `ring ring-line border-0` everywhere; border only for dashed badge and table rules | — | Uses `border-border` as the semantic border | — |
| Radius | — | Custom numeric scale (`rounded-6`, `rounded-4`); t-shirt names are wrong | — | tma: `rounded-lg` before `rounded-[10px]` |
| Animation inside the Tailwind rule | Lives in `motion.md` | Full section here (see motion conflicts) | Short section, defers to `motion.md` | Same as swissCRM |
| `!important` exceptions | Two (third-party DOM, reduced-motion backstop) | — | Same two | tma: only one (third-party DOM) |

## Dropped as generic (model already knows)

Accessibility (`aria-label` on icon buttons, visible focus), blur /
`backdrop-filter` / `will-change` performance notes, `truncate` /
`line-clamp`, "don't override defaults you can avoid" (swissCRM).

## Stays in repo

**frontq**
- Token files `packages/ui/src/styles/{tokens,theme,base,animations}.css`; no `tailwind.config`
- Design language source (`.docs/decisions/design-language.md`), `kumo-design` skill, `design-tokens.md`
- Computed ink ramp (`--ink-*`, `--brand*`, `--ink-link`), `--accent` / `--pole` / `--dir` / `--contrast-scale`; `--contrast` is the inverted surface
- `sonner.svelte` / `button.svelte` raw-token and template-literal notes; `sizes.ts`
- Banned leftovers list (`shadow-elevate-*`, `system-gray-*`, `material-*`, shadcn aliases); role names `fill` / `hover` / `sunken` / `hairline`, `subtle` / `placeholder` / `faint`
- `pnpm check:classes` guard (four dead classes had shipped)
- `ring ring-line border-0` and its two border exceptions
- Shell measure (`max-w-content`, `px-page`, `shell-layout.ts`, `mainClass()` / `columnClass()`)
- `Page.Root` / `Header` / `Body` / `Footer`, `bounded`, `shell: { height: "viewport" }`
- `h-table-cell`

**dronelist**
- `cn()` import path `$lib/utils`
- `design-system` skill refs (`references/typography.md`, `references/design-tokens.md`), `ui-components.md` §1
- `material-*` elevation, numeric radius scale (`rounded-6`, `rounded-4`)
- `.pcss` glob (kept in shared rule, harmless elsewhere)

**swissCRM**
- `system-gray` ramp values, `shadow-elevate-1..3`, `material-menu` / `material-modal` contents
- Semantic token preference (`bg-muted`, `text-muted-foreground`, `border-border`, `bg-system-blue`)
- `design.md` application matrix
- `svelte-sonner` / `svelte-dnd-action` override examples

**compass / tma** (reference only): `material-small`, `shadow-button`, `src/routes/layout.css` as the `@theme inline` home, Apple grey values.

---

# Topic: motion

## motion — conflicts and leftovers

Sources: frontq `motion.md` (Sep 2026), swissCRM `motion.md` (Oct 3), compass
(Oct 3, near-copy of swissCRM), tma (Jun 2026). dronelist has no `motion.md`;
its position comes from the Animation section of `tailwind-patterns.md`.
"—" = silent.

## Conflicts (left out of the shared rule)

| Rule | frontq | dronelist | swissCRM | compass / tma |
| --- | --- | --- | --- | --- |
| What unlocks animation | When it guides, gives feedback or expresses brand | Only when explicitly requested | Same as frontq | Same as frontq |
| Animating `height` | Only expand/collapse, via `animate-collapsible-*` (accordion removed) | Never; one exception: shared `Textarea` auto-grow, 150ms | Only expand/collapse, `animate-accordion-*` / `animate-collapsible-*` | Same as swissCRM |
| Bounce / spring easing | `ease-bounce`, `ease-pop` etc. retired 2026-09-24, "do not bring back" (but its Expressive line still says bounce/spring) | — | `ease-out-bounce` is the signature curve; `ease-spring` for input | Same as swissCRM |
| Stock numeric durations (`duration-150`) | Banned; only ours drive `animate-in/out` | Its own example uses `duration-150` | — (tokens only) | — |
| Duration scale | 4 steps: 120 / 200 / 320 ms + 1200ms highlight; exit = 0.7× enter | None defined | 10 steps, 0–1200ms (`fast-100` … `slow-1200`) | compass: `slow-1100` named but valued 1000ms (bug); tma same |
| Default easing curve | `ease-soft` = `cubic-bezier(0.23, 1, 0.32, 1)` | Tailwind `ease-out` | `ease-out-soft` = `cubic-bezier(0.22, 1, 0.36, 1)` | Same as swissCRM |
| Hover colour transitions | Immediate, no `transition-colors` (Kumo rule) | — | — | — |
| `animate-pulse` | Banned; use `animate-text-shimmer` | — | — | — |

Note: the three agree on the 200ms ceiling for interaction feedback and on
compositor-only properties, so those are in the shared rule.

## Dropped as generic

The three "Principles" paragraphs (eye-level, speed, memorable) and "duration
tracks size and travel distance" — design advice, not a project convention.

## Stays in repo

**frontq**
- Token tables: `duration-fast` / `base` / `base-out` / `slow` / `slow-out`, `--duration-highlight`; `ease-soft`, `ease-drawer`; exit = 0.7× enter (design language §7)
- Retired easings list (2026-09-24)
- Overlay table (dialog 0.95, menu 0.96, tooltip 0.9, sheet 16px)
- `origin-anchor` reading bits-ui `--bits-floating-transform-origin`; arbitrary `origin-*` lost the cascade (candidate to promote if swissCRM / dronelist hit it)
- `slide-in-from-bottom-1p` dialog settle
- `Button` `press` (`scale(0.97)`), `link` variant opts out
- Utility inventory in `packages/ui/src/styles/animations.css` (`animate-pop-in`, `animate-chat-in`, `animate-icon-swap`, `animate-text-shimmer`, …) and removed list
- Hover colour is immediate; `button.svelte` note; `animate-pulse` ban
- `kumo-design` skill pointer

**dronelist**
- `Textarea` height exception
- (No motion file. It may want one carrying its token names, if any.)

**swissCRM**
- Duration table (`duration-inst` … `slow-1200`) and easing table (`ease-out-soft`, `ease-out-bounce`, `ease-spring`, `ease-in-out-smooth`)
- `animate-pop-in` on `ease-out-bounce`; `animate-accordion-*`
- `packages/ui/**` path glob; `theme.css`, `animations.css`, `design.md` pointers

**compass / tma** (reference only): `slow-1100` naming bug; tma `src/lib/components/ui/**` glob, tokens in `src/routes/layout.css`, no global backstop mention.

---

# Topic: ux-accessibility

## ux-accessibility — merge notes

Sources: `apps/{swissCRM,compass,tma}/.claude/rules/ux-accessibility.md` (233 / 233 / 226 lines).
swissCRM and compass are identical except the `paths` glob. All differences are tma vs the other two.

## (a) Conflicts

No real conflict: swissCRM and compass agree on every rule, so swissCRM wins each row. Check the rows marked **check**.

| Rule | swissCRM | compass | tma | Merged |
| --- | --- | --- | --- | --- |
| `paths` | `**/*.svelte`, `apps/web/src/routes/**`, `packages/ui/**` | `**/*.svelte`, `apps/studio/src/routes/**`, `packages/ui/**` | `**/*.svelte`, `src/routes/**`, `src/lib/components/ui/**` | `**/*.svelte` only |
| Screen reader target | NVDA | NVDA | (no line) | NVDA — **check** if this is true for tma |
| Page title pattern | `[Company name] + [Page description]` | same | `[App name] + [Page description]` | swissCRM wording — **check**: for one-product repos "App name" may be what you mean |
| Audio & video (captions, audio description, transcripts) | yes | yes | (no section) | dropped as generic (see c) |
| Focus ring color token | `ring-action-blue` | `ring-action-blue` | `ring-system-blue` | token left out; "the project's focus color token" |
| Button example | "Book flight", "Delete booking" | same | "Add account", "Delete transaction" | moved to `ux-content.md` with neutral examples |
| Image alt example | "Aircraft parked at gate C12" | same | "Quarterly net-worth trend chart" | dropped (generic alt-text advice) |
| Icon button example | `<!-- SVG here -->` | same | `<IconX class="size-4" />` | dropped |

## (b) Stays in repo

- **swissCRM**: `ring-action-blue` focus token; path globs `apps/web/src/routes/**`, `packages/ui/**`; aviation examples ("Book flight", gate C12).
- **compass**: `ring-action-blue` focus token; path glob `apps/studio/src/routes/**`, `packages/ui/**`. Note: compass carries the same aviation examples as swissCRM — likely copy drift, worth replacing there.
- **tma**: `ring-system-blue` focus token, `IconX` component; path globs `src/routes/**`, `src/lib/components/ui/**`; finance examples.
- After the shared rule lands, each repo file can shrink to these lines only (project rules load after user rules and win).

## (c) Dropped as generic

- POUR principles list — WCAG basics.
- "Use h1–h6, never skip levels" — generic.
- Semantic element list (`article`, `nav`, `main`…) — generic; kept only "wrong element is worse than div" and the `<time>` rule.
- Keyboard key table (Tab, Shift+Tab, arrows, Enter, Space) — generic; kept Esc + return focus.
- ARIA landmarks block — generic, and the source example was wrong (it nested `<main>` inside `<nav>`, and adds `role=` to native elements, which is redundant).
- "aria-label on repeated landmarks" — generic.
- "All mouse content reachable by screen reader" — generic.
- Field anatomy list (hint, visual indicator, focus state) — generic; kept label, optional marker, inline error.
- `for`/`id` labels, `autocomplete` attributes — generic.
- Contrast table (4.5:1, 3:1, graphics 3:1), "measure, don't assume" — WCAG AA basics.
- "Color is never the only signal" — generic here; the icon + text pairing is kept in `ux-content.md` for alert states.
- "Text resizable without horizontal scroll" — WCAG basic.
- Link text "never click here / read more" and button action verbs — moved to `ux-content.md` (was duplicated there).
- "Headings short, avoid long blocks without headings" — generic.
- Images: alt describes content, `alt=""` for decorative, icon buttons need `aria-label`, logo link alt = destination, no flashing — generic.
- Audio & video section (swissCRM + compass only) — generic WCAG, and not used in these B2B apps.
- Implementation quick-reference code block — generic; kept the focus-ring pattern only.

---

# Topic: ux-content

## ux-content — merge notes

Sources: `apps/{swissCRM,compass,tma}/.claude/rules/ux-content-guidelines.md` (202 / 195 / 162 lines).
compass = swissCRM minus the "in-app copy only" scope note. tma replaced the aviation sections with finance ones.
Merged file is renamed `ux-content.md`.

## (a) Conflicts

| Rule | swissCRM | compass | tma | Merged |
| --- | --- | --- | --- | --- |
| Scope note (in-app only; marketing copy follows `.docs/engineering/marketing-copy.md`) | yes | no | no | **conflict** — compass disagrees. Merged keeps a generic one-liner ("a repo's marketing-copy doc wins for public pages"); the path and claim rules stay in swissCRM |
| Verb for pointing at controls | "click the button below" | "click" | "select the button below" | **conflict** — compass agrees with swissCRM, so "click" is used. tma's "select" is device-neutral; **decide** |
| Domain format section | Flight Number Format (`LX003`, mono, uppercase) | same (flight numbers) | Money & Identifier Formatting (`formatCurrency`, ISIN/IBAN mono) | **conflict** — no shared rule. Merged keeps only the common part: codes/IDs in `font-mono tabular-nums`, uppercase, never cut mid-token |
| Alert section | IRREG: icon table + Mustard background reserved | same | Warning & Destructive: `--system-orange` / `--system-red`, AlertDialog for destructive | **conflict** — different domains. Merged keeps the common idea (reserved alert colors from tokens, icon + text) plus tma's "destructive always behind a confirm dialog, never auto-submit" — **added from tma only; check** |
| Empty states (explain what appears, one next action, no blank tables) | no section | no section | yes | **added from tma only; check** — trimmed to one line + one action to match CLAUDE.md "Text in the Product" |
| Images (naming, 100 KB, colored background fallback) | yes | yes | no | kept (swissCRM + compass agree) — **check** that tma is fine with it |
| External logos alphabetical | yes | yes | no | kept (swissCRM + compass agree) |
| Mobile checklist extras: "Videos and graphics preferred over text" | yes | yes | no | dropped as generic/marketing |
| "Follow SEO guidelines for content pages" | yes | yes | no | dropped — marketing, not in-app |
| Microcopy "where it appears" includes empty states | no | no | yes | n/a (list dropped as generic) |
| Mobile intro "More than half of visits are mobile" | yes | yes | no | dropped (rationale only); mobile-first already in `svelte5.md` |
| `paths` | `apps/web/...`, `packages/ui/**` | `apps/studio/...`, `packages/ui/**` | `src/routes/**`, `src/lib/components/ui/**` | `**/*.svelte` only |

## (b) Stays in repo

- **swissCRM**: scope note + link to `.docs/engineering/marketing-copy.md` and its claim rules; Flight Number Format (`[Carrier][Number][Suffix]`, 3-digit padding, `LX1234a`); IRREG icon table and Mustard background; image content criteria (real customers, all age groups) and the AirEM fallback; "Partner Guideline & External Brand Labeling" document reference; aviation examples ("Book flight", "Continue to payment", "load your bookings").
- **compass**: same aviation sections as swissCRM (flight numbers, IRREG, AirEM, partner guideline). Likely copy drift — check whether compass needs them at all.
- **tma**: `formatCurrency` from `$lib/utils/formatters` and money display rules (`€12,345`, sign + `success-solid` / `destructive-solid`, `+5.2%` with arrow, relative dates); ISIN example; `--system-orange` / `--system-red` tokens and `AlertDialog`; "Trust indicators" (local-first, "All data stored locally", no syncing spinners); finance examples ("Add account", "Import your first CSV").

## (c) Dropped as generic

- Error rule "use personal pronouns" — folded into Voice.
- Form error structure (summary at top + per-field message) — kept once, in `ux-accessibility.md`.
- Language guidelines 9-point priority list — kept only voice, "less is more", user's words, consistency.
- "Guide the user, answer questions proactively", "clear, well-structured page" — generic.
- "Match tonality to page type" — generic.
- Microcopy intro and "where it appears" list — generic.
- Microcopy "focus on context", "be helpful", "direct the user", "conversational" — generic; kept "under 8 words", exact verbs, consistency, warmth only on 404/empty.
- Mobile checklist: "fully responsive", "test on real devices" (a verification step), "catchy text", "tabs where useful", "high contrast", "white space generously" — generic.
- Image criteria "fit the context", "correct aspect ratios" — generic.
- Logos "follow partner brand guidelines for sizing and spacing" — generic.
