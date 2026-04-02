---
# METADATA
template_version: "2.0"
template_category: "entity"
editable: true
marketplace_eligible: false
id: "hero_rusty_zombie"
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
  tv_showrunner: "planned"
  notes: "Full zombie replacement for Rusty. All base slots replaced with zombie-specific art."

# PRIMARY IMAGE
primary_image: ""

# ASSEMBLY IDENTITY
assembly_type: "character"
name: "Rusty McDaniels — Zombie Variant"
description: "Full zombie transformation of Rusty McDaniels (stage 4). Replaces all base slots with zombie-specific art. Overlay slots use the green/purple/black palette restriction."

# SOURCE ENTITY
source_entity_type: "character"
source_entity_id: "rusty_mcdaniels"

# TEMPLATE HIERARCHY — Zombie variant inherits from profile (stage 4 full_replace)
hierarchy_level: "zombie_variant"
parent_assembly_id: "hero_rusty_profile"
inheritance_mode: "full"
# Zombie variant locks down all base slots — children (if any) cannot override them
locked_slots:
  - "head.head_base"
  - "eyes.eyes_base"
  - "mouth.mouth_base"
  - "body.torso_base"
  - "body.legs_base"
  - "hands_right.hands_right_set"
  - "hands_left.hands_left_set"
  - "feet.feet_base"

# SLOT DEFINITIONS — full replacement set for zombie appearance
slot_definitions:
  head:
    head_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Zombie head — decomposed skin, green pallor (palette-restricted)"
    face_overlay:
      required: true
      z_index: 90
      overlay_modes: ["overlay", "blend"]
      accepted_types: ["png", "webp"]
      description: "Full zombie face overlay — necrosis and green tinting"

  eyes:
    eyes_base:
      required: true
      z_index: 20
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Zombie eyes — milky/glowing (no pupils)"
      variants_expected: 6
      variant_names: ["open", "half", "wide", "rolled_back", "glowing", "closed"]
    eyes_overlay:
      required: true
      z_index: 91
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Zombie eye glow overlay (green/purple only)"

  mouth:
    mouth_base:
      required: true
      z_index: 20
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Zombie mouth — slack jaw, dark gums"

  body:
    torso_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Zombie torso — shredded overalls with necrosis"
    torso_overlay:
      required: true
      z_index: 85
      overlay_modes: ["overlay", "blend"]
      accepted_types: ["png", "webp"]
      description: "Heavy zombie torso damage overlay"
    legs_base:
      required: true
      z_index: 8
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Zombie legs — shambling, torn clothing"
    legs_overlay:
      required: true
      z_index: 84
      overlay_modes: ["overlay", "blend"]
      accepted_types: ["png", "webp"]
      description: "Heavy zombie legs damage overlay"

  hands_right:
    hands_right_set:
      required: true
      z_index: 30
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Zombie right hand pose set — grasping/shambling poses"
      variants_expected: 6
      variant_keys: ["Reach", "Grasp", "Drag", "Limp", "Fist", "Open"]

  hands_left:
    hands_left_set:
      required: true
      z_index: 30
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Zombie left hand pose set"
      variants_expected: 6
      variant_keys: ["Reach", "Grasp", "Drag", "Limp", "Fist", "Open"]
      mirror_of: "hands_right.hands_right_set"
      mirror_strategy: "flip_x"

  feet:
    feet_base:
      required: true
      z_index: 6
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Zombie feet — dragging gait"
      variants_expected: 3
      variant_names: ["standing", "shambling", "dragging"]

  overlays_infection:
    allow_custom_slots: true
    layer_type: "overlay"
    default_blend_mode: "multiply"
    content_rules:
      - "NO red blood anywhere. Fluids must be green or dark purple/black."
      - "Gore is stylized, not realistic."
    green_veins_face:
      required: true
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Full-face green vein network (palette: green/black)"
    necrosis_patches:
      required: true
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Extensive necrosis patches — purple/black"
    green_goo_drip_mouth:
      required: false
      z_index: 95
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Green fluid drip from mouth"

# COLOR VARIANTS
color_variants:
  - name: "default"
    description: "Standard zombie appearance — green pallor"
  - name: "advanced"
    description: "Advanced decomposition — more purple/black tones"

# ZOMBIE PROGRESSION — this IS the zombie stage
zombie_progression:
  enabled: true
  zombie_mode: "full_replace"
  active_stage: 4

# EXPORT PROFILES
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
  style_consistency_threshold: 0.70
  parent_similarity_threshold: 0.65

tags: ["rusty_mcdaniels", "zombie", "zombie_variant", "stage_4", "full_replace"]
---

# Rusty McDaniels — Zombie Variant

## Overview

Full zombie transformation of Rusty McDaniels (infection stage 4). This is a **full_replace**
zombie variant — all base slots are replaced with zombie-specific art. This assembly is the
fourth and final tier in the hierarchy:

```
hero_base_template (Template, depth 1)
  └── hero_rusty_profile (Profile, depth 2)
        └── hero_rusty_zombie (Zombie Variant, depth 3)
```

## Palette Restriction

All overlay assets in `overlays_infection` **must** comply with the green/purple/black palette
restriction:
- Greens: HSV hue 80–160
- Purples: HSV hue 260–320
- Blacks: HSV value ≤ 20
- No red blood. Stylized gore only.

## Slot Map

All base slots are **locked** on this assembly so no further child assemblies can create
"zombie-of-zombie" hierarchies inadvertently.

**Overridden (full replace):** head, eyes, mouth, body, hands, feet
**New overlays:** `green_veins_face`, `necrosis_patches`, `green_goo_drip_mouth`

## Inheritance

**Zombie Variant (depth 3)** inheriting from `hero_rusty_profile` (depth 2).

## Export Notes

Exported to Showrunner (TV zombie scenes) and Unreal Mutable (game character swap).

## Changelog

- 2026-04-01 Created zombie variant (SBAI-1633)
