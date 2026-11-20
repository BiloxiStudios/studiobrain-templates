---
global: false
entity_type: source
template_reference: SOURCE_TEMPLATE.md
rules:
- id: source_locator
  rule: Supply a source URL or a retrievable citation so another researcher can find the original.
  validation_type: warning
  fields:
  - source_url
  - citation
  applies_to:
  - source
---
# Source rules
