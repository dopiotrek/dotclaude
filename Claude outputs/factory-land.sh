#!/usr/bin/env bash
# One-off: land the agent-factory setup (2026-10-03). Run on your Mac:
#   bash ~/repos/dotclaude/"Claude outputs"/factory-land.sh
# Every step that changes something asks first.
# Run factory-runner.sh FIRST: CI runs on the self-hosted runner.
set -euo pipefail
OWNER=dopiotrek; APPS=~/repos/apps; DOT=~/repos/dotclaude
step(){ printf '\n\033[1m== %s\033[0m\n' "$*"; }
ask(){ read -r -p "$1 [y/N] " a; [[ ${a:-n} == y* ]]; }

step "1/4 Settings: what the live file has that the template lacks"
python3 - <<'EOF'
import json, os
lp = os.path.expanduser("~/.claude/settings.json")
tp = os.path.expanduser("~/repos/dotclaude/settings/settings.template.json")
live, tpl = json.load(open(lp)), json.load(open(tp))
merged = []
for k, v in live.items():
    if k not in tpl:
        tpl[k] = v; merged.append(k)
    elif isinstance(v, dict) and isinstance(tpl[k], dict) and k in ("enabledPlugins", "extraKnownMarketplaces", "skillOverrides"):
        for sk, sv in v.items():
            if sk not in tpl[k]:
                tpl[k][sk] = sv; merged.append(f"{k}.{sk}")
for kind in ("allow", "ask", "deny"):
    extra = sorted(set(live.get("permissions", {}).get(kind, [])) - set(tpl.get("permissions", {}).get(kind, [])))
    if extra:
        print(f"permissions.{kind} only in live (NOT copied — review by hand):", *extra, sep="\n  ")
for kind in ("environment", "allow", "soft_deny", "hard_deny"):
    extra = [e for e in live.get("autoMode", {}).get(kind, []) if e not in tpl.get("autoMode", {}).get(kind, [])]
    if extra:
        print(f"autoMode.{kind} only in live (NOT copied — review by hand):", *extra, sep="\n  ")
print("additive keys only in live:", ", ".join(merged) or "none")
if merged:
    json.dump(tpl, open(tp + ".synced", "w"), indent=2); open(tp + ".synced", "a").write("\n")
    print(f"wrote {tp}.synced with those keys added")
EOF
T=$DOT/settings/settings.template.json
if [ -f "$T.synced" ]; then
  diff -u "$T" "$T.synced" || true
  if ask "Take these additions into the template and commit?"; then
    mv "$T.synced" "$T"
    git -C "$DOT" commit -qm "chore(settings): sync additive keys from live settings" -- settings/settings.template.json
  else rm "$T.synced"; fi
fi
python3 "$DOT/Claude outputs/fix-claude-md-docs.py" && git -C "$DOT" commit -qm "docs(claude-md): Project Docs section points to rules/docs-conventions.md" -- CLAUDE.md 2>/dev/null || true
if ask "Run ./install.sh now (backs up ~/.claude first, then regenerates settings.json)?"; then
  (cd "$DOT" && ./install.sh)
fi

step "2/4 Push dotclaude"
git -C "$DOT" log --oneline origin/main..main || true
ask "Push dotclaude main?" && git -C "$DOT" push origin main

step "3/4 Repos: push branch, open PR (you merge with factory-prs)"
land(){ local dir=$1; shift
  printf '\n-- %s\n' "$dir"
  ask "Land $dir?" || return 0
  cd "$APPS/$dir"
  git push -u origin chore/agent-factory
  gh pr view chore/agent-factory >/dev/null 2>&1 || gh pr create --head chore/agent-factory --base main \
    --title "chore(agents): factory setup" \
    --body "Factory setup from dotclaude. Merge with factory-prs once CI is green."
  echo "   PR open. Free plan: no branch protection, so it is never merged here — use factory-prs."
}
land frontq
land dronelist
land swissCRM
land piotrek-cc
land compass
land tma
land loom
echo
echo "-- ui-registry has no GitHub remote. Merge locally when its working tree is clean:"
echo "   git -C $APPS/ui-registry merge chore/agent-factory"

step "4/4 Left for you"
echo "- Merge the factory PRs with factory-prs once CI is green."
