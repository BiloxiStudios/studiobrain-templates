---
system_prompt: 'This location exists after the collapse of civilisation. State what the place was before, what ended the old world and how long ago, and what makes the place worth holding now: clean water, shelter, fuel, walls, or seed. Show time passing through nature and decay. In visual descriptions use rusted vehicles, collapsed concrete with plants growing through, sun-bleached signage, structures patched with scrap, salvaged solar panels and rain barrels, dust or overgrowth depending on climate, and a faded palette with a few bright salvaged colours. Keep the cause and date of the collapse the same as the project records.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: postapoc_loc_before
  category: lore
  priority: high
  rule: State what the place was before the collapse and one recognisable remnant of that use.
  validation_type: warning
- id: postapoc_loc_cause
  category: consistency
  priority: high
  rule: Keep the cause of the collapse and the years since consistent with the project.
  validation_type: warning
- id: postapoc_loc_resource
  category: design
  priority: high
  rule: Name the resource that makes the place valuable and who controls it.
  validation_type: warning
- id: postapoc_loc_decay
  category: design
  priority: medium
  rule: 'Show decay that matches the time elapsed: rust, plant growth, collapse, or sand.'
  validation_type: suggestion
- id: postapoc_loc_improvised
  category: design
  priority: medium
  rule: Describe one improvised repair or reuse of an old-world object.
  validation_type: suggestion
---

# Post-Apocalyptic Locations

Ruins and refuges after the collapse: what it was, what broke the world, what people fight over now.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
