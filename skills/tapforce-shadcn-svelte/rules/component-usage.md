---
name: component-usage
description: Best practices for using shadcn-svelte components effectively by taking advantage of available options like variant, size, and class properties.
---

# Component Usage Best Practices Rule

## Overview

This rule provides guidelines for effectively using shadcn-svelte components by leveraging their built-in options and customization capabilities.

## Core Principle

**Always take advantage of component options when using shadcn components.**

## Why This Rule Exists

shadcn-svelte components are designed with extensive customization options that provide:

- Consistent design patterns
- Accessibility features
- Responsive behavior
- Theme integration
- Reduced code duplication

## Common Component Options

### Button Component

The Button component is a perfect example of leveraging component options:

```svelte
<script lang="ts">
  import { Button } from "$lib/components/ui/button";
</script>

<!-- ✅ Good: Using built-in variants and sizes -->
<Button variant="default" size="lg">Large Default Button</Button>
<Button variant="destructive" size="sm">Small Destructive Button</Button>
<Button variant="outline" size="icon">
  <Icon />
</Button>

<!-- ❌ Avoid: Creating separate components for each style -->
<!-- Instead of creating CustomLargeButton, CustomDestructiveButton, etc. -->
```

#### Available Button Options

- **variant**: `default` | `destructive` | `outline` | `secondary` | `ghost` | `link`
- **size**: `default` | `sm` | `lg` | `icon`
- **class**: Additional CSS classes for custom styling

### Input Component

```svelte
<script lang="ts">
  import { Input } from "$lib/components/ui/input";
</script>

<!-- ✅ Good: Using class prop for additional styling -->
<Input 
  type="email" 
  placeholder="Enter your email"
  class="w-full max-w-sm"
/>

<!-- ✅ Good: Combining with other components -->
<div class="space-y-2">
  <Label for="email">Email</Label>
  <Input id="email" type="email" />
</div>
```

### Card Component

```svelte
<script lang="ts">
  import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "$lib/components/ui/card";
</script>

<!-- ✅ Good: Using card components as a system -->
<Card class="w-full max-w-md">
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

## Best Practices by Component Category

### Form Components

#### Input Fields
- Use `class` prop for layout-specific styling
- Combine with `Label` components for accessibility
- Leverage `Field` components for form validation

```svelte
<script lang="ts">
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Field, FieldLabel, FieldContent, FieldDescription, FieldError } from "$lib/components/ui/field";
</script>

<Field>
  <FieldLabel>Username</FieldLabel>
  <FieldContent>
    <Input type="text" placeholder="Enter username" />
  </FieldContent>
  <FieldDescription>Choose a unique username</FieldDescription>
  <FieldError>Username is required</FieldError>
</Field>
```

#### Selection Components
- Use `Select` for dropdown menus
- Use `Checkbox` and `Radio Group` for selections
- Leverage built-in validation states

```svelte
<script lang="ts">
  import * as Select from "$lib/components/ui/select";
  import { Checkbox } from "$lib/components/ui/checkbox";
  import { Label } from "$lib/components/ui/label";
</script>

<!-- Select with options (namespace import due to many sub-components) -->
<Select.Root>
  <Select.Trigger>
    <Select.Label>Select an option</Select.Label>
  </Select.Trigger>
  <Select.Content>
    <Select.Item value="option1">Option 1</Select.Item>
    <Select.Item value="option2">Option 2</Select.Item>
  </Select.Content>
</Select.Root>

<!-- Checkbox with label -->
<div class="flex items-center gap-2">
  <Checkbox id="terms" class="border-2" />
  <Label for="terms">Accept terms</Label>
</div>
```

### Layout Components

#### Cards and Containers
- Use `Card` components for content grouping
- Leverage `Separator` for visual division
- Use `Sheet` and `Dialog` for overlays

```svelte
<script lang="ts">
  import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "$lib/components/ui/card";
  import { Separator } from "$lib/components/ui/separator";
</script>

