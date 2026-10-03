# Prompt audit — Claude Code configuration (2026-10-02)

Nothing was edited. Every change below is a proposal.

## Assumptions

- **Target model:** Claude Opus 5.5 (the model this session runs on). The three subagents pin `sonnet` / `opus` aliases; they were audited against the current models behind those aliases.
- **Scope:** configuration that loads into sessions started in `/Users/piotrek/repos`. Paths below are relative to that folder.
- **`~/.claude` is a set of symlinks into `dotclaude/`.** Every edit proposed under `dotclaude/` affects **all projects**.
- **No language or API code in scope.** Group 4 (request config) is not applicable. The subagent roster was checked: three agents, no duplicates.
- **Provenance:** `git blame` was used where a finding needed a date.

### Inventory

| Surface                                                  | Files                 | How it was audited                                                                                        |
| -------------------------------------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------- |
| User-level `CLAUDE.md`, `AGENTS.md`, `RTK.md` (import)   | 3                     | Read in full                                                                                              |
| User-level rules (`dotclaude/rules/`)                    | 4                     | Read in full                                                                                              |
| User-level agents (`dotclaude/agents/`)                  | 4 (3 agents + README) | Read in full                                                                                              |
| User-level skills (`dotclaude/skills/*/SKILL.md`)        | 51                    | Signal greps on all; read in full: `frontend-design`, `agent-browser`, `tdd-workflow`, `ship`, `uiverify` |
| Nested `CLAUDE.md` / `AGENTS.md`                         | 18 in 8 repos         | Read in full (identical copies read once)                                                                 |
| Plugin skills active in this session (`data:*`, `exa:*`) | 12                    | Signal greps only, report only                                                                            |

Not present: project-root `CLAUDE.md`, `CLAUDE.local.md`, `.claude/` at `/Users/piotrek/repos`; ancestor instruction files; commands; output styles; managed-policy `CLAUDE.md`.

Skipped: settings files, `.mcp.json`, `~/.claude.json`, `.env*`; skill reference files (only `SKILL.md` was in scope); nested projects' own `.claude/rules/` and `.claude/skills/`; the rest of the plugin cache (about 1,350 files that are not active in this session).

Imports found: `dotclaude/CLAUDE.md:102` → `RTK.md` (read). `apps/tma/CLAUDE.md` and `apps/tma/AGENTS.md` → `.claude/rules/*.md` (rule files, not audited). `apps/frontq/.docs/product-description/CLAUDE.md:1` → `AGENTS.md` (read).

## Summary

The main problem is **stale facts**, not old-model wording. Sixteen instructions name a file, script, skill or value that the repository contradicts. The worst ones: `apps/dronelist/CLAUDE.md` sends the model to `gstack-*` skills that were deleted; `tdd-workflow` teaches Jest, React and Next.js in a Vitest and SvelteKit stack; `apps/tma/AGENTS.md` describes a module layout that no longer exists and imports a rule file with a misspelled name.

The second problem is **the two engineer subagents**. They are mostly generic skill lists, which `agents/README.md` itself says to cut, and `backend-engineer` carries SvelteKit 1 and superforms v1 examples.

Third, **user-level files and project rules disagree** in six places (RLS, `TODO.md` name, icons, design rules, browser tool, npm). These are flagged only. You have to decide which side wins.

| Group                                     | Findings       |
| ----------------------------------------- | -------------- |
| 1 — Dated prompt text                     | 7              |
| 2 — Brittle skill and configuration files | 29             |
| 3 — Tool / agent descriptions             | 1 (3 files)    |
| 4 — Request config                        | not applicable |

Plugin skills: zero findings by signal.

## Findings — high confidence

All are Group 2 (stale fact or conflict) and are **proposed for you to confirm**, as the facts come from files anyone with commit access can change.

