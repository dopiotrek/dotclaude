# Scripts

Utility scripts for Claude Code that extend functionality beyond hooks/agents/skills.

## Included Scripts

### file-suggest.sh

Custom file suggestion script using `rg` + `fzf` for fast fuzzy matching.

**Features:**

- Respects `.gitignore`
- Includes hidden files
- Follows symlinks
- Returns relative paths

**Requirements:**

- `rg` (ripgrep)
- `fzf`
- `jq`

**Configuration:**

Add to `settings.json`:

```json
{
  "fileSuggestion": {
    "type": "command",
    "command": "$HOME/.claude/scripts/file-suggest.sh"
  }
}
```

**Usage:**

The script receives JSON input with a `query` field and returns matching file paths:

```bash
echo '{"query": "component"}' | ./file-suggest.sh
# Returns: src/components/Button.svelte, src/components/Card.svelte, ...
```

## Adding New Scripts

1. Create your script in this directory
2. Make it executable: `chmod +x scripts/my-script.sh`
3. Configure in `settings/settings.template.json` if needed
4. Re-run `./install.sh` to regenerate settings

## factory-sync

Copies the shared rules (`rules/`), `factory/core.md` and the guard hooks into
each factory repo's `.claude/` folder, so cloud and dispatched agents get them
too. Run it after you change a shared rule or hook, then commit in each repo.
`factory-sync --check` exits 1 when a repo is out of date.

## factory-prs

Lists open PRs in every repo under `~/repos/apps` with their CI state
(green / running / red) and offers to merge the green ones (squash, delete
branch; `d` shows the diff first). Agents never merge; this is how you do.
