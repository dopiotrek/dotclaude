# Seed Patterns Reference

## Seed File Structure

Every seed file in `./seeds/` must follow this pattern:

```typescript
import { db } from '@dronelist/db';
import { myTable } from '@dronelist/db/schema';
import { sql } from 'drizzle-orm';

export const MY_TABLE_SEED_DATA = [
  { slug: 'item-1', name: 'Item 1' },
  { slug: 'item-2', name: 'Item 2' }
];

export async function seedMyTable() {
  console.log('🔵 Seeding My Table...');
  const operationCounts = { created: 0, updated: 0, skipped: 0 };

  for (const item of MY_TABLE_SEED_DATA) {
    try {
      const result = await db
        .insert(myTable)
        .values(item as typeof myTable.$inferInsert)
        .onConflictDoUpdate({
          target: myTable.slug,
          set: {
            name: sql.raw(`excluded."name"`),
            updatedAt: new Date()
          }
        })
        .returning({ id: myTable.id, xmax: sql`xmax` });

      if (String(result[0]?.xmax) === '0') {
        console.log(`   ✔ INSERTED: ${item.slug} (${item.name})`);
        operationCounts.created++;
      } else {
        console.log(`   ↻ UPDATED: ${item.slug} (${item.name})`);
        operationCounts.updated++;
      }
    } catch (error) {
      console.error(`   ❌ ERROR processing ${item.slug}:`, error);
      operationCounts.skipped++;
      throw error;
    }
  }

  console.log(
    `✔ My Table completed: ${operationCounts.created} created, ` +
    `${operationCounts.updated} updated, ${operationCounts.skipped} skipped`
  );
}

export async function seed() {
  try {
    await seedMyTable();
    return { success: true };
  } catch (error: unknown) {
    console.error('🔴 Error running my table seed script:');
    if (error instanceof Error) {
      console.error(`   Message: ${error.message}`);
      if (error.stack) console.error(`   Stack: ${error.stack}`);
    } else {
      console.error(error);
    }
    throw error;
  }
}
```

## Rules

- **Always use `onConflictDoUpdate`** — seeds must be idempotent
- **Detect INSERT vs UPDATE via `xmax`**: `String(result[0]?.xmax) === '0'` → INSERT
- **Export two functions**: `seedMyTable()` (specific) and `seed()` (orchestrator wrapper)
- **Package imports only**: `@dronelist/db`, never `$db` or relative paths
- **Re-throw errors** — stop on first failure, don't silently skip

## Logging Standards

- `🔵` — starting seed operation
- `✔` — successful INSERT
- `↻` — successful UPDATE
- `❌` — error
- `⚠️` — warning (e.g. skipping due to missing dependency)

## Seeds with Dependencies

```typescript
export async function seed(profileId?: string, organizationId?: string) {
  try {
    let targetProfileId = profileId;
    let targetOrganizationId = organizationId;

    if (!targetProfileId || !targetOrganizationId) {
      const profile = await db.query.profiles.findFirst();
      if (!profile) {
        console.warn('⚠️ No profiles found. Skipping seed.');
        return { success: true, skipped: true };
      }
      targetProfileId = profile.id;

      const membership = await db.query.organizationMembers.findFirst({
        where: (m, { eq }) => eq(m.profileId, profile.id),
        with: { organization: true }
      });
      if (!membership?.organization) {
        console.warn('⚠️ Profile has no organization. Skipping seed.');
        return { success: true, skipped: true };
      }
      targetOrganizationId = membership.organization.id;
    }

    await seedMyTable(targetProfileId, targetOrganizationId);
    return { success: true };
  } catch (error) {
    throw error;
  }
}
```

## Hierarchical Data (Parent-Child)

```typescript
const SEED_DATA = [
  { seedId: 1, parentSeedId: null, slug: 'parent' },
  { seedId: 2, parentSeedId: 1, slug: 'child' }
];

const seedIdToDbIdMap = new Map<number, string>();
const sortedData = [...SEED_DATA].sort((a, b) => a.level - b.level);

for (const item of sortedData) {
  const { seedId, parentSeedId, ...insertData } = item;
  const dbParentId = parentSeedId ? seedIdToDbIdMap.get(parentSeedId) : null;

  const result = await db
    .insert(table)
    .values({ ...insertData, parentId: dbParentId })
    .returning({ id: table.id });

  seedIdToDbIdMap.set(seedId, result[0].id);
}
```

## Adding a New Seed

```bash
cp packages/db/seeds/_TEMPLATE-seed.ts packages/db/seeds/my-table-seed.ts
```

Then register in `packages/db/seed.ts`:

```typescript
import { seed as seedMyTable } from './seeds/my-table-seed';

const SEEDS_TO_RUN = [
  { name: 'My Table', func: seedMyTable }
];
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| unique constraint violation | Missing `onConflictDoUpdate` | Add upsert pattern |
| relation does not exist | Migrations not applied | `pnpm db:migrate` first |
| DB_SEEDING is not set | Missing env var | Prefix with `DB_SEEDING=true` |
| Creates duplicates | Wrong conflict target | Check unique constraint matches `onConflictDoUpdate` target |
