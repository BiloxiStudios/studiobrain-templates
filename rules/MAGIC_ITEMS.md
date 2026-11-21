---
system_prompt: This item is magical. Give it a maker or origin, one clear effect, and a limit or cost so it cannot solve every problem. Its look should hint at what it does.
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: item
rules:
- id: magic_item_effect
  category: design
  priority: high
  rule: State one primary effect in a single sentence.
  validation_type: warning
- id: magic_item_limit
  category: balance
  priority: high
  rule: 'State a limit: charges, a condition, a cost to the user, or a drawback.'
  validation_type: warning
- id: magic_item_origin
  category: lore
  priority: medium
  rule: Say who made it or where it came from, using people and places in the project.
  validation_type: suggestion
- id: magic_item_appearance
  category: design
  priority: low
  rule: Describe one visual detail that hints at its power.
  validation_type: suggestion
---

# Magic Items

Enchanted objects with an origin, a limit and a price for using them.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the item type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
