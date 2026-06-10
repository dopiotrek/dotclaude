# Method — the teaching craft

This is the *how* behind the pipeline in SKILL.md. Read it when you're running a
deep-dive and want the technique right. It covers: writing one chunk, the Feynman
levels, running and grading the recall gate, finding a grammar, and capturing
tangents.

The throughline: **the learner's reconstruction is the product, not your
explanation.** Everything here is in service of getting them to rebuild the idea
themselves.

---

## Writing one chunk

A chunk is the smallest idea that stands on its own. Test: can the learner do
something or answer something *new* after this chunk, and could you write a single
recall question about it? If it needs two recall questions, it's two chunks.

A good chunk, in order:

1. **Anchor.** Start from something the learner already believes or can see. "You
   know how a spreadsheet recalculates a cell when its input changes…"
2. **One move.** Introduce exactly one new idea built on the anchor. "…a reactive
   signal is that, generalized: a value that knows who depends on it."
3. **One analogy** — concrete and _visualizable_. Pull from the wells in
   `config.yaml` (`analogies.prefer`): reach for an **airport/airline** picture
   first (the learner knows it cold), then **everyday physical life**. Avoid
   framework internals and abstract math as analogies unless asked. The test: can
   they _see_ it as a physical scene? If not, it's the wrong analogy. Concrete
   beats clever.
4. **Stop.** Do not bolt on the next idea because it's "right there." The stop is
   what keeps working memory from overflowing.

Length: a few sentences to a short paragraph. If you wrote half a page, you wrote
a region, not a chunk — split it.

Banned: buzzwords, throat-clearing ("it's important to note"), and undefined
jargon. If a term is load-bearing, derive it from the anchor so the learner earns
the word instead of memorizing a label.

### Where analogies come from

Default to two wells, in this order (set in `config.yaml`):

1. **Airlines and airports** — professional home turf, so the picture lands
   instantly. Some that travel well:
   - _Idempotency_: scanning the same boarding pass twice still boards you once.
   - _A queue vs a log_: the baggage belt (each bag taken off once, then gone) vs
     the departure board (everyone reads the same listing; reading doesn't consume
     it).
   - _Cache with a TTL_: a gate change announced once and trusted until it expires.
   - _Load balancing_: extra check-in desks opening to drain one long line.
   - _Rate limiting_: the jet bridge only lets so many board per minute.
2. **Everyday physical life** — luggage, queues, the post, a kitchen, traffic.
   Use when an airline frame would be a stretch; never force one.

Avoid explaining the unfamiliar with the unfamiliar (framework internals, abstract
math). The analogy's whole job is to turn an abstract idea into a scene the learner
can watch happen.

### First principles, concretely

"From first principles" means: don't state a rule, *regenerate* it. Instead of
"React re-renders on state change," walk the why: the UI is a function of state →
when state changes the output is stale → something must recompute it → the cheapest
correct option is to re-run the function and diff. Now the rule isn't a fact to
memorize; it's a conclusion the learner can rederive when they forget it. That's
the entire point — first-principles understanding is *recomputable*, rote facts
decay.

---

## The Feynman levels (match the level to the moment)

When a chunk isn't landing, change altitude rather than repeating yourself.

- **ELI5** — pure intuition and analogy, zero jargon. For first contact with a
  scary idea, or when the learner is lost.
- **ELI14** — real concepts in plain language, light jargon that you define. The
  default working altitude.
- **Intern** — technically correct and concrete, assumes general competence but
  not familiarity with *this* domain. For when the learner has the gist and wants
  the real mechanics.

Offer to shift levels explicitly: "Want the five-year-old version or the intern
version?" A failed recall almost always means *drop a level*, give a different
analogy, and re-gate — not say the same thing louder.

---

## Running the recall gate

After each chunk, before advancing, the learner must produce — not recognize —
the idea. Recognition ("yeah that makes sense") is the illusion of knowing;
production is knowing.

Two gate styles, alternate them so it doesn't feel mechanical:

- **Teach-back:** "Explain that back to me like I'm the one learning it." Listen
  for whether they reconstruct the *why*, not just echo your words.
- **Pointed question:** one question that can't be answered by parroting. Prefer
  "what would break if…" / "predict what happens when…" / "why this and not the
  obvious alternative…" over "what is the definition of…".

Use the **AskUserQuestion** tool for multiple-choice checks when you want a fast,
unambiguous signal; use open chat for teach-back. When you do multiple choice:
vary which position is correct, make the distractors plausible (common
misconceptions, not nonsense), and follow a right answer with "why are the others
wrong?" — that's where the real test is.

### Grading recall (drives the spaced schedule)

Grade honestly; inflating it only cheats the learner's future self.

- **easy** — fluent, correct, included the why, unprompted. Push the next review
  out hard.
- **ok** — correct but effortful, needed a nudge, or missed the why. Normal
  interval.
- **hard / miss** — wrong, or right-by-luck, or pure recognition. Re-teach at a
  lower level with a new analogy, re-gate, and reset the review interval short.

