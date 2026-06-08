---
name: learn
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
  is the tutor skill. Reach for learn when the unit is a whole domain and the
  horizon is weeks, not one answer.
---

# Learn

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
`scripts/build_map.py` — never hand-write the HTML.

---

## How the learner likes it (defaults — honor these)

These are the non-negotiable style defaults. Override only if the user asks.

- **Big picture before any detail.** Never start a deep-dive before the terrain
  map exists and the learner has seen it. They need a place to *put* each new
  fact. A fact with no home is forgotten by morning.
- **One chunk at a time.** The smallest self-contained idea, then stop. No walls
  of text. Working memory holds ~4 items; respect that budget.
- **First principles, plain language.** Build each idea up from something the
  learner already believes. Strip jargon. When a term is unavoidable, derive it,
  don't drop it. Buzzwords are banned — if a sentence survives deleting a word,
  delete it.
- **An analogy per hard idea.** Concrete and from a domain they already know.
- **Conversational, not a textbook.** Talk to them. Simplicity is the aesthetic.
- **Make them work.** Active recall over passive reading. The learner explaining
  it back is the product; your explanation is just the setup.

---

## 1. Frame (cheap, fast — one or two questions max)

Establish just enough to aim. Don't run a survey; ask at most two questions, and
only the ones whose answers change what you do:

- What's the topic, and what does *done* look like — conversational fluency, a
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
`references/state-schema.md`). Default location: `learn/<topic-slug>/` under the
working directory. If a state file for this topic already exists, **resume** —
read it, tell the learner where they left off and what's due for review, don't
start over.

## 2. Terrain map (the gate that makes everything else work)

Produce the map of the *whole* territory before diving into any part of it. This
is the single most important step and the one most learning skips.

The map answers: what are the major regions of this domain, how do they connect,
which are core vs periphery, and where are the edges (what this is *not*). Keep
it honest and small — 4 to 8 regions, each one phrase. Resist the urge to teach
here; you're drawing the coastline, not exploring inland.

Also produce **the one sentence**: "Stripped to its core, this whole domain is
about ___." If you can't write that sentence, you don't understand the domain
well enough to teach it yet — go learn more first.

Write the regions and edges into `state.json`, run `build_map.py`, and **show the
learner the HTML map.** Then gate:

> "Here's the terrain. Does this match your mental picture, or is something
> missing / mis-sized before we go in?"

Adjust until it resonates. A map the learner co-signed is a map they'll use.

## 3. Pick a path

From the map, choose the first region to descend into. Be opinionated — pick the
one with the highest leverage for *their* goal and say why, rather than offering
a neutral menu. Usually that's the region everything else depends on, or the one
blocking their immediate need. Mark "you are here" in the state.

## 4. Chunked deep-dive (the core loop — repeats)

For the chosen region, loop this until the region is covered or the learner wants
to stop. The full craft is in `references/method.md`; the rhythm is:

1. **Deliver one chunk.** Smallest self-contained idea. First principles, plain
   language, one analogy. A few sentences, not a page. Then *stop*.
2. **Recall gate.** Ask the learner to either explain it back in their own words
   or answer one pointed question about it. This is non-negotiable — it's where
   the learning actually happens, and it's the only honest signal of whether to
   continue.
3. **Grade and branch:**
   - Solid → mark the chunk learned, schedule its first review, advance.
   - Fuzzy → **re-explain differently** (new analogy, different level — ELI5 /
     ELI14 / intern, per method.md). Do not just repeat yourself louder. Re-gate.
4. **Log it.** Append the chunk (with its recall question and a one-line answer
   key) to `state.json`. Regenerate the map so progress and "you are here" stay
   live.
5. **Capture tangents separately.** If something interesting but off-path comes
   up, park it in the open-questions list. Don't chase it mid-dive — that's how
   learners get lost.

If the `tutor` skill is available and the learner wants to go deep on one chunk
(drill the whys hard, multi-level), hand off to it for that chunk, then come back
here to log and continue. Don't reimplement its machinery.

## 5. Compress to a grammar

Once a region has enough chunks (roughly 5+), stop adding facts and find the
*grammar* — the 2 to 4 variables that generate most of the region's behavior.
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
  active-recall pass over due items before any new material. Grade each
  (easy / ok / hard) and push its next date out or pull it in accordingly.
- **Offer to schedule it.** If the learner wants, set up a recurring review via a
  scheduled task ("quiz me on my due `learn` items each weekday at 8am"). Don't
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
