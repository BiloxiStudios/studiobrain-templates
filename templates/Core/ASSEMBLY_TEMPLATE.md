---
# METADATA
template_version: "1.0"
template_category: "core"
editable: false
marketplace_eligible: false
id: "[snake_case_name]"
entity_type: "assembly"
folder_name: "Assemblies"
file_prefix: "ASM_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "2026-02-12"
last_updated: "2026-02-12"
status: "active"

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""

# PRIMARY IMAGE (composite preview)
primary_image: ""

# ─── ASSEMBLY IDENTITY ───────────────────────────────────────────────
assembly_type: "character"   # character | prop | building
name: "[Assembly Display Name]"
description: "[Brief description of what this assembly represents]"

# ─── SOURCE ENTITY REFERENCE ─────────────────────────────────────────
# Links this assembly to the narrative entity it represents
source_entity_type: "character"  # character | item | location
source_entity_id: ""             # e.g. "billy_mcgee"

# ─── TEMPLATE HIERARCHY ──────────────────────────────────────────────
# Template → Profile → Variant → Zombie Variant
hierarchy_level: "template"      # template | profile | variant | zombie_variant | transformation_variant
parent_assembly_id: ""           # ID of parent assembly (empty for templates)
inheritance_mode: "full"         # full | selective | none
locked_slots: []                 # Slots that children CANNOT override

# ─── SLOT DEFINITIONS ────────────────────────────────────────────────
# Defines all available slots for this assembly type.
# Each slot has: required (bool), default z_index, allowed overlay modes,
# and accepted file types.
#
# slot_group organizes slots into collapsible UI sections.
# slot_name is the specific slot identifier within a group.

slot_definitions:
  # --- CHARACTER SLOTS ---
  head:
    head_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Base head shape and skin"
    face_features:
      required: false
      z_index: 15
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Freckles, scars, makeup, etc."
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
      expected_dimensions: [512, 512]
      variant_keys: ["Aa", "i", "Kk", "O", "Sil", "Th", "U"]
      # Showrunner expects these exact filenames in mouths/: Aa.png, i.png, Kk.png, O.png, Sil.png, Th.png, U.png

  hair:
    hair_front:
      required: true
      z_index: 50
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Front-facing hair"
    hair_side:
      required: false
      z_index: 48
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Side hair profile"
    hair_back:
      required: false
      z_index: 5
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Back of hair (behind head)"
    hair_blowing:
      required: false
      z_index: 51
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Wind-blown hair variant"

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
      description: "Zombie/damage torso overlay"
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
      description: "Zombie/damage legs overlay"

  overlays_damage:
    allow_custom_slots: true
    layer_type: "overlay"
    default_blend_mode: "multiply"
    scratch_light:
      required: false
      z_index: 90
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Light scratches / scuffs overlay"
    scratch_heavy:
      required: false
      z_index: 90
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Heavy scratches / damage overlay"
    bruise_face:
      required: false
      z_index: 90
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Face bruising overlay"
    dirt_smudge:
      required: false
      z_index: 90
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Dirt / grime overlay"

  overlays_infection:
    allow_custom_slots: true
    layer_type: "overlay"
    default_blend_mode: "multiply"
    content_rules:
      - "NO red blood anywhere. Fluids must be green or dark purple/black."
      - "Gore is stylized, not realistic."
    bite_neck:
      required: false
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Bite wound (neck) overlay"
    bite_arm_left:
      required: false
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Bite wound (left arm) overlay"
    bite_arm_right:
      required: false
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Bite wound (right arm) overlay"
    green_veins_face:
      required: false
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Green veins (face) overlay"
    green_goo_drip_mouth:
      required: false
      z_index: 95
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Green goo drip (mouth) overlay"
    necrosis_patches:
      required: false
      z_index: 92
      overlay_modes: ["overlay", "multiply", "blend"]
      accepted_types: ["png", "webp"]
      description: "Necrosis / discoloration overlay"


  hands_right:
    hands_right_set:
      required: true
      z_index: 30
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Showrunner hand pose set (RIGHT hand)"
      variants_expected: 20
      variant_keys: ["Fist_Back", "Fist_Front", "Fist2_Back", "Fist2_Front", "Open_Back", "Open_Front", "PeaceSign_Back", "PeaceSign_Front", "Pointing_Back", "Pointing_Front", "PointingRelaxed_Back", "PointingRelaxed_Front", "Push_Back", "Push_Front", "Relaxed_Back", "Relaxed_Front", "Shake_Back", "Shake_Front", "ThumbsUp_Back", "ThumbsUp_Front"]

  hands_left:
    hands_left_set:
      required: true
      z_index: 30
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Showrunner hand pose set (LEFT hand)"
      variants_expected: 20
      variant_keys: ["Fist_Back", "Fist_Front", "Fist2_Back", "Fist2_Front", "Open_Back", "Open_Front", "PeaceSign_Back", "PeaceSign_Front", "Pointing_Back", "Pointing_Front", "PointingRelaxed_Back", "PointingRelaxed_Front", "Push_Back", "Push_Front", "Relaxed_Back", "Relaxed_Front", "Shake_Back", "Shake_Front", "ThumbsUp_Back", "ThumbsUp_Front"]
      mirror_of: "hands_right.hands_right_set"
      mirror_strategy: "flip_x"   # UI can offer one-click mirroring; export may auto-derive if desired


  feet:
    feet_base:
      required: true
      z_index: 6
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Feet/shoes set"
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
    necklace:
      required: false
      z_index: 12
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Necklace/choker"
    bag:
      required: false
      z_index: 40
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Backpack/bag/purse"
    held_item:
      required: false
      z_index: 35
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Item held in hand"

  # --- PROP SLOTS (used when assembly_type = "prop") ---
  prop:
    prop_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp", "glb", "fbx"]
      description: "Base prop mesh/sprite"
    prop_detail:
      required: false
      z_index: 15
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Detail layer (labels, decals)"
    prop_damage:
      required: false
      z_index: 80
      overlay_modes: ["overlay", "blend"]
      accepted_types: ["png", "webp"]
      description: "Damage/wear overlay"

  # --- BUILDING SLOTS (used when assembly_type = "building") ---
  structure:
    facade:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Building facade"
    windows:
      required: false
      z_index: 15
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Window variations"
    signage:
      required: false
      z_index: 20
      overlay_modes: ["overlay"]
      accepted_types: ["png", "webp"]
      description: "Signs, brand logos"
    damage:
      required: false
      z_index: 80
      overlay_modes: ["overlay", "blend"]
      accepted_types: ["png", "webp"]
      description: "Structural damage overlay"
    environment:
      required: false
      z_index: 5
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Background/environment context"

