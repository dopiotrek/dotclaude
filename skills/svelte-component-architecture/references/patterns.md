# Component Patterns

Good and bad examples for common scenarios.

## Page Structure

**Good: Page as orchestrator**
```svelte
<!-- +page.svelte -->
<script>
  import ProposalBuilder from '$lib/components/features/proposal/ProposalBuilder.svelte';
  import DroneList from '$lib/components/features/drone/DroneList.svelte';
  
  let { data } = $props();
</script>

<main class="container py-8">
  <h1 class="text-2xl font-bold mb-6">Dashboard</h1>
  
  <section class="mb-12">
    <ProposalBuilder client={data.client} />
  </section>
  
  <section>
    <h2 class="text-xl mb-4">Your Drones</h2>
    <DroneList drones={data.drones} />
  </section>
</main>
```

**Bad: Page with too much inline UI**
```svelte
<!-- +page.svelte — doing too much -->
<script>
  let { data } = $props();
  let selectedDrone = $state(null);
  let filterText = $state('');
  let sortOrder = $state('name');
  // ... 50 more lines of state and logic
</script>

<main class="container py-8">
  <h1>Dashboard</h1>
  
  <!-- 200 lines of inline markup, filters, tables, modals... -->
  <div class="grid grid-cols-3 gap-4">
    {#each data.drones.filter(d => d.name.includes(filterText)).sort(...) as drone}
      <div class="card p-4 border rounded">
        <h3>{drone.name}</h3>
        <p>{drone.specs.weight}kg</p>
        <!-- ... 30 more lines per card -->
      </div>
    {/each}
  </div>
</main>
```

## Feature Components

**Good: Self-contained feature**
```svelte
<!-- DroneList.svelte — owns its filtering/sorting logic -->
<script>
  import DroneCard from '$lib/components/ui/DroneCard.svelte';
  import SearchInput from '$lib/components/ui/SearchInput.svelte';
  
  let { drones, onselect } = $props();
  
  let filter = $state('');
  let sortBy = $state('name');
  
  let filtered = $derived(
    drones
      .filter(d => d.name.toLowerCase().includes(filter.toLowerCase()))
      .sort((a, b) => a[sortBy].localeCompare(b[sortBy]))
  );
</script>

<div class="space-y-4">
  <SearchInput bind:value={filter} placeholder="Filter drones..." />
  
  <div class="grid grid-cols-3 gap-4">
    {#each filtered as drone}
      <DroneCard {drone} onclick={() => onselect?.(drone)} />
    {/each}
  </div>
</div>
```

**Bad: Feature leaking implementation**
```svelte
<!-- DroneList.svelte — exposing too much internal state -->
<script>
  let { 
    drones, 
    filter,           // parent controls filter
    onFilterChange,   // parent handles changes
    sortBy,           // parent controls sort
    onSortChange,     // parent handles changes
    selectedId,       // parent tracks selection
    onSelect          // parent handles selection
  } = $props();
  // This component is just a template, not a feature
</script>
```

## UI Components

**Good: Pure presentation**
```svelte
<!-- Button.svelte -->
<script>
  let { 
    variant = 'primary', 
    size = 'md',
    disabled = false,
    onclick,
    children 
  } = $props();
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };
  
  const sizes = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };
</script>

<button 
  class="rounded font-medium transition-colors {variants[variant]} {sizes[size]}"
  {disabled}
  {onclick}
>
  {@render children()}
</button>
```

**Bad: UI component with business logic**
```svelte
<!-- Button.svelte — doing too much -->
<script>
  import { submitForm } from '$lib/api';  // Business logic!
  
  let { formData, onSuccess } = $props();
  let loading = $state(false);
  
  async function handleClick() {
    loading = true;
    const result = await submitForm(formData);  // API call in UI component!
    onSuccess(result);
    loading = false;
  }
</script>

<button onclick={handleClick} disabled={loading}>
  {loading ? 'Submitting...' : 'Submit'}
</button>
```

## Wrapper Anti-Pattern

**Bad: Unnecessary wrapper**
```svelte
<!-- PageContainer.svelte — adds nothing -->
<script>
  let { children } = $props();
</script>

<div class="container mx-auto px-4">
  {@render children()}
</div>

<!-- Usage -->
<PageContainer>
  <h1>Title</h1>
  <p>Content</p>
</PageContainer>
```

**Good: Just use the class**
```svelte
<!-- No component needed -->
<div class="container mx-auto px-4">
  <h1>Title</h1>
  <p>Content</p>
</div>
```

## Prop Drilling Fix

**Bad: Drilling through layers**
```svelte
<!-- Page passes user through 4 levels -->
<Page {user}>
  <Dashboard {user}>
    <Sidebar {user}>
      <UserMenu {user} />  <!-- Finally used here -->
    </Sidebar>
  </Dashboard>
</Page>
```

**Good: Context for global data**
```svelte
<!-- +layout.svelte — set context once -->
<script>
  import { setContext } from 'svelte';
  let { data, children } = $props();
  setContext('user', data.user);
</script>

{@render children()}

<!-- UserMenu.svelte — consume directly -->
<script>
  import { getContext } from 'svelte';
  const user = getContext('user');
</script>
```

**Good: Restructure so data is closer**
```svelte
<!-- Dashboard.svelte — UserMenu is direct child now -->
<script>
  let { user } = $props();
</script>

<div class="flex">
  <Sidebar>
    <UserMenu {user} />
  </Sidebar>
  <MainContent />
</div>
```

## Slots vs Props

**Good: Slots for composition**
```svelte
<!-- Card.svelte -->
<script>
  let { header, children, footer } = $props();
</script>

<div class="border rounded-lg">
  {#if header}
    <div class="border-b p-4 font-semibold">
      {@render header()}
    </div>
  {/if}
  
  <div class="p-4">
    {@render children()}
  </div>
  
  {#if footer}
    <div class="border-t p-4 bg-gray-50">
      {@render footer()}
    </div>
  {/if}
</div>

<!-- Usage — flexible composition -->
<Card>
  {#snippet header()}
    <h3>Drone Details</h3>
  {/snippet}
  
  <p>Main content here</p>
  
  {#snippet footer()}
    <Button>Save</Button>
  {/snippet}
</Card>
```

**Less flexible: Props for everything**
```svelte
<!-- Card.svelte — rigid -->
<script>
  let { title, content, buttonText, onButtonClick } = $props();
</script>

<div class="border rounded-lg">
  <div class="border-b p-4 font-semibold">{title}</div>
  <div class="p-4">{content}</div>
  <div class="border-t p-4">
    <button onclick={onButtonClick}>{buttonText}</button>
  </div>
</div>
```