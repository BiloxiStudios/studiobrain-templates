---
# METADATA
template_version: "2.0"
template_category: "entity"
editable: true
marketplace_eligible: true
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
status: "active"

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"         # concept, in_progress, needs_work, art_done, complete
  game_uefn: "none"          # none, planned, in_progress, review, published, live
  tv_showrunner: "none"      # none, planned, in_progress, review, episode, current, archived
  notes: ""

# PRIMARY IMAGE
primary_image: ""

# ASSEMBLY IDENTITY
assembly_type: "[character|prop|building]"
name: "[Assembly Name]"
description: "[Brief description of this assembly]"

# SOURCE ENTITY REFERENCE
source_entity_type: "character"
source_entity_id: ""

# TEMPLATE HIERARCHY
hierarchy_level: "template"      # template | profile | variant | zombie_variant
parent_assembly_id: ""
inheritance_mode: "full"         # full | selective | none
locked_slots: []

# SLOT DEFINITIONS
slot_definitions:
  head:
    head_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Base head shape and skin"
  body:
    torso_base:
      required: true
      z_index: 10
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Base torso/shirt"
    legs_base:
      required: true
      z_index: 8
      overlay_modes: ["replace"]
      accepted_types: ["png", "webp"]
      description: "Base legs/pants"

# COLOR VARIANTS
color_variants:
  - name: "default"
    description: "Standard/canonical colors"

# EXPORT PROFILES
export_profile_files:
  - id: "showrunner_v1"
    file: "templates/Standard/ExportProfiles/showrunner_v1.yaml"

# AI VALIDATION
ai_validation:
  auto_validate_on_slot_assign: true
  validation_model: "florence2"
  slot_detection_confidence_threshold: 0.75
  style_consistency_threshold: 0.80
  parent_similarity_threshold: 0.70

# TAGS
tags: []
---

# [Assembly Name]

## Overview

[Brief description of this assembly.]

## Slot Map

[Filled vs. empty slots — auto-generated in the UI.]

## Inheritance

[If this assembly has a parent, describe what is inherited and what is overridden.]

## Color Variants

[List available color variants.]

## Export Notes

[Pipeline-specific notes.]

## Changelog

- [YYYY-MM-DD] Created assembly
