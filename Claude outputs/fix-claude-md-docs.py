#!/usr/bin/env python3
"""Replace the "Project Docs" section of dotclaude/CLAUDE.md so it matches
rules/docs-conventions.md (the layout the repos actually use)."""
import difflib, os, sys
p = os.path.expanduser("~/repos/dotclaude/CLAUDE.md")
t = open(p).read()
start, end = "## Project Docs (`.docs/`)", "## Deferred Work"
if start not in t or end not in t:
    sys.exit("Section markers not found; edit CLAUDE.md by hand.")
new = """## Project Docs (`.docs/`)

Internal docs go in `.docs/`. The full layout, front matter and life cycle are in `rules/docs-conventions.md`, which loads when you work in `.docs/`. In short: `README.md` routes a task to the right doc, `handoff.md` holds the last session only, then `product/` (what), `decisions/` (why), `engineering/` (how), `specs/` (plan), `research/` (evidence), `reviews/` (`YYYY-MM-DD-slug.md` audits) and `_archive/`. Coding rules live in `.claude/rules/`, never in `.docs/`.

"""
a, b = t.index(start), t.index(end)
out = t[:a] + new + t[b:]
sys.stdout.writelines(difflib.unified_diff(t.splitlines(True), out.splitlines(True), "CLAUDE.md", "CLAUDE.md (new)"))
if input("\nApply? [y/N] ").lower().startswith("y"):
    open(p, "w").write(out); print("CLAUDE.md updated")
