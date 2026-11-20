---
system_prompt: "Write a vegan recipe for this kitchen. Use only plant-based ingredients: no meat, poultry, fish, shellfish, dairy, eggs, honey or gelatin. Name each plant-based product exactly (oat milk, not milk). Follow the vegan recipe template."
global: false
priority: high
entity_type: vegan_recipe
template_reference: VEGAN_RECIPE_TEMPLATE.md

rules:
# The one blocking rule in this pack. A recipe that names meat, poultry, fish
# or shellfish is refused on save and on generation.
- id: vegan_001
  category: dietary
  priority: critical
  rule: "No meat, poultry, fish or shellfish in any ingredient, step or note."
  validation_type: error
  applies_to: [vegan_recipe]
  fields: [name, description, ingredients, steps, chef_notes, protein_source]
  forbidden_terms:
    - beef
    - steak
    - veal
    - pork
    - bacon
    - ham
    - prosciutto
    - pancetta
    - chorizo
    - salami
    - sausage
    - lard
    - lamb
    - mutton
    - goat meat
    - venison
    - chicken
    - turkey
    - duck
    - goose
    - quail
    - fish
    - salmon
    - tuna
    - cod
    - anchovy
    - anchovies
    - sardine
    - sardines
    - mackerel
    - shrimp
    - prawn
    - prawns
    - crab
    - lobster
    - oyster
    - oysters
    - mussel
    - mussels
    - clam
    - clams
    - scallop
    - scallops
    - squid
    - octopus
    - fish sauce
    - oyster sauce
    - bone broth
    - chicken stock
    - beef stock
  # Plant-based products whose names contain a forbidden word. No evaluator
  # reads this key yet (work item R3 in the report adds it). Until then a
  # recipe that names one of these is refused.
  allowed_phrases:
    - jackfruit pulled pork
    - vegan sausage
    - plant-based sausage
    - vegan fish sauce
    - mushroom oyster sauce
    - king oyster mushroom
    - oyster mushroom
    - oyster mushrooms
    - hen of the woods
    - chicken of the woods

# Non-blocking: the save succeeds and the cook is asked to confirm.
- id: vegan_002
  category: dietary
  priority: high
  rule: "Animal by-products are not vegan: dairy, eggs, honey, gelatin and similar. Name the plant-based product instead."
  validation_type: warning
  applies_to: [vegan_recipe]
  fields: [ingredients, steps, chef_notes]
  forbidden_terms:
    - milk
    - butter
    - ghee
    - cream
    - cheese
    - yogurt
    - yoghurt
    - whey
    - casein
    - egg
    - eggs
    - mayonnaise
    - honey
    - gelatin
    - gelatine
    - beeswax
    - shellac
    - carmine
    - isinglass
  allowed_phrases:
    - oat milk
    - soy milk
    - almond milk
    - coconut milk
    - rice milk
    - peanut butter
    - almond butter
    - cashew butter
    - cocoa butter
    - vegan butter
    - coconut cream
    - cashew cream
    - oat cream
    - vegan cheese
    - cashew cheese
    - nutritional yeast
    - coconut yogurt
    - soy yogurt
    - vegan mayonnaise
    - flax egg
    - chia egg

- id: vegan_003
  category: completeness
  priority: high
  rule: "A recipe needs ingredients, steps and a serving count before it goes to testing."
  validation_type: warning
  applies_to: [vegan_recipe]
  required_fields: [ingredients, steps, servings]

- id: vegan_004
  category: safety
  priority: medium
  rule: "List every allergen the dish contains. A dish with none says so in the chef notes."
  validation_type: suggestion
  applies_to: [vegan_recipe]
  required_fields: [allergens]

- id: vegan_005
  category: style
  priority: low
  rule: "Give quantities in the units this kitchen uses, and write one action per step."
  validation_type: info
  applies_to: [vegan_recipe]
---

# Vegan recipe guidance

These rules keep the menu vegan and the recipes usable on the line.

`vegan_001` is the only rule that blocks. It refuses a recipe that names meat, poultry, fish or shellfish in its name, description, ingredients, steps, notes or protein source. Everything else is recorded and does not block a save or a generation.

`vegan_002` warns on animal by-products. Many vegan products carry the old name (oat milk, peanut butter, vegan cheese), so this rule warns and never blocks. Write the full plant-based name and the warning goes away once the allow-list is honoured.

Term lists catch the common cases. They do not catch a brand name, a dish name such as carbonara, or another language. A kitchen that needs that adds its own terms here.
