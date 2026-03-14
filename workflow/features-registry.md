# Features Registry

When creating, updating, or removing a feature, update `.claude/features.json`.

Read this file at the start of any feature work to understand what exists. The registry tracks:
- Feature status: `shipped` | `in-progress` | `planned` | `paused` | `deprecated`
- Routes, dependencies, and notes
- Timeline (plannedAt, shippedAt, updatedAt)

When a feature's status changes, update both `features.json` and the `lastUpdated` field.
