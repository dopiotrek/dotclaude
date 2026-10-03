---
name: latent-economy
version: 2.0.0
description: |
  Full content-lifecycle engine for the Latent Economy publication: mine
  sources for takes, run candidates through the filter, draft replies and
  quote-tweets, build launch packages (warm-up tweets, threads, post-publish
  shorts), and track where every topic stands. Use when the user wants to
  "run it through the filter", check if something is on-brand, mine a
  podcast/book/article/tweet for content ideas, reply to or quote a tweet,
  prepare or run an article launch, draft warm-ups or shorts, check the
  receipts trap list, ask "where are we with <topic>", or do any Latent
  Economy content work. Triggers: "latent economy", "the ledger", "the
  filter", "new piece", "warm-up", "launch package", "shorts", "reply to
  this", "quote this".
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebFetch
  - WebSearch
  - Skill
  - AskUserQuestion
---

# Latent Economy — content lifecycle engine

This skill is a **router and process engine, not a source of truth**. All
rules, voice, cadence, and data live in the repo at:

```
/Users/piotrek/repos/projects/latent-economy
```

Never restate that content here or from memory — read the files live, every
invocation. If a governing file is missing, stop and tell the user; do not
improvise the rules.

## Read order (before any verdict or draft work)

Read these, in this order. On any conflict between them, the earlier file wins.

1. `the-ledger-operating-brain.md` — THE governing doc: worldview, core
   beliefs, evidence rules, topic evaluation (§4), worked example (§5).
2. `brand.md` — the operational layer: lane (Positioning), register (Voice),
   Audience, the three pillars (Delta / Stack Traces / Refactor).
3. `content/filter.md` — the kill / rewrite / ship gate, including the
   external-tweet mode (steal / quote / skip).
4. `receipts.md` — the **trap list** (always check before citing any famous
   number) and shared cross-piece numbers.

For planning and launch work also read `content/series-bible.md` (the arc)
and `content/playbook.md` (the release engine: cadence and the `launch.md`
structure in §3, warm-up angles §4, engagement list + reply rules §5,
per-channel format cards §7).

The repo's own `CLAUDE.md` holds the full working rules, the receipts rule,
and the list of decisions that are **not locked yet** — read it before making
any call that touches naming, pricing, or strategy.

## Two skill-wide rules

- **Who drafts what:** the user drafts article bodies — never produce body
  text. Agents DO draft all social copy: warm-up tweets, threads, shorts,
  replies, quote-tweets. Every drafted item carries a receipt (checked
  against the trap list, ⚠ flags kept) and the user approves it before it
  posts.
- **Humanizer pass:** every piece of drafted copy is run through the
  `humanizer` skill (via the Skill tool) before it is shown to the user or
  saved to a file. If the humanizer skill is not available in the session,
  say so explicitly and continue — never skip silently.

## State model (all state lives in the repo)

- `content/pieces/<slug>/piece.md` frontmatter `status`
  (`idea → filtered → drafting → pretest → published → retro-done`) + its
  release checklist.
- `content/pieces/<slug>/launch.md` — the launch package; its checkboxes ARE
  the posting state (checked = posted).
- `content/engage.md` — the reply/quote queue (`pending → posted | skipped`).
- Backlog: `content/ideas.md`. Shipped log: `content/published.md`.
  Deferred: `TODO.md`.

## Modes

Pick by the user's input. A pasted candidate defaults to `filter`; a source
to mine defaults to `find`; "where are we / what's next" defaults to `status`.

### `find <link | pasted text | notes from a podcast or book>`

Mine a source for takes that could become content.

1. If given a link, fetch it (WebFetch). Podcast/book input is the user's
   pasted notes or quotes.
2. Mine the material for candidate takes using the filter's four-question
   screen: name the trapped value, the gatekeeper, the release, the receipt.
3. Run each candidate through the filter; report a compact scorecard and
   verdict per candidate — including the kills, with the one-line reason.
4. Survivors (SHIP / REWRITE): write to `content/ideas.md` under the right
   pillar, with source attribution. If a take deserves a full piece, say so
   and offer `new-piece`.

### `engage <tweet/post> [reply | quote | both]`

Draft engagement with someone else's post. Default to `both` only when the
user asks for both.

