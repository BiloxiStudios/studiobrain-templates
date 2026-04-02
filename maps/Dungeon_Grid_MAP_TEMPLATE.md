---
template_category: map
template_name: Dungeon Grid
template_id: dungeon-grid
description: Grid-based dungeon map with paintable terrain tiles, entity placement, and fog of war overlay.
icon: grid-2x2
renderer: tile-2d
renderer_config:
  grid_size: [32, 32]
  tile_size: 64
  hex: false
layers:
  - id: terrain
    label: Terrain
    type: tile-paint
    tiles: [stone, water, lava, grass, void, door, wall, trap]
    default_visible: true
  - id: entities
    label: Entities
    type: entity-pins
    pin_types: [character, npc, item, trap]
    default_visible: true
  - id: fog
    label: Fog of War
    type: overlay
    default_visible: false
pin_types:
  character:
    icon: user
    color: "#3b82f6"
    entity_types: [character]
  npc:
    icon: bot
    color: "#22c55e"
    entity_types: [character]
  item:
    icon: gem
    color: "#eab308"
    entity_types: [item]
  trap:
    icon: alert-triangle
    color: "#ef4444"
    entity_types: [item]
fields:
  dungeon_name:
    type: text
    label: Dungeon Name
    required: true
  difficulty:
    type: select
    label: Difficulty
    options: [easy, medium, hard, deadly]
  notes:
    type: textarea
    label: DM Notes
tags:
  - game-dev
  - ttrpg
  - dungeon
---

# Dungeon Grid

A tile-based dungeon map for tabletop RPG encounters. Paint terrain, place characters and items, and toggle fog of war for dramatic reveals.
