---
system_prompt: This character lives in a fantasy world. Place them inside the project's own ancestries, magic, and social order. Magic must have a source, a cost, and a limit. Avoid modern technology and modern slang unless the project records them.
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: fantasy_ancestry
  category: identity
  priority: medium
  rule: Use an ancestry or people the project already records, or state clearly that a new one is being introduced.
  validation_type: warning
- id: fantasy_magic_cost
  category: lore
  priority: high
  rule: If the character uses magic, state its source, what it costs them, and one thing it cannot do.
  validation_type: warning
- id: fantasy_no_modern
  category: tone
  priority: medium
  rule: Do not use modern technology, brands, or slang unless the project records them.
  validation_type: warning
- id: fantasy_station
  category: lore
  priority: low
  rule: 'State the character''s place in society: trade, rank, guild, or allegiance.'
  validation_type: suggestion
---

# Fantasy Characters

Heroes, villains and townsfolk for a fantasy world with a consistent magic and ancestry system.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
