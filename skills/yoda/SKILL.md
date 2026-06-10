---
name: yoda
description: >
  Learn a new domain the way that actually sticks: map the whole terrain first
  (the big picture, as a navigable HTML map), then take guided first-principles
  deep-dives one small chunk at a time, with Feynman teach-back gates and spaced
  repetition so it stays in memory. Use whenever the user wants to get into a
  broad or unfamiliar field over time — "teach me X from scratch", "I want to
  learn this domain", "help me understand this field", "build me a learning map
  for X", "map out X for me", "where do I even start with X", "I keep forgetting
  X, help me retain it", "make me a study plan for X". Persists a per-topic map
  you can reopen and resume. Do NOT use it to explain a single artifact already
  in front of you in one sitting (a specific diff, PR, function, or paper) — that
  is the tutor skill. Reach for yoda when the unit is a whole domain and the
  horizon is weeks, not one answer.
---

# Yoda

A companion for entering a new domain and actually retaining it. The whole design
serves one belief: **you understand a territory only once you can see its map,
hold its grammar in your head, and rebuild any piece from first principles.** Not
once someone has explained it well to you.

This skill is a gated pipeline, not a lecture. Each gate exists because skipping
it is how learning quietly fails — a map nobody confirmed, a chunk that was nodded
at but not understood, a fact learned once and never reviewed.

## The shape of it

```
FRAME ──▶ TERRAIN MAP ──▶ PICK A PATH ──▶ CHUNKED DEEP-DIVE ──▶ COMPRESS ──▶ REVIEW
 (1)        (2) gate          (3)         (4) recall gate, loops    (5)       (6) spaced
```

