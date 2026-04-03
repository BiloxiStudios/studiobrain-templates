---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "core"
ui_icon: "Clock"
ui_color: "#64748b"
editable: false
marketplace_eligible: false
id: "[snake_case_name]"  # Must match timeline entry (e.g., campaign_start_main_story)
entity_type: "timeline"
folder_name: "Timelines"
file_prefix: "TIMEL_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
status: "active"  # active, draft, archived

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Timeline Entry Title"
entry_type: "event"  # event, quest_start, quest_end, dialogue, world_change, campaign_start, campaign_end
timestamp: "YYYY-MM-DDTHH:MM:SSZ"  # ISO 8601 format

# TEMPORAL DETAILS
game_year: 1998  # Year in the game narrative (1998-1999 for City of Brains)
game_date: null  # Optional: Specific date like "June 15, 1998"
duration: "30 minutes"  # How long this event/action lasts
timeline_category: "main"  # main, character, location, campaign, faction

# ENTITY RELATIONSHIPS
campaign_id: "campaign_id"  # If part of a campaign
quest_id: "quest_id"        # If part of a quest
event_id: "event_id"        # If this is an event
dialogue_id: "dialogue_id"  # If this involves dialogue

# CROSS-REFERENCES (Arrays of entity IDs)
characters_involved:
  - "character_id1"
  - "character_id2"
locations_involved:
  - "location_id1"
  - "location_id2"
brands_involved:
  - "brand_id1"
factions_involved:
  - "faction_id1"

# CONSEQUENCES AND CHANGES
world_state_changes:
  - type: "faction_reputation"
    target: "scientists_guild"
    change: 100
    description: "Guild reputation increased"
  - type: "location_status"
    target: "chemical_plant"
    change: "secured"
    description: "Plant is now under guild control"

relationship_changes:
  - characters: ["character_id1", "character_id2"]
    change: "trust_increased"
    description: "Characters now trust each other more"
  - characters: ["character_id1", "faction_leader"]
    change: "alliance_formed"
    description: "Character joins the faction"

item_changes:
  - action: "gained"  # gained, lost, consumed, transformed
    item_id: "cure_sample"
    quantity: 1
    description: "Obtained rare cure sample"
  - action: "lost"
    item_id: "keycard_alpha"
    quantity: 1
    description: "Keycard was destroyed in explosion"

# AUTO-POPULATION METADATA
source: "manual"  # manual, auto_discovered, imported, story_sync
confidence: 1.0   # 0.0-1.0 confidence score for auto-discovered entries
vector_references:  # IDs of documents in vector database that support this entry
  - "doc_id_1"
  - "doc_id_2"

# TIMELINE ORGANIZATION
timeline_id: "master_timeline"  # For nested/sub-timelines
sequence_order: 1  # Order within a sequence of related events
prerequisites:  # Events that must happen before this one
  - "previous_event_id"
enables:  # Events that this one makes possible
  - "next_event_id"

# VISUAL AND METADATA
importance_level: "major"  # minor, moderate, major, critical
visual_markers:
  - "campaign_milestone"
  - "character_development"
  - "world_changing"

# AI GENERATION CONTEXT
generation_context:
  mood: "tense"
  atmosphere: "urgent"
  narrative_focus: "character_growth"
  themes:
    - "sacrifice"
    - "redemption"
    - "consequences"

# CONTENT FIELDS
description: null  # Will be in markdown below
detailed_account: null  # Will be in markdown below
consequences_analysis: null  # Will be in markdown below
---

# Timeline Entry Description

[Detailed description of what happens during this timeline entry. This should be written as a narrative account that can be used by AI systems and human writers.]

## Context and Background

[Background information that led to this moment. What were the circumstances that created this situation?]

## Key Moments

### [Timestamp] - [Event Name]
[Detailed description of specific moments within this timeline entry]

### [Timestamp] - [Event Name]  
[Another key moment if this entry spans multiple events]

## Immediate Consequences

[What happened immediately as a result of this timeline entry?]

## Long-term Impact

[How did this timeline entry affect the broader story, world, or characters in the long term?]

## Character Reactions

### [Character Name]
[How did this character react to or participate in this timeline entry?]

### [Character Name]
[Another character's involvement or reaction]

## World State Changes

[Detailed description of how this timeline entry changed the state of the world, factions, locations, or other story elements]

## AI Generation Notes

[Notes for AI systems about how to use this timeline entry in generation, what themes to emphasize, what connections to make with other entries, etc.]

## Developer Notes

[Internal notes for developers and writers about this timeline entry, including any special considerations for implementation or presentation]