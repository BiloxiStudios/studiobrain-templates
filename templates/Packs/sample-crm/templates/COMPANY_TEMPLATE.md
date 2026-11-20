---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: company
folder_name: Companies
file_prefix: COMPANY_
ui_icon: Building2
ui_color: '#0e7490'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Summarize the business from known account information. Link the actual primary contact, and leave company size or commercial details unspecified when unknown.
associated_rules: []
field_config:
  status:
    type: enum
    widget: select
    options:
    - value: prospect
      label: Prospect
    - value: customer
      label: Customer
    - value: former
      label: Former
  description:
    type: text
    widget: textarea
  industry:
    type: string
    widget: text
  website:
    type: url
    widget: url
  account_owner:
    type: string
    widget: text
  primary_contact:
    type: reference
    widget: entity-selector
    reference_type: contact
  headquarters:
    type: string
    widget: text
  territory:
    type: string
    widget: text
  account_tier:
    type: string
    widget: text
  next_review:
    type: date
    widget: date
  priorities:
    type: tags
    widget: tag-input
    allow_custom: true
  account_notes:
    type: text
    widget: textarea
status: prospect
description: ''
industry: ''
website: ''
account_owner: ''
primary_contact: ''
headquarters: ''
territory: ''
account_tier: ''
next_review: null
priorities: []
account_notes: ''
views:
  default: table
  enabled:
  - table
  - cards
  - calendar
  roles:
    title: name
    subtitle: industry
    badges:
    - status
    - account_tier
    card_fields:
    - primary_contact
    - account_owner
    - territory
  calendar:
    date_field: next_review
  table:
    columns:
    - key: name
    - key: industry
    - key: account_owner
    - key: primary_contact
    - key: next_review
---
# Company