<Card class="col-span-2">
  <CardHeader>
    <CardTitle>Dashboard</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Welcome to your dashboard</p>
    <Separator class="my-4" />
    <p>Additional content</p>
  </CardContent>
</Card>
```

### Navigation Components

#### Menus and Navigation
- Use `Navigation Menu` for primary navigation
- Use `Dropdown Menu` for action menus
- Leverage `Breadcrumb` for navigation hierarchy

```svelte
<script lang="ts">
  import * as NavigationMenu from "$lib/components/ui/navigation-menu";
  import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "$lib/components/ui/dropdown-menu";
</script>

<!-- Navigation menu (uses namespace import due to many sub-components) -->
<NavigationMenu.Root>
  <NavigationMenu.List>
    <NavigationMenu.Item>
      <NavigationMenu.Trigger>Products</NavigationMenu.Trigger>
      <NavigationMenu.Content>
        <NavigationMenu.Link href="/product1">Product 1</NavigationMenu.Link>
      </NavigationMenu.Content>
    </NavigationMenu.Item>
  </NavigationMenu.List>
</NavigationMenu.Root>

<!-- Dropdown with custom trigger -->
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Actions</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Edit</DropdownMenuItem>
    <DropdownMenuItem>Delete</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

## Advanced Usage Patterns

### Combining Components

```svelte
<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
</script>

<Card>
  <CardHeader class="flex items-center justify-between">
    <div>
      <CardTitle>Feature Title</CardTitle>
      <CardDescription>Feature description</CardDescription>
    </div>
    <Badge variant="secondary">New</Badge>
  </CardHeader>
  <CardContent>
    <p>Content goes here</p>
  </CardContent>
  <CardFooter class="flex justify-between">
    <Button variant="outline">Cancel</Button>
    <Button>Save</Button>
  </CardFooter>
</Card>
```

### Responsive Design with Component Options

```svelte
<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
</script>

<!-- Responsive button sizes -->
<Button 
  size="sm" 
  class="hidden sm:inline-flex md:size-default lg:size-lg"
>
  Responsive Button
</Button>

<!-- Responsive input -->
<Input 
  class="w-full sm:w-auto"
  placeholder="Search..."
/>
```

## Custom Styling Guidelines

### Using the Class Prop Effectively

```svelte
<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { cn } from "$lib/utils";
</script>

<!-- ✅ Good: Using class prop with utility classes -->
<Button 
  variant="outline"
  class={cn(
    "w-full sm:w-auto",           // Responsive width
    "transition-all duration-200", // Smooth transitions
    "hover:scale-105"             // Hover effects
  )}
>
  Enhanced Button
</Button>

<!-- ✅ Good: Conditional classes -->
<Button 
  variant={isPrimary ? "default" : "outline"}
  class={cn(
    "font-semibold",
    isDisabled && "opacity-50 cursor-not-allowed"
  )}
>
  {isPrimary ? "Primary Action" : "Secondary Action"}
</Button>
```

### Theme Integration

```svelte
<script lang="ts">
  import { Button } from "$lib/components/ui/button";
</script>

<!-- ✅ Good: Using theme colors -->
<Button class="bg-sidebar text-sidebar-foreground">
  Sidebar Styled Button
</Button>

<!-- ✅ Good: Dark mode aware -->
<Button class="border-border bg-card hover:bg-accent">
  Theme Aware Button
</Button>
```

## Common Anti-Patterns to Avoid

- ❌ Creating wrapper components for simple variant changes
- ❌ Hardcoding styles that could use component props
- ❌ Ignoring accessibility features built into components
- ❌ Not using the `class` prop for custom styling
- ❌ Rebuilding existing functionality instead of using component options

## Approved Patterns

- ✅ Using built-in variants and sizes
- ✅ Leveraging the `class` prop for additional styling
- ✅ Combining components for complex UI patterns
- ✅ Using theme variables for consistent styling
- ✅ Following component composition patterns
- ✅ Implementing responsive design with utility classes
