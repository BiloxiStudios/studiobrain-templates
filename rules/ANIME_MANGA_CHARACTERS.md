---
system_prompt: 'Design this character in an anime or manga style. In text, give a recognisable role (rival, mentor, class representative, lone wanderer) plus one trait that contradicts it, and make hair shape, hair colour, and eye shape the main identifiers. State whether the project is colour animation or black-and-white print and stay with it. For images and video: thin clean line art, large detailed eyes with layered highlights, a small simplified nose and mouth, hair drawn as bold separate clumps, hard-edged cel shading with one shadow tone for colour work, or pure black, white, and dot screentone for print work, long limbs, costume with one signature accessory, speed lines and simplified faces for strong emotion.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: anime_char_medium
  category: consistency
  priority: high
  rule: State whether the character is drawn for colour animation or black-and-white print, and describe shading to match.
  validation_type: warning
- id: anime_char_identifiers
  category: design
  priority: high
  rule: Give a hair silhouette, a hair colour, and an eye shape that no other character in the project shares.
  validation_type: warning
- id: anime_char_archetype
  category: design
  priority: medium
  rule: Name the role the character plays in the cast and one trait that goes against that role.
  validation_type: suggestion
- id: anime_char_outfits
  category: design
  priority: medium
  rule: Describe a default outfit and one signature accessory that stays the same in every scene.
  validation_type: suggestion
- id: anime_char_age_read
  category: consistency
  priority: high
  rule: 'State the age and draw to it: adult characters need adult height, face length, and build.'
  validation_type: warning
---

# Anime and Manga Characters

Characters in an anime or manga style: line-led design, signature hair and eyes, clear archetype with a twist.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
