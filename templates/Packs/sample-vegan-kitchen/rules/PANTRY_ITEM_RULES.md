---
global: false
entity_type: pantry_item
template_reference: PANTRY_ITEM_TEMPLATE.md
system_prompt: "Use the receiving record and product label for stock quantities, units and allergen declarations."
rules:
  - id: pantry_001
    category: stock_count
    rule: "Record the stock unit so the cook can compare quantity on hand with the reorder level."
    validation_type: suggestion
    applies_to: [pantry_item]
    required_fields: [stock_unit]
---
# Pantry item rules

Use one stock unit consistently for each counted product.
