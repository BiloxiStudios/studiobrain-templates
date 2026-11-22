---
system_prompt: 'Describe this location as a painted background for traditional 2D animation. In text, state the staging area where characters stand and move, the three biggest shapes in the layout, and the mood the colour should carry. For images and video: gouache or soft digital paint with visible brushwork, simplified architecture with slightly bent or tilted perspective, detail gathered at the edges and kept out of the centre where characters act, a restricted colour scheme chosen for the time of day, lower contrast and saturation than the characters, no drawn outline on background objects unless a character touches them. No photo textures, no lens effects.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: anim2d_loc_staging
  category: design
  priority: high
  rule: State where characters stand and move, and keep that area free of busy detail.
  validation_type: warning
- id: anim2d_loc_big_shapes
  category: design
  priority: medium
  rule: Name the three largest shapes in the layout before describing any small detail.
  validation_type: suggestion
- id: anim2d_loc_colour_script
  category: design
  priority: high
  rule: Give one colour scheme per time of day or mood, with one dominant hue and one accent.
  validation_type: warning
- id: anim2d_loc_contrast
  category: consistency
  priority: medium
  rule: Keep background contrast and saturation lower than the characters so figures read clearly against it.
  validation_type: warning
- id: anim2d_loc_reuse
  category: design
  priority: low
  rule: Note which parts of the location are reused across scenes, such as a doorway, a counter, or a street corner.
  validation_type: suggestion
---

# Hand-Drawn Animation Locations

Painted 2D backgrounds: clear staging space, simplified shapes and a colour script that never fights the characters.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
