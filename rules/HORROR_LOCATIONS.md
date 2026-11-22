---
system_prompt: 'This location is a setting for horror. State why help cannot easily reach it, what happened here before, and how many ways out there are. Build dread through sound, smell, temperature, and one thing that is out of place, before anything is seen. In visual descriptions use darkness with a single weak light source, long empty corridors or tree lines, decay, and cold desaturated colour with one sickly accent. Keep the layout consistent so that readers can fear a specific door or stair.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: horror_loc_isolation
  category: design
  priority: high
  rule: State why people here cannot easily leave or call for help.
  validation_type: warning
- id: horror_loc_history
  category: lore
  priority: high
  rule: Say what harm happened here before and what trace of it remains.
  validation_type: warning
- id: horror_loc_exits
  category: design
  priority: medium
  rule: List the exits and say which are blocked, locked, or dangerous.
  validation_type: suggestion
- id: horror_loc_senses
  category: design
  priority: medium
  rule: Describe one sound, one smell, and the temperature before describing what is seen.
  validation_type: suggestion
- id: horror_loc_wrong_thing
  category: design
  priority: medium
  rule: Include one object or detail that should not be there.
  validation_type: suggestion
---

# Horror Locations

Places that frighten: isolation, a history of harm, limited exits and one thing that is not right.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