| #   | Location                                                              | Evidence                                                                                       | Why it is wrong                                                                                                                                                         | Action  |
| --- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| H1  | `dotclaude/rules/drizzle-supabase.md:16`                              | "(Parameterized queries and other security rules stay always-on in `CLAUDE.md` …)"             | `CLAUDE.md` has no such rules. The model is told a guard exists that does not.                                                                                          | remove  |
| H2  | `dotclaude/RTK.md:29`                                                 | "Refer to CLAUDE.md for full command reference."                                               | `CLAUDE.md` has no RTK command reference.                                                                                                                               | remove  |
| H3  | `dotclaude/skills/latent-economy/SKILL.md:34`                         | `/Users/piotrek/repos/latent-economy`                                                          | Path does not exist. The repo is at `repos/projects/latent-economy`.                                                                                                    | rewrite |
| H4  | `dotclaude/skills/frontend-design/SKILL.md:12,15`                     | "`/ui-skills`"                                                                                 | The skill is named `frontend-design`. Line dates from 2026-02-01.                                                                                                       | rewrite |
| H5  | `dotclaude/agents/backend-engineer.md:144`                            | `from "sveltekit-superforms/server"`                                                           | `skills/superforms-reference/SKILL.md:115` imports from `sveltekit-superforms`. Two files in the same repo teach different imports.                                     | rewrite |
| H6  | `dotclaude/skills/tdd-workflow/SKILL.md:133-193, 249-314`             | `@testing-library/react`, `jest.fn()`, `NextRequest`, `Button.tsx`, `jest.mock("@/lib/redis")` | `CLAUDE.md:5` says SvelteKit; `skills/test-audit/SKILL.md:128` says Vitest. Examples are the strongest signal in a prompt, so these pull output toward the wrong stack. | remove  |
| H7  | `apps/dronelist/CLAUDE.md:32-34`                                      | "The `gstack-*` skills carry this project's opinionated workflows…"                            | No `gstack-*` skill exists. dotclaude commit `b98827c` removed them.                                                                                                    | remove  |
| H8  | `apps/dronelist/apps/web/CLAUDE.md:7`                                 | "use `NODE_OPTIONS='--max-old-space-size=4096'`"                                               | `apps/web/package.json:14` already sets 8192 inside the `check` script.                                                                                                 | rewrite |
| H9  | `apps/compass/CLAUDE.md:222`                                          | "record it in `TODOS.md`"                                                                      | The file is `TODO.md`. `TODOS.md` does not exist.                                                                                                                       | rewrite |
| H10 | `apps/loom/CLAUDE.md:19-20, 351` and `apps/loom/AGENTS.md` same lines | `scripts/lint-wiki.ts`, `scripts/migrate-wiki.ts`                                              | The files are `.mjs`. `package.json:14` runs `node scripts/lint-wiki.mjs`.                                                                                              | rewrite |
| H11 | `apps/loom/CLAUDE.md:122`                                             | "Stubs get the tag `stub`"                                                                     | Line 132 of the same file says `stub` is never a tag. `wiki/tags.md:69,81` and `AGENTS.md:122` say `status: stub`.                                                      | rewrite |
| H12 | `apps/loom/AGENTS.md:411-418`                                         | `pandoc … --reference-doc=templates/company.pptx`                                              | `templates/company.pptx` does not exist. `templates/lh-master.pptx`, `scripts/md2pptx.py` and the `pptx` script do. `CLAUDE.md` has the current text.                   | rewrite |
| H13 | `apps/tma/AGENTS.md:24`                                               | `@.claude/rules/code-guidlines.md`                                                             | Broken import. The file is `code-guidelines.md`.                                                                                                                        | rewrite |
| H14 | `apps/tma/AGENTS.md:10, 31-33`                                        | "sveltekit-superforms + Zod"; module table with only "Portfolio"                               | superforms is not in `package.json`. There is no `portfolio` module. `CLAUDE.md` (2026-06-05) is newer than `AGENTS.md` (2026-01-28) and is right.                      | rewrite |
| H15 | `apps/swissCRM/CLAUDE.md:209`                                         | "Example: `--system-blue: #007aff`"                                                            | `tokens.css:39` is `#457aae`, and line 225 of the same file says so.                                                                                                    | rewrite |
| H16 | `projects/latent-economy/CLAUDE.md:64`                                | "(`archive/naming.md`)"                                                                        | `archive/` is empty. I cannot tell where the file went.                                                                                                                 | flag    |

## Findings — medium confidence

