---
system_prompt: 'This location is on a nineteenth-century frontier in a western. State what brought people here (cattle, silver, a railway, a river crossing), who holds power, and how far it is to the next town or fort. In visual descriptions use wide open land under a big sky, a single dusty main street with false-front timber buildings, hitching rails, a water tower or well, heat haze, hard noon light or a low golden sun, and a palette of dust, timber, and sky. Keep buildings, transport, and communication at the technology of the period.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: western_loc_reason
  category: lore
  priority: high
  rule: 'State why the settlement or site exists: the resource, route, or crossing that supports it.'
  validation_type: warning
- id: western_loc_power
  category: lore
  priority: medium
  rule: Say who holds power here and who keeps the law, if anyone does.
  validation_type: suggestion
- id: western_loc_distance
  category: design
  priority: medium
  rule: Give the distance and travel time to the nearest other settlement.
  validation_type: suggestion
- id: western_loc_period_tech
  category: consistency
  priority: high
  rule: Keep buildings, transport, and communication to what existed in the stated year.
  validation_type: warning
- id: western_loc_landscape
  category: design
  priority: medium
  rule: 'Describe the land around it: terrain, water, and weather.'
  validation_type: suggestion
---

# Western Locations

Frontier towns, ranches and trails: who owns the water, who keeps the law, how far the next town is.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
