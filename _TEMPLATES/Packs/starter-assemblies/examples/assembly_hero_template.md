---
# METADATA
template_version: "2.0"
template_category: "entity"
editable: true
marketplace_eligible: false
id: "hero_base_template"
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
  tv_showrunner: "none"
  notes: "Root template for all hero-tier character assemblies."

# PRIMARY IMAGE
primary_image: ""

# ASSEMBLY IDENTITY
assembly_type: "character"
name: "Hero Base Template"
description: "Root template for all biped hero characters. Defines canonical slot structure and z-index ordering. All hero profiles must inherit from this template."

# SOURCE ENTITY
source_entity_type: "character"
source_entity_id: ""

# TEMPLATE HIERARCHY — this IS the root template
hierarchy_level: "template"
parent_assembly_id: ""
inheritance_mode: "none"
# Lock the head base so all child profiles must use the same canonical head shape
locked_slots:
  - "head.head_base"

# SLOT DEFINITIONS — canonical slot structure for hero characters
slot_definitions:
  head:
    head_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Base head shape and skin (LOCKED — set at template level)"
    face_features:
      required: false
      z_index: 15
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Freckles, scars, makeup overlays"
    face_overlay:
      required: false
      z_index: 90
      overlay_modes: ["overlay", "blend"]
      accepted_types: ["png", "webp"]
      description: "Zombie/infection face overlay"

  eyes:
    eyes_base:
      required: true
      z_index: 20
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Default eye state"
      variants_expected: 12
      variant_names: ["open", "closed", "half", "wide", "squint", "wink_left", "wink_right", "angry", "sad", "surprised", "happy", "looking_up"]
    eyes_overlay:
      required: false
      z_index: 91
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Zombie eye glow overlay"

  mouth:
    mouth_base:
      required: true
      z_index: 20
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Default mouth state"
    mouth_visemes:
      required: false
      z_index: 20
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Lip sync viseme set"
      variants_expected: 7
      variant_keys: ["Aa", "i", "Kk", "O", "Sil", "Th", "U"]

  hair:
    hair_front:
      required: true
      z_index: 50
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Front-facing hair"
    hair_back:
      required: false
      z_index: 5
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Back of hair (behind head)"

  body:
    torso_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Base torso/shirt"
    torso_overlay:
      required: false
      z_index: 85
      overlay_modes: ["overlay", "blend"]
      accepted_types: ["png", "webp"]
      description: "Damage/zombie torso overlay"
    legs_base:
      required: true
      z_index: 8
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Base legs/pants"
    legs_overlay:
      required: false
      z_index: 84
      overlay_modes: ["overlay", "blend"]
      accepted_types: ["png", "webp"]
      description: "Damage/zombie legs overlay"

  hands_right:
    hands_right_set:
      required: true
      z_index: 30
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Hand pose set (RIGHT)"
      variants_expected: 20
      variant_keys: ["Fist_Back", "Fist_Front", "Fist2_Back", "Fist2_Front", "Open_Back", "Open_Front", "PeaceSign_Back", "PeaceSign_Front", "Pointing_Back", "Pointing_Front", "PointingRelaxed_Back", "PointingRelaxed_Front", "Push_Back", "Push_Front", "Relaxed_Back", "Relaxed_Front", "Shake_Back", "Shake_Front", "ThumbsUp_Back", "ThumbsUp_Front"]

  hands_left:
    hands_left_set:
      required: true
      z_index: 30
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Hand pose set (LEFT)"
      variants_expected: 20
      variant_keys: ["Fist_Back", "Fist_Front", "Fist2_Back", "Fist2_Front", "Open_Back", "Open_Front", "PeaceSign_Back", "PeaceSign_Front", "Pointing_Back", "Pointing_Front", "PointingRelaxed_Back", "PointingRelaxed_Front", "Push_Back", "Push_Front", "Relaxed_Back", "Relaxed_Front", "Shake_Back", "Shake_Front", "ThumbsUp_Back", "ThumbsUp_Front"]
      mirror_of: "hands_right.hands_right_set"
      mirror_strategy: "flip_x"

  feet:
    feet_base:
      required: true
      z_index: 6
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Feet/shoes"
      variants_expected: 4
      variant_names: ["standing", "walking", "running", "tiptoe"]

  accessories:
    hat:
      required: false
      z_index: 55
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Hat/headwear"
    glasses:
      required: false
      z_index: 25
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Glasses/eyewear"
    held_item:
      required: false
      z_index: 35
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Item held in hand"

  overlays_damage:
    allow_custom_slots: true
    layer_type: "overlay"
    default_blend_mode: "multiply"
    scratch_light:
      required: false
      z_index: 90
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Light scratches overlay"
    dirt_smudge:
      required: false
      z_index: 90
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Dirt/grime overlay"

  overlays_infection:
    allow_custom_slots: true
    layer_type: "overlay"
    default_blend_mode: "multiply"
    content_rules:
      - "NO red blood anywhere. Fluids must be green or dark purple/black."
      - "Gore is stylized, not realistic."
    green_veins_face:
      required: false
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Green veins (face) overlay"
    necrosis_patches:
      required: false
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Necrosis / discoloration patches"