| #   | Location                                                                                      | Evidence                                                                                                                                                                         | Pattern                                                         | Why                                                                                                                                           | Action                  |
| --- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| M1  | `dotclaude/agents/frontend-engineer.md:4`, `agents/code-reviewer.md:4`, `agents/README.md:93` | Three and two `<example>` dialogues in the `description`; the README template tells authors to add them                                                                          | Group 3 — fake dialogue in a description                        | Descriptions ride in every request. Intent categories route better than sample dialogues. `backend-engineer.md:4` already has the clean form. | rewrite                 |
| M2  | `dotclaude/agents/backend-engineer.md:14-66, 168-176`                                         | "You master: File-based Routing… Load Functions…"; "1. Analyze Requirements 2. Design Data Flow…"                                                                                | Group 2 — explains what the model knows; 1c — step choreography | Generic SvelteKit knowledge. `agents/README.md:123` says to cut exactly this.                                                                 | remove                  |
| M3  | `dotclaude/agents/backend-engineer.md:72-127`                                                 | `throw error(404…)`, `throw redirect(303…)`, `streamed: { comments }`                                                                                                            | 1c — stale examples                                             | SvelteKit 1 idioms. SvelteKit 2 does not throw these and streams top-level promises. The model copies examples.                               | remove                  |
| M4  | `dotclaude/agents/frontend-engineer.md:12-54`                                                 | "You are fluent in: `$state()`…", lists for responsive design, performance, WCAG                                                                                                 | Group 2 — explains what the model knows                         | Only a few lines are project facts (shadcn in `$lib/components/ui`, superforms + Zod, `.svelte.ts` shared state).                             | rewrite                 |
| M5  | `dotclaude/agents/frontend-engineer.md:62, 65`                                                | "No html style tags, only if there is no TailwidCSS class, use a style tag"; "Structure components in `/lib/features/[feature name]/`"                                           | Group 2 — unclear rule; conflict                                | Line 62 is hard to parse. Line 65 disagrees with `skills/svelte-component-architecture/SKILL.md:25` (`lib/components/features/`).             | rewrite                 |
| M6  | `dotclaude/agents/README.md:134`                                                              | "These models narrate more by default."                                                                                                                                          | 1d — stale model claim                                          | Opus 5.5 and Sonnet 5.5 narrate less, not more. An author who follows this adds a "be terse" line that makes agents silent.                   | rewrite                 |
| M7  | `dotclaude/CLAUDE.md:25`                                                                      | "Confirmed 2026-08-27 after a plan I could not follow."                                                                                                                          | Group 2 — history narrative                                     | The rule stands on its own. The incident adds nothing the model can use.                                                                      | rewrite                 |
| M8  | `dotclaude/skills/frontend-design/SKILL.md:54-114`                                            | 29 lines of `MUST` / `NEVER` / `SHOULD` in capitals                                                                                                                              | 1a — pressure language                                          | When every line shouts, no line stands out, and current models over-apply shouted rules.                                                      | rewrite                 |
| M9  | `dotclaude/skills/frontend-design/SKILL.md:104`                                               | "NEVER use `useEffect` for anything that can be expressed as render logic"                                                                                                       | Group 2 — wrong stack                                           | React hook in a Svelte-only setup.                                                                                                            | rewrite                 |
| M10 | `dotclaude/skills/tdd-workflow/SKILL.md:430-432`                                              | "**Remember**: Tests are not optional. They are the safety net…"                                                                                                                 | 1c — padding                                                    | Repeats line 22 as a slogan.                                                                                                                  | remove                  |
| M11 | `dotclaude/skills/uiverify/SKILL.md:18, 20`                                                   | "with the browser MCP tool"; "Use the JS-eval tool"                                                                                                                              | Group 2 — conflict                                              | `CLAUDE.md:64` says to use the `agent-browser` CLI, not an MCP tool.                                                                          | rewrite                 |
| M12 | `apps/swissCRM/CLAUDE.md:14, 47-52, 54, 59-63, 136-140`                                       | "Vercel served it until 2026-09-10"; "is now a second working path (fixed 2026-09-11 — 88/88 files…)"; "the `:remote` family was deleted on 2026-09-11, because…"                | 1d — migration-relative phrasing; Group 2 — history             | The text describes a diff against an older setup the model never saw. It hints at alternatives that no longer exist.                          | rewrite                 |
| M13 | `apps/swissCRM/CLAUDE.md:123-127`                                                             | "the GitHub Actions allowance ran out on 2026-09-10 and every workflow fails in seconds until it resets"                                                                         | Group 2 — time-sensitive                                        | The allowance resets monthly, so this is probably already false. I did not check.                                                             | rewrite (confirm first) |
| M14 | `projects/latent-economy/CLAUDE.md:48-57, 85`                                                 | "Locked 2026-07-14"; "(2026-07-15, replaces the territory limit)"; "This supersedes the constitution's narrower one-paragraph rule; the old TODO territory tension is resolved." | 1d — migration-relative phrasing                                | Same as M12. State the current rule only.                                                                                                     | rewrite                 |
| M15 | `apps/loom/CLAUDE.md:47` and `AGENTS.md:47`                                                   | "The five theme folders (`governance/`, `products/`, `regulatory/`, `strategy/`, plus `summaries/`, `briefings/`)"                                                               | Group 2 — self-contradiction                                    | Lists six names and calls them five. Four are theme folders, two are structural.                                                              | rewrite                 |

