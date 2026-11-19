# Custom Rules

This directory holds tenant-specific rule customizations.

Rules placed here override Standard/ rules for the tenant's project.
Files should follow the same YAML format as Standard/ and Core/ rules.

Custom rules are DB-backed per tenant — this directory is for local development
and reference only. Cloud tenants store custom rules in the content database.

## File Format

Same as Standard/ rules — YAML with required fields: `rule_id`, `name`, `applies_to`.

A new rule defaults to `validation_type: warning` (or `severity: warning`). Use `error` only when accepting the write would store unsafe or corrupt data. Warning, info, and suggestion are recorded and do not block.

See `_Rules/Standard/character_consistency.yaml` for a complete example.
