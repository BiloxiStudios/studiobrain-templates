---
system_prompt: >-
  Design a playable tile-based encounter map. Keep terrain, routes, encounter pins, and fog of war aligned so the map can be read and used at the selected difficulty.
global: false
priority: high
entity_type: dungeon_grid
template_reference: Dungeon_Grid_MAP_TEMPLATE.md
rules:
  - id: dungeon_grid_001
    category: terrain
    priority: high
    rule: >-
      Draw rooms and corridors within the configured grid using the available terrain tiles. Mark walls, doors, and blocked terrain clearly and give intended destinations a traversable route.
    validation_type: warning
    applies_to: [dungeon_grid]
  - id: dungeon_grid_002
    category: encounters
    priority: high
    rule: >-
      Place character, NPC, item, and trap pins on tiles that make sense for the encounter. Match hazards and encounter density to difficulty, and describe what players can notice or do about each obstacle.
    validation_type: warning
    applies_to: [dungeon_grid]
  - id: dungeon_grid_003
    category: visibility
    priority: medium
    rule: >-
      Align fog-of-war regions with rooms or sight boundaries. Use notes to identify when a hidden area or encounter is revealed.
    validation_type: warning
    applies_to: [dungeon_grid]
---

# Dungeon grid generation rules

Mark the starting tile and show usable routes to intended destinations. Use
the available terrain tiles to distinguish traversable ground, walls, doors,
and hazards. Place encounter pins where players can interact with them.

Use Encounter Notes to explain how hazards fit the chosen difficulty and how
players can discover or avoid them. Name the trigger for revealing any area
hidden by fog of war.
