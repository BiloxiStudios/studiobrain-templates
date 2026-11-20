---
global: false
entity_type: finding
template_reference: FINDING_TEMPLATE.md
rules:
- id: finding_source
  rule: Cite at least one existing source that supports this finding.
  validation_type: warning
  required_fields:
  - source_refs
  references:
    source_refs:
    - source
  applies_to:
  - finding
- id: finding_confidence
  rule: State the confidence warranted by the available evidence.
  validation_type: suggestion
  required_fields:
  - confidence
  applies_to:
  - finding
---
# Finding rules