You move left to right, but the loop at step 4 runs many times, and step 6 keeps
firing forever (that's the point of spaced repetition). State lives in one file
per topic so any session can resume exactly where the last one stopped.

Read `references/method.md` for the teaching craft (how to write a chunk, run a
recall gate, find a grammar). Read `references/state-schema.md` for the exact
state file the agent maintains. The HTML map is produced by
`scripts/build_map.py` — never hand-write the HTML. The map renders as a clickable
roadmap — regions banded by tier (foundations → frontier), every node badged with
its mastery level (0–4); clicking a node opens a right-side drawer with its detail,
key models, and the honest gap to the next level.

## Two ladders: tiers and mastery

Two different things both get called "levels"; keep them straight.

**Tiers — where a topic sits in the domain.** Set when you draw the map. Every
region gets one, and the map stacks them so the learner sees what rests on what:

1. **Foundations** — first principles; everything else is built on these.
2. **Core** — the main working mechanics that sit on the foundations.
3. **Advanced** — deeper mechanics and edges for real competence.
4. **Frontier** — expert, rare-air territory.

**Mastery — the learner's grip on a single chunk.** You rate it 0–4, honestly:

- **0 Unseen** — not taught yet.
- **1 Fragile** — heard it, can't reconstruct it.
- **2 Working** — explains it with a nudge; the _why_ is still shaky.
- **3 Solid** — reconstructs it cleanly from first principles, unprompted.
- **4 Expert** — applies it to novel cases, knows the failure modes, could teach it.

Tier is fixed by the material; mastery grows with the learner. The map shows both —
regions banded by tier, every node badged with its mastery. Labels are renameable
in `config.yaml`.

## Configuration — read `config.yaml` first

At the start of every session, read `config.yaml` (sibling of this file) and honor
it; fall back to the defaults below if the file or a key is missing. It holds the
knobs that change per person — the _method_ stays in this skill, your _preferences_
live in config (the same split that keeps a model's assumptions out of its
formulas):

- `topics_dir` — where per-topic folders get written (default `yoda`).
- `analogies.prefer` / `avoid` / `rule` — which domains to draw analogies from.
  Default: airlines/airports and everyday physical life, kept concrete and
  visualizable.
- `recall.mode` — `active` (teach-back gate after every chunk; default) or
  `passive` (explain with light optional checks).
- `visuals.diagrams` — when to draw a simple schema (boxes + arrows) for a chunk,
  shown in the map's detail drawer (see step 4).
- `review_on_resume` — open a returning session with what's due (default true).
- `tutor_handoff` — hand a deep single-chunk drill to the `tutor` skill when
  available (default true).
- `roadmap.tiers` / `mastery.levels` — the display names for the two ladders
  (rename freely). `mastery.honesty` — how blunt to be when rating answers
  (default `brutal`: name the gap, never flatter).

Use config values where they apply; never hardcode into the method something that
belongs in config.

---

## How the learner likes it (defaults — honor these)

These are the non-negotiable style defaults. Override only if the user asks.

- **Big picture before any detail.** Never start a deep-dive before the terrain
  map exists and the learner has seen it. They need a place to _put_ each new
  fact. A fact with no home is forgotten by morning.
- **One chunk at a time.** The smallest self-contained idea, then stop. No walls
  of text. Working memory holds ~4 items; respect that budget.
- **First principles, plain language.** Build each idea up from something the
  learner already believes. Strip jargon. When a term is unavoidable, derive it,
  don't drop it. Buzzwords are banned — if a sentence survives deleting a word,
  delete it.
- **An analogy per hard idea.** Concrete and _visualizable_ — something they can
  picture — drawn from the domains in `config.yaml` (`analogies.prefer`; default:
  airlines and everyday life). If you can't picture it, it's the wrong analogy.
- **Conversational, not a textbook.** Talk to them. Simplicity is the aesthetic.
- **Make them work.** Active recall over passive reading. The learner explaining
  it back is the product; your explanation is just the setup.

---

## 1. Frame (cheap, fast — one or two questions max)

Establish just enough to aim. Don't run a survey; ask at most two questions, and
only the ones whose answers change what you do:

- What's the topic, and what does _done_ look like — conversational fluency, a
  decision, shipping something, passing an exam?
- Current level: total beginner, or do they already hold some pieces?

Infer the rest. If they say "teach me Kubernetes because we're migrating
swissCRM off Vercel," you have topic, goal, and level without asking.

**Research routing (cheapest capable tier first).** Decide whether you even need
to search:

- Evergreen / conceptual domain (thermodynamics, double-entry accounting, how
  TCP works) → build the map from what you already know. Don't burn a search.
- Fast-moving / factual / versioned (current SuccessFactors module pricing, the
  latest Svelte 5 runes API, who leads a field now) → search before mapping, and
  cite.
- Unsure → one search to calibrate, then proceed.

Create the topic folder and an initial `state.json` (see
`references/state-schema.md`). Default location: `<topics_dir>/<topic-slug>/`
(from `config.yaml`, default `yoda/<topic-slug>/`) under the working directory. If a state file for this topic already exists, **resume** —
read it, tell the learner where they left off and what's due for review, don't
start over.

## 2. Terrain map (the gate that makes everything else work)

Produce the map of the _whole_ territory before diving into any part of it. This
is the single most important step and the one most learning skips.

As soon as you've framed (and asked any refining question), your **first
deliverable is the map** — the visual of the whole path, before any teaching. Lay
out, into `state.json`:

- The major **regions** (4–8, each a phrase) and how they connect.
- Each region's **tier** — `foundation` / `core` / `advanced` / `frontier` — so the
  map stacks first-principles at the base and expert territory on top. Be
  deliberate: this stratification is the first thing the learner reads.
- The **planned chunks** in each region (titles, `status: locked`, `mastery: 0`),
  so the roadmap shows the _whole_ curriculum up front, not only what's been
  learned. They light up as mastery grows.
- A few **key theories / models** per region (`models`: name + one line) — the
  canonical frameworks worth knowing. These anchor and strengthen the topic.
- **The one sentence**: "Stripped to its core, this domain is about \_\_\_." If you
  can't write it, you don't yet understand the domain well enough to teach it.

Keep regions honest and small; you're drawing the coastline, not exploring inland.
Run `build_map.py`, **show the learner the HTML roadmap**, then gate:

> "Here's the terrain — foundations at the base, building toward the frontier.
> Does this match your picture, or is something missing / mis-tiered before we go
> in?"

Adjust until it resonates. A map the learner co-signed is a map they'll use.

## 3. Pick a path

From the map, choose the first region to descend into. Be opinionated — pick the
one with the highest leverage for _their_ goal and say why, rather than offering
a neutral menu. Usually that's the region everything else depends on, or the one
blocking their immediate need. Mark "you are here" in the state.

## 4. Chunked deep-dive (the core loop — repeats)

For the chosen region, loop this until the region is covered or the learner wants
to stop. The full craft is in `references/method.md`; the rhythm is:

1. **Deliver one chunk.** Smallest self-contained idea. First principles, plain
   language, one analogy. A few sentences, not a page. Then _stop_.
2. **Recall gate.** Ask the learner to either explain it back in their own words
   or answer one pointed question about it. This is non-negotiable — it's where
   the learning actually happens, and it's the only honest signal of whether to
   continue.
3. **Rate it honestly, then branch.** Score the answer on the mastery ladder (0–4)
   and say the number plainly. Be blunt — no "great job" for a half-answer; name
   the _specific_ thing missing and the one move that lifts it a level. Write the
   score to `mastery` and that one-line delta to `gap` on the chunk.
   - Mastery ≥ 3 (Solid) → schedule its first/next review, advance.
   - Mastery ≤ 2 → re-explain differently (new analogy, drop a level — ELI5 / ELI14
     / intern, per method.md), then re-gate. Don't advance on a 2 — that's the
     illusion of knowing.
4. **Log it.** Append the chunk (recall question, one-line answer key, `mastery`,
   `gap`, any `models`) to `state.json`. Regenerate the map so the node's level and
   "you are here" stay live.
5. **Capture tangents separately.** If something interesting but off-path comes
   up, park it in the open-questions list. Don't chase it mid-dive — that's how
   learners get lost.

**Optional — add a schema.** For a chunk that's structural or has moving parts (a
flow, a pipeline, a layered stack, a request round-trip), attach a small diagram so
the shape is _visible_, not just described. Write it as a `schema` on the chunk in
`state.json` — a tiny structured spec (`type: flow | stack`, a list of `nodes`,
optional `labels` between them); the map draws it as clean boxes-and-arrows in that
node's detail drawer. No image model — it's rendered from the spec, so it stays
consistent and version-controllable. Honor `visuals.diagrams` (`none` /
`key_chunks_and_grammars` / `every_chunk`) for how often. A words-only chunk needs
no schema — don't force one.

