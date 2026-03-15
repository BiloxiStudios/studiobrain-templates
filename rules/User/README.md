# User Rules

This directory holds user-created rules for this project.

Rules placed here are project-specific and take lowest priority in the resolution chain:
Standard > Core > Custom > User

User rules can be created from the StudioBrain UI or by adding YAML files here directly.
They are scoped to this project and not shared across tenants.

## File Format

Same as Standard/ rules — YAML with required fields: `rule_id`, `name`, `applies_to`.

See `_Rules/Standard/character_consistency.yaml` for a complete example.
