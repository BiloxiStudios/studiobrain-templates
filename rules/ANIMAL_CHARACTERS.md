---
system_prompt: 'This character is an animal. Name the real species and decide how human it is: a natural animal, a talking animal on four legs, or a fully anthropomorphic one that walks upright and wears clothes. Keep that level the same for every animal character in the project. Let the species show in size, movement, diet, and temperament.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: animal_species
  category: identity
  priority: high
  rule: Name a specific species or breed, not just a broad group such as 'bird' or 'dog'.
  validation_type: warning
- id: animal_anthro_level
  category: design
  priority: high
  rule: State how anthropomorphic the character is (natural, talking, or fully upright and clothed) and match the level the project already uses.
  validation_type: warning
- id: animal_traits
  category: design
  priority: medium
  rule: Carry at least two real traits of the species into personality or ability, such as a fox's caution or an owl's night vision.
  validation_type: suggestion
- id: animal_scale
  category: consistency
  priority: medium
  rule: Keep relative sizes believable between species, or state the world's rule if every animal is the same size.
  validation_type: warning
- id: animal_predator_prey
  category: lore
  priority: low
  rule: Say how the world handles predators and prey living together if both appear.
  validation_type: suggestion
---

# Animal Characters

Talking or anthropomorphic animals: pick the species, pick how human they are, and stay consistent.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