# ─── COLOR VARIANTS ───────────────────────────────────────────────────
# Named color variants allow alternate colorways for same slot structure
color_variants:
  - name: "default"
    description: "Standard/canonical colors"
  # - name: "alt_1"
  #   description: "Alternate color scheme 1"

# ─── ZOMBIE / INFECTION PROGRESSION ──────────────────────────────────
# Five stages of infection transformation (0 = clean, 4 = full zombie)
# Each stage activates overlay slots with specific assets
# PALETTE RESTRICTION: Zombie overlays may ONLY use green, purple, and black
infection_system:
  enabled: false
  # Infection stages 0-3 are OVERLAY-BASED (add to current character).
  # Stage 4 (Zombie) is typically a FULL REPLACEMENT sprite/mesh set via a zombie_variant assembly.
  stages:
    - id: "clean"
      display_name: "Clean"
      kind: "base"
      overlay_groups_active: []
      overlay_opacity: 0.0

    - id: "exposed"
      display_name: "Exposed"
      kind: "overlay"
      overlay_groups_active: ["overlays_damage", "overlays_infection"]
      overlay_opacity: 0.15
      notes: "Subtle discoloration, minor scratches, slight green tint."

    - id: "infected"
      display_name: "Infected"
      kind: "overlay"
      overlay_groups_active: ["overlays_infection"]
      overlay_opacity: 0.4
      notes: "Visible bite marks/veins/discoloration; still the same character."

    - id: "turning"
      display_name: "Turning"
      kind: "overlay"
      overlay_groups_active: ["overlays_infection", "overlays_damage"]
      overlay_opacity: 0.7
      notes: "Major transformation cues; stronger overlays and eye glow."

    - id: "zombie"
      display_name: "Zombie"
      kind: "full_replace"
      requires_full_variant: true
      notes: "Full zombie uses a dedicated zombie_variant assembly (new sprite set / new mesh)."


