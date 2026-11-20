---
global: false
entity_type: menu
template_reference: MENU_TEMPLATE.md
system_prompt: "Use the kitchen's approved vegan recipe records when planning a menu. Ask which recipe to use when there is no approved match."
rules:
  - id: menu_001
    category: recipe_selection
    rule: "Each menu item should link to an existing vegan_recipe with status approved. Flag draft, testing, retired or missing recipes for the cook to review."
    validation_type: warning
    applies_to: [menu]
    fields: [recipe_ids]
    references: {recipe_ids: [vegan_recipe]}
---
# Menu rules

Before marking a menu ready for service, open its linked recipes and check their approval status.
