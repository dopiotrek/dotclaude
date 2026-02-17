---
name: component-imports
description: Best practices for importing shadcn-svelte components using folder paths to support both named exports and compatibility with different import patterns.
---

# Component Imports Rule

## Overview

This rule provides guidelines for importing shadcn-svelte components using folder paths to ensure maximum compatibility and support for different import patterns.

## Core Principle

**Always prefer destructuring imports for shadcn-svelte components using folder paths.**

## Why This Rule Exists

Using folder paths for imports provides several advantages:

- **Better Compatibility**: Works with both named exports and default exports
- **Cleaner Syntax**: More readable and maintainable import statements
- **Future-Proof**: Less likely to break when component structure changes
- **Standard Practice**: Follows modern JavaScript/TypeScript module conventions

## Correct Import Pattern

### ✅ Recommended: Destructuring Imports

```typescript
// ✅ Best: Destructuring imports for individual components
import { Button } from "$lib/components/ui/button";
import { Input } from "$lib/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
```

### ⚠️ Acceptable: Namespace Imports (when necessary)

```typescript
// ⚠️ Acceptable: Namespace imports for complex component systems
import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
```

### ❌ Avoid: Namespace Imports for Simple Components

```typescript
// ❌ Avoid: Namespace imports for simple components
import * as Card from "$lib/components/ui/card";
import * as Button from "$lib/components/ui/button";
```

### ❌ Avoid: Explicit File Path Imports

```typescript
// ❌ Avoid: Import using explicit file path
import { Button } from "$lib/components/ui/button/index.js";
import { Input } from "$lib/components/ui/input/index.js";
import { Card } from "$lib/components/ui/card/index.js";
```

## Supported Import Cases

Folder path imports support multiple scenarios:

### 1. Destructuring Imports (Preferred)
```typescript
// Preferred: Import specific components from their own folders
import { Button } from "$lib/components/ui/button";
import { Input } from "$lib/components/ui/input";
import { Label } from "$lib/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
```

### 2. Namespace Imports (Use Sparingly)
```typescript
// Use for complex component systems with many sub-components
import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
import * as NavigationMenu from "$lib/components/ui/navigation-menu";
```

### 3. Mixed Imports
```typescript
// Works with mixed import patterns
import { Button } from "$lib/components/ui/button";
import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
```

## Component-Specific Examples

### Button Component
```typescript
// ✅ Correct
import { Button } from "$lib/components/ui/button";

// Usage
<Button variant="default" size="lg">Click me</Button>
```

### Card Component System
```typescript
// ✅ Correct: Destructuring import
import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";

// Usage
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### Form Components
```typescript
// ✅ Correct: Destructuring imports
import { Input } from "$lib/components/ui/input";
import { Label } from "$lib/components/ui/label";
import * as Select from "$lib/components/ui/select";

// Usage
<div class="space-y-2">
  <Label for="email">Email</Label>
  <Input id="email" type="email" />
</div>

<Select.Root>
  <Select.Trigger>
    <Select.Value placeholder="Select option" />
  </Select.Trigger>
  <Select.Content>
    <Select.Item value="option1">Option 1</Select.Item>
  </Select.Content>
</Select.Root>
```

## Import Organization Best Practices

### Group Imports by Type
```typescript
// shadcn-svelte components
import { Button } from "$lib/components/ui/button";
import { Input } from "$lib/components/ui/input";
import { Label } from "$lib/components/ui/label";

// Third-party libraries
import { createForm } from "@tanstack/svelte-form";

// Local utilities
import { cn } from "$lib/utils";
```

### Use Aliases When Needed
```typescript
// When importing components with the same name from different packages
import { Button as ShadcnButton } from "$lib/components/ui/button";
import { Button as CustomButton } from "$lib/components/custom/button";
```

## Common Import Patterns

### Single Component Import
```typescript
import { Button } from "$lib/components/ui/button";
```

### Multiple Components Import
```typescript
// ✅ Best: Each component from its own folder, sub-components from their parent
import { Button } from "$lib/components/ui/button";
import { Input } from "$lib/components/ui/input";
import { Label } from "$lib/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
```

### Namespace Import for Complex Component Systems
```typescript
// Use only when component has many sub-components
import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
import * as NavigationMenu from "$lib/components/ui/navigation-menu";
```

### Mixed Import Pattern
```typescript
import { Button } from "$lib/components/ui/button";
import * as Card from "$lib/components/ui/card";
import { cn } from "$lib/utils";
```

## Migration Guide

### Converting Existing Imports

If you have existing imports using explicit file paths, convert them as follows:

#### Before
```typescript
// ❌ Before: Namespace imports
import * as Card from "$lib/components/ui/card/index.js";
import * as Button from "$lib/components/ui/button/index.js";
```

#### After
```typescript
// ✅ After: Destructuring imports
import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
import { Button } from "$lib/components/ui/button";
```

### Batch Update Script

For large projects, you can use a script to update imports:

```bash
# Find and replace namespace imports with destructuring imports
find src -name "*.svelte" -o -name "*.ts" -o -name "*.js" | xargs sed -i 's|import \* as \([^ ]*\) from "$lib/components/ui/\([^/]*\)/index.js"|import { \1, \1Content, \1Header, \1Title } from "$lib/components/ui/\2"|g'
```

## IDE Configuration

### VS Code Settings
Configure your IDE to prefer folder path imports:

```json
{
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

### Auto-Import Configuration
Ensure your auto-import features are configured to use folder paths:

```javascript
// svelte.config.js
const config = {
  // ... other config
  kit: {
    // ... other config
    alias: {
      "$lib": "./src/lib"
    }
  }
};
```

## Troubleshooting

### Common Issues

#### Import Not Found
If you get "module not found" errors:
1. Verify the component is installed: `pnpm dlx shadcn-svelte@latest add button`
2. Check the file structure in `$lib/components/ui/`
3. Ensure your `svelte.config.js` has correct path aliases

#### Type Errors
If you experience TypeScript errors:
1. Check your `tsconfig.json` path mapping
2. Verify component exports in `index.js` files
3. Restart your TypeScript server

#### Circular Dependencies
If you encounter circular dependency warnings:
1. Review your import structure
2. Consider using lazy imports for large component systems
3. Ensure components are properly structured

## Best Practices Summary

1. **Prefer destructuring imports**: `import { Card, CardContent, CardHeader } from "$lib/components/ui/card"`
2. **Use namespace imports sparingly**: Only for complex component systems with many sub-components
3. **Group related imports**: Organize imports by type and source
4. **Use folder paths**: Always use folder paths instead of explicit file paths
5. **Configure your IDE**: Set up auto-import preferences for destructuring
6. **Test imports**: Verify imports work after adding new components
7. **Keep imports clean**: Remove unused imports regularly

## Anti-Patterns to Avoid

- ❌ Using explicit file paths: `from "$lib/components/ui/button/index.js"`
- ❌ Using namespace imports for simple components: `import * as Card from "$lib/components/ui/card"`
- ❌ Mixing import styles inconsistently
- ❌ Not organizing imports logically
- ❌ Ignoring TypeScript errors related to imports
- ❌ Using relative paths for shadcn components

## Approved Patterns

- ✅ Destructuring imports: `import { Card, CardContent, CardHeader } from "$lib/components/ui/card"`
- ✅ Namespace imports for complex systems: `import * as DropdownMenu from "$lib/components/ui/dropdown-menu"`
- ✅ Organized import groups
- ✅ Consistent import style across the project
- ✅ Proper IDE configuration for auto-imports
- ✅ Folder path imports (never explicit file paths)
