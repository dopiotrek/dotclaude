---
name: component-maintenance
description: Guidelines for maintaining shadcn components to ensure future update compatibility and prevent breaking changes when updating shadcn-svelte versions.
---

# Component Maintenance Rule

## Overview

This rule provides guidelines for maintaining shadcn-svelte components in your project to ensure compatibility with future updates and prevent breaking changes.

## Core Principle

**Do not modify shadcn components directly after adding them to your project.**

## Why This Rule Exists

shadcn-svelte components are designed to be updated automatically when new versions are released. Direct modifications to these components can:

- Prevent automatic updates
- Cause merge conflicts during updates
- Break component functionality when new features are added
- Make it difficult to track changes and debug issues

## Recommended Approach

### When You Need Customization

1. **Create a New Component**: Instead of modifying an existing shadcn component, create a new component that extends or wraps the original.

2. **Use Composition**: Build custom functionality by composing multiple shadcn components.

3. **Override Styles**: Use CSS classes and Tailwind utilities to customize appearance without changing component logic.

### Example: Custom Button Component

```svelte
<!-- Instead of modifying the original Button component -->
<script lang="ts">
  import { Button as BaseButton } from "$lib/components/ui/button";
  import { cn } from "$lib/utils";
  
  interface Props {
    variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
    size?: "default" | "sm" | "lg" | "icon";
    class?: string;
    children: import("svelte").Snippet;
  }
  
  let {
    variant = "default",
    size = "default",
    class: className,
    children,
    ...restProps
  }: Props = $props();
</script>

<BaseButton
  {variant}
  {size}
  class={cn("custom-button-styles", className)}
  {...restProps}
>
  {@render children()}
</BaseButton>

<style>
  :global(.custom-button-styles) {
    /* Your custom styles here */
  }
</style>
```

### When Modification is Unavoidable

If you absolutely must modify a shadcn component:

1. **Document Changes**: Keep a detailed record of all modifications made
2. **Version Lock**: Consider locking the shadcn-svelte version to prevent automatic updates
3. **Test Thoroughly**: Ensure modifications don't break component functionality
4. **Plan for Migration**: Have a strategy to migrate your changes when updating

## Update Strategy

### Before Updating

1. **Backup Custom Components**: Ensure all custom components are backed up
2. **Review Changes**: Check the shadcn-svelte changelog for breaking changes
3. **Test Environment**: Update in a test environment first

### During Update

1. **Use CLI**: Use the official CLI for updates: `pnpm dlx shadcn-svelte@latest add [component]`
2. **Review Conflicts**: Carefully review any merge conflicts
3. **Test Components**: Test all components after update

### After Update

1. **Verify Functionality**: Ensure all components work as expected
2. **Update Custom Components**: Update any custom components that depend on modified shadcn components
3. **Document Issues**: Keep track of any issues encountered during update

## Best Practices

1. **Prefer Composition Over Inheritance**: Build complex components by combining simpler ones
2. **Use Props and Slots**: Leverage Svelte's props and slots system for customization
3. **CSS Customization**: Use CSS variables and Tailwind classes for visual changes
4. **Regular Updates**: Keep shadcn-svelte updated to benefit from bug fixes and new features
5. **Component Testing**: Test components thoroughly after any modifications or updates

## Common Anti-Patterns to Avoid

- ❌ Directly editing files in `$lib/components/ui/`
- ❌ Copying and pasting component code with minor changes
- ❌ Ignoring version updates for extended periods
- ❌ Modifying component internal logic without understanding implications

## Approved Patterns

- ✅ Creating wrapper components that use shadcn components
- ✅ Using CSS classes and Tailwind utilities for styling
- ✅ Extending functionality through props and slots
- ✅ Keeping shadcn components up to date
- ✅ Documenting all customizations and workarounds
