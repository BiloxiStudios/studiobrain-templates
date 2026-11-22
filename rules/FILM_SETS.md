---
system_prompt: 'This location is a set or a real place used for filming. State whether it is interior or exterior, day or night, and a built set or a found location. Describe what the camera sees from the main angle, then the practical facts: dimensions, entrances for cast and equipment, where lights and camera can go, power, sound problems such as traffic or echo, and the hours it is available. List the set dressing and props that must be present for continuity. For images and video: frame it as a production still or a reference photograph for the art department, in the project''s aspect ratio, with the light source and time of day stated.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: film_set_slugline
  category: design
  priority: high
  rule: State interior or exterior, the place name, and day or night, as a screenplay scene heading does.
  validation_type: warning
- id: film_set_camera_view
  category: design
  priority: high
  rule: Describe what is visible from the main camera position.
  validation_type: warning
- id: film_set_practical
  category: design
  priority: medium
  rule: Give dimensions, entrances, power, and any sound problem.
  validation_type: suggestion
- id: film_set_dressing_continuity
  category: consistency
  priority: high
  rule: List the set dressing and props that must match between scenes shot here.
  validation_type: warning
- id: film_set_light
  category: design
  priority: medium
  rule: State the natural and practical light available and the time of day it looks best.
  validation_type: suggestion
---

# Film Sets

Locations written as shootable sets: what the camera sees, where the light is, and what the crew needs to know.

How it maps onto the location type: location type and building type say whether it is a stage build or a found location, entrance points and interior zones hold access and shooting areas, lighting and colour palette hold the look, ambient sounds hold sound problems, operating hours hold availability, hazards hold safety notes, and notable features hold the set dressing list.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
