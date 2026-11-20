---
global: false
entity_type: deal
template_reference: DEAL_TEMPLATE.md
rules:
- id: deal_company
  rule: Connect the deal to an existing company account.
  validation_type: warning
  required_fields:
  - company_ref
  references:
    company_ref:
    - company
  applies_to:
  - deal
- id: deal_next_step
  rule: Record the next customer action before the next review.
  validation_type: suggestion
  required_fields:
  - next_step
  applies_to:
  - deal
---
# Deal rules
