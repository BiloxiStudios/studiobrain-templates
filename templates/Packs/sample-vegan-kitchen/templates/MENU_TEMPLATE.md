---
id: "unique_lowercase_id"
name: "Menu name"
template_version: "1.0"
template_category: entity
entity_type: menu
folder_name: Menus
file_prefix: MENU_
ui_icon: Utensils
ui_color: "#a24c26"
editable: true
marketplace_eligible: true
associated_rules: [MENU_RULES.md]
generation_instructions: |
  Plan one service. Link existing approved vegan recipes and leave the selection
  empty when no approved recipe is known. Keep guest-facing copy in description
  and line instructions in service_notes. Leave dates, prices and headcounts
  empty until the kitchen supplies them.
field_config:
  status:
    type: enum
    widget: select
    options:
      - {value: draft, label: Draft}
      - {value: ready, label: Ready for service}
      - {value: served, label: Served}
  description: {type: text, widget: textarea}
  service_date: {type: date, widget: date}
  service_period:
    type: enum
    widget: select
    options:
      - {value: breakfast, label: Breakfast}
      - {value: lunch, label: Lunch}
      - {value: dinner, label: Dinner}
      - {value: event, label: Special event}
  venue: {type: string, widget: text}
  lead_cook: {type: string, widget: text}
  expected_guests: {type: integer, widget: number, min: 0}
  recipe_ids:
    type: references
    widget: entity-multiselect
    reference_type: vegan_recipe
    help: Select the approved recipes being served.
  menu_price: {type: number, widget: number, min: 0, step: 0.01}
  currency: {type: string, widget: text, help: Use the three-letter currency code for the menu price.}
  allergen_notes: {type: text, widget: textarea}
  service_notes: {type: text, widget: textarea}
status: draft
description: ""
service_date: null
service_period: ""
venue: ""
lead_cook: ""
expected_guests: null
recipe_ids: []
menu_price: null
currency: ""
allergen_notes: ""
service_notes: ""
views:
  default: board
  enabled: [board, table, calendar, cards]
  roles:
    title: name
    subtitle: venue
    badges: [service_period, status]
    card_fields: [service_date, expected_guests, lead_cook]
  board: {group_by: status}
  calendar: {date_field: service_date}
  facets: [status, service_period]
---
# Menu

## Service notes

Record the order of service, last-minute substitutions and handover details.