# COLOR VARIANTS
color_variants:
  - name: "default"
    description: "Standard canonical colors"

# INFECTION SYSTEM
infection_system:
  enabled: true
  stages:
    - id: "clean"
      display_name: "Clean"
      kind: "base"
      overlay_groups_active: []
      overlay_opacity: 0.0
    - id: "exposed"
      display_name: "Exposed"
      kind: "overlay"
      overlay_groups_active: ["overlays_damage"]
      overlay_opacity: 0.15
    - id: "infected"
      display_name: "Infected"
      kind: "overlay"
      overlay_groups_active: ["overlays_infection"]
      overlay_opacity: 0.4
    - id: "turning"
      display_name: "Turning"
      kind: "overlay"
      overlay_groups_active: ["overlays_infection", "overlays_damage"]
      overlay_opacity: 0.7
    - id: "zombie"
      display_name: "Zombie"
      kind: "full_replace"
      requires_full_variant: true
      notes: "Full zombie requires a dedicated zombie_variant assembly."

# ZOMBIE PROGRESSION
zombie_progression:
  enabled: true
  palette_restriction:
    allowed_hues:
      green: [80, 160]
      purple: [260, 320]
    allowed_values:
      black_max_v: 20
    max_saturation_exception: 15
  stages:
    0:
      name: "Clean"
      active_overlays: []
      overlay_opacity: 0.0
    1:
      name: "Exposed"
      active_overlays: ["face_overlay"]
      overlay_opacity: 0.15
    2:
      name: "Infected"
      active_overlays: ["face_overlay", "torso_overlay"]
      overlay_opacity: 0.4
    3:
      name: "Turning"
      active_overlays: ["face_overlay", "torso_overlay", "legs_overlay", "eyes_overlay"]
      overlay_opacity: 0.7
    4:
      name: "Zombie"
      active_overlays: ["face_overlay", "torso_overlay", "legs_overlay", "eyes_overlay"]
      overlay_opacity: 1.0
      requires_full_variant: true
      zombie_mode: "full_replace"

# EXPORT PROFILES
export_profile_files:
  - id: "showrunner_v1"
    file: "templates/Standard/ExportProfiles/showrunner_v1.yaml"
  - id: "unreal_mutable_v1"
    file: "templates/Standard/ExportProfiles/unreal_mutable_v1.yaml"
  - id: "comfyui_trellis_v1"
    file: "templates/Standard/ExportProfiles/comfyui_trellis_v1.yaml"
  - id: "uefn_scene_graph_v1"
    file: "templates/Standard/ExportProfiles/uefn_scene_graph_v1.yaml"

# AI VALIDATION
ai_validation:
  auto_validate_on_slot_assign: true
  validation_model: "florence2"
  slot_detection_confidence_threshold: 0.75
  style_consistency_threshold: 0.80
  parent_similarity_threshold: 0.70

tags: ["hero", "character", "template", "biped"]
---

# Hero Base Template

## Overview

Root template for all biped hero characters in the assembly system. Defines the canonical
slot structure — every hero profile, variant, and zombie variant in the hierarchy must
inherit from this template.

## Slot Map

See `slot_definitions` above. The `head.head_base` slot is **locked** at this level so that
all child assemblies share the same canonical head shape.

## Inheritance

This is the **Template** (depth 1) — the root of the chain. It has no parent.
Child profiles should set `parent_assembly_id: "hero_base_template"`.

## Color Variants

- `default` — Standard canonical colors

## Zombie Progression

Full 5-stage infection progression enabled. Stages 0–3 are overlay-based. Stage 4 requires
a dedicated `zombie_variant` assembly.

## Export Notes

Supports all four export profiles: Showrunner, Unreal Mutable, ComfyUI Trellis, and UEFN
Scene Graph.

## Changelog

- 2026-04-01 Created hero base template (SBAI-1633)
