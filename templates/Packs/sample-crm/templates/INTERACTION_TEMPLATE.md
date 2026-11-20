---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: interaction
folder_name: Interactions
file_prefix: INTERACTION_
ui_icon: MessagesSquare
ui_color: '#115e59'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Record a factual account of a business conversation. Summarize the outcome and the agreed next step. Omit credentials, payment card data and secrets.
associated_rules:
- INTERACTION_RULES.md
field_config:
  interaction_kind:
    type: enum
    widget: select
    options:
    - value: call
      label: Call
    - value: email
      label: Email
    - value: meeting
      label: Meeting
    - value: message
      label: Message
  occurred_on:
    type: date
    widget: date
  company_ref:
    type: reference
    widget: entity-selector
    reference_type: company
  participant_refs:
    type: references
    widget: entity-multiselect
    reference_type: contact
  deal_ref:
    type: reference
    widget: entity-selector
    reference_type: deal
  notes:
    type: text
    widget: textarea
  outcome:
    type: text
    widget: textarea
  recorded_by:
    type: string
    widget: text
  commitments:
    type: tags
    widget: tag-input
    allow_custom: true
  next_step:
    type: text
    widget: textarea
  next_contact_date:
    type: date
    widget: date
  follow_up_owner:
    type: string
    widget: text
interaction_kind: ''
occurred_on: null
company_ref: ''
participant_refs: []
deal_ref: ''
notes: ''
outcome: ''
recorded_by: ''
commitments: []
next_step: ''
next_contact_date: null
follow_up_owner: ''
views:
  default: calendar
  enabled:
  - calendar
  - cards
  - table
  roles:
    title: name
    subtitle: recorded_by
    badges:
    - interaction_kind
    card_fields:
    - company_ref
    - next_step
    - follow_up_owner
  calendar:
    date_field: next_contact_date
  table:
    columns:
    - key: name
    - key: occurred_on
    - key: company_ref
    - key: next_contact_date
---
# Interaction
