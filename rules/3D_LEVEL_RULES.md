---
system_prompt: >-
  Design a spatially coherent 3D preview for the project. Use the level's world scale and environment to place markers, connect areas of interest, and explain the terrain and lighting.
global: false
priority: high
entity_type: 3d_level
template_reference: 3D_Level_MAP_TEMPLATE.md
rules:
  - id: 3d_level_001
    category: scale
    priority: high
    rule: >-
      Use a consistent world scale in meters and keep coordinates within the configured ground size unless the scene explicitly extends beyond it. Match terrain and lighting to the selected environment.
    validation_type: warning
    applies_to: [3d_level]
  - id: 3d_level_002
    category: placement
    priority: high
    rule: >-
      Place character, item, location, and spawn pins at usable scene coordinates. Match entity links to the pin type and leave spawn pins unlinked.
    validation_type: warning
    applies_to: [3d_level]
  - id: 3d_level_003
    category: navigation
    priority: medium
    rule: >-
      Use the connections layer for routes between meaningful points. Distinguish traversable paths from obstacles, height changes, or routes that depend on an interaction.
    validation_type: warning
    applies_to: [3d_level]
---

# 3D level generation rules

Set the scale in meters and use the same units for ground dimensions and pin
coordinates. Keep placements within the preview area unless the design calls
for an extension. Use the selected environment to guide lighting and terrain.

Link character, item, and location pins to the corresponding project entities.
Keep spawn pins unlinked. Use Design Notes to explain whether a connection is
walkable, blocked, or opened by an interaction.
