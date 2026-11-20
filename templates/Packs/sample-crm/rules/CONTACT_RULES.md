---
global: false
entity_type: contact
template_reference: CONTACT_TEMPLATE.md
rules:
- id: contact_method
  rule: Check that the contact has at least one reachable work email address or phone number.
  validation_type: warning
  fields:
  - email_address
  - phone_number
  applies_to:
  - contact
---
# Contact rules
