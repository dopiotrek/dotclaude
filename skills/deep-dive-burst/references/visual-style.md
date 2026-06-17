# Visual Style — HTML the skill generates

One aesthetic governs everything this skill renders: the burst workspace, learning visuals, and the post visual. These rules derive from the user's own "Technical Swiss" UI skill (frontend-design) — apply them to every HTML output so it all looks made by the same hand. The concrete reference implementation is `references/workspace.html`; copy its tokens and patterns rather than reinventing.

## Core principles

1. **Grid is law** — 4px base unit; everything aligns.
2. **Typography does the work** — hierarchy through size and weight, not colour.
3. **One accent, used sparingly** — a single accent (from `config.yaml` `workspace.accent_color`, default `#2563eb`) for primary actions and progress only. Never colour body text with it.
4. **Separators, not boxes** — do NOT wrap each component in a border. Group with a single hairline rule between sections and with whitespace. The only borders that earn their place: inputs (textarea), the tab underline, the prompt block, and the modal. A box around everything reads as clutter.
5. **Sharp, not round** — NYT-style. `border-radius: 0` on containers, buttons, inputs, dialogs; chart bars and rectangles are square. The only curves allowed are true circles used as data/indicators (status dots, the progress ring). No rounded "card" corners.
6. **Sans for almost everything** — use a monospace stack ONLY for code, file paths, and copyable prompt blocks. Numbers get `tabular-nums` in the sans face, not mono. Labels, data readouts, eyebrows: all sans.
7. **Whitespace is intentional** — dense but never cramped. Page can be wide (~1180px) to hold tables and charts.
8. **No decoration** — every element is functional.
9. **Contrast is non-negotiable** — accessibility over aesthetics.

## Hard nos

- No gradients (use a flat fill; render progress with SVG stroke, not a conic gradient).
- No purple or multicolour schemes.
- No glow effects as affordances; use the default shadow scale sparingly if at all.
- No second accent. Small semantic status dots (done/now/todo: green/amber/neutral) are the only allowed extra colour, and only as tiny indicators — never as text colour.

## Palette tokens

Neutral first: white/zinc surfaces, zinc ink and muted greys, hairline borders. Plus the single accent and the three status-dot colours. Always include a `prefers-color-scheme: dark` variant. Use the token set in `workspace.html` verbatim unless config overrides the accent.

## Self-contained, always

Every HTML output is a single self-contained file — no external CSS/JS files, no iframes to sibling files. Allowed CDNs: Chart.js and Mermaid (only these). Prefer inline SVG and plain HTML tables for visuals so the file works offline; reach for Chart.js only when a real chart needs it.

## Progressive disclosure

Surface the important data; tuck the rest behind:
- **Tabs** for parallel sections of equal weight (workspace: Overview / Research / Visuals / Draft / Ship).
- **Accordions** (`<details>`) for long secondary content.
- **Tooltips** (CSS `data-tip`) for definitions and small caveats.
- **Dialog** (`<dialog>`) for help/about and anything that would otherwise clutter the page.
Keep the primary action and current status always visible; everything optional is one interaction away.

## Accessibility

- Icon-only buttons get an `aria-label`.
- Tabs use `role="tablist"/"tab"/"tabpanel"`, `aria-selected`, and arrow-key navigation.
- `<dialog>` for modals (native focus handling); never hand-roll focus traps.
- Respect `prefers-reduced-motion`; animate only `transform`/`opacity`, never layout, never over 200ms.

## Two standards for visuals

- **Learning visuals (for understanding):** accuracy first. Built only from researched data, each figure's source noted. If data is missing, show the gap, never invent numbers.
- **Post visual (for readers):** honesty of tone first. Clean and plain, not corporate-glossy — over-polished consultant charts signal fake expertise. A simple labelled chart, a tidy table, or a hand-drawn-style schema all fit the learner-notebook brand.

Chart styling: follow NYT conventions — square bars (no rounded corners), thin axis/gridlines or none, direct labels on the data rather than a separate legend where possible, one accent plus greys, generous whitespace. Readable at a glance beats dense and decorated.

### Pick the right form (default to the simplest that carries the point)

Most of the time a **table** is the honest answer — reach for a chart only when the *shape* of the data is the point, not the numbers themselves.

- **Table** — a handful of items compared on a few attributes; exact values matter; mixed types (text + numbers). Default here. (E.g. SpaceX segments × what-they-sell × who-pays.)
- **Bar chart** — comparing one number across categories (ranking, magnitude). Horizontal bars when labels are long or there are many categories. (E.g. revenue by segment.)
- **Line chart** — one or a few series changing over continuous time; the trend/direction is the point. (E.g. Falcon 9 launches per year.)
- **Area chart** — only when a cumulative total or composition over time genuinely matters; otherwise prefer a line (area is easy to misread). Use sparingly.
- **Stacked bar / 100% stacked** — parts of a whole across a few categories (composition). Cap at ~4–5 segments or it turns to mush.
- **Scatter** — relationship between two numeric variables across many points. Rare for these posts.
- **Simple schema / flow / 2×2 / spectrum** — relationships, positioning, or a sorting that isn't numeric at all. Often the strongest "one visual" for a learning post (e.g. a believe→skeptic spectrum of ambitions). Hand-drawn-style fits the brand.

Rules of thumb: one chart makes one point — if it needs a legend of 6 colours, it's two charts. Never a pie chart with more than 2–3 slices (a bar is clearer). Don't chart 3 numbers you could just say in a sentence. If exact figures matter more than the trend, use a table. When unsure between a chart and a table, choose the table.
