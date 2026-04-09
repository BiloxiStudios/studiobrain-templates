---
# METADATA
template_version: "2.0"
template_category: "entity"
ui_icon: "Layers"
ui_color: "#a855f7"
generation_instructions: |
  Generate an assembly that groups related entities into a structured composition. Define a clear hierarchy level, source entity, and slot definitions. Assemblies represent how parts combine into wholes — focus on component relationships, ordering, and layout constraints.
editable: true
marketplace_eligible: false
id: "[assembly_id]"
entity_type: "assembly"
folder_name: "Assemblies"
file_prefix: "ASM_"
asset_subfolders:
  - images
  - models
created_date: "[YYYY-MM-DD]"
last_updated: "[YYYY-MM-DD]"
associated_rules:
  - ASSEMBLY_RULES.md
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  source_entity_id:
    widget: entity-selector
    reference_type: character
    max_selections: 1
  parent_assembly_id:
    widget: entity-selector
    reference_type: assembly
    max_selections: 1

status: "active"

# ASSEMBLY METADATA
assembly_type: "character"  # character, prop, or building
hierarchy_level: "template"  # template or instance
parent_assembly_id: ""
source_entity_id: ""

# PRIMARY IMAGE
primary_image: ""  # Path to primary preview image

# BASIC IDENTITY
name: "[Assembly Name]"
description: "[Brief description of this assembly]"