## Flags — no edit proposed

**User-level file against a project file. You decide which side wins.**

- **F1** `dotclaude/rules/drizzle-supabase.md:12` "New table → add Row Level Security" against `apps/swissCRM` and `apps/compass` `tenant-isolation.md` "CRITICAL: no RLS". The user-level rule loads in both repos when a schema file is open.
- **F2** `dotclaude/CLAUDE.md:98` "Every project keeps a root `TODO.md`" against `apps/swissCRM/CLAUDE.md:277`, which uses `TODOS.md` (that file exists).
- **F3** `dotclaude/skills/frontend-design/SKILL.md:21-50, 77, 93, 111`: lime accent, Geist Mono, "aesthetic connection to drones", "never add animation unless requested", Tailwind default shadows. This is dronelist's design language in a skill that loads everywhere. swissCRM and compass rules say the opposite on colour, font, motion and shadows.
- **F4** `dotclaude/agents/frontend-engineer.md:61, 68-74`: Tabler icons and tokens such as `bg-bg-1-secondary`. swissCRM allows only Phosphor. The tokens belong to one project.
- **F5** `apps/tma/CLAUDE.md:64-83` and `apps/tma/AGENTS.md:43-62` describe `scripts/browser-tools.ts`. `dotclaude/CLAUDE.md:64` says to use `agent-browser`. Neither file says which one to use in tma.
- **F6** `apps/dronelist/…/product-tour/CLAUDE.md:40-49` and the `niche-vs-experience-motion` copy use `npm run` and `npx`. `dotclaude/CLAUDE.md:6` says pnpm only. The scripts really are pinned `npx` calls, so this looks like a fair local exception, but nothing says so.

**History cannot show which side is current.**

- **F7** `apps/loom/CLAUDE.md:294` "Which articles exceed 150 lines and should be split?" against `:161-162` "Target ~200–400 lines; split pages exceeding ~500". Same file, same commit. Pick one number.
- **F8** `product-tour/CLAUDE.md:105` "Videos use `muted` with a separate `<audio>`" against the newer copy in `niche-vs-experience-motion/CLAUDE.md:105` and `dotclaude/skills/general-video/SKILL.md:67` ("the sound stays on the clip"). The older project pins CLI 0.8.104, so its rule may be right for that version.

**Low confidence or outside the patterns.**

- **F9** `dotclaude/CLAUDE.md:19` "at most one short sentence before the first tool call, then stay quiet until done". This matches the "update suppressor" pattern, and on Opus 5.5 it can mean long silent stretches. It is recent (2026-08-23), it is your stated preference, and it already says when to speak. Kept.
- **F10** `dotclaude/agents/code-reviewer.md:8, 18`: `isolation: worktree` plus "Create a review file in `.docs/reviews/`". The report is written inside the temporary worktree, not your checkout. Check that reviews land where you expect.
- **F11** `dotclaude/AGENTS.md:5` "Claude Code reads `CLAUDE.md` in this repo instead." This session loaded `~/.claude/AGENTS.md` as well, so its browser and tooling rules arrive twice. The copies agree, so no harm.
- **F12** `apps/tma/CLAUDE.md:46-52`: the module table lists five modules. `chat`, `simulations` and `vehicles` also exist.
- **F13** `dotclaude/RTK.md:14-22`: install checks written for a person, loaded into every session. The file looks tool-generated, so an edit may be overwritten.
- **F14** Seen while reading, out of scope: `apps/tma/.claude/rules/code-guidelines.md` §3.1 says state lives in "stores (`$lib/stores`)", which conflicts with the runes-only rule and with its own §5.

## Proposed diff

One finding per hunk. Take any hunk alone. Hunks marked ⚠ affect all projects.

### H1 ⚠ `dotclaude/rules/drizzle-supabase.md`

```diff
@@ -14,3 +14 @@
 - Follow the existing schema conventions (`_meta.ts` base types, shared timestamps, id config) instead of inventing new ones.
-
-(Parameterized queries and other security rules stay always-on in `CLAUDE.md` — they apply to query code too, not just schema files.)
```

### H2 ⚠ `dotclaude/RTK.md`

