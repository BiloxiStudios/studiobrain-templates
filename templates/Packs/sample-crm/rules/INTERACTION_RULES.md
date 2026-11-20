---
global: false
entity_type: interaction
template_reference: INTERACTION_TEMPLATE.md
rules:
- id: crm_private_data
  rule: Keep credentials and payment card data out of interaction notes, outcomes and follow-up text.
  validation_type: error
  fields:
  - notes
  - outcome
  - next_step
  forbidden_terms:
  - password
  - cvv
  - card number
  applies_to:
  - interaction
---
# Interaction rules
