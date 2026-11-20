---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: deal
folder_name: Deals
file_prefix: DEAL_
ui_icon: Handshake
ui_color: '#9a3412'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Describe the opportunity and its next customer action. Link the actual company, state the currency for quoted amounts and leave the expected close date empty until estimated.
associated_rules:
- DEAL_RULES.md
field_config:
  stage:
    type: enum
    widget: select
    options:
    - value: discovery
      label: Discovery
    - value: proposal
      label: Proposal
    - value: negotiation
      label: Negotiation
    - value: won
      label: Won
    - value: lost
      label: Lost
  description:
    type: text
    widget: textarea
  company_ref:
    type: reference
    widget: entity-selector
    reference_type: company
  contact_ref:
    type: reference
    widget: entity-selector
    reference_type: contact
  amount:
    type: number
    widget: number
    min: 0
    step: 0.01
  currency:
    type: string
    widget: text
  expected_close:
    type: date
    widget: date
  deal_owner:
    type: string
    widget: text
  decision_criteria:
    type: text
    widget: textarea
  next_step:
    type: text
    widget: textarea
  next_contact_date:
    type: date
    widget: date
  deal_notes:
    type: text
    widget: textarea
stage: discovery
description: ''
company_ref: ''
contact_ref: ''
amount: null
currency: ''
expected_close: null
deal_owner: ''
decision_criteria: ''
next_step: ''
next_contact_date: null
deal_notes: ''
views:
  default: board
  enabled:
  - board
  - cards
  - table
  - calendar
  roles:
    title: name
    subtitle: deal_owner
    badges:
    - stage
    card_fields:
    - company_ref
    - amount
    - currency
    - expected_close
  board:
    group_by: stage
  calendar:
    date_field: next_contact_date
  table:
    columns:
    - key: name
    - key: company_ref
    - key: stage
    - key: amount
    - key: expected_close
  facets:
  - stage
  - deal_owner
---
# Deal