If `tutor_handoff` is on, the `tutor` skill is available, and the learner wants to
go deep on one chunk (drill the whys hard, multi-level), hand off to it for that
chunk, then come back here to log and continue. Don't reimplement its machinery.

## 5. Compress to a grammar

Once a region has enough chunks (roughly 5+), stop adding facts and find the
_grammar_ — the 2 to 4 variables that generate most of the region's behavior.
This is the "hold it in your head" payoff: mastery isn't more facts, it's fewer,
more generative ones. Method and examples in `references/method.md`.

Deliver the grammar as **one tight paragraph**, not a template. Then test it
live: give the learner a new case and have them predict it using the grammar. Log
the grammar to state; it becomes a high-value review item.

## 6. Spaced review (runs forever)

Memory is the whole reason this skill persists state. Every learned chunk and
every grammar carries a next-review date on an expanding schedule (1d → 3d → 7d →
16d → 35d …; exact algorithm in `references/state-schema.md`).

- **Start sessions with what's due.** When resuming a topic, open with a quick
  active-recall pass over due items before any new material. Re-rate each honestly
  (update `mastery` and `gap`), grade the recall (easy / ok / hard), and push its
  next date out or pull it in accordingly.
- **Offer to schedule it.** If the learner wants, set up a recurring review via a
  scheduled task ("quiz me on my due yoda reviews each weekday at 8am"). Don't
  force it; some people prefer to pull reviews themselves.

Regenerate the map after reviews so the due-panel and progress stay accurate.

---

## Always end a working session by

1. Writing the latest `state.json` (it's the source of truth — never let the chat
   be the only record).
2. Regenerating `map.html` + `map.md` via `build_map.py`.
3. Telling the learner, in one or two lines: what they locked in today, what's
   next on the path, and when the next reviews come due.

## What good looks like / what to avoid

- Good: the learner can draw the map from memory, state the one sentence, and
  rebuild a chunk from first principles a week later.
- Avoid: dumping the whole region at once; advancing past a fuzzy recall; teaching
  detail before the map exists; hand-editing the HTML; letting the grammar
  balloon past 4 variables (if it does, you haven't found the real one yet).
