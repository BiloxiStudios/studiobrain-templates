---
system_prompt: 'Describe this location as a setting for a comic book or graphic novel. In text, write one establishing view that shows the whole place, then two or three landmarks that can appear in the corner of later panels so readers always know where they are. For images and video: inked line art with ruled perspective, large areas of solid black, flat colour with a limited scheme per scene, halftone dots or hatching for texture, dramatic camera angles, strong shapes of light and shadow, simplified crowds and background detail. The scene should hold up in black and white before colour is added.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: comic_loc_establishing
  category: design
  priority: high
  rule: Write one establishing view that shows the whole location and the viewpoint it is seen from.
  validation_type: warning
- id: comic_loc_landmarks
  category: design
  priority: high
  rule: Name two or three landmarks that identify the location when only a corner of it is in panel.
  validation_type: warning
- id: comic_loc_scene_colours
  category: design
  priority: medium
  rule: Give a limited colour scheme of three or four colours for scenes set here.
  validation_type: suggestion
- id: comic_loc_black_and_white
  category: design
  priority: medium
  rule: Describe where the solid black shadows fall so the scene reads without colour.
  validation_type: suggestion
---

# Comic Book Locations

Settings drawn for comics: an establishing panel, heavy shadow, and a few landmarks that anchor every page.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