zombie_progression:
  enabled: false              # Set true to activate zombie system
  palette_restriction:
    allowed_hues:             # HSV hue ranges
      green: [80, 160]        # Green range
      purple: [260, 320]      # Purple range
    allowed_values:
      black_max_v: 20         # Max V for "black" (0-255)
    max_saturation_exception: 15  # Below this S, any hue allowed (grays/whites OK)
  stages:
    0:
      name: "Clean"
      description: "No infection, normal appearance"
      active_overlays: []
      overlay_opacity: 0.0
    1:
      name: "Exposed"
      description: "Subtle discoloration, slight green tint on extremities"
      active_overlays: ["face_overlay"]
      overlay_opacity: 0.15
    2:
      name: "Infected"
      description: "Visible veins, purple discoloration spreading"
      active_overlays: ["face_overlay", "torso_overlay"]
      overlay_opacity: 0.4
    3:
      name: "Turning"
      description: "Major transformation, skin cracking, glowing eyes"
      active_overlays: ["face_overlay", "torso_overlay", "legs_overlay", "eyes_overlay"]
      overlay_opacity: 0.7
    4:
      name: "Zombie"
      description: "Full transformation. Pre-zombie stages are overlay-based; full Zombie is typically a NEW mesh/sprite set."
      active_overlays: ["face_overlay", "torso_overlay", "legs_overlay", "eyes_overlay"]
      overlay_opacity: 1.0
      requires_full_variant: true
      zombie_mode: "full_replace"   # full_replace | overlay_only
      notes: "If full_replace: zombie_variant assemblies should override base slots (head_base/eyes_base/mouth_base/torso_base/legs_base/hands_*_set/feet_base). If overlay_only: treat like stage 3 with max overlays."

# ─── EXPORT PROFILES ─────────────────────────────────────────────────
# Pipeline-specific export configurations.
# Original filenames are stored on the Asset record.
# These profiles apply naming conventions at EXPORT TIME only.
export_profile_files:
  # Export profiles are stored as separate files so multiple pipelines can be supported
  # without modifying the assembly template. Each profile defines folder layout,
  # exact filenames, naming rules, and required slots for that pipeline.
  #
  # Suggested path: _Templates/ExportProfiles/
  #   - showrunner_v1.yaml
  #   - comfyui_trellis_v1.yaml
  #   - unreal_mutable_v1.yaml
  #   - uefn_scene_graph_v1.yaml
  #
  # Assemblies choose one or more profiles at export time via /export/{profile_id}.
  - id: "showrunner_v1"
    file: "_Templates/ExportProfiles/showrunner_v1.yaml"
  - id: "comfyui_trellis_v1"
    file: "_Templates/ExportProfiles/comfyui_trellis_v1.yaml"
  - id: "unreal_mutable_v1"
    file: "_Templates/ExportProfiles/unreal_mutable_v1.yaml"
  - id: "uefn_scene_graph_v1"
    file: "_Templates/ExportProfiles/uefn_scene_graph_v1.yaml"



# ─── AI VALIDATION CONFIG ────────────────────────────────────────────
ai_validation:
  auto_validate_on_slot_assign: true
  validation_model: "florence2"
  slot_detection_confidence_threshold: 0.75
  style_consistency_threshold: 0.80
  parent_similarity_threshold: 0.70

# ─── TAGS ─────────────────────────────────────────────────────────────
tags: []
---

# {name}

## Overview
[Brief description of this assembly — what it represents, what pipeline(s) it targets, and its place in the hierarchy]

## Slot Map
[Auto-generated section showing filled vs empty slots, visual grid of current assignments]

## Inheritance
[If this assembly has a parent, describe what is inherited and what is overridden]

## Color Variants
[List available color variants and what changes between them]

## Zombie Progression
[If zombie_progression.enabled, describe each stage and what overlays activate]

## Export Notes
[Pipeline-specific notes — any special handling needed for Showrunner, ComfyUI, or Unreal]

## Art Direction
[Notes on visual style, color palette, proportions, and other art guidance for asset creators]

## Changelog
- [YYYY-MM-DD] Created assembly template
