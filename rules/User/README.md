# User Rules

This directory holds user-created rules for this project.

Rules placed here are project-specific and take lowest priority in the resolution chain:
Standard > Core > Custom > User

User rules can be created from the StudioBrain UI or by adding YAML files here directly.
They are scoped to this project and not shared across tenants.

## File Format

Same as Standard/ rules — YAML with required fields: `rule_id`, `name`, `applies_to`.

A new rule defaults to `validation_type: warning` (or `severity: warning`). Warning, info, and suggestion are recorded and do not block. `error` blocks a write. A starter pack keeps one `error` example. Do not add another.

See `_Rules/Standard/character_consistency.yaml` for a complete example.
