---
system_prompt: 'This location is in a fantasy world. Tie it to the land around it and to the project''s history: who founded it, who holds it now, and what it trades or guards. Magic present here must follow the project''s rules for magic.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: fantasy_loc_reason
  category: lore
  priority: high
  rule: 'Give the reason the place exists where it does: water, a road, a mine, a holy site, a border.'
  validation_type: warning
- id: fantasy_loc_holder
  category: lore
  priority: medium
  rule: Name who controls the place now and one group that would like to.
  validation_type: warning
- id: fantasy_loc_magic
  category: consistency
  priority: medium
  rule: Any magical feature must follow the magic rules the project records.
  validation_type: warning
- id: fantasy_loc_hook
  category: story
  priority: low
  rule: Include one rumour, danger, or secret that could start a story here.
  validation_type: suggestion
---

# Fantasy Locations

Villages, keeps, ruins and wild places that feel lived in and fit the world's history.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
