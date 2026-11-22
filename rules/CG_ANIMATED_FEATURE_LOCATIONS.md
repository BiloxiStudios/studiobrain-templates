---
system_prompt: 'Describe this location as a set for a 3D computer-animated feature film. In text, say how the real-world version has been caricatured (what is bigger, more curved, more leaning), what the surfaces are made of, and where the light comes from. For images and video: architecture and props with exaggerated, slightly wonky proportions and no perfectly straight lines, tactile materials with real-world detail (chipped paint, wood grain, brushed metal), volumetric light with visible beams or haze, a warm and cool colour contrast between key light and shadow, depth built from clear foreground, midground, and background layers. Scale every prop to the stylised characters, not to real people.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: cg_loc_caricature
  category: design
  priority: high
  rule: 'State how the location is caricatured: which elements are enlarged, curved, tilted, or simplified compared with the real thing.'
  validation_type: warning
- id: cg_loc_materials
  category: design
  priority: medium
  rule: Name the main surface materials and show their age or wear.
  validation_type: suggestion
- id: cg_loc_light_plan
  category: design
  priority: high
  rule: State the main light source, its colour, and the colour of the shadows.
  validation_type: warning
- id: cg_loc_scale
  category: consistency
  priority: medium
  rule: Size doors, furniture, and props for the project's stylised character proportions.
  validation_type: warning
- id: cg_loc_depth
  category: design
  priority: low
  rule: Describe one foreground element, one midground element, and one background element.
  validation_type: suggestion
---

# 3D Animated Feature Locations

Stylised 3D sets for an animated feature: caricatured architecture, tactile surfaces and a clear light plan.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
