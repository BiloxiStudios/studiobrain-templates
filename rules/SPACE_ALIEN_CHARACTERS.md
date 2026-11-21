---
system_prompt: 'This character is a non-human being from another world. Start from the species: its home environment, body plan, senses, and how it communicates. Let those facts shape personality, culture, clothing, and speech. Do not write a human with a cosmetic change. Keep the species consistent with any other member of it the project already records.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: alien_species_basis
  category: design
  priority: high
  rule: State the species and the home environment it evolved in, and make at least two physical traits follow from that environment.
  validation_type: warning
- id: alien_senses
  category: design
  priority: medium
  rule: Describe how the character senses the world and communicates. If it is not sight and speech, show how that changes daily life.
  validation_type: suggestion
- id: alien_not_human
  category: design
  priority: high
  rule: Avoid a human body with one changed feature such as skin colour, ears, or forehead ridges. Change silhouette, proportion, or movement.
  validation_type: warning
- id: alien_culture
  category: lore
  priority: medium
  rule: Give one custom, taboo, or value that comes from the species' biology or home world.
  validation_type: suggestion
- id: alien_species_consistency
  category: consistency
  priority: high
  rule: If the project already records this species, match its recorded anatomy, naming style, and technology.
  validation_type: warning
---

# Space Alien Characters

Non-human species from other worlds: biology first, culture second, no humans in costume.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