# SLOT DEFINITIONS
# This defines the available slot groups and individual slots for this assembly type.
# Different assembly types use different slot groups:
# - character: head, eyes, mouth, hair, body, hands_right, hands_left, feet, accessories, overlays_damage, overlays_infection
# - prop: prop, overlays_damage
# - building: structure, overlays_damage
slot_definitions:
  # Character slot groups
  head:
    head_base:
      required: true
      z_index: 10
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Base head shape and skin
    face_features:
      required: false
      z_index: 15
      overlay_modes:
        - overlay
      accepted_types:
        - png
        - webp
      description: Freckles, scars, makeup, etc.
    face_overlay:
      required: false
      z_index: 90
      overlay_modes:
        - overlay
        - blend
      accepted_types:
        - png
        - webp
      description: Zombie/infection face overlay
  eyes:
    eyes_base:
      required: true
      z_index: 20
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Default eye state
      variants_expected: 12
      variant_names:
        - open
        - closed
        - half
        - wide
        - squint
        - wink_left
        - wink_right
        - angry
        - sad
        - surprised
        - happy
        - looking_up
    eyes_overlay:
      required: false
      z_index: 91
      overlay_modes:
        - overlay
      accepted_types:
        - png
        - webp
      description: Zombie eye glow overlay
  mouth:
    mouth_base:
      required: true
      z_index: 20
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Default mouth state
    mouth_visemes:
      required: false
      z_index: 20
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Lip sync viseme set
      variants_expected: 7
      expected_dimensions:
        - 512
        - 512
      variant_keys:
        - Aa
        - i
        - Kk
        - O
        - Sil
        - Th
        - U
  hair:
    hair_front:
      required: true
      z_index: 50
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Front-facing hair
    hair_side:
      required: false
      z_index: 48
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Side hair profile
    hair_back:
      required: false
      z_index: 5
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Back of hair (behind head)
    hair_blowing:
      required: false
      z_index: 51
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Wind-blown hair variant
  body:
    torso_base:
      required: true
      z_index: 10
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Base torso/shirt
    torso_overlay:
      required: false
      z_index: 85
      overlay_modes:
        - overlay
        - blend
      accepted_types:
        - png
        - webp
      description: Zombie/damage torso overlay
    legs_base:
      required: true
      z_index: 8
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Base legs/pants
    legs_overlay:
      required: false
      z_index: 84
      overlay_modes:
        - overlay
        - blend
      accepted_types:
        - png
        - webp
      description: Zombie/damage legs overlay
  hands_right:
    hands_right_set:
      required: true
      z_index: 30
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Showrunner hand pose set (RIGHT hand)
      variants_expected: 20
      variant_keys:
        - Fist_Back
        - Fist_Front
        - Fist2_Back
        - Fist2_Front
        - Open_Back
        - Open_Front
        - PeaceSign_Back
        - PeaceSign_Front
        - Pointing_Back
        - Pointing_Front
        - PointingRelaxed_Back
        - PointingRelaxed_Front
        - Push_Back
        - Push_Front
        - Relaxed_Back
        - Relaxed_Front
        - Shake_Back
        - Shake_Front
        - ThumbsUp_Back
        - ThumbsUp_Front
  hands_left:
    hands_left_set:
      required: true
      z_index: 30
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Showrunner hand pose set (LEFT hand)
      variants_expected: 20
      variant_keys:
        - Fist_Back
        - Fist_Front
        - Fist2_Back
        - Fist2_Front
        - Open_Back
        - Open_Front
        - PeaceSign_Back
        - PeaceSign_Front
        - Pointing_Back
        - Pointing_Front
        - PointingRelaxed_Back
        - PointingRelaxed_Front
        - Push_Back
        - Push_Front
        - Relaxed_Back
        - Relaxed_Front
        - Shake_Back
        - Shake_Front
        - ThumbsUp_Back
        - ThumbsUp_Front
      mirror_of: hands_right.hands_right_set
      mirror_strategy: flip_x
  feet:
    feet_base:
      required: true
      z_index: 6
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Feet/shoes set
      variants_expected: 4
      variant_names:
        - standing
        - walking
        - running
        - tiptoe
  accessories:
    hat:
      required: false
      z_index: 55
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Hat/headwear
    glasses:
      required: false
      z_index: 25
      overlay_modes:
        - overlay
      accepted_types:
        - png
        - webp
      description: Glasses/eyewear
    necklace:
      required: false
      z_index: 12
      overlay_modes:
        - overlay
      accepted_types:
        - png
        - webp
      description: Necklace/choker
    bag:
      required: false
      z_index: 40
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Backpack/bag/purse
    held_item:
      required: false
      z_index: 35
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Item held in hand
  # Prop slot groups
  prop:
    prop_base:
      required: true
      z_index: 10
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
        - glb
        - fbx
      description: Base prop mesh/sprite
    prop_detail:
      required: false
      z_index: 15
      overlay_modes:
        - overlay
      accepted_types:
        - png
        - webp
      description: Detail layer (labels, decals)
    prop_damage:
      required: false
      z_index: 80
      overlay_modes:
        - overlay
        - blend
      accepted_types:
        - png
        - webp
      description: Damage/wear overlay
  # Building slot groups
  structure:
    facade:
      required: true
      z_index: 10
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Building facade
    windows:
      required: false
      z_index: 15
      overlay_modes:
        - overlay
      accepted_types:
        - png
        - webp
      description: Window variations
    signage:
      required: false
      z_index: 20
      overlay_modes:
        - overlay
      accepted_types:
        - png
        - webp
      description: Signs, brand logos
    damage:
      required: false
      z_index: 80
      overlay_modes:
        - overlay
        - blend
      accepted_types:
        - png
        - webp
      description: Structural damage overlay
    environment:
      required: false
      z_index: 5
      overlay_modes:
        - replace
      accepted_types:
        - png
        - webp
      description: Background/environment context
  # Damage overlays (shared by all types)
  overlays_damage:
    allow_custom_slots: true
    layer_type: overlay
    default_blend_mode: multiply
    scratch_light:
      required: false
      z_index: 90
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Light scratches / scuffs overlay
    scratch_heavy:
      required: false
      z_index: 90
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Heavy scratches / damage overlay
    bruise_face:
      required: false
      z_index: 90
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Face bruising overlay
    dirt_smudge:
      required: false
      z_index: 90
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Dirt / grime overlay
  # Infection overlays (character only)
  overlays_infection:
    allow_custom_slots: true
    layer_type: overlay
    default_blend_mode: multiply
    content_rules:
      - NO red blood anywhere. Fluids must be green or dark purple/black.
      - Gore is stylized, not realistic.
    bite_neck:
      required: false
      z_index: 92
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Bite wound (neck) overlay
    bite_arm_left:
      required: false
      z_index: 92
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Bite wound (left arm) overlay
    bite_arm_right:
      required: false
      z_index: 92
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Bite wound (right arm) overlay
    green_veins_face:
      required: false
      z_index: 92
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Green veins (face) overlay
    green_goo_drip_mouth:
      required: false
      z_index: 95
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Green goo drip (mouth) overlay
    necrosis_patches:
      required: false
      z_index: 92
      overlay_modes:
        - overlay
        - multiply
        - blend
      accepted_types:
        - png
        - webp
      description: Necrosis / discoloration overlay

