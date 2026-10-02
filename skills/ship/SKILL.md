---
name: ship
description: Commit, push and deploy the current project to production, then verify it is live. Use when the user says ship, deploy, release, push to prod, or commit and deploy.
---

1. Read the project's CLAUDE.md for its deploy command (Vercel CLI or Coolify). If none is written, ask once and add it there.
2. Run `git status`. List uncommitted and unpushed changes. Group them into atomic conventional commits. Ask once about anything that looks unrelated.
3. Confirm which environment and database the app points to.
4. Run the type check, lint and tests. Stop on failure and report the output.
5. Commit and push.
6. Deploy with the project's direct command. Do not wait on GitHub Actions.
7. Check the live site: key pages return 200 and the changed feature renders.
8. Report: commits shipped, deploy URL, checks passed or failed, anything not done, and the rollback command.
