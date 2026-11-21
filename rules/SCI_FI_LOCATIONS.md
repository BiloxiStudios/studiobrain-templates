---
system_prompt: This location is in a science fiction setting. State where it is (planet surface, orbit, deep space, underground), what keeps people alive there, and who built it. Technology must match the level the project records. Describe what a visitor hears, smells, and feels, not only what they see.
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: scifi_environment
  category: design
  priority: high
  rule: State gravity, atmosphere, and what provides air, power, and water.
  validation_type: warning
- id: scifi_tech_level
  category: consistency
  priority: high
  rule: Keep technology at the level the project records. Do not add faster-than-light travel, AI, or weapons the project has not established.
  validation_type: warning
- id: scifi_builders
  category: lore
  priority: medium
  rule: Say who built the place, how old it is, and what it was first meant for.
  validation_type: suggestion
- id: scifi_wear
  category: design
  priority: low
  rule: 'Show age and use: repairs, improvised fixes, or sections that no longer work.'
  validation_type: suggestion
---

# Sci-Fi Locations

Stations, ships, colonies and alien worlds with a stated environment and technology level.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
