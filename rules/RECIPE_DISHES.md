---
system_prompt: 'This item is a dish in a cookbook, or an ingredient used by one. For a dish, state what it is, how many it serves, preparation and cooking time, a full ingredient list with quantities and units, numbered method steps in the order a cook does them, and how to tell it is done. Use one unit system throughout and give oven temperatures. Note common allergens. For images and video: overhead or forty-five-degree food photography, natural window light from one side, a shallow depth of field, a plain plate on wood, linen, or stone, a garnish that is actually in the recipe, and visible texture such as steam, crumb, or glaze.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: item
rules:
- id: recipe_dish_ingredients
  category: design
  priority: high
  rule: List every ingredient with a quantity and a unit, in the order it is used.
  validation_type: warning
- id: recipe_dish_method
  category: design
  priority: high
  rule: Write the method as numbered steps, one action per step, with times and temperatures.
  validation_type: warning
- id: recipe_dish_yield_time
  category: design
  priority: high
  rule: State servings, preparation time, and cooking time.
  validation_type: warning
- id: recipe_dish_units
  category: consistency
  priority: medium
  rule: Use one unit system, metric or cups and ounces, throughout the project.
  validation_type: warning
- id: recipe_dish_allergens
  category: design
  priority: medium
  rule: 'Name any common allergens: nuts, dairy, gluten, eggs, shellfish, soy.'
  validation_type: suggestion
- id: recipe_dish_doneness
  category: design
  priority: low
  rule: Say how the cook can tell the dish is ready by look, feel, or temperature.
  validation_type: suggestion
---

# Recipe Dishes

Turn the item type into a cookbook: each item is a dish with ingredients, quantities, steps and a serving note.

How it maps onto the item type: the item is the dish (or an ingredient), the description holds the headnote, the crafting recipe field holds ingredients and method, the category and tags hold course and cuisine, and consumable is true. Game-only fields such as damage, defense and rarity can be left empty.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the item type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
