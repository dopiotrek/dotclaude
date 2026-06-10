# Content Ideas — Claim Bank

## Rules don't hold. Gates do.

- **Status:** new · **Altitude:** L2
- **Claim:** Past a handful of rules, instruction files stop steering agents — my own corrections prove it. The only rules that ever reached 100% compliance were the ones converted into failing checks. Steering agents is environment design: make the wrong action impossible, not forbidden.
- **Receipts:**
  - Three rules in my global CLAUDE.md ("verify in the running app", "re-grep after sweeps", "treat my numbers as authoritative") are each violated in 2–4 sessions _after_ the rule was written.
  - The one sweep that actually hit 100%: a `/goal` stop hook that blocked the session from ending until every 300-line-limit violation was fixed — produced ~12 clean decompose commits in my finance app, no nagging.
  - Same shape in repo history: two "fix: resolve rules compliance violations from audit" commits — the audit (a check) caught what the rules file (prose) didn't prevent.
- **Why now:** Everyone is bloating CLAUDE.md/AGENTS.md files right now; "my instruction file doesn't work" is a live, unarticulated frustration.
- **Format:** Substack essay, with an X post as a teaser.
- **Added:** 2026-06-10 · **Evidence:** 9 sessions / 14 commits

## Token optimization is a reliability tax

- **Status:** new · **Altitude:** L2
- **Claim:** Every layer that compresses agent context to save tokens — proxy CLIs, summarized tool output, truncated retrieval — trades cost for epistemic reliability, and the trade is asymmetric: a lossy result that drops a match lets the agent assert _absence_, and agents act on absence claims (delete, refactor, conclude "unused") more aggressively than on presence claims. The wrong cheap answer costs more than the expensive right one.
- **Receipts:**
  - My token-compressing CLI proxy produced grep false negatives in two sessions: one corrupted an architecture audit ("superforms is not used" — it is), one nearly removed a form-enhancement directive that was live in production code.
  - Both times the failure mode was the same: zero results → confident negative assertion → downstream action premised on it.
  - I run that proxy precisely because it saves 60–90% of tokens on dev operations — the trade is real, not hypothetical.
- **Why now:** Context-window cost optimization is a whole emerging tool category; nobody is pricing in the wrong-answer rate.
- **Format:** X thread.
- **Added:** 2026-06-10 · **Evidence:** 2 sessions

## The agent's "done" and your "done" are different events

- **Status:** new · **Altitude:** L2
- **Claim:** The agent's definition of done is "the diff is written"; mine is "I watched it work." That gap is where most of my correction traffic lives — which means the productivity frontier in agent coding isn't better generation, it's cheaper verification. Budget the harness that closes the gap (screenshot loops, live-test gates) as part of the task, or you're just moving QA onto your own calendar.
- **Receipts:**
  - Four sessions in a month where "fixed" wasn't: a blank desktop app reported as built, a chart that ignored every input, a scrollbar "hidden" twice that was visible in my screenshot, 193 database rules of which the UI showed one.
  - One shipped feature took six consecutive review-fix commits across two review rounds before the filter logic actually held (cert filter PR in my directory product).
  - My fix: screenshot-verification loops and live-test steps — budgeted as part of the task, not QA afterthought.
- **Why now:** "Agents write 90% of my code" discourse ignores that acceptance testing has silently become the human's full-time job.
- **Format:** Substack essay.
- **Added:** 2026-06-10 · **Evidence:** 5 sessions / 7 commits

## Specs are mutable. Agents treat them as frozen.

- **Status:** new · **Altitude:** L2
- **Claim:** Agent harnesses assume requirements freeze at context-load time; real work has living specs that change mid-session. The standard advice — keep sessions short, don't edit specs while the agent runs — gets the fix backwards: it bends human workflow around an agent limitation. The missing primitive is cache invalidation for context — declare which files are source-of-truth and force a re-read before every generation, because an agent's in-context copy of a spec is a stale cache, not a contract.
- **Receipts:**
  - Three sessions in my writing-workflow project where I updated the governing skill/design file and the agent kept producing artifacts to the old spec — "I updated the skill again… read and redo" is a message I've now sent in three variants.
  - The repo history of that project is mostly spec-refinement commits ("refine playbook", "enhance with clarity and structure") — the spec churns _by design_; the agent's read model doesn't.
- **Why now:** Everyone designs agent harnesses around a static system prompt; nobody talks about requirement drift inside a session.
- **Format:** X post (with essay potential if it resonates).
- **Added:** 2026-06-10 · **Evidence:** 3 sessions / 3 commits

## Enterprise controls were never bureaucracy — my agent workflow re-invented them in weeks

- **Status:** new · **Altitude:** L3
- **Claim:** Within weeks of delegating real work to agents, my solo workflow independently re-grew the controls I spent 15 years around in enterprise IT — dry-run gates before production changes, standing compliance audits, separation of duties between pipelines. Nobody imposed them; they re-emerged from error-correction pressure. That's the strongest evidence I've seen that those controls were never bureaucracy — they're what delegated work requires, and agents are delegated work. What agents kill isn't governance, it's governance latency.
- **Receipts:**
  - Mid-session I type the dry-run commands myself (`db:deploy:dry`, `migration list`) before letting any migration touch production — a manual change-advisory-board of one.
  - My repo has a standing audits directory (security audit, rules compliance, SEO, performance) and commits like "resolve rules compliance violations from audit" — internal audit, rediscovered.
  - My DB stack deliberately separates schema DDL from row-level-security policies into two pipelines that must both move — separation of duties, rediscovered.
  - An agent caught me about to commit `.env` files I believed were ignored — the control worked; the human was the weak link.
- **Why now:** The dominant narrative is that agents remove process; my sessions show process re-emerging from first principles within weeks.
- **Format:** Substack essay, with an X post as a teaser.
- **Added:** 2026-06-10 · **Evidence:** 4 sessions / 6 commits
