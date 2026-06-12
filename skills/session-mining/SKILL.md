---
name: session-mining
description: Mine Claude Code session history for recurring corrections and turn the friction into a persistent bank of content claim cards about AI-assisted software development. Use whenever the user wants to analyze their coding sessions ("what do I keep correcting", "mine my sessions", "update coding-sessions.md"), asks for content ideas, post topics, or what to write about on X/Twitter or Substack based on their work, wants to refresh or review their idea bank (content-ideas.md), or asks what their sessions reveal about how they work with AI agents — even if they only say "idea machine", "find me something to write about", or "what patterns are in my sessions".
---

# Session Mining: corrections → coding-sessions.md → claim cards

Two-stage pipeline. Stage 1 mines the user's last ~50 Claude Code sessions for corrections they keep making and maintains `coding-sessions.md`. Stage 2 elevates that friction into *claim cards* — arguable, evidence-backed content ideas about AI-assisted software development — and maintains `content-ideas.md`.

The user may ask for one stage or both. "What do I keep correcting?" → Stage 1 only. "What should I write about?" → Stage 2 (run Stage 1 first if `coding-sessions.md` is missing or older than ~2 weeks). Default when ambiguous: run both.

**Files (all live in `~/.claude/mining/`, which is part of a git repo — they're meant to be tracked):**

- `~/.claude/mining/coding-sessions.md` — recurring corrections, merged across runs
- `~/.claude/mining/content-ideas.md` — persistent idea bank with statuses
- `~/.claude/mining/.session-mining-ledger.json` — which session IDs support which pattern (machine state, prevents double-counting)

Never overwrite these wholesale. Read them first, merge new findings in, preserve the user's manual edits and statuses.

## Stage 1 — Mine corrections

### 1. Extract (deterministic)

Run the bundled script — do NOT read raw transcripts yourself; 50 sessions of JSONL would drown the context window, and the script's pre-filter is the point:

```bash
python3 <skill-dir>/scripts/extract_corrections.py --sessions 50 --out /tmp/corrections.json
```

(Use the script's absolute path — your shell's cwd is rarely the skill dir.) If fewer sessions exist than requested, or some project dirs turn out to be inaccessible later, proceed with what's available and state the shortfall in the report rather than stopping.

Flags: `--claude-dir` to override `~/.claude` (used in testing), `--sessions N` for a different window (offer a wider sweep, e.g. 200, if the user says 50 feels shallow). The output contains a `date_range` for the window covered, and per session: session ID, project dir, flagged user messages (`msg`), the tail of the assistant message they were reacting to (`ctx`), and a `kind` (`pattern` regex hit, `interrupt`, `post-interrupt` — a short directive typed right after the user hit Esc, usually the purest correction signal — or `terse-after-action`, a short non-approval reply to an agent action).

Read the JSON output. If it's large, read it in chunks; prioritize `post-interrupt` and `interrupt` hits — they have the best signal-to-noise.

### 2. Cluster (judgment)

The regexes over-trigger by design ("actually", "instead" catch plenty of non-corrections). Your job is to separate true corrections — the user redirecting agent behavior — from ordinary instructions. A correction implies the agent did, or was about to do, something the user didn't want.

Group true corrections into recurring patterns. A pattern is *recurring* when it appears in **2+ distinct sessions**. Name each pattern by the behavior being corrected, not the words used (e.g. "agent uses npm despite pnpm-only rule", not "user says 'use pnpm'"). One-off corrections go to a short "Observed once" list — they're next month's recurring patterns.

### 3. Write coding-sessions.md (merge by session ID, never sum counts)

Mining windows overlap across runs — the same session must never be counted twice. The ledger (`~/.claude/mining/.session-mining-ledger.json`) makes merging idempotent:

```json
{"last_mined": "<date>", "patterns": {"<pattern name>": ["<session-id>", "..."]}}
```

Merge rule: for each pattern, the count is the **size of the union** of ledger session IDs and newly mined session IDs. Update the ledger first, derive every count in coding-sessions.md from it. "Observed once" items go in the ledger too (a one-element list) — that's what makes their later promotion to recurring provable. If the ledger is missing (first run, or user deleted it), rebuild it from this run only and treat existing file counts as historical footnotes, not addends.

Then merge the markdown: append new examples (cap at 4 verbatim examples per pattern, prefer recent), add new patterns, move "Observed once" items up if they recurred. Keep this exact structure:

```markdown
# Coding Sessions — Recurring Corrections

Last mined: <date> · <N> sessions scanned (<from> → <to>) · <M> correction signals

## Recurring corrections

### 1. <behavior-named pattern>   (seen <K>× across <S> sessions · projects: <list>)
- **What happens:** one sentence.
- **Examples:**
  > verbatim user message (trimmed)
- **Candidate CLAUDE.md rule:** one imperative line, or "already covered by: <existing rule>".

## Observed once
- <one-liner each>
```

The **candidate rule** matters: the user's `~/.claude/CLAUDE.md` "Things to Always/Never Do" lists are built from exactly these corrections. Read that CLAUDE.md and check each pattern against it — if a rule already exists and the correction *still* recurs, say so explicitly ("rule exists but isn't holding") instead of proposing a duplicate. That's a more interesting finding than a new rule. Do not edit CLAUDE.md yourself; propose, don't apply.

## Stage 2 — Ideate claim cards

### Sources

Work from, in order of weight:

1. `coding-sessions.md` — the recurring corrections (just produced or already on disk).
2. `project_dirs` from the extraction JSON — for the top 3–5 dirs, run `git -C <dir> log --oneline -n 80` and skim for rework arcs (revert/fix-the-fix chains, the same subsystem touched repeatedly) and shipped-feature themes. Skip dirs that aren't git repos; never run anything but read-only git commands.
3. `.docs/specs/` and `.docs/reviews/` in those same dirs — `ls` them; read at most 2–3 files whose names suggest architecture decisions or review findings.

This grounding step is what separates the output from generic AI-thinkfluencer content: every card must trace back to something that actually happened in the user's sessions, commits, or docs.

### What a claim card is — and the altitude bar

The user writes for X and Substack at the meta level: AI software development, agent architectures, how teams and solo builders will actually work with agents — strategic, but grounded in practice. They argue, they don't explain. A **topic is not an idea**, and a **tool fix is not a claim**.

Every observation sits on an altitude ladder. Cards must live at L2 or L3 — L0/L1 material stays in coding-sessions.md, where it's useful but not publishable:

- **L0 — tool fix:** "agents keep using npm; pin pnpm." A correction. Never a card.
- **L1 — behavior pattern:** "agents regress to training-data defaults under load." An observation. Still not a card — it's a receipt for one.
- **L2 — architecture principle:** "Past ~20 rules, instruction files stop working. Steering agents is environment design — make the wrong action *impossible* (lockfiles, hooks, gates), not forbidden. I'm deleting CLAUDE.md rules and replacing them with failing checks."
- **L3 — industry/strategic claim:** "Solo builders are speedrunning enterprise change management. Everything I learned running SAP governance at scale — gates, audit trails, separation of duties — I now run for an audience of one agent. The org chart got compressed into a pipeline."

Four tests for every card: **(1) Altitude** — is this L2/L3? Would it still matter if the specific tool in the receipts disappeared tomorrow? **(2) Arguable** — could a reasonable, experienced AI-native builder disagree? If not, it's an observation; sharpen or kill. **(3) Receipted** — does the evidence come from the user's own sessions, commits, or docs? "Everyone knows..." kills a card. **(4) Translated** — read only the Claim and Why-now: would a founder or product leader who has never opened an agent config file still care, and understand every noun? Tool artifacts (CLAUDE.md, grep, lockfiles, hooks, specific CLIs) belong in receipts, never in the claim or why-now. Claims name human and organizational concepts — trust, verification, delegation, governance, requirements, cost. A claim that fails translation isn't wrong, it's mis-audienced: reframe it in those terms, or tag its audience honestly and accept the smaller reach.

After L3, always ask one more question: **who beyond people who code with agents does this matter to** — what does it change about how software is bought, staffed, priced, governed? When a claim lands naturally there, pull it there; that's where the user's enterprise background turns a dev observation into a take nobody else can write (e.g. "an agent is a vendor that builds to the signed contract, not the living requirement — and never asks for a change request"). Aim for at least half of each run's cards passing the translation test for the broad founder/product audience.

Elevation is the whole job: climb the ladder explicitly. Correction → what behavior pattern does it instance? → what architecture principle explains the pattern? → what does that principle mean for how software gets built? Stop climbing only when the claim stops being about *the user's tools* and starts being about *how this discipline works*. The corrections are receipts at the bottom of the card — never the claim itself.

One sharpening lens, used sparingly: the user spent ~15 years in enterprise IT (strategic sourcing, HR systems, vendor governance). When an L3 claim genuinely connects agent workflows to enterprise patterns — procurement-style vendor scoring for models, change-management gates, requirements engineering for prompts — that contrast is their unfair angle. Don't force it onto every card.

### 4. Write content-ideas.md (persistent bank)

Read the existing bank first. **Dedupe by claim, not by wording**: if a new claim substantially matches an existing card, strengthen that card with the new receipts and bump its `evidence` line — do not add a near-duplicate. Never change a card's status; statuses belong to the user (`new` → they move to `drafted` / `posted` / `killed`). Never delete or rewrite cards that aren't `new`.

Add 3–7 new cards per run — quality over volume; an empty-handed run ("nothing new cleared the bar") is a valid result, say so. Format:

```markdown
# Content Ideas — Claim Bank

## <short claim title>
- **Status:** new · **Altitude:** L2 | L3 · **Audience:** founders & product leaders | AI-native builders
- **Claim:** one or two sentences, first person, arguable, zero tool nouns.
- **Receipts:** 2–4 bullets of concrete evidence from sessions/commits/docs (anonymize client or company specifics).
- **Why now:** one line — what makes this timely or contrarian.
- **Format:** X post | X thread | Substack essay (pick one primary; a card can note "essay, with an X post as a teaser").
- **Added:** <date> · **Evidence:** <N> sessions / <M> commits
```

Order: `new` cards first (newest at top), then `drafted`, `posted`, `killed` at the bottom.

### 5. Report back

End with a compact summary in chat: top 3 recurring corrections (with counts), how many claim cards were added or strengthened, and the single card you'd lead with — one sentence on why. No full file dumps; the user can open the files.

## Privacy

Transcripts contain client and employer specifics. Verbatim examples in `coding-sessions.md` are fine (the file is private). In `content-ideas.md` receipts, generalize anything identifying a client, employer, or unreleased product — "an enterprise RFP tool" not the client's name.
