---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
ui_icon: "Clock"
ui_color: "#64748b"
editable: true
marketplace_eligible: false
id: "[snake_case_name]"
entity_type: "timeline"
folder_name: "Timeline"
file_prefix: "TL_"
asset_subfolders:
  - images
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
# FIELD WIDGET CONFIGURATION
field_config:
  campaign_id:
    widget: entity-selector
    reference_type: campaign
    max_selections: 1
  quest_id:
    widget: entity-selector
    reference_type: quest
    max_selections: 1
  event_id:
    widget: entity-selector
    reference_type: event
    max_selections: 1
  dialogue_id:
    widget: entity-selector
    reference_type: dialogue
    max_selections: 1
  characters_involved:
    widget: entity-selector
    reference_type: character
    max_selections: 20
  locations_involved:
    widget: entity-selector
    reference_type: location
    max_selections: 20
  brands_involved:
    widget: entity-selector
    reference_type: brand
    max_selections: 10
  factions_involved:
    widget: entity-selector
    reference_type: faction
    max_selections: 10
  game_year:
    widget: year
    min: 1900
    max: 1998

status: "active"

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"
  game_uefn: "none"
  tv_showrunner: "none"
  notes: ""

# PRIMARY IMAGE
primary_image: ""

# BASIC INFORMATION (REQUIRED)
name: "Timeline Entry Display Name"
entry_type: "event"

# TIMING
timestamp: "YYYY-MM-DD"
duration: "1 hour"
game_year: 1998
game_date: "June 15, 1998"

# CONTEXT REFERENCES
campaign_id: null
quest_id: null
event_id: null
dialogue_id: null

# ENTITIES INVOLVED
characters_involved:
  - "character_id"
locations_involved:
  - "location_id"
brands_involved: []
factions_involved: []

# CONSEQUENCES AND CHANGES
world_state_changes:
  - type: "faction_reputation"
    target: "faction_id"
    change: 10
relationship_changes:
  - characters:
      - "char1"
      - "char2"
    change: "trust_increased"
item_changes:
  - action: "gained"
    item_id: "item_id"
    quantity: 1

# AUTO-POPULATION METADATA
source: "manual"
confidence: 1.0
vector_references: []

# TIMELINE ORGANIZATION
parent_timeline_id: null
timeline_category: "main"
sequence_order: 0
prerequisites: []
enables: []
importance_level: "moderate"
visual_markers: []
generation_context: {}

# DETAILED CONTENT
detailed_account: null
consequences_analysis: null

# CONTENT
description: null
---

# Timeline Entry: [Timeline Entry Display Name]

Timeline entry narrative context.
