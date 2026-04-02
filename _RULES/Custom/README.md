# Custom Rules

This directory holds tenant-specific rule customizations.

Rules placed here override Standard/ rules for the tenant's project.
Files should follow the same YAML format as Standard/ and Core/ rules.

Custom rules are DB-backed per tenant — this directory is for local development
and reference only. Cloud tenants store custom rules in the content database.

## File Format

Same as Standard/ rules — YAML with required fields: `rule_id`, `name`, `applies_to`.

See `_Rules/Standard/character_consistency.yaml` for a complete example.
