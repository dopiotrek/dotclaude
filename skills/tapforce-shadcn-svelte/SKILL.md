---
name: tapforce-shadcn-svelte
description: Best practices for setup and use of shadcn-svelte library to develop UX/UI in Svelte projects. Use this skill when project is using Svelte/SvelteKit framework as main app framework, when user attempts to setup new project or when user is developing on existing project using shadcn-svelte components.
license: Apache-2.0
metadata:
  author: tapforce
  version: "1.0"
compatibility: Requires SvelteKit ^2.0, Svelte ^5.0, pnpm, and recommends TailwindCSS ^4
allowed-tools: Bash Read Write
---

# tapforce-shadcn-svelte

This skill provides comprehensive guidance for setting up and using the shadcn-svelte library in Svelte projects. It covers installation, configuration, component usage, theming, and best practices.

## Requirements

- Project must be based on SvelteKit framework version 2.0 or higher
- Project must use Svelte 5.0 or higher  
- Project should use TailwindCSS (recommended)

## Resources

- [Official documentation]: https://www.shadcn-svelte.com/llms.txt
- [Components documentation]: https://www.shadcn-svelte.com/docs/components

## Available Components

- [Accordion](https://www.shadcn-svelte.com/docs/components/accordion)
- [Alert](https://www.shadcn-svelte.com/docs/components/alert)
- [Alert Dialog](https://www.shadcn-svelte.com/docs/components/alert-dialog)
- [Aspect Ratio](https://www.shadcn-svelte.com/docs/components/aspect-ratio)
- [Avatar](https://www.shadcn-svelte.com/docs/components/avatar)
- [Badge](https://www.shadcn-svelte.com/docs/components/badge)
- [Breadcrumb](https://www.shadcn-svelte.com/docs/components/breadcrumb)
- [Button](https://www.shadcn-svelte.com/docs/components/button)
- [Button Group](https://www.shadcn-svelte.com/docs/components/button-group)
- [Calendar](https://www.shadcn-svelte.com/docs/components/calendar)
- [Card](https://www.shadcn-svelte.com/docs/components/card)
- [Carousel](https://www.shadcn-svelte.com/docs/components/carousel)
- [Chart](https://www.shadcn-svelte.com/docs/components/chart)
- [Checkbox](https://www.shadcn-svelte.com/docs/components/checkbox)
- [Collapsible](https://www.shadcn-svelte.com/docs/components/collapsible)
- [Combobox](https://www.shadcn-svelte.com/docs/components/combobox)
- [Command](https://www.shadcn-svelte.com/docs/components/command)
- [Context Menu](https://www.shadcn-svelte.com/docs/components/context-menu)
- [Data Table](https://www.shadcn-svelte.com/docs/components/data-table)
- [Date Picker](https://www.shadcn-svelte.com/docs/components/date-picker)
- [Dialog](https://www.shadcn-svelte.com/docs/components/dialog)
- [Drawer](https://www.shadcn-svelte.com/docs/components/drawer)
- [Dropdown Menu](https://www.shadcn-svelte.com/docs/components/dropdown-menu)
- [Empty](https://www.shadcn-svelte.com/docs/components/empty)
- [Field](https://www.shadcn-svelte.com/docs/components/field)
- [Form](https://www.shadcn-svelte.com/docs/components/form)
- [Hover Card](https://www.shadcn-svelte.com/docs/components/hover-card)
- [Input](https://www.shadcn-svelte.com/docs/components/input)
- [Input Group](https://www.shadcn-svelte.com/docs/components/input-group)
- [Input OTP](https://www.shadcn-svelte.com/docs/components/input-otp)
- [Item](https://www.shadcn-svelte.com/docs/components/item)
- [Kbd](https://www.shadcn-svelte.com/docs/components/kbd)
- [Label](https://www.shadcn-svelte.com/docs/components/label)
- [Menubar](https://www.shadcn-svelte.com/docs/components/menubar)
- [Native Select](https://www.shadcn-svelte.com/docs/components/native-select)
- [Navigation Menu](https://www.shadcn-svelte.com/docs/components/navigation-menu)
- [Pagination](https://www.shadcn-svelte.com/docs/components/pagination)
- [Popover](https://www.shadcn-svelte.com/docs/components/popover)
- [Progress](https://www.shadcn-svelte.com/docs/components/progress)
- [Radio Group](https://www.shadcn-svelte.com/docs/components/radio-group)
- [Range Calendar](https://www.shadcn-svelte.com/docs/components/range-calendar)
- [Resizable](https://www.shadcn-svelte.com/docs/components/resizable)
- [Scroll Area](https://www.shadcn-svelte.com/docs/components/scroll-area)
- [Select](https://www.shadcn-svelte.com/docs/components/select)
- [Separator](https://www.shadcn-svelte.com/docs/components/separator)
- [Sheet](https://www.shadcn-svelte.com/docs/components/sheet)
- [Sidebar](https://www.shadcn-svelte.com/docs/components/sidebar)
- [Skeleton](https://www.shadcn-svelte.com/docs/components/skeleton)
- [Slider](https://www.shadcn-svelte.com/docs/components/slider)
- [Sonner](https://www.shadcn-svelte.com/docs/components/sonner)
- [Spinner](https://www.shadcn-svelte.com/docs/components/spinner)
- [Switch](https://www.shadcn-svelte.com/docs/components/switch)
- [Table](https://www.shadcn-svelte.com/docs/components/table)
- [Tabs](https://www.shadcn-svelte.com/docs/components/tabs)
- [Textarea](https://www.shadcn-svelte.com/docs/components/textarea)
- [Toggle](https://www.shadcn-svelte.com/docs/components/toggle)
- [Toggle Group](https://www.shadcn-svelte.com/docs/components/toggle-group)
- [Tooltip](https://www.shadcn-svelte.com/docs/components/tooltip)
- [Typography](https://www.shadcn-svelte.com/docs/components/typography)

## Check Project Installation

You must check if shadcn-svelte is already installed in the project. To check, look for the `components.json` file in the project root directory.

```bash
# Check if components.json exists
ls -la components.json
```

If the file exists, shadcn-svelte is already configured in the project.

## Installation

### Prerequisites

Project requires SvelteKit ^2 and TailwindCSS ^4 ready before initializing shadcn-svelte.

### Initialize shadcn-svelte

```bash
pnpm dlx shadcn-svelte@latest init
```

The `@latest` tag indicates installing the latest version. For adding components by command, you need to get the real version from `package.json` and use it in the command.

### Configure components.json

You will be asked a few questions to configure `components.json`:

- Which base color would you like to use? › Slate
- Where is your global CSS file? (this file will be overwritten) › src/routes/layout.css
- Configure the import alias for lib: › $lib
- Configure the import alias for components: › $lib/components
- Configure the import alias for utils: › $lib/utils
- Configure the import alias for hooks: › $lib/hooks
- Configure the import alias for ui: › $lib/components/ui

### Setup Path Aliases (if needed)

If you are not using the default alias `$lib`, you'll need to update your `svelte.config.js` file to include those aliases:

```javascript
const config = {
  // ... other config
  kit: {
    // ... other config
    alias: {
      "@/*": "./path/to/lib/*",
    },
  },
};
```

## CLI Usage

### Initialize Project

```bash
pnpm dlx shadcn-svelte@latest init
```

Options:
- `-c, --cwd <path>`: the working directory (default: the current directory)
- `-o, --overwrite`: overwrite existing files (default: false)
- `--no-deps`: disable adding & installing dependencies
- `--skip-preflight`: ignore preflight checks and continue (default: false)
- `--base-color <name>`: the base color for the components (choices: "slate", "gray", "zinc", "neutral", "stone")
- `--css <path>`: path to the global CSS file
- `--components-alias <path>`: import alias for components
- `--lib-alias <path>`: import alias for lib
- `--utils-alias <path>`: import alias for utils
- `--hooks-alias <path>`: import alias for hooks
- `--ui-alias <path>`: import alias for ui
- `--proxy <proxy>`: fetch items from registry using a proxy

### Add Components

```bash
pnpm dlx shadcn-svelte@latest add [component]
```

Example:
```bash
pnpm dlx shadcn-svelte@latest add button
```

Options:
- `-c, --cwd <path>`: the working directory (default: the current directory)
- `--no-deps`: skips adding & installing package dependencies
- `--skip-preflight`: ignore preflight checks and continue (default: false)
- `-a, --all`: install all components to your project (default: false)
- `-y, --yes`: skip confirmation prompt (default: false)
- `-o, --overwrite`: overwrite existing files (default: false)
- `--proxy <proxy>`: fetch components from registry using a proxy

### Import and Use Components

After adding a component, you can import it like this:

```svelte
<script lang="ts">
  import { Button } from "$lib/components/ui/button";
</script>

<Button>Click me</Button>
```

**Import Guidelines:**
- Always use destructuring imports from the component's own folder: `import { Button } from "$lib/components/ui/button"`
- Import sub-components together from their parent: `import { Card, CardHeader, CardTitle } from "$lib/components/ui/card"`
- Never use namespace imports for simple components: `import * as Button from "$lib/components/ui/button"`
- Use direct component paths without `/index.js` suffix

## Theming

### CSS Variables Convention

shadcn-svelte uses a simple background and foreground convention for colors. The background variable is used for the background color of the component and the foreground variable is used for the text color.

For example, given these CSS variables:
```css
--primary: oklch(0.208 0.042 265.755);
--primary-foreground: oklch(0.984 0.003 247.858);
```

The background color will be `var(--primary)` and the foreground color will be `var(--primary-foreground)`:

```html
<div class="bg-primary text-primary-foreground">Hello</div>
```

### Generated CSS Structure

The `init` command generates the full CSS structure in your global CSS file. The exact oklch values depend on the chosen base color (slate, gray, zinc, neutral, stone). The generated file includes:

1. **TailwindCSS import** and **tw-animate-css** animation library
2. **Dark mode custom variant**: `@custom-variant dark (&:is(.dark *))`
3. **`:root` CSS variables** for light mode colors
4. **`.dark` CSS variables** for dark mode colors
5. **`@theme inline` block** mapping CSS variables to TailwindCSS v4 utilities
6. **`@layer base`** block for default border and background styles

### Available CSS Variables

The following variables are available (values shown are for the **slate** base color):

| Variable | Purpose |
|----------|---------|
| `--background` / `--foreground` | Page background and text |
| `--card` / `--card-foreground` | Card component colors |
| `--popover` / `--popover-foreground` | Popover/dropdown colors |
| `--primary` / `--primary-foreground` | Primary action colors |
| `--secondary` / `--secondary-foreground` | Secondary action colors |
| `--muted` / `--muted-foreground` | Muted/subtle content |
| `--accent` / `--accent-foreground` | Accent/highlight colors |
| `--destructive` | Destructive action color |
| `--border` | Border color |
| `--input` | Input border color |
| `--ring` | Focus ring color |
| `--chart-1` through `--chart-5` | Chart colors |
| `--sidebar-*` | Sidebar-specific variants |
| `--radius` | Base border radius |

### TailwindCSS v4 Theme Mapping

The init command also generates a `@theme inline` block required by TailwindCSS v4 to map CSS variables to Tailwind utility classes (e.g., `bg-primary`, `text-foreground`, `border-border`):

```css
@theme inline {
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  /* ... maps all CSS variables to Tailwind color utilities */
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

## Dark Mode

### Install mode-watcher

```bash
pnpm i mode-watcher
```

### Add the ModeWatcher Component

Import the ModeWatcher component and use it in your root layout:

```svelte
<script lang="ts">
  import { ModeWatcher } from "mode-watcher";
  let { children } = $props();
</script>

<ModeWatcher />
{@render children?.()}
```

### Add a Mode Toggle

#### Simple Toggle Button

```svelte
<script lang="ts">
  import SunIcon from "@lucide/svelte/icons/sun";
  import MoonIcon from "@lucide/svelte/icons/moon";
  import { toggleMode } from "mode-watcher";
  import { Button } from "$lib/components/ui/button";
</script>

<Button onclick={toggleMode} variant="outline" size="icon">
  <SunIcon class="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 !transition-all dark:scale-0 dark:-rotate-90" />
  <MoonIcon class="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 !transition-all dark:scale-100 dark:rotate-0" />
  <span class="sr-only">Toggle theme</span>
</Button>
```

#### Dropdown Menu Toggle

```svelte
<script lang="ts">
  import SunIcon from "@lucide/svelte/icons/sun";
  import MoonIcon from "@lucide/svelte/icons/moon";
  import { resetMode, setMode } from "mode-watcher";
  import { 
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger
  } from "$lib/components/ui/dropdown-menu";
  import { buttonVariants } from "$lib/components/ui/button";
</script>

<DropdownMenu>
  <DropdownMenuTrigger class={buttonVariants({ variant: "outline", size: "icon" })}>
    <SunIcon class="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 !transition-all dark:scale-0 dark:-rotate-90" />
    <MoonIcon class="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 !transition-all dark:scale-100 dark:rotate-0" />
    <span class="sr-only">Toggle theme</span>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end">
    <DropdownMenuItem onclick={() => setMode("light")}>Light</DropdownMenuItem>
    <DropdownMenuItem onclick={() => setMode("dark")}>Dark</DropdownMenuItem>
    <DropdownMenuItem onclick={() => resetMode()}>System</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

## Rules

This skill includes the following rules:

### [Component Maintenance]
- **Rule**: [component-maintenance](rules/component-maintenance.md)
- **Description**: Guidelines for maintaining shadcn components to ensure future update compatibility

### [Component Usage Best Practices]
- **Rule**: [component-usage](rules/component-usage.md)
- **Description**: Best practices for using shadcn components effectively with their options

### [Component Imports]
- **Rule**: [component-imports](rules/component-imports.md)
- **Description**: Best practices for importing shadcn-svelte components using folder paths for maximum compatibility

### [CLI Usage]
- **Rule**: [cli-usage](rules/cli-usage.md)
- **Description**: Always use CLI commands for installation, initialization, and adding components - never manually create config files
