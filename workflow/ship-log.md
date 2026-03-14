# Ship Log

Before finishing any non-trivial task, append an entry to `.claude/logs/ship-log.md`. This replaces the old build-log and lessons files. Used for content creation — tweets, blog posts, changelogs.

**Two entry types:**

🚀 **Ship entries** — when you build/fix/ship something worth talking about:
```
## YYYY-MM-DD | 🚀 Category: Short title

**Ship it:** One paragraph — what was built and why it matters.

**The insight:** The reusable takeaway worth sharing.

**Tweet draft:** A tweet-ready summary. Build-in-public style. Include a hook.

**Tags:** comma, separated, tags
```

💡 **Lesson entries** — when something breaks or you learn something new (auto-logged by hook, but you can write these manually too):
```
## YYYY-MM-DD | 💡 Lesson: What went wrong

**What broke:** The failure and its impact.

**Rule:** The rule to follow going forward.

**Tags:** comma, separated, tags
```

**Quality bar for ship entries:**
- Skip: running type checks, installing deps, fixing typos, formatting
- Log: new features, architectural decisions, performance wins, DX improvements, clever solutions
- Ask yourself: "Would someone building a SaaS with AI tools find this interesting?"

**Quality bar for lessons:**
- Skip: same error repeating, trivial typos
- Log: novel failure patterns, surprising behaviors, rules worth remembering

Categories for 🚀: Feature, Fix, Refactor, Infrastructure, Performance, DX, Design.
