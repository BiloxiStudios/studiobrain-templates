---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
ui_icon: "MessageSquare"
ui_color: "#3b82f6"
generation_instructions: |
  Generate a dialogue tree with branching conversation paths. Define participants, primary speaker, and context (quest, campaign, event, location). Include dialogue nodes with conditions, responses, and outcomes. A good dialogue tree feels natural, reflects each character's voice, and advances the narrative or reveals information.
editable: true
marketplace_eligible: false
id: "[snake_case_name]"
entity_type: "dialogue"
folder_name: "Dialogue"
file_prefix: "DLG_"
asset_subfolders:
  - audio
  - images
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
# FIELD WIDGET CONFIGURATION
field_config:
  quest_id:
    widget: entity-selector
    reference_type: quest
    max_selections: 1
  campaign_id:
    widget: entity-selector
    reference_type: campaign
    max_selections: 1
  event_id:
    widget: entity-selector
    reference_type: event
    max_selections: 1
  location_id:
    widget: entity-selector
    reference_type: location
    max_selections: 1
  participants:
    widget: entity-selector
    reference_type: character
    max_selections: 10
  primary_speaker:
    widget: entity-selector
    reference_type: character
    max_selections: 1

status: "draft"

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"
  game_uefn: "none"
  tv_showrunner: "none"
  notes: ""

# PRIMARY IMAGE
primary_image: ""

# BASIC INFORMATION (REQUIRED)
name: "Dialogue Tree Display Name"
tree_type: "conversation"

# CONTEXT AND RELATIONSHIPS
quest_id: null
campaign_id: null
event_id: null
location_id: null

# PARTICIPANTS
participants:
  - "character_id"
  - "player"
primary_speaker: "character_id"

# TREE CONFIGURATION
branching_complexity: "medium"
estimated_duration: "5-10 minutes"
max_depth: 8
multiple_paths: true

# CONDITIONAL LOGIC
prerequisites: []
unlock_conditions: []

# ATMOSPHERE
atmosphere: "casual"

# GAME MECHANICS
skill_checks:
  - skill: "charisma"
    threshold: 50
reputation_effects:
  - faction_id: "faction_id"
    change: 5
item_requirements: []

# VISUAL AND AUDIO
background_music: ""
lighting: "ambient"
camera_style: "over_the_shoulder"
visual_effects: []
voice_acting: []

# TREE STRUCTURE
root_node: "greeting"
node_count: 0
choice_count: 0
ending_count: 1

# EXPORT AND VERSIONING
auto_export: true
json_backup: true
localization_ready: false
json_structure: {}

# CONTENT
description: null
dialogue_script: null
implementation_notes: null
# NEW-ENTITY MARKDOWN SKELETON (SBAI-1857)
markdown_skeleton: |
  ## Context

  ## Script

  ## Notes
---

# Dialogue: [Dialogue Tree Display Name]

Dialogue tree narrative context and notes.
