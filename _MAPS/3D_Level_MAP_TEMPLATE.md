---
template_category: map
template_name: 3D Level Preview
template_id: 3d-level
description: Interactive 3D scene for level previews with entity markers, model imports, and multiple camera modes.
icon: box
renderer: three-3d
renderer_config:
  ground_size: [100, 100]
  lighting: outdoor
  grid: true
layers:
  - id: entities
    label: Entity Markers
    type: entity-pins
    pin_types: [character, item, location, spawn]
    default_visible: true
  - id: connections
    label: Connections
    type: line-overlay
    default_visible: true
  - id: labels
    label: Labels
    type: text-markers
    default_visible: true
pin_types:
  character:
    icon: user
    color: "#3b82f6"
    entity_types: [character]
  item:
    icon: gem
    color: "#eab308"
    entity_types: [item]
  location:
    icon: map-pin
    color: "#8b5cf6"
    entity_types: [location]
  spawn:
    icon: target
    color: "#ef4444"
    entity_types: []
fields:
  level_name:
    type: text
    label: Level Name
    required: true
  scale:
    type: number
    label: World Scale (m)
    default: 1
  environment:
    type: select
    label: Environment
    options: [indoor, outdoor, underground, space, underwater]
tags:
  - game-dev
  - level-design
  - 3d
---

# 3D Level Preview

An interactive 3D visualization for level design. Import .glb models, place entity markers, and explore the scene with orbit, fly-through, or first-person cameras.