```diff
@@ -27,3 +27 @@
 Example: `git status` → `rtk git status` (transparent, 0 tokens overhead)
-
-Refer to CLAUDE.md for full command reference.
```

### H3 ⚠ `dotclaude/skills/latent-economy/SKILL.md`

```diff
@@ -34 +34 @@
-/Users/piotrek/repos/latent-economy
+/Users/piotrek/repos/projects/latent-economy
```

### H4 ⚠ `dotclaude/skills/frontend-design/SKILL.md`

```diff
@@ -12,4 +12,4 @@
-- `/ui-skills`
+- `/frontend-design`
   Apply these constraints to any UI work in this conversation.

-- `/ui-skills <file>`
+- `/frontend-design <file>`
```

### H5 ⚠ `dotclaude/agents/backend-engineer.md`

```diff
@@ -144 +144 @@
-import { superValidate } from "sveltekit-superforms/server";
+import { superValidate } from "sveltekit-superforms";
```

### H6 ⚠ `dotclaude/skills/tdd-workflow/SKILL.md`

```diff
@@ -131,63 +131,2 @@
 ## Testing Patterns

-### Unit Test Pattern (Jest/Vitest)
-  … lines 133-159: React Testing Library + jest.fn() Button example …
-### API Integration Test Pattern
-  … lines 161-193: NextRequest route-handler example …
@@ -249,66 +188 @@
-## Test File Organization
-  … lines 249-270: Button.tsx / app/api/markets/route.ts tree …
-## Mocking External Services
-  … lines 272-314: jest.mock() for Supabase, Redis, OpenAI …
```

The Playwright pattern (lines 195-247) stays. It is valid for the stack.

### H7 `apps/dronelist/CLAUDE.md`

```diff
@@ -32,4 +31 @@
-## Skills
-
-The `gstack-*` skills carry this project's opinionated workflows. Reach for them when the task fits: `gstack-ship` (ship/deploy/PR), `gstack-investigate` (bugs, 500s), `gstack-qa`, `gstack-review`, `gstack-design-review` (visual polish), `gstack-office-hours` (is this worth building). Answering a quick question directly is fine.
-
```

### H8 `apps/dronelist/apps/web/CLAUDE.md`

```diff
@@ -7 +7 @@
-- `pnpm check` is memory hungry — use `NODE_OPTIONS='--max-old-space-size=4096'`
+- `pnpm check` is memory hungry — the script sets an 8 GB heap itself, so run it through `pnpm`, not `svelte-check` directly
```

### H9 `apps/compass/CLAUDE.md`

```diff
@@ -222 +222 @@
-important work intentionally not done now — record it in `TODOS.md` at the repo
+important work intentionally not done now — record it in `TODO.md` at the repo
```

### H10 `apps/loom/CLAUDE.md` and `apps/loom/AGENTS.md` (same three lines in each)

```diff
@@ -19,2 +19,2 @@
-scripts/lint-wiki.ts            Structural + frontmatter enforcement. Run after every batch.
-scripts/migrate-wiki.ts         One-shot migration script (reference only, already executed).
+scripts/lint-wiki.mjs           Structural + frontmatter enforcement. Run after every batch.
+scripts/migrate-wiki.mjs        One-shot migration script (reference only, already executed).
@@ -351 +351 @@
-`scripts/lint-wiki.ts` is the authoritative structural checker. Run it after every ingest batch, every restructure, and any time you suspect drift.
+`scripts/lint-wiki.mjs` is the authoritative structural checker. Run it after every ingest batch, every restructure, and any time you suspect drift.
```

### H11 `apps/loom/CLAUDE.md` (line 98 also in `AGENTS.md`)

```diff
@@ -98 +98 @@
-status: open | in-progress | blocked | done
+status: open | in-progress | blocked | done | stub
@@ -122 +122 @@
-- Stubs get the tag `stub`
+- Stubs get `status: stub` (not a tag)
```

### H12 `apps/loom/AGENTS.md`

