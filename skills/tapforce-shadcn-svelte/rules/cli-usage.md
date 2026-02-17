---
name: cli-usage
description: Guidelines for using shadcn-svelte CLI commands properly without manual configuration
---

# CLI Usage Rule

## Overview

This rule ensures that all shadcn-svelte operations are performed through official CLI commands rather than manual file creation or configuration.

## Core Principle

**Always use CLI commands for shadcn-svelte operations - never manually create configuration files.**

## Why This Rule Exists

shadcn-svelte CLI commands handle:
- Proper configuration validation
- Dependency management
- File structure setup
- Version compatibility
- Component registration

## Required CLI Commands

### Installation
```bash
pnpm dlx shadcn-svelte@latest init
```

### Adding Components
```bash
pnpm dlx shadcn-svelte@latest add [component-name]
```

### Multiple Components
```bash
pnpm dlx shadcn-svelte@latest add button card input
```

## Forbidden Actions

❌ **Never manually create these files:**
- `components.json`
- Component files in `$lib/components/ui/`
- Utility files in `$lib/utils/`
- CSS configuration files

## Correct Usage Examples

### ✅ Correct: Initialize project
```bash
pnpm dlx shadcn-svelte@latest init
```

### ✅ Correct: Add component
```bash
pnpm dlx shadcn-svelte@latest add button
```

### ✅ Correct: Add multiple components
```bash
pnpm dlx shadcn-svelte@latest add button card input label
```

## Error Handling

### When CLI fails with configuration errors:
1. **DO NOT** manually create missing files
2. **DO** check project prerequisites (SvelteKit, TailwindCSS)
3. **DO** run CLI with `--skip-preflight` if appropriate
4. **DO** re-run init command if configuration is corrupted

### Example error resolution:
```bash
# If components.json is missing or corrupted
pnpm dlx shadcn-svelte@latest init --overwrite

# If preflight checks fail
pnpm dlx shadcn-svelte@latest add button --skip-preflight
```

## CLI Options Reference

### Init Options
- `--overwrite`: Overwrite existing files
- `--skip-preflight`: Ignore preflight checks
- `--base-color <name>`: Set base color
- `--css <path>`: Specify CSS file path

### Add Options
- `--no-deps`: Skip dependency installation
- `--skip-preflight`: Ignore preflight checks
- `--yes`: Skip confirmation prompts
- `--overwrite`: Overwrite existing components

## Troubleshooting

### Common Issues and Solutions

1. **"components.json not found"**
   - Run `pnpm dlx shadcn-svelte@latest init`
   - Do not manually create the file

2. **"Invalid component configuration"**
   - Run `pnpm dlx shadcn-svelte@latest init --overwrite`
   - Do not manually edit components.json

3. **"Dependencies not installed"**
   - Run `pnpm dlx shadcn-svelte@latest add [component] --no-deps`
   - Then run `pnpm install` separately

4. **"Path alias issues"**
   - Check `svelte.config.js` alias configuration
   - Re-run init if needed

## Best Practices

1. **Always use latest CLI version**: `pnpm dlx shadcn-svelte@latest`
2. **Check prerequisites before running**: SvelteKit ^2, TailwindCSS ^4
3. **Use project-specific version**: Get version from `package.json` after init
4. **Run commands from project root**: Use `--cwd` option if needed
5. **Read CLI output**: Pay attention to warnings and suggestions

## Example Workflow

```bash
# 1. Check prerequisites
ls package.json  # Verify SvelteKit and TailwindCSS

# 2. Initialize shadcn-svelte
pnpm dlx shadcn-svelte@latest init

# 3. Add components
pnpm dlx shadcn-svelte@latest add button card input

# 4. Use components in your code
import { Button, Card, Input } from "$lib/components/ui/button";
```

## Anti-Patterns to Avoid

- ❌ Manually creating `components.json`
- ❌ Copying component files from other projects
- ❌ Editing component registration manually
- ❌ Creating utility files manually
- ❌ Ignoring CLI error messages and creating files anyway

## Approved Patterns

- ✅ Always use CLI commands
- ✅ Follow CLI prompts and recommendations
- ✅ Use CLI options for customization
- ✅ Re-run init when configuration issues occur
- ✅ Read and understand CLI output
