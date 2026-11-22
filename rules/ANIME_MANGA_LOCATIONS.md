---
system_prompt: 'Describe this location as a background for anime or manga. In text, ground the place in specific everyday detail (signage, wiring, vending machines, shoes at the door, weather) and say what time of day defines it. For images and video in colour: carefully ruled perspective, dense realistic detail painted with clean edges, large skies with towering clouds, strong directional light, glowing highlights at sunset or night, and saturated blues, oranges, and greens. For black-and-white print: ruled ink line work, screentone for sky and shadow, solid black for night. Backgrounds are more realistic than the characters who stand in them.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: anime_loc_everyday_detail
  category: design
  priority: high
  rule: List at least four small everyday details that make the place feel used, such as signs, cables, bicycles, or laundry.
  validation_type: warning
- id: anime_loc_time_of_day
  category: design
  priority: high
  rule: State the defining time of day and weather, and describe the sky.
  validation_type: warning
- id: anime_loc_perspective
  category: design
  priority: medium
  rule: 'Give one establishing view with a clear viewpoint: street level, from above, or looking up.'
  validation_type: suggestion
- id: anime_loc_medium
  category: consistency
  priority: medium
  rule: 'Match the project''s medium: painted colour for animation, or ink line and screentone for print.'
  validation_type: warning
- id: anime_loc_quiet_shot
  category: design
  priority: low
  rule: Describe one still, quiet detail that could hold a scene on its own, such as a wind chime or a railway crossing light.
  validation_type: suggestion
---

# Anime and Manga Locations

Backgrounds in an anime or manga style: precise perspective, everyday detail and strong skies and light.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
