---
system_prompt: 'This biome is on a world that is not Earth. State the star, gravity, atmosphere, and day length, then let plants and animals follow from them. Life here should be unfamiliar but consistent: every creature eats something and is eaten by something.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: biome
rules:
- id: alien_biome_conditions
  category: design
  priority: high
  rule: State sunlight colour and strength, gravity, atmosphere, and temperature range.
  validation_type: warning
- id: alien_biome_food_chain
  category: ecology
  priority: high
  rule: Name at least one producer, one grazer, and one predator, and what each feeds on.
  validation_type: warning
- id: alien_biome_no_earth_copy
  category: design
  priority: medium
  rule: Avoid Earth species with a new colour. Change how life moves, feeds, or reproduces.
  validation_type: suggestion
- id: alien_biome_hazard
  category: design
  priority: medium
  rule: Give one hazard that comes from the environment itself.
  validation_type: suggestion
---

# Alien World Biomes

Ecosystems for other planets: unfamiliar life that still obeys its own physics and food chain.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the biome type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