# UI LAYOUT (for assembly editor)
# This defines the visual layout in the assembly editor UI
layout:
  assemblyType: character
  displayName: Character (Biped)
  gridTemplateAreas: '".        hair   hair   ." ".        head   head   ." "hand-l   body   body   hand-r" "hand-l   body   body   hand-r" ".        legs   legs   ." ".        feet   feet   ."'
  gridTemplateColumns: 1fr 1fr 1fr 1fr
  gridTemplateRows: repeat(6, 1fr)
  regions:
    - gridArea: hair
      label: Hair
      slotGroups:
        - hair
      anchorX: 44
      anchorY: 10.3
      hitRadius: 10
    - gridArea: head
      label: Head
      slotGroups:
        - head
      anchorX: 75
      anchorY: 18.6
      hitRadius: 6
      expanded: true
      children:
        - gridArea: eyes
          label: Eyes
          slotGroups:
            - eyes
          anchorX: 50.7
          anchorY: 11.6
          hitRadius: 6
        - gridArea: mouth
          label: Mouth
          slotGroups:
            - mouth
          anchorX: 48.7
          anchorY: 19.4
          hitRadius: 4
        - gridArea: face-detail
          label: Face
          slotGroups:
            - face
          anchorX: 77.6
          anchorY: 27.7
          hitRadius: 6
        - gridArea: head-acc
          label: Accessories
          slotGroups:
            - accessories
            - headwear
            - eyewear
          anchorX: 88.4
          anchorY: 12
          hitRadius: 6
    - gridArea: body
      label: Body
      slotGroups:
        - body
        - torso
        - chest
        - shirt
        - jacket
        - overlays_damage
        - overlays_infection
        - overlays
      anchorX: 50
      anchorY: 37.9
      hitRadius: 15
      isCatchAll: true
    - gridArea: hand-l
      label: Left Hand
      slotGroups:
        - hands_left
        - hand_left
        - left_hand
      anchorX: 19.5
      anchorY: 52.2
      hitRadius: 8
    - gridArea: hand-r
      label: Right Hand
      slotGroups:
        - hands_right
        - hand_right
        - right_hand
      anchorX: 83
      anchorY: 51.6
      hitRadius: 8
    - gridArea: legs
      label: Legs
      slotGroups:
        - legs
        - lower_body
        - pants
        - bottoms
        - prop
        - structure
        - held_item
      anchorX: 48.2
      anchorY: 73.2
      hitRadius: 12
    - gridArea: feet
      label: Feet
      slotGroups:
        - feet
        - shoes
        - footwear
      anchorX: 64.5
      anchorY: 90.8
      hitRadius: 10
  silhouetteType: biped
  aspectRatio: 0.75

# INHERITANCE SETTINGS
inheritance:
  max_depth: 4
  allow_full: true
  allow_slots_only: true
  allow_metadata_only: false

# EXPORT SETTINGS
export:
  default_profile: "unreal_engine_5"
  supported_profiles:
    - unreal_engine_5
    - unity_2023
    - godot_4
    - showrunner_v2
  color_variants:
    - default
    - alt1
    - alt2
  zombie_stages:
    - 0
    - 1
    - 2
    - 3
# NEW-ENTITY MARKDOWN SKELETON (SBAI-1857)
markdown_skeleton: |
  ## Overview

  ## Components

  ## Notes
---

# [Assembly Name]

## Overview

[Brief description of this assembly, its intended use, and its role in the City of Brains project.]

## Assembly Type

[Specify the assembly type: character, prop, or building. Each type has different slot groups available.]

## Design Notes

[Any specific design decisions, art direction notes, or technical constraints for this assembly.]

## Variations

[Document any planned variations, color variants, or customization options.]

## Inheritance

[If this assembly inherits from another, describe the parent relationship and what is being inherited or overridden.]

## Export Targets

[List any specific export pipelines or game engines this assembly is designed for.]