````diff
@@ -411,8 +411,8 @@
-For formal presentations using the company's `.pptx` template, use pandoc:
+For formal presentations using the company's `.pptx` template:

 ```bash
-# Convert markdown to .pptx using company template
-pandoc wiki/my-deck.md -o output.pptx --reference-doc=templates/company.pptx
+pnpm pptx wiki/my-deck.md
+# Output: wiki/my-deck.pptx
````

-The template lives at `templates/company.pptx`. Pandoc copies master slides, fonts, colors, and layouts from it. Slide format uses heading levels:
+The template lives at `templates/lh-master.pptx`. The script (`scripts/md2pptx.py`) builds slides from markdown with the template's own layouts. Slide format uses heading levels:
@@ -440 +440 @@
-Use **Marp** for quick internal decks and previews. Use **pandoc + company template** for external/formal presentations.
+Use **Marp** for quick internal decks and previews. Use **pnpm pptx** for external/formal presentations with company branding.

````

The `::: notes` block at `AGENTS.md:435-437` is pandoc syntax. Remove it in the same edit.

### H13 + H14 `apps/tma/AGENTS.md`

```diff
@@ -10 +10 @@
-- **Forms**: sveltekit-superforms + Zod
+- **Forms**: Zod validation schemas
@@ -24 +24 @@
-- @.claude/rules/code-guidlines.md — Guidlines for coding
+- @.claude/rules/code-guidelines.md — Coding guidelines
@@ -31,3 +31,7 @@
-| Module        | Purpose                                                 |
-| ------------- | ------------------------------------------------------- |
-| **Portfolio** | Assets, accounts, transactions, prices — _what you own_ |
+| Module          | Purpose                                               |
+| --------------- | ----------------------------------------------------- |
+| **banking**     | Bank accounts, balances, transactions                 |
+| **core**        | Shared foundations — currencies, tags, CSV import     |
+| **investments** | Brokerage accounts, assets, positions, prices         |
+| **net-worth**   | Cross-module aggregation into a single financial view |
+| **retirement**  | Pension accounts and projections                      |
````

### H15 `apps/swissCRM/CLAUDE.md`

```diff
@@ -209 +209 @@
-1. **`packages/ui/src/styles/tokens.css`** — raw CSS custom properties, all values terminate at static hex/values. Example: `--system-blue: #007aff`. Defines both Light (`:root`) and Dark (`.dark`) values for every chromatic token.
+1. **`packages/ui/src/styles/tokens.css`** — raw CSS custom properties, all values terminate at static hex/values. Example: `--system-blue: #457aae`. Defines both Light (`:root`) and Dark (`.dark`) values for every chromatic token.
```

### M1 ⚠ agent descriptions

`dotclaude/agents/frontend-engineer.md`

```diff
@@ -3,2 +3,2 @@
 description: >
-  Use this agent when you need to create, modify, or optimize Svelte 5 components … Examples: <example>…</example> <example>…</example> <example>…</example>
+  Use this agent to create, modify, or optimize Svelte 5 (runes) components: shadcn-svelte UI, responsive layouts, client-side state, accessibility, and frontend performance problems.
```

`dotclaude/agents/code-reviewer.md`

```diff
@@ -3,2 +3,2 @@
 description: >
-  Use this agent proactively when you need comprehensive code review and quality assurance. Use after writing or modifying code. Examples: <example>…</example> <example>…</example>
+  Use this agent proactively after writing or modifying code, and before shipping, for a ranked security and quality review. It writes a dated report to `.docs/reviews/`.
```

`dotclaude/agents/README.md`

```diff
@@ -93 +93 @@
-description: Use this agent when... Examples: <example>user: "..." assistant: "I'll use my-agent..."</example>
+description: Use this agent to… (what it does and when to pick it — no sample dialogues)
```

### M2 + M3 ⚠ `dotclaude/agents/backend-engineer.md`

```diff
@@ -12,116 +12,5 @@
-You are an expert SvelteKit backend engineer specializing in server-side architecture and full-stack development patterns. Your deep expertise spans file-based routing, load functions, form actions, hooks, middleware, and adapter configuration.
-
-## Core Expertise
-  … lines 14-66: expertise list, five-step "Implementation Approach", four heading-only topic lists …
+You are a SvelteKit backend engineer working in a SvelteKit 2 + Drizzle + Supabase codebase.
+
 ## Code Patterns You Follow

 - use $lib/\* alias for imports
-
-**Load Functions:** … lines 72-99 …
-**Form Actions:** … lines 101-127 …
@@ -168,10 +57,5 @@
 ## Best Practices You Enforce

 - **Progressive Enhancement**: Forms work without JavaScript, then enhance with client-side features
