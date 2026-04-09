# Database Package - Development Guide

See @../../CLAUDE.md for general project guidelines and @../../apps/web/CLAUDE.md for SvelteKit integration patterns.

## Overview

`@dronelist/db` — Drizzle ORM + Supabase PostgreSQL. Manages schemas, migrations, seeds, and the db connection.

## Schema Organization

```
packages/db/schema/
├── _meta.ts              # Base types, timestamps, ID config, auth users
├── index.ts              # Re-exports all schemas
├── companies/            # Company entities, types, members
├── crm/                  # CRM accounts, deals, contacts, interactions
├── expenses/             # Expense tracking, categories, recurring periods
├── finance/              # Invoices, profitability
├── fleet/                # Equipment, maintenance, certifications
├── lookup/               # Service categories, industry verticals
├── missions/             # Missions, projects, tasks
├── organization/         # Organizations, members, invitations
├── platform/             # Accounts, subscriptions, billing, notifications
├── profile/              # Profiles, qualifications, portfolio
├── projects/             # Project management
└── tasks/                # Task management
```

## Key Conventions

### Enums — use `text()` + constants, not `pgEnum`

```typescript
// In module constants (client-safe)
export const STATUS = { ACTIVE: 'ACTIVE', INACTIVE: 'INACTIVE' } as const;

// In schema
status: t.text('status').notNull().default('ACTIVE'),
```

Existing `pgEnum` columns: leave as-is (5 total in `profile/availability.ts` and `platform/`).

### Custom IDs — prefixed via `generateId`

```typescript
import { generateId } from '../src/utils/generate-id';
import { ID_CONFIG } from './_meta';

id: t.varchar('id', { length: ID_CONFIG.ACCOUNT.TOTAL_LENGTH })
  .$defaultFn(() => generateId(ID_CONFIG.ACCOUNT.PREFIX, ID_CONFIG.ACCOUNT.RANDOM_LENGTH))
```

### Timestamps — always spread

```typescript
export const timestamps = {
  createdAt: t.timestamp('created_at').defaultNow().notNull(),
  updatedAt: t.timestamp('updated_at').defaultNow().notNull()
};

// In every table
...timestamps
```

### Imports

- `@dronelist/db` — db connection
- `@dronelist/db/schema` — schema definitions
- `$db` — path alias for db connection
- `#schema`, `#migrations`, `#seeds`, `#utils` — internal package aliases

## Commands

```bash
pnpm db:generate      # Generate migrations from schema changes
pnpm db:migrate       # Apply migrations
pnpm db:studio        # Open Drizzle Studio
pnpm db:push          # Push schema directly (dev only)

# Seeds (from packages/db)
DB_SEEDING=true tsx seed.ts
DB_SEEDING=true DB_ALLOW_SEED_OVERRIDE=true tsx seed.ts   # local Supabase
DB_SEEDING=true tsx seed.ts --reset --confirm              # DANGEROUS
```

## Migration Safety

- Always set `DB_MIGRATING=true` when running migrations
- Review generated SQL before applying
- Never run seeds in production (`DB_ALLOW_SEED_OVERRIDE` blocked when `NODE_ENV=production` or URL matches `db.*.supabase.co`)

## Seed Pattern (summary)

- Use `onConflictDoUpdate` — seeds must be idempotent
- Detect INSERT vs UPDATE via `xmax`: `String(result[0]?.xmax) === '0'` → INSERT
- Export both `seedMyTable()` (specific) and `seed()` (orchestrator wrapper)
- Use package imports only: `@dronelist/db`, never `$db` or relative paths
- Template: `./seeds/_TEMPLATE-seed.ts`

For full seed patterns and troubleshooting: `@../../.docs/architecture/seed-patterns.md`

## Schema Changes Workflow

1. Edit files in `./schema/`
2. `pnpm db:generate` → review generated migration
3. `pnpm db:migrate`

## Documentation

- Architecture decisions: `.docs/architecture/`
- Migration plans/reports: `.docs/migrations/`
- Seed reference: `.docs/architecture/seed-patterns.md`
