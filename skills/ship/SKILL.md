---
name: ship
description: Land the current work. In a factory repo (root `package.json` has a `verify` script) that means branch and PR, left open for Piotrek to merge, never a push to main. Elsewhere, commit, push and deploy to production. Then verify it is live. Use when the user says ship, deploy, release, push to prod, or commit and deploy.
---

1. Check the root `package.json` for a `verify` script. If it has one, this is a factory repo: follow `rules/factory-workflow.md` and the factory steps below. If not, use the direct steps.
2. Run `git status`. List uncommitted and unpushed changes. Group them into atomic conventional commits. Ask once about anything that looks unrelated.
3. Confirm which environment and database the app points to.

## Factory repo

4. Never commit on `main` or in the main checkout. If the work is there, move it to a worktree on its own branch first (in a cloud session, the clone's branch is enough).
5. Run `pnpm verify`. Stop on failure and report the output. Fix the cause; never weaken, skip or delete a check.
6. Commit, then `git push -u origin HEAD`.
7. `gh pr create --fill`. The body says what changed, why, how it was verified, and lists any new migration or env variable.
8. Do not merge. Leave the PR open; Piotrek merges after CI is green. Never run `gh pr merge` (without branch protection it merges at once, CI or not), never push to `main`.
9. Do not deploy by hand. The deploy runs from `main` after the merge. If the PR is already merged and that deploy has finished, check the live site: key pages return 200 and the changed feature renders. Otherwise say the PR is open and stop.
10. Report: commits, PR URL, CI state, checks passed or failed, anything not done, and how to roll back (revert the squash commit through a new PR).

## Other repos

4. Read the project's CLAUDE.md for its deploy command (Vercel CLI or Coolify). If none is written, ask once and add it there.
5. Run the type check, lint and tests. Stop on failure and report the output.
6. Commit and push.
7. Deploy with the project's direct command. Do not wait on GitHub Actions.
8. Check the live site: key pages return 200 and the changed feature renders.
9. Report: commits shipped, deploy URL, checks passed or failed, anything not done, and the rollback command.
