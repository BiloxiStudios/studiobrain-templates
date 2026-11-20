---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: supplier
folder_name: Suppliers
file_prefix: SUPPLIER_
ui_icon: Truck
ui_color: '#475569'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Record the supplier’s ordering details and the terms actually agreed. Use the supplied ordering contact and leave commercial terms empty if they have not been agreed.
associated_rules: []
field_config:
  status:
    type: enum
    widget: select
    options:
    - value: active
      label: Active
    - value: on_hold
      label: On hold
    - value: retired
      label: Retired
  description:
    type: text
    widget: textarea
  supplier_code:
    type: string
    widget: text
  website:
    type: url
    widget: url
  ordering_contact:
    type: string
    widget: text
  ordering_email:
    type: email
    widget: email
  ordering_phone:
    type: string
    widget: text
  lead_days:
    type: integer
    widget: number
    min: 0
  min_order:
    type: string
    widget: text
  payment_terms:
    type: string
    widget: text
  delivery_region:
    type: string
    widget: text
  ordering_notes:
    type: text
    widget: textarea
status: active
description: ''
supplier_code: ''
website: ''
ordering_contact: ''
ordering_email: ''
ordering_phone: ''
lead_days: null
min_order: ''
payment_terms: ''
delivery_region: ''
ordering_notes: ''
views:
  default: table
  enabled:
  - table
  - cards
  - board
  roles:
    title: name
    subtitle: supplier_code
    badges:
    - status
    card_fields:
    - ordering_contact
    - lead_days
    - delivery_region
  board:
    group_by: status
  table:
    columns:
    - key: name
    - key: supplier_code
    - key: ordering_contact
    - key: lead_days
    - key: status
---
# Supplier
