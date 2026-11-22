---
system_prompt: 'This location is in a cyberpunk city: advanced technology, extreme inequality, and corporate power in place of government. State who owns the place, who actually uses it, and what is watching. Show the gap between rich and poor in one view. In visual descriptions use night, rain, wet reflective streets, crowded vertical architecture, layered signage and holographic adverts in several languages, exposed cables and pipes, steam vents, market stalls under expressways, and neon magenta, cyan, and acid green against deep shadow. Keep the technology level to what the project records.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: cyberpunk_loc_owner
  category: lore
  priority: high
  rule: State which company, gang, or authority owns or controls the place.
  validation_type: warning
- id: cyberpunk_loc_inequality
  category: design
  priority: high
  rule: 'Show wealth and poverty in the same description: what is above, what is below.'
  validation_type: warning
- id: cyberpunk_loc_surveillance
  category: design
  priority: medium
  rule: Say what records or watches people here and who sees the data.
  validation_type: suggestion
- id: cyberpunk_loc_layers
  category: design
  priority: medium
  rule: 'Describe the vertical layers: street, mid-level walkways, and rooftops or towers.'
  validation_type: suggestion
- id: cyberpunk_loc_tech_level
  category: consistency
  priority: high
  rule: Keep implants, networks, and weapons at the level the project has established.
  validation_type: warning
---

# Cyberpunk Locations

Dense near-future city spaces: corporate towers above, improvised street life below, screens everywhere.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
