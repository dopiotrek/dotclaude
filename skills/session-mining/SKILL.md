---
name: session-mining
description: Mine Claude Code session history for recurring corrections and turn the friction into a persistent bank of content claim cards about AI-assisted software development. Use whenever the user wants to analyze their coding sessions ("what do I keep correcting", "mine my sessions", "update coding-sessions.md"), asks for content ideas, post topics, or what to write about on X/Twitter or Substack based on their work, wants to refresh or review their idea bank (content-ideas.md), or asks what their sessions reveal about how they work with AI agents — even if they only say "idea machine", "find me something to write about", or "what patterns are in my sessions".
---

# Session Mining: corrections → coding-sessions.md → claim cards → drafts

Three-stage pipeline. Stage 1 mines the user's last ~50 Claude Code sessions for corrections they keep making and maintains `coding-sessions.md`. Stage 2 elevates that friction into *claim cards* — arguable, evidence-backed content ideas about AI-assisted software development — and maintains `content-ideas.md`. Stage 3 drafts a tweet from a chosen card using the friction-first structure.

The user may ask for one stage or several. "What do I keep correcting?" → Stage 1 only. "What should I write about?" → Stage 2 (run Stage 1 first if `coding-sessions.md` is missing or older than ~2 weeks). "Draft this / turn this card into a tweet" → Stage 3. Default when ambiguous: run Stage 1 + Stage 2.

**Where the files live — the current repo, not a central one.**

Write to `.docs/mining/` inside the **git root of the current working directory** — the repo the user is actually working in. Resolve it once at the start: `git -C "$PWD" rev-parse --show-toplevel`; the output is `<repo-root>`, and the mining dir is `<repo-root>/.docs/mining/`. Create it if missing. If the cwd is not inside a git repo, fall back to `~/.claude/mining/` and say so in the report. Never assume the path resolves from your shell cwd — always derive `<repo-root>` first.

- `<repo-root>/.docs/mining/coding-sessions.md` — recurring corrections, merged across runs
- `<repo-root>/.docs/mining/content-ideas.md` — persistent idea bank with statuses
- `<repo-root>/.docs/mining/.session-mining-ledger.json` — which session IDs support which pattern (machine state, prevents double-counting)

**Keep the dir out of git.** The extractor scans *all* projects' sessions, so these files can contain verbatim corrections and receipts from other clients and repos. Landing that in a project repo (especially client work) is a cross-client leak. Before writing, make sure `.docs/mining/` is gitignored: if the repo's `.gitignore` doesn't already cover it, append a `.docs/mining/` line. Treat the bank as private working state, not tracked docs.

Each repo keeps its own bank and its own ledger — merging and counts are per-repo, scoped to that location. Never overwrite these wholesale. Read them first, merge new findings in, preserve the user's manual edits and statuses.

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

Mining windows overlap across runs — the same session must never be counted twice. The ledger (`<repo-root>/.docs/mining/.session-mining-ledger.json`) makes merging idempotent:

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

## Stage 3 — Draft (friction-first)

On request only ("draft this", "turn this card into a tweet"). You write here — this skill drafts. But the pain has to be real: only the user knows which friction actually hurt, so draft from the chosen card's receipts and confirm the felt pain rather than inventing it.

**Why the card isn't a tweet yet.** A claim card's Claim line is a statement of fact — true, sharp, and inert. It states the conclusion without the struggle that earned it. On X that dies: nobody reposts a verdict they didn't watch you reach. The fix is to show the pain of the problem before you reveal the cleverness of the solution.

**The four beats** — the spine, not a template to pad:

1. **Hook — the pain.** What was the agent doing wrong *before*? Name the concrete failure the receipts show: the hallucination loop, regressing to npm, inventing a DB schema, claiming "done" on a blank screen. Specific friction, not "AI is unreliable."
2. **The aha.** The reframe that flipped it — e.g. "you don't prompt better, you constrain better." This is the card's L2/L3 claim, finally earned by the pain above it.
3. **The fix — the minuscule task.** How you actually did it, named tools (linter rules, a stop hook, a lockfile). The smaller and more boring the action, the stronger the contrast with the strategic point.
4. **The result.** The payoff in one line — the agent reads its own error and fixes itself before you step in.

**On the altitude bar.** Stage 2 strips tool nouns out of the Claim on purpose. The tweet puts them back — but only in beats 1 and 3 (the pain and the fix). The aha and the result stay at claim altitude. Tools are the texture; the claim is still the point. A draft that's *all* tool mechanics regressed to L0 — pull it back up.

**Pick one angle, don't list all three.** Choose by what the receipts actually support, draft that one, and name your second choice in a single line so the user can swap:

- **Show the friction** — lead with the universal pain every agent user knows (the loop). Best when the receipt is a failure mode lots of people share.
- **Stack-specific** — anchor in the real stack (Svelte 5, Drizzle, Supabase) so it reads as lived, not generic AI-thinkfluencing. Best when the friction is stack-shaped (the model falling back to legacy syntax).
- **Short & punchy** — a contrarian one-liner hook, then 3–4 short lines. Best for a single sharp claim that needs no setup.

**Close by checking the pain, not the polish.** End with the one question only the user can answer: which friction actually happened when you built this? The receipts prove a pattern; they don't tell you which moment stung. Fix the hook to the real one before anything ships. If the user wants reach tuning after the structure is right, hand off to `twitter-algorithm-optimizer` — keep this stage about narrative, not signals.

## Privacy

Transcripts contain client and employer specifics, and the bank now lives inside whatever project repo the user runs from — possibly a client's repo. So the gitignore step above is not optional: `.docs/mining/` must be ignored before you write anything into it.

Verbatim examples in `coding-sessions.md` are fine as long as the dir stays gitignored (the file is local-only). In `content-ideas.md` receipts, still generalize anything identifying a client, employer, or unreleased product — "an enterprise RFP tool" not the client's name — because a card might get copied into a draft or another repo. The cross-project nature of the scan is the risk: receipts mined from khira or swissCRM sessions can surface in a bank stored under dronelist. Never let one client's specifics travel into another client's repo.
