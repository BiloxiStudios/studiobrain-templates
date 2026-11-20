---
id: "unique_lowercase_id"
name: "Pantry item name"
template_version: "1.0"
template_category: entity
entity_type: pantry_item
folder_name: PantryItems
file_prefix: PANTRY_
ui_icon: Package
ui_color: "#50734d"
editable: true
marketplace_eligible: true
associated_rules: [PANTRY_ITEM_RULES.md]
generation_instructions: |
  Record one ingredient or packaged product from the kitchen's stock count.
  Use the same unit for the quantity on hand and the reorder level. Copy the
  supplier, lot, dates and allergen declarations from the label or receiving
  record when available. Leave unknown facts empty.
field_config:
  status:
    type: enum
    widget: select
    options:
      - {value: active, label: In use}
      - {value: to_order, label: To order}
      - {value: retired, label: Retired}
  description: {type: text, widget: textarea}
  ingredient_group: {type: string, widget: text, help: "For example, pulse, grain, spice or chilled ingredient."}
  quantity_on_hand: {type: number, widget: number, min: 0, step: 0.01}
  stock_unit: {type: string, widget: text, help: "For example, kg, litres or tins."}
  reorder_level: {type: number, widget: number, min: 0, step: 0.01}
  storage_location: {type: string, widget: text}
  supplier: {type: string, widget: text}
  lot_code: {type: string, widget: text}
  received_date: {type: date, widget: date}
  best_before: {type: date, widget: date}
  label_allergens: {type: tags, widget: tag-input, allow_custom: true}
  handling_notes: {type: text, widget: textarea}
status: active
description: ""
ingredient_group: ""
quantity_on_hand: null
stock_unit: ""
reorder_level: null
storage_location: ""
supplier: ""
lot_code: ""
received_date: null
best_before: null
label_allergens: []
handling_notes: ""
views:
  default: table
  enabled: [table, board, calendar, cards]
  roles:
    title: name
    subtitle: storage_location
    badges: [ingredient_group, status]
    card_fields: [quantity_on_hand, stock_unit, best_before]
  table:
    columns: [{key: name}, {key: quantity_on_hand}, {key: stock_unit}, {key: reorder_level}, {key: storage_location}]
  board: {group_by: status}
  calendar: {date_field: best_before}
  facets: [status, ingredient_group, storage_location]
---
# Pantry item

## Receiving notes

Record changes to the supplier's label, pack size or storage instructions here.
