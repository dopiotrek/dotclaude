# Skills

Reusable procedures Claude Code can run. Each skill is a directory with a
`SKILL.md` (frontmatter + instructions) and optional `references/` and
`scripts/`. `install.sh` symlinks this whole directory to `~/.claude/skills/`,
so these are **user-level** skills available in every project.

## How a skill is invoked

- **By command:** type `/<directory-name>` (e.g. `/clean-comments`). The command
  is the **directory** name, not the `name` field — keep them the same to avoid
  confusion.
- **Automatically:** Claude reads each skill's `description` every turn and loads
  the body when it matches your prompt. Add a `paths` glob to auto-trigger only
  when working with matching files.

Unlike agents (which run in their own context), a skill's body loads into the
current conversation when it runs.

## Frontmatter

| Property                   | Required | Purpose                                                            |
| -------------------------- | -------- | ------------------------------------------------------------------ |
| `name`                     | yes      | Listing label. Keep equal to the directory name.                   |
| `description`              | yes      | When Claude should auto-load it; trigger phrases.                  |
| `paths`                    | no       | Glob(s) that scope auto-activation to matching files.              |
| `allowed-tools`            | no       | Tools pre-approved while the skill is active.                      |
| `disable-model-invocation` | no       | `true` = only you can run it (`/name`), never auto-loaded.          |
| `user-invocable`           | no       | `false` = hidden from the `/` menu; Claude-only background knowledge.|

## Installed skills

Grouped for orientation; run `/` in Claude Code for the live list.

**Stack & dev**

- `ai-sdk` — Vercel AI SDK questions and building AI features (generateText, streamText, tools, useChat).
- `superforms-reference` — sveltekit-superforms + Zod patterns (scoped to Svelte/TS files).
- `svelte-component-architecture` — component decomposition for SvelteKit / Svelte 5.
- `tapforce-shadcn-svelte` — shadcn-svelte setup and usage.
- `tdd-workflow` — enforces test-driven development on test files.
- `turborepo` — Turborepo monorepo build/pipeline/caching guidance.
- `frontend-design` — "Technical Swiss" UI constraints for consistent interfaces.
- `clean-comments` — remove redundant/obvious code comments.
- `playwright-cli` — browser automation for testing, screenshots, scraping.

**SEO & growth**

- `ai-seo` — optimize content to be cited by AI search (AEO / GEO / LLMO).
- `seo-audit` — technical and on-page SEO audit.
- `programmatic-seo` — generate SEO pages at scale from templates + data.
- `find-keywords` — keyword research, difficulty, intent, prioritization.
- `free-tool-strategy` — plan/evaluate/build free tools for lead gen.
- `google-search-console` — analyze GSC data and search performance.
- `web-design-guidelines` — review UI against Web Interface Guidelines.

**Writing & content**

- `deep-dive-burst` — copilot for learning-in-public company deep dives.
- `humanizer` — strip AI-writing tells from text.
- `writing-linkedin-posts` — author engaging LinkedIn posts.
- `twitter-algorithm-optimizer` — optimize tweets for reach.
- `session-mining` — mine session history into content ideas.

**Workflow**

- `agent-handoff` — write a handoff doc so the next agent can continue.
- `tutor` — rigorous tutor that checks you understand before ending.

> A vendored `gstack/` set (the `gstack-*` directories) ships alongside these.
> Treat it as third-party and prune what you don't use.

## Create your own

```
skills/<skill-name>/
├── SKILL.md          # frontmatter + instructions
├── references/       # optional supporting docs
└── scripts/          # optional helper scripts
```

```markdown
---
name: my-skill
description: Use when [scenario]. Triggers on [phrases].
# paths: ["src/**/*.ts"]        # optional: scope auto-activation
# disable-model-invocation: true  # optional: manual-only
---

# My Skill

What it does, the workflow, and examples.
```

Keep one skill single-purpose, give it a specific `description` (that's what
makes auto-activation reliable), and put long reference material in
`references/` so it only loads when the skill runs.