-- **Svelte superForms**: Setup correct handling of superforms
-- **Type Safety**: …
-- **Error Boundaries**: …
-- **Security First**: …
-- **Performance**: …
-- **SEO Optimization**: …
```

The superforms example (lines 129-166, with H5 applied) stays. It encodes a library choice.

### M4 + M5 ⚠ `dotclaude/agents/frontend-engineer.md`

```diff
@@ -12,43 +12,9 @@
-You are an expert Svelte 5 frontend developer specializing in … frontend optimization techniques.
-
-**Core Responsibilities:**
-  … lines 16-54: six numbered responsibility lists …
+You are a Svelte 5 frontend engineer. Runes only.
+
+**What this codebase does:**
+
+- shadcn-svelte is the component library. Check `$lib/components/ui` before you build a custom component
+- Shared state lives in `.svelte.ts` modules that export runes-backed state
+- Forms use sveltekit-superforms with Zod validation
+- Mobile-first layouts; WCAG 2.1 AA
@@ -62 +28 @@
-- No html style tags, only if there is no TailwidCSS class, use a style tag
+- Style with Tailwind classes. Use a `<style>` block only when no Tailwind class can express it
@@ -65 +31 @@
-- Structure components in `/lib/features/[feature name]/` directory
+- Follow the component folder layout the project already uses
```

### M6 ⚠ `dotclaude/agents/README.md`

```diff
@@ -134,3 +134,3 @@
-5. **State the reporting shape.** These models narrate more by default. If you
-   want terse, say so — and say what a good update looks like rather than
-   listing what to avoid. Positive examples land better than prohibitions
+5. **State the reporting shape.** Say what a good update looks like and when
+   you want one, rather than listing what to avoid. Positive examples land
+   better than prohibitions
```

### M7 ⚠ `dotclaude/CLAUDE.md`

```diff
@@ -25 +25 @@
-This is the shape I want, every time. Confirmed 2026-08-27 after a plan I could not follow.
+This is the shape I want, every time.
```

### M8 + M9 ⚠ `dotclaude/skills/frontend-design/SKILL.md`

Apply the same change to every bullet in lines 54-114: drop the capital keyword and state the rule plainly. `MUST x` → `Use x`. `NEVER x` → `Don't x`. `SHOULD x` → `Prefer x`. Sample:

```diff
@@ -54,3 +54,3 @@
-- MUST use Tailwind CSS defaults unless custom values already exist or are explicitly requested
-- SHOULD use `tw-animate-css` for entrance and micro-animations in Tailwind CSS
-- MUST use `cn` utility (`clsx` + `tailwind-merge`) for class logic
+- Use Tailwind CSS defaults unless custom values already exist or are explicitly requested
+- Prefer `tw-animate-css` for entrance and micro-animations in Tailwind CSS
+- Use the `cn` utility (`clsx` + `tailwind-merge`) for class logic
@@ -104 +104 @@
-- NEVER use `useEffect` for anything that can be expressed as render logic
+- Don't use `$effect` for anything `$derived` can express
```

### M10 ⚠ `dotclaude/skills/tdd-workflow/SKILL.md`

```diff
@@ -428,5 +428 @@
 - Tests catch bugs before production
-
----
-
-**Remember**: Tests are not optional. They are the safety net that enables confident refactoring, rapid development, and production reliability.
```

### M11 ⚠ `dotclaude/skills/uiverify/SKILL.md`

```diff
@@ -18 +18 @@
-2. Navigate to the affected route(s) with the browser MCP tool (see the root `CLAUDE.md` Browser Automation section for which one to use).
+2. Navigate to the affected route(s) with `agent-browser` (see the Browser Automation section of `~/.claude/CLAUDE.md`).
@@ -20 +20 @@
-4. Use the JS-eval tool to read `getBoundingClientRect()` and `getComputedStyle()` …
+4. Evaluate JavaScript in the page to read `getBoundingClientRect()` and `getComputedStyle()` …
```

### M12 `apps/swissCRM/CLAUDE.md`

