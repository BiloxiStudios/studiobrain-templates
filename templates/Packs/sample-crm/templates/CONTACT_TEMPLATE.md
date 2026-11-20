---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: contact
folder_name: Contacts
file_prefix: CONTACT_
ui_icon: Contact
ui_color: '#4338ca'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Capture the person’s supplied business contact information and follow-up preferences. Leave unknown details empty. Keep notes free of credentials and payment card data.
associated_rules:
- CONTACT_RULES.md
field_config:
  status:
    type: enum
    widget: select
    options:
    - value: prospect
      label: Prospect
    - value: active
      label: Active
    - value: inactive
      label: Inactive
  job_title:
    type: string
    widget: text
  company_ref:
    type: reference
    widget: entity-selector
    reference_type: company
  email_address:
    type: email
    widget: email
  phone_number:
    type: string
    widget: text
  contact_preference:
    type: enum
    widget: select
    options:
    - value: email
      label: Email
    - value: phone
      label: Phone
    - value: meeting
      label: Meeting
  relationship_owner:
    type: string
    widget: text
  last_contact_date:
    type: date
    widget: date
  next_contact_date:
    type: date
    widget: date
  next_step:
    type: text
    widget: textarea
  business_interests:
    type: tags
    widget: tag-input
    allow_custom: true
  contact_notes:
    type: text
    widget: textarea
status: prospect
job_title: ''
company_ref: ''
email_address: ''
phone_number: ''
contact_preference: ''
relationship_owner: ''
last_contact_date: null
next_contact_date: null
next_step: ''
business_interests: []
contact_notes: ''
views:
  default: table
  enabled:
  - table
  - cards
  - board
  - calendar
  roles:
    title: name
    subtitle: job_title
    badges:
    - status
    card_fields:
    - company_ref
    - relationship_owner
    - next_contact_date
  board:
    group_by: status
  calendar:
    date_field: next_contact_date
  table:
    columns:
    - key: name
    - key: company_ref
    - key: email_address
    - key: phone_number
    - key: next_contact_date
  facets:
  - status
  - relationship_owner
---
# Contact
