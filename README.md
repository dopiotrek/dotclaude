# dotclaude

> Claude Code agentic framework - hooks, agents, skills, and configuration

A comprehensive, shareable configuration framework for [Claude Code](https://claude.ai/download) that provides automated guardrails, specialized agents, reusable skills, and sensible defaults for productive AI-assisted development.

## What's Included

| Component     | Count | Description                                                    |
| ------------- | ----- | -------------------------------------------------------------- |
| **Hooks**     | 13    | Automated guardrails for security, formatting, and validation  |
| **Agents**    | 9     | Specialized task handlers (frontend, backend, debugging, etc.) |
| **Skills**    | 4     | Reusable skill definitions with reference materials            |
| **Settings**  | 1     | Comprehensive permission rules and hook configuration          |
| **CLAUDE.md** | 1     | Global preferences and instructions                            |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/dopiotrek/dotclaude.git ~/repos/dotclaude

# Run the installer (creates symlinks)
cd ~/repos/dotclaude
./install.sh

# Start a new Claude Code session
claude
```

The installer creates symlinks from `~/.claude` to this repository, making it the single source of truth. Any changes you make here automatically apply to Claude Code.

### Installation Options

```bash
./install.sh            # Default: symlink mode (recommended)
./install.sh --copy     # Copy files instead of symlinks
./install.sh --uninstall  # Remove symlinks and optionally restore backup
```

## Hooks

Hooks are Python scripts that run before/after Claude Code tool invocations, providing automated guardrails:

### Security & Safety

- **no-secrets.py** - Blocks hardcoded API keys, tokens, and passwords
- **permission-auto-approve.py** - Auto-approves safe read-only operations
- **bash-command-validator.py** - Enforces use of modern CLI tools (rg over grep)

### Code Quality

- **auto-format.py** - Auto-formats code after edits (Prettier, Black, etc.)
- **import-path-validator.py** - Enforces import conventions ($lib, package imports)
- **sveltekit-route-validator.py** - Validates SvelteKit routing conventions
- **sveltekit-perf-guard.py** - Monitors bundle size and performance anti-patterns

### Database & Migrations

- **drizzle-migration-guard.py** - Warns about destructive schema changes
- **supabase-rls-reminder.py** - Reminds to add Row Level Security policies

### Utilities

- **command-logger.py** - Logs all Claude Code operations for audit
- **dependency-audit.py** - Runs security audits when dependencies change
- **stop-verification.py** - Runs type checks when Claude completes work
- **web-search-enhancer.py** - Adds current year to tech documentation searches

See [hooks/README.md](hooks/README.md) for detailed documentation.

## Agents

Specialized agents handle complex, domain-specific tasks:

| Agent                        | Model  | Purpose                                               |
| ---------------------------- | ------ | ----------------------------------------------------- |
| **frontend-engineer**        | sonnet | Svelte 5 components, shadcn-svelte, responsive design |
| **backend-engineer**         | sonnet | SvelteKit server-side, load functions, form actions   |
| **superforms-expert**        | sonnet | sveltekit-superforms + Zod validation                 |
| **debug-specialist**         | sonnet | Error diagnosis, test failures, performance issues    |
| **code-reviewer**            | opus   | Comprehensive security and quality review             |
| **discovery-agent**          | sonnet | Requirements gathering and feature specification      |
| **vercel-deployment-expert** | sonnet | Vercel deployment and configuration                   |
| **seo-expert**               | sonnet | Content structure and SEO optimization                |
| **mobile-ui-designer**       | sonnet | Mobile-first UI design with TailwindCSS               |

See [agents/README.md](agents/README.md) for detailed documentation.

## Skills

Skills are reusable task definitions with supporting reference materials:

- **clean-comments** - Remove unnecessary code comments
- **code-reviewer** - Code review with checklists and analysis scripts
- **frontend-design** - UI constraints for consistent design
- **svelte-component-architecture** - Component decomposition guidelines

See [skills/README.md](skills/README.md) for detailed documentation.

## Configuration

### CLAUDE.md

Global preferences and instructions that apply to all Claude Code sessions:

```markdown
# Global Claude Preferences

## About Me

- Primary stack: SvelteKit, TypeScript, Supabase
- All projects use pnpm (never npm or yarn)

## Things to Always Do

- Run type checks before considering work complete
- Preserve existing code style in files being edited
- Use existing patterns from the codebase
  ...
```

### Settings

The `settings/settings.template.json` contains:

- **Permissions** - Fine-grained allow/deny/ask rules
- **Hooks** - Hook configuration for each event type
- **Model** - Default model preference
- **Plugins** - Enabled marketplace plugins

## Customization

### Adding Your Own Hooks

1. Create a Python script in `hooks/`:

```python
#!/usr/bin/env python3
import json
import sys

def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")

    # Your logic here

    sys.exit(0)  # 0=allow, 1=warn, 2=block

if __name__ == "__main__":
    main()
```

2. Add the hook to `settings/settings.template.json`
3. Re-run `./install.sh` to regenerate settings

### Adding Your Own Agents

Create a markdown file in `agents/` with YAML frontmatter:

```markdown
---
name: my-agent
description: When and how to use this agent
model: sonnet
color: blue
---

You are an expert in...
```

### Modifying Skills

Skills in `skills/` follow the structure:

```
skill-name/
├── SKILL.md           # Main skill definition
├── references/        # Supporting documentation
└── scripts/           # Automation scripts (optional)
```

## Project Structure

```
dotclaude/
├── README.md                    # This file
├── CLAUDE.md                    # Global preferences
├── install.sh                   # Installation script
├── settings/
│   └── settings.template.json   # Settings with $HOME placeholders
├── hooks/
│   ├── README.md
│   └── *.py                     # 13 hook scripts
├── agents/
│   ├── README.md
│   └── *.md                     # 9 agent definitions
├── skills/
│   ├── README.md
│   └── */                       # 4 skill directories
└── docs/
    └── *.md                     # Additional documentation
```

## Requirements

- [Claude Code CLI](https://claude.ai/download)
- Python 3.8+ (for hooks)
- Bash (for installation)

### Optional Dependencies

Some hooks have optional dependencies for full functionality:

- `prettier` - For auto-formatting JS/TS/Svelte
- `black` - For auto-formatting Python
- `terminal-notifier` (macOS) - For notifications

## License

MIT License - Feel free to use, modify, and share.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Ideas for contributions:

- New hooks for additional validations
- Agents for other frameworks/languages
- Skills for common development tasks
- Documentation improvements