```diff
@@ -13,2 +13,2 @@
 - `apps/web` — SvelteKit app (`@swisscrm/web`), deployed as a Docker image to a
-  Hetzner box via Coolify (`pnpm ship`). Vercel served it until 2026-09-10
+  Hetzner box via Coolify (`pnpm ship`)
@@ -47,6 +47,4 @@
-`pnpm db:migrate` on an empty database is now a second working path (fixed
-2026-09-11 — 88/88 files apply to stock Postgres, and it needs no `pg_trgm`
-pre-step because 0022 creates the extension itself, where `db:push` reaches the
-`gin_trgm_ops` indexes without one). Use `db:push` when you are iterating on the
-schema definition; use `db:migrate` when you want the database a recovery would
-produce.
+`pnpm db:migrate` on an empty database also works, with no `pg_trgm` pre-step
+(0022 creates the extension). Use `db:push` when you are iterating on the
+schema definition; use `db:migrate` when you want the database a recovery
+would produce.
@@ -54 +52 @@
-**Migration lifecycle** (regularized 2026-06-11): `packages/db/src/migrations/*.sql`,
+**Migration lifecycle**: `packages/db/src/migrations/*.sql`,
@@ -59,5 +57,3 @@
-(wipe + rebuild) — do not use them against production. **Every `db:*` command is
-local, and there is no remote variant of any of them** — the `:remote` family was
-deleted on 2026-09-11, because after the database cutover it could only reach the
-paused Supabase copy. Production migrates itself: the container applies the ledger
-before it serves. Schema
+(wipe + rebuild) — do not use them against production. **Every `db:*` command is
+local, and there is no remote variant of any of them.** Production migrates
+itself: the container applies the ledger before it serves. Schema
@@ -136,5 +132,3 @@
-- `.env.remote` — the **paused Supabase rollback copy**, not production since
-  the 2026-09-10 cutover. **Never loaded by Vite** (not a recognized Vite env
-  file name — deliberate), and since 2026-09-11 **read by nothing at all**: its
-  only consumers were the `db:*:remote` scripts, which were deleted. Delete the
-  file with the Supabase project. Production runtime env lives in Coolify.
+- `.env.remote` — credentials for the paused Supabase rollback copy, **not
+  production**. Nothing reads it. Delete it together with the Supabase
+  project. Production runtime env lives in Coolify.
```

### M13 `apps/swissCRM/CLAUDE.md` — confirm that CI works again before taking this

```diff
@@ -123,5 +123,3 @@
-- **The gate that actually runs is `pnpm verify`** (lint, format:check, check,
-  knip, test), because the GitHub Actions allowance ran out on 2026-09-10 and
-  every workflow fails in seconds until it resets. `pnpm ship` runs it first.
-  Note it does **not** run `build` — a bundle-size or adapter regression is not
-  caught locally.
+- **Local gate: `pnpm verify`** (lint, format:check, check, knip, test).
+  `pnpm ship` runs it first. It does **not** run `build` — a bundle-size or
+  adapter regression is not caught locally.
```

### M14 `projects/latent-economy/CLAUDE.md`

```diff
@@ -48,10 +48,8 @@
-**Locked 2026-07-14 — the master worldview:** the lane is the _pattern_, not a
-topic ("latent patterns in economic systems," `brand.md` → Positioning). The
-brain (2026-07-15) completes it with three levels: the main question (idea
-engines), the core claim (put numbers on hidden value; show the release),
-and the goal (a world that stops wasting people).
-**History must end in the present (2026-07-15, replaces the territory limit):**
-history and other geographies enter as data — named mechanisms, real numbers,
-never as decoration — and every piece must land on something happening now
-(brain §3). This supersedes the constitution's narrower one-paragraph rule;
-the old TODO territory tension is resolved.
+**Locked — the master worldview:** the lane is the _pattern_, not a topic
+("latent patterns in economic systems," `brand.md` → Positioning). The brain
+adds three levels: the main question (idea engines), the core claim (put
+numbers on hidden value; show the release), and the goal (a world that stops
+wasting people).
+**History must end in the present:** history and other geographies enter as
+data — named mechanisms, real numbers, never as decoration — and every piece
+must land on something happening now (brain §3).
@@ -85 +83 @@
-- **The ladder doesn't relax this** (brain §4a, added 2026-07-17): an idea may
+- **The ladder doesn't relax this** (brain §4a): an idea may
```

### M15 `apps/loom/CLAUDE.md` and `apps/loom/AGENTS.md`

```diff
@@ -47 +47 @@
-- The five theme folders (`governance/`, `products/`, `regulatory/`, `strategy/`, plus `summaries/`, `briefings/`) are the complete allowed set. Don't invent new subfolder names.
+- The four theme folders (`governance/`, `products/`, `regulatory/`, `strategy/`) plus `summaries/` and `briefings/` (and `people/` in the shared wiki) are the complete allowed set. Don't invent new subfolder names.
```

## Before applying

- Grep for any removed text first. A hook or a test may match on it.
- H6, M2, M3, M4 and M8 change behaviour, not only facts. Take them one at a time and watch the next few sessions.
- No behavioural probes were run. The high-confidence findings were checked against the repositories; the medium ones rest on documented model behaviour.