Record the grade on the chunk in `state.json`; the interval math in
`references/state-schema.md` consumes it.

---

## Rating mastery (be brutally honest)

The recall grade (easy/ok/hard) drives _scheduling_. Mastery is a different axis —
_how well the learner actually owns the idea_, 0–4 — and it drives the roadmap and
the honest feedback. Rate it after every answer and say the number out loud.

The cardinal rule: **no flattery.** A half-answer that gets a "nice!" robs the
learner of the one thing they came for — an accurate read of where they stand.
Praise a 2 and they walk away thinking they're a 3, and the gap compounds.

Map the answer to a level, name the **specific** thing missing, and give the **one
move** that raises it:

| Mastery | The answer looked like… | What you say (blunt, specific) |
|---|---|---|
| **1 Fragile** | recognized it, couldn't reconstruct it; vague, hand-wavy | "That's recognition, not understanding — you named _what_ but not _why_. To reach Working: explain, from the Pod up, why a bare container can't be scheduled." |
| **2 Working** | correct mechanics, needed a nudge, the _why_ is thin or borrowed | "Right mechanically, but you leaned on my words for the why. To reach Solid: rebuild it from first principles with no hint." |
| **3 Solid** | clean reconstruction from first principles, unprompted | "Solid — you rebuilt it yourself. To reach Expert: apply it to a case you haven't seen, and tell me where it _breaks_." |
| **4 Expert** | applies it to novel cases, knows the failure modes, could teach it | "Expert. You can predict it and you know the edges. Nothing to close here." |

Write the level to `mastery` and the one-move delta to `gap` on the chunk (`gap` is
empty at 4). The map badges the level and shows the gap in the drawer, so the
learner always sees exactly what stands between them and the next rung — and the
topic's overall level is just the mastery of its chunks, so "reach expert" stops
being a vibe and becomes a checklist.

Be the same blunt with yourself: if you can't tell which level an answer is, your
question was too soft. Ask a sharper one (predict / break / why-not) and re-rate.

## Tiering the map, and naming the models

When you lay the terrain (SKILL.md step 2), two extra moves pay off for the whole
journey:

**Assign a tier to each region** — `foundation` / `core` / `advanced` / `frontier`.
The test: could the learner understand this region _without_ the ones below it? If
not, it sits higher. Foundations are the few regions everything else silently
assumes; the frontier is where even practitioners argue. Getting the tiers right is
most of what makes the map feel like a map and not a flat list.

**Name the key models per region** — the two or three canonical theories,
frameworks, or named results a competent person reaches for here (for an auth
region: the _confused-deputy problem_, the _OAuth threat model_; for a stats
region: _Bayes' theorem_, the _central limit theorem_). Store them as `models`
(name + one line). They aren't chunks to grind — they're landmarks that tell the
learner the territory is real and hand them the vocabulary to go deeper on their
own.

## Finding a grammar (compression)

After ~5 chunks in a region, switch from accumulating to compressing. A grammar
is not a summary — a summary describes what exists; a grammar *generates* it. You
want the 2–4 variables whose settings explain most of the region's variation.

Procedure:

1. **Hunt patterns.** What recurs across the chunks? What single change would
   ripple through everything else? What do practitioners argue about (arguments
   cluster on the load-bearing variables)?
2. **Hypothesize 2–3 variables.** Variables, not parts. "Cooling cost" is a part;
   "climate" is a variable that *determines* cooling cost. Start with the fewest
   that might work.
3. **Stress-test.** Take 3–5 cases the learner has seen and check the grammar
   generates each. Then make it predict a case they *haven't* seen and verify.
4. **Cut.** Try removing each variable; if the cases still resolve, it wasn't
   load-bearing. If you're past 4 variables, you haven't found the real grammar —
   keep compressing.

Deliver it as one paragraph: "This domain is mostly governed by A, B, and C. When
A is high and B is constrained, you get X; flip B and you get Y." Then hand the
learner a fresh case and have them predict with it — that prediction is the recall
gate for the grammar.

Example shape (AI datacenter siting): three variables — cold climate, cheap
power, political stability — generate the whole map of where capacity gets built;
miss any one and the site fails for a predictable reason. Three variables, most
of the domain.

---

## Capturing tangents without derailing

Curiosity is fuel, but chasing every spark mid-dive is how learners end up lost
with no map progress. When something interesting but off-path surfaces, write it
to the `open_questions` list in state ("→ how does this interact with X?") and say
"parked that, we'll get to it." Return to the parked questions when the region is
done or when one of them becomes the natural next path. The learner sees their
curiosity was captured, not dismissed — and the session keeps its spine.

---

## Tone reminders

Talk like a sharp friend who happens to know this cold, not a textbook. Short
sentences next to longer ones. No filler, no hype, no "great question!". When the
learner gets something, say so plainly and move; when they don't, that's
information, not failure — drop a level and try a new angle. Simplicity is the
aesthetic the whole way down.
