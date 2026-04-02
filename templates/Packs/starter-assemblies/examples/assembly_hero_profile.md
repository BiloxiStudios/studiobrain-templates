---
# METADATA
template_version: "2.0"
template_category: "entity"
editable: true
marketplace_eligible: false
id: "hero_rusty_profile"
entity_type: "assembly"
folder_name: "Assemblies"
file_prefix: "ASM_"
created_date: "2026-04-01"
last_updated: "2026-04-01"
associated_rules:
  - ASSEMBLY_RULES.md
status: "active"

# PRODUCTION STATUS
production_status:
  general: "in_progress"
  game_uefn: "planned"
  tv_showrunner: "planned"
  notes: "Rusty McDaniels character profile. Inherits canonical slot structure from hero_base_template."

# PRIMARY IMAGE
primary_image: ""

# ASSEMBLY IDENTITY
assembly_type: "character"
name: "Rusty McDaniels — Character Profile"
description: "Character profile for Rusty McDaniels. Inherits slot structure from the Hero Base Template and supplies Rusty's specific assets. Child variants can override hair/outfit slots."

# SOURCE ENTITY
source_entity_type: "character"
source_entity_id: "rusty_mcdaniels"

# TEMPLATE HIERARCHY — Profile inherits from Template
hierarchy_level: "profile"
parent_assembly_id: "hero_base_template"
inheritance_mode: "full"
# Lock Rusty's face features so variants cannot change the freckle overlay
locked_slots:
  - "head.face_features"

# SLOT DEFINITIONS — only override/fill slots that differ from the parent template defaults
# (Full slot structure is inherited from hero_base_template)
slot_definitions:
  head:
    head_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Rusty's head — LOCKED by parent template, cannot be overridden"
    face_features:
      required: false
      z_index: 15
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Rusty's freckles — LOCKED at profile level"

  hair:
    hair_front:
      required: true
      z_index: 50
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Rusty's sandy-blonde front hair"
    hair_back:
      required: false
      z_index: 5
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Rusty's back hair"

  body:
    torso_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Rusty's mechanic overalls — default outfit"
    legs_base:
      required: true
      z_index: 8
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Rusty's work pants"

  accessories:
    hat:
      required: false
      z_index: 55
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Rusty's baseball cap (optional)"

# COLOR VARIANTS
color_variants:
  - name: "default"
    description: "Rusty's standard appearance"
  - name: "dirty"
    description: "Greasy, oil-stained variant — activates dirt_smudge overlays"

# INFECTION SYSTEM — inherited from parent, no changes needed
infection_system:
  enabled: true

# ZOMBIE PROGRESSION — inherited from parent
zombie_progression:
  enabled: true

# EXPORT PROFILES — inherited from parent template
export_profile_files:
  - id: "showrunner_v1"
    file: "templates/Standard/ExportProfiles/showrunner_v1.yaml"
  - id: "unreal_mutable_v1"
    file: "templates/Standard/ExportProfiles/unreal_mutable_v1.yaml"

# AI VALIDATION
ai_validation:
  auto_validate_on_slot_assign: true
  validation_model: "florence2"
  slot_detection_confidence_threshold: 0.75
  style_consistency_threshold: 0.80
  parent_similarity_threshold: 0.70

tags: ["rusty_mcdaniels", "character", "profile", "mechanic"]
---

# Rusty McDaniels — Character Profile

## Overview

Profile-tier assembly for Rusty McDaniels (mechanic, City of Brains). Inherits the full
canonical hero slot structure from `hero_base_template` and supplies Rusty's specific
character assets.

## Slot Map

All required slots must be filled before this profile can be exported:
- `head.head_base` — **locked by parent template** (cannot override)
- `head.face_features` — **locked at this profile** (freckle overlay is part of Rusty's identity)
- `hair.hair_front`, `body.torso_base`, `body.legs_base` — must be filled here
- `hands_right.hands_right_set`, `hands_left.hands_left_set`, `feet.feet_base` — inherited and filled

## Inheritance

**Profile (depth 2)** inheriting from `hero_base_template` (depth 1).
Effective locked slots (cumulative): `head.head_base`, `head.face_features`.

## Color Variants

- `default` — Standard Rusty appearance
- `dirty` — Activates `overlays_damage.dirt_smudge` at 0.35 opacity

## Export Notes

Exports to Showrunner and Unreal Mutable. ComfyUI/UEFN are available via the parent template.

## Changelog

- 2026-04-01 Created Rusty profile (SBAI-1633)
