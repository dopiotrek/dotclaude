---
name: superforms-reference
description: "Reference patterns for sveltekit-superforms + Zod: schemas, server actions, client components, file uploads, multi-step wizards, shadcn-svelte integration."
paths: "src/**/*.svelte, src/**/*.ts, src/**/+page.server.ts"
user-invocable: false
---

# sveltekit-superforms + Zod Reference

## Core Principles

### 1. State Initialization: Server is the Source of Truth

A component's state should be correct from the very first render. Never use `$effect` to initialize or patch missing state objects.

```typescript
// ✅ Good: Complete data shape in +page.server.ts
export const load = async () => {
	const form = await superValidate(zod(schema), {
		defaults: {
			compensation: {
				type: 'hourly',
				amount: 0,
				currency: 'USD'
			},
			location: {
				type: 'remote',
				address: '',
				travel: false
			}
		}
	});
	return { form };
};

// ❌ Bad: Using $effect to patch missing data
```

### 2. Form Submission: Use `formaction`, Not Proxy Forms

A single logical form should be represented by a single `<form>` element.

```svelte
<!-- ✅ Good: Single form with formaction -->
<form method="POST" use:enhance>
	<input bind:value={$form.title} />
	<button formaction="?/saveDraft">Save Draft</button>
	<button formaction="?/publish">Publish</button>
</form>
```

### 3. UI Validation Logic: Use the Schema, Not Manual Checks

The Zod schema is the single source of truth for validation.

```svelte
<script lang="ts">
	// ✅ Good: Schema-based validation
	let canSaveAsDraft = $derived(draftSchema.safeParse($form).success);
	let canPublish = $derived(publishSchema.safeParse($form).success);

	// ❌ Bad: Manual validation checks
	// let canPublish = $derived($form.title && $form.description && ...)
</script>
```

## Schema Design Patterns

### Basic Schema

```typescript
import { z } from 'zod';

export const userProfileSchema = z.object({
	name: z.string().min(2, 'Name must be at least 2 characters'),
	email: z.string().email('Invalid email address'),
	age: z.number().min(18, 'Must be at least 18 years old').optional(),
	bio: z.string().max(500, 'Bio must be under 500 characters').optional()
});

export type UserProfile = z.infer<typeof userProfileSchema>;
```

### Multi-Step Schema Validation (Draft vs Publish)

```typescript
// Draft schema - minimal requirements
export const draftSchema = z.object({
	title: z.string().min(1, 'Title is required'),
	description: z.string().optional(),
	compensation: z.object({
		type: z.enum(['hourly', 'salary', 'contract']),
		amount: z.number().optional()
	}).optional()
});

// Publish schema - complete requirements
export const publishSchema = z.object({
	title: z.string().min(3, 'Title must be at least 3 characters'),
	description: z.string().min(50, 'Description must be at least 50 characters'),
	compensation: z.object({
		type: z.enum(['hourly', 'salary', 'contract']),
		amount: z.number().min(1, 'Amount must be greater than 0'),
		currency: z.string()
	}),
	requirements: z.array(z.string()).min(1, 'At least one requirement needed')
});
```

## Server-Side Implementation

### Load Function + Actions

```typescript
// +page.server.ts
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { fail } from '@sveltejs/kit';
import { message } from 'sveltekit-superforms';

export const load = async () => {
	const form = await superValidate(zod(schema), {
		defaults: { title: '', description: '', requirements: [] }
	});
	return { form };
};

export const actions = {
	saveDraft: async ({ request }) => {
		const form = await superValidate(request, zod(draftSchema));
		if (!form.valid) return fail(400, { form });
		const id = await saveJobDraft(form.data);
		return message(form, `Draft saved! ID: ${id}`);
	},
	publish: async ({ request }) => {
		const form = await superValidate(request, zod(publishSchema));
		if (!form.valid) return fail(400, { form });
		const id = await publishJob(form.data);
		return message(form, `Published! ID: ${id}`);
	}
};
```

## Client-Side Implementation

### Basic Form Component

```svelte
<script lang="ts">
	import { superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';

	let { data } = $props();

	const { form, errors, enhance, submitting, message } = superForm(data.form, {
		validators: zodClient(draftSchema),
		onUpdated({ form }) {
			if (form.valid && form.message) showToast(form.message);
		},
		onError({ result }) {
			console.error('Form error:', result.error);
		}
	});
</script>

<form method="POST" use:enhance class="space-y-6">
	<div class="space-y-2">
		<Label for="title">Title</Label>
		<Input id="title" bind:value={$form.title} aria-invalid={$errors.title ? 'true' : undefined} />
		{#if $errors.title}<p class="text-sm text-red-600">{$errors.title}</p>{/if}
	</div>
	<Button type="submit" formaction="?/saveDraft" disabled={$submitting}>Save Draft</Button>
</form>
```

### Nested Data (JSON mode)

```svelte
<script lang="ts">
	const { form, errors, enhance } = superForm(data.form, {
		dataType: 'json' // Enable JSON mode for nested data
	});
</script>
```

### Dynamic Array Fields

```svelte
{#each $form.requirements as _, i}
	<div class="flex gap-2">
		<Input bind:value={$form.requirements[i]} />
		<Button type="button" onclick={() => {
			$form.requirements = $form.requirements.filter((_, idx) => idx !== i);
		}}>Remove</Button>
	</div>
{/each}
<Button type="button" onclick={() => { $form.requirements = [...$form.requirements, '']; }}>
	Add Requirement
</Button>
```

### File Upload

```typescript
const fileSchema = z.object({
	resume: z.instanceof(File)
		.refine((f) => f.size < 5_000_000, 'File must be < 5MB')
		.refine((f) => ['application/pdf'].includes(f.type), 'Only PDF allowed')
});
```

```svelte
<script lang="ts">
	import { fileProxy } from 'sveltekit-superforms';
	const resumeFile = fileProxy(form, 'resume');
</script>
<form method="POST" enctype="multipart/form-data" use:enhance>
	<input type="file" bind:files={$resumeFile} accept=".pdf" />
</form>
```

### Multi-Step Wizard

```svelte
<script lang="ts">
	let currentStep = $state(1);

	function getSchemaForStep(step: number) {
		switch (step) {
			case 1: return basicInfoSchema;
			case 2: return compensationSchema;
			case 3: return requirementsSchema;
		}
	}

	async function nextStep() {
		const result = getSchemaForStep(currentStep).safeParse($form);
		if (result.success && currentStep < totalSteps) currentStep++;
	}
</script>
```

### shadcn-svelte Select Integration

```svelte
<Select.Root type="single" bind:value={$form.location.type}>
	<Select.Trigger>{selectedLabel}</Select.Trigger>
	<Select.Content>
		{#each options as opt}
			<Select.Item value={opt.value} label={opt.label}>{opt.label}</Select.Item>
		{/each}
	</Select.Content>
</Select.Root>
```

### Real-time Validation

```svelte
const { form, errors, enhance, validate } = superForm(data.form, {
	validators: zodClient(schema),
	validationMethod: 'onblur',
	clearOnSubmit: 'errors-and-message'
});
```
