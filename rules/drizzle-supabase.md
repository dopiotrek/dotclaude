---
paths:
  - "**/schema/**"
  - "**/migrations/**"
  - "**/*.sql"
---

# Drizzle + Supabase (schema & migrations)

Loads when editing schema, migrations, or SQL. Reinforces the `drizzle-migration-guard` and `supabase-rls-reminder` hooks.

- New table → add Row Level Security before it ships: `ENABLE ROW LEVEL SECURITY` plus a tenant-scoped policy, e.g. `organization_id = auth.jwt() ->> 'organization_id'`.
- No destructive schema change without explicit confirmation: never `DROP TABLE` / `DROP SCHEMA` / `TRUNCATE`, never `DELETE` without `WHERE`. Treat `DROP COLUMN`, `ALTER COLUMN TYPE`, and `SET NOT NULL` without a default as risky — flag before applying.
- Follow the existing schema conventions (`_meta.ts` base types, shared timestamps, id config) instead of inventing new ones.

(Parameterized queries and other security rules stay always-on in `CLAUDE.md` — they apply to query code too, not just schema files.)
