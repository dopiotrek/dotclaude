---
name: test-audit
description: "Invoke whenever writing, changing, reviewing, or sweeping tests. Authoring gate for new tests plus audit workflow for low-value, implementation-coupled, or duplicative tests and the test-only production seams they demand. Triggers: 'audit tests', 'prune tests', 'are these tests useful', 'test cleanup', 'too many tests'."
---

# Test Audit

Adapted from openclaw's `test-audit` skill.

Three modes, one value bar. **Authoring** gates every new or changed test at
write time. **Audit** runs focused sweeps for tests that re-assert source,
duplicate stronger proof, couple to implementation, or keep test-only
production seams alive. **Campaign** prunes one whole subsystem's test surface
(a route group, a package, a feature folder); before starting one, read
[CAMPAIGN.md](CAMPAIGN.md). Optimize for confidence, not deletion count, and
not coverage percentage.

## Authoring gate

Before adding any test, answer four questions. A missing answer means do not
add it yet:

1. What observable behavior, invariant, or independent contract does it protect?
2. What credible regression makes it fail?
3. Why does existing coverage not already catch that failure? Each contract has
   one primary test owner at the strongest boundary (e.g. the `load` function
   or form action, not the helper it calls). Another layer needs its own
   distinct risk. Prefer extending a table-driven case (`it.each`) or shared
   fixture over a near-duplicate test.
4. Does it need a production seam (export, flag, wrapper, injection hook) that
   no production caller needs? If yes, test at the real boundary instead.

Then check it against every [junk pattern](#junk-patterns). A match fails the
gate unless the [retention bar](#retention-bar) names the contract it
independently guards. A test that breaks under behavior-preserving refactoring
asserts implementation, not behavior; rewrite it at the owning boundary.

Bug regression tests must fail on the pre-fix code for the intended reason and
pass after the fix. A regression test that never demonstrably failed proves the
mock, not the fix. One regression at the owner boundary covers the bug; do not
replay it at every layer it crosses.

## Junk patterns

The shared checklist: authoring rejects a new test that matches one, audits
hunt for existing tests that do.

- assertion-free coverage probes (renders without throwing, nothing checked);
- self-comparisons and identity copiers;
- copied fixtures, inventories, manifests, or export lists;
- exact source, import, or string greps;
- private helper or call-shape tests duplicated at the real boundary;
- duplicate invocations of the same contract;
- tests whose only purpose is keeping test-only exports or wrappers alive;
- dead production code whose only callers are tests;
- expected values produced by the helper or renderer under test;
- mocks that implement the asserted behavior (e.g. a mocked Supabase client
  that returns exactly what the assertion checks), or one mock standing in for
  different APIs;
- `toHaveBeenCalledWith` on internals when the observable result could be
  asserted instead;
- snapshot tests nobody reads, of markup with no contract;
- negative controls that pass for an unrelated reason (a different guard
  rejects, or the path is never reached);
- names that promise more than the assertions check.

## Value bar

A test earns its maintenance cost by protecting behavior, a credible
regression, or an independent contract. In an audit, an existing test that
must change for a behavior-preserving refactor is suspect, not automatically
deletable.

Before judging a candidate, read the whole test and its production owner: entry
point, callers, callees, sibling implementations, overlapping tests, and
`git log` for why it exists. Read the root and scoped `CLAUDE.md` first. When a
test claims dependency-backed behavior (Supabase, Drizzle, SvelteKit), check
the dependency's source or types directly.

## Discovery

Keep discovery read-only and report evidence before editing. Prefer a few
high-confidence candidates over a large speculative list. For a wide monorepo
sweep, split lanes by area (`apps/*`, `packages/*`, e2e, a cross-cutting
pattern sweep); use subagents only when the lanes are genuinely independent.

## Retention bar

Keep a test when it independently enforces a public API, schema or migration,
RLS or auth/security rule, config default, form validation contract, route
contract, or package export. Also keep:

- call ordering when order is observable behavior;
- regressions with a credible failure mode;
- source inspection when it is the cheapest independent guard: it fails when
  the contract changes and survives an identifier-only rename;
- a retained test that fails on the baseline: treat it as a possible product
  bug, reproduce it, and fix the owner rather than deleting the test.

Static or slow is not a deletion reason. Prove a test is redundant before
removing it.

## Candidate evidence

Record every field before editing. A missing field means the candidate is not
ready for deletion:

- exact test name and location;
- what failure it can actually detect;
- non-test callers of the covered production seam;
- stronger remaining owner-boundary proof, or why no proof is needed;
- history and the reason the test or seam exists;
- production or test-support code the deletion unlocks;
- risk and the focused validation command.

## Edit shape

Pick one coherent owner-boundary batch. Delete obsolete test-only exports,
wrappers, and dead production paths instead of keeping aliases. Move retained
regressions to their canonical owner. Prefer net-negative production LOC. Do
not add replacement tests that restate the same implementation, and do not
turn uncertain candidates into cleanup to raise the deletion count.

## Validation

Never edit source or tests while Vitest runs in watch mode in the checkout.

1. Run the smallest owner and sibling tests: `pnpm vitest run <path>`
   (or `pnpm turbo test --filter=<pkg>` in a monorepo).
2. For removed source greps, run the script or build that owns the real
   contract.
3. Run the type checker (`pnpm check` / `svelte-check`, or `tsc --noEmit`),
   targeted formatting, then `git diff --check`.
4. Inspect `git diff --numstat`; report production separately from tests and
   test support.

## Landing

Commit or open a PR only when asked. One coherent batch per commit. For a broad
audit, continue in follow-up batches after re-running read-only discovery.

## Handoff

Report briefly:

- removed low-value categories and why;
- production simplifications;
- retained false positives and why they stay;
- validation actually run and its result;
- production vs test LOC;
- follow-ups (append to `TODO.md`).
