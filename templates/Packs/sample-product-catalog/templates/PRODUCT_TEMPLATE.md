---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: product
folder_name: Products
file_prefix: PRODUCT_
ui_icon: ShoppingBag
ui_color: '#155e75'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Write store copy from the supplied specifications. Keep price and currency together. Use the chosen supplier record and leave unknown product claims empty.
associated_rules:
- PRODUCT_RULES.md
field_config:
  status:
    type: enum
    widget: select
    options:
    - value: draft
      label: Draft
    - value: active
      label: Active
    - value: retired
      label: Retired
  primary_image:
    type: image
    widget: image-ref
  description:
    type: text
    widget: textarea
  sku:
    type: string
    widget: text
  unit_price:
    type: number
    widget: number
    min: 0
    step: 0.01
  currency:
    type: string
    widget: text
  stock_on_hand:
    type: integer
    widget: number
    min: 0
  stock_unit:
    type: string
    widget: text
  supplier_ref:
    type: reference
    widget: entity-selector
    reference_type: supplier
  variant_rows:
    type: array
    widget: object-array
    sub_fields:
    - key: name
      label: Variant
      ui_component: text
    - key: sku
      label: Variant SKU
      ui_component: text
    - key: stock
      label: Units in stock
      ui_component: number
    - key: price
      label: Unit price
      ui_component: number
  materials:
    type: tags
    widget: tag-input
    allow_custom: true
  care_notes:
    type: text
    widget: textarea
  merchandising_notes:
    type: text
    widget: textarea
status: draft
primary_image: ''
description: ''
sku: ''
unit_price: null
currency: ''
stock_on_hand: null
stock_unit: ''
supplier_ref: ''
variant_rows: []
materials: []
care_notes: ''
merchandising_notes: ''
views:
  default: gallery
  enabled:
  - gallery
  - cards
  - table
  - board
  roles:
    title: name
    subtitle: sku
    badges:
    - status
    card_fields:
    - unit_price
    - currency
    - stock_on_hand
    - stock_unit
    image: primary_image
  board:
    group_by: status
  gallery:
    aspect: landscape
  table:
    columns:
    - key: name
    - key: sku
    - key: unit_price
    - key: currency
    - key: stock_on_hand
    - key: supplier_ref
  facets:
  - status
  - materials
---
# Product
