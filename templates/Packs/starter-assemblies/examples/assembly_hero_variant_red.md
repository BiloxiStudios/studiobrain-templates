---
# METADATA
template_version: "2.0"
template_category: "entity"
editable: true
marketplace_eligible: false
id: "hero_rusty_variant_red"
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
  general: "concept"
  game_uefn: "planned"
  tv_showrunner: "none"
  notes: "Red-shirt outfit variant for Rusty. Overrides torso and hat slots only."

# PRIMARY IMAGE
primary_image: ""

# ASSEMBLY IDENTITY
assembly_type: "character"
name: "Rusty McDaniels — Red Shirt Variant"
description: "Color variant of Rusty with a red shirt instead of overalls. Used for flashback scenes and UEFN game contexts."

# SOURCE ENTITY
source_entity_type: "character"
source_entity_id: "rusty_mcdaniels"

# TEMPLATE HIERARCHY — Variant inherits from Profile
hierarchy_level: "variant"
parent_assembly_id: "hero_rusty_profile"
inheritance_mode: "selective"
# No additional locks — cumulative locks from ancestors still apply:
#   head.head_base (locked by hero_base_template)
#   head.face_features (locked by hero_rusty_profile)
locked_slots: []

# SLOT DEFINITIONS — only the slots this variant overrides
slot_definitions:
  body:
    torso_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Red flannel shirt (overrides mechanic overalls from parent profile)"

  accessories:
    hat:
      required: false
      z_index: 55
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Red baseball cap (overrides parent profile's default cap)"

# COLOR VARIANTS
color_variants:
  - name: "default"
    description: "Red shirt — canonical colorway for this variant"
  - name: "faded"
    description: "Faded/washed-out version of the red shirt"

# INFECTION SYSTEM — inherited unchanged
infection_system:
  enabled: true

# ZOMBIE PROGRESSION — inherited unchanged
zombie_progression:
  enabled: true

# EXPORT PROFILES — inherited from parent chain
export_profile_files:
  - id: "showrunner_v1"
    file: "templates/Standard/ExportProfiles/showrunner_v1.yaml"
  - id: "uefn_scene_graph_v1"
    file: "templates/Standard/ExportProfiles/uefn_scene_graph_v1.yaml"

# AI VALIDATION
ai_validation:
  auto_validate_on_slot_assign: true
  validation_model: "florence2"
  slot_detection_confidence_threshold: 0.75
  style_consistency_threshold: 0.80
  parent_similarity_threshold: 0.70

tags: ["rusty_mcdaniels", "variant", "red_shirt", "flashback"]
---

# Rusty McDaniels — Red Shirt Variant

## Overview

Variant-tier assembly for Rusty McDaniels. Overrides only the `body.torso_base` and
`accessories.hat` slots. All other slots are inherited from `hero_rusty_profile`.

## Slot Map

This variant uses `inheritance_mode: selective` — only the overridden slots are defined here.
All other slots (eyes, mouth, hair, hands, feet, etc.) are inherited from the parent profile.

**Overridden slots:**
- `body.torso_base` — red flannel shirt
- `accessories.hat` — red baseball cap

**Locked (from ancestors):**
- `head.head_base` (hero_base_template)
- `head.face_features` (hero_rusty_profile)

## Inheritance

**Variant (depth 3)** inheriting from `hero_rusty_profile` (depth 2) → `hero_base_template` (depth 1).

## Export Notes

Exported to Showrunner (TV flashback) and UEFN (game context).

## Changelog

- 2026-04-01 Created red shirt variant (SBAI-1633)