1. Run the filter's **external-tweet mode first** → STEAL / QUOTE / SKIP.
   Check the author against the playbook §5 research-only list — those
   accounts are never engaged, regardless of content.
2. On SKIP: say why, stop. On STEAL: the insight becomes an own post — route
   it through `find`-style filtering into `ideas.md`; no reply/quote drafted.
3. On QUOTE, draft what was asked:
   - **Reply** — short, in-thread, the operator's view plus exactly one
     receipt (a number, a named case, a date — playbook §5; never "great
     point", never a dunk).
   - **Quote** — expands, never repeats the reply: own frame, the lane angle,
     a different receipt or a costed comparison.
   - **Stay in THEIR topic.** The receipt must be native to the thread's
     subject; if the bank has nothing germane, source one first or don't
     engage. Never inject home-turf numbers (Mittelstand/Nachfolgewelle,
     the Delta) into an unrelated thread — those are on-request only
     (playbook §5). Apply the lane as a way of thinking (hidden forces,
     named mechanisms), not as a mention — no plugging the worldview,
     the publication, or the pillars by name.
4. Humanizer pass on each draft; trap-list check on every number.
5. Append the entry to `content/engage.md` (its Entry format), status
   `pending`. The user posts manually and flips the status.

### `launch <slug>`

Build the promotion package for a finished article.

1. Preconditions: `content/pieces/<slug>/piece.md` exists and its canonical
   body is drafted (status `drafting` or later). Otherwise report the actual
   status and what's missing, and stop.
2. Read the piece: its receipts, sharpest claims, most surprising stats, the
   two-sentence version, the coinage if present.
3. Generate `content/pieces/<slug>/launch.md` per playbook §3 (cadence and
   structure live THERE — follow it, don't restate it). In short: warm-up
   tweets day −7…−1 (2–3/day) + 1–2 threads across the window, a pointer to
   the launch thread in `x.md` (never duplicated), and shorts day +1…+3
   (2–3/day, one tidbit each). One checkbox per item: `- [ ] D−6 #2: <draft>`.
4. Every draft: receipt attached (trap list checked, ⚠ flags kept) → voice
   check (brain §6) → humanizer pass. Respect the teaser rule (none until the
   final 3 days, max 2).
5. Set the piece status to `pretest` when warm-up starts; remind about the
   Reddit pre-test (playbook §6) and logging in `content/published.md` after
   publish.

### `status [slug | topic]`

Answer "where are we with this?"

1. Named or matched piece → report: frontmatter status, release-checklist
   progress in `piece.md`, `launch.md` checkbox progress (posted vs. remaining,
   per day), and the single next action.
2. Topic matches nothing in `content/pieces/`, `content/ideas.md`, or
   `content/engage.md` → say it's a new topic and offer `find` or `filter`.
3. No argument → portfolio view: every piece with its stage, pending engage
   entries, and next actions.

### `filter <idea | draft | pasted tweet>`

Run the candidate through `content/filter.md` exactly as that file specifies
— its gates, its scorecard, its rewrite protocol. Return the verdict:
kill / rewrite / block / ship.

### `evaluate <topic>`

Run the brain's §4 topic evaluation and answer, in its terms: is it a fit,
what angle, what format, which platform, where it slots in the series, what
proof (receipts) it needs.

### `new-piece <slug>`

Copy `content/pieces/_template.md` to `content/pieces/<slug>/piece.md`, fill
the frontmatter, set `status: idea`. No body text.

### `draft-check <draft>`

Audit an existing draft against the voice guardrails (brain §6 + `brand.md`
→ Voice) and the receipts rule: every claim sourced, ⚠ figures keep their
caveat, both sides of the ledger present, ends on what was built. Report
findings; edit only if asked.

## Standing flags

- **Publication-name conflict:** the brain says "The Ledger (final)" but the
  ratified 2026-07-14 decision is _Latent Economy_. Flag the tension when it
  comes up; never silently resolve it. Details in the repo `CLAUDE.md` and
  `TODO.md`.
- Several decisions (coinage, bio, service name/price, and more) are
  explicitly not locked — the list lives in the repo `CLAUDE.md`. Don't pick
  for the user.
