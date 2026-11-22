---
system_prompt: 'Describe this location as a miniature set built on a tabletop for stop-motion animation. In text, name what each part is built from (card, balsa wood, clay, cotton wool for smoke, cling film or resin for water) and the scale against the puppets. For images and video: a real physical miniature photographed with a macro lens, shallow depth of field, tiny practical lights such as bulbs in windows, visible material texture at the wrong scale (large wood grain, coarse fabric), hand-painted surfaces, slightly crooked walls and props, a painted or fabric sky backdrop. No computer-generated smoothness, no photoreal full-scale buildings.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: stopmo_loc_materials
  category: design
  priority: high
  rule: Name the build material for the ground, the walls, and at least two props.
  validation_type: warning
- id: stopmo_loc_scale
  category: consistency
  priority: high
  rule: State the scale relative to the puppets and keep doors and furniture sized to them.
  validation_type: warning
- id: stopmo_loc_practical_effects
  category: design
  priority: medium
  rule: Describe weather, water, fire, or smoke as a physical craft material, not a digital effect.
  validation_type: warning
- id: stopmo_loc_lighting
  category: design
  priority: medium
  rule: State the miniature light sources and the overall mood they create.
  validation_type: suggestion
- id: stopmo_loc_imperfection
  category: design
  priority: low
  rule: 'Include one charming imperfection: a wobbly fence, uneven tiles, a visible brush stroke.'
  validation_type: suggestion
---

# Stop-Motion Locations

Miniature tabletop sets for stop-motion: real materials at small scale, practical lights, handmade charm.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
