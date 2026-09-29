# Test-pruning campaign

Campaign mode prunes one subsystem's whole test surface in one branch: a
package, a route group, or one feature area. The value bar, retention bar,
candidate evidence, and validation in [SKILL.md](SKILL.md) apply to every lane.
This file adds the order of work. Each step ends on its completion criterion;
do not start the next step early.

Heavy by design: steps 3 and 6 use parallel read-only subagents. Confirm scope
with the user before starting.

## 1. Baseline

Record the subsystem's test and support line counts and every test file's
pass/fail state at a pinned commit SHA. Keep baseline failures in their own
list — they are often real bugs, not stale tests.

Done when every in-scope test file has a recorded baseline result.

## 2. Lanes and inventory

Split the surface into **lanes** along production owner boundaries, not file
names (e.g. auth, data loading, form actions, persistence, UI components,
e2e). Include the subsystem's cases in shared packages and its e2e specs.

Done when every test file the subsystem owns belongs to exactly one lane.

## 3. Read-only ledger per lane

Give each lane to its own read-only agent. It reads every assigned test in
full, including `it.each` tables, plus the production owners, their callers,
and history. Each test declaration goes into a **ledger** with one mark (an
`it.each` is one declaration unless its rows need different marks):

- `R`: retain, naming the contract and the bug it catches;
- `F`: retain the contract but fix the assertion (e.g. a vacuous negative);
- `C`: consolidate, naming the owner that absorbs the assertion;
- `D`: delete, naming the proof that remains, or why no contract exists.

Judge a test by its assertions, not its name.

Done when every declaration in the lane has a mark and an evidence line.

## 4. Layer plan per lane

Treat the ledger as input, not the edit list. A second read-only pass looks for
the redundant **layer**: suites that replay the same logic through a mock
around a stronger real-boundary suite. Name the **keeper** suite per contract.
Prefer the real boundary with a fake network or local Supabase over a mocked
collaborator. Correct ledger errors this pass finds.

Done when each lane plan names retired files, the keeper per contract,
assertions to carry into keepers, and test-only production seams unlocked.

## 5. Cutover

Edit lane by lane. Serialize changes to shared test helpers through one owner.
With each lane, remove the test-only production seams it unlocks (injection
params, getters, reset exports). Update CI config if suites moved. Put durable
test-ownership rules in the subsystem's `CLAUDE.md`, drawn only from mistakes
this campaign actually found.

Done when every lane plan is applied and each lane's keepers pass.

## 6. Preservation review

Before claiming done, compare deleted coverage against the keepers, one
reviewer per boundary group. Look for contracts that lost their only proof and
new assertions that cannot fail.

For each restored contract, make one deliberate **mutation** of the production
owner and confirm the keeper goes red, then restore the source exactly.

Done when every gap is restored or rejected with source evidence, and every
restored contract has a caught mutation.

## 7. Product defects

A baseline failure that survives into a keeper is a bug report. Fix it at its
owner in a separate commit, with a **control** run that reverts the fix and
shows the old failure. Record unrelated issues in `TODO.md` instead of fixing
them in the campaign.

Done when each fixed defect has a failing control and a passing candidate.

## 8. Reconcile and hand off

Merge `main` rather than rebasing a long campaign. When `main` changed a file
the campaign deleted, keep the deletion and port the new contract into the
keeper. Rerun the whole subsystem suite on the merged head.

Hand off with the SKILL.md report, plus: baseline and final line counts
(production separate), lanes and keepers, preservation gaps and their
mutations, and product defects with control proof.
