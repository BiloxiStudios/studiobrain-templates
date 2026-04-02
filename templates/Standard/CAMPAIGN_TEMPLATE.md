---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
ui_icon: "Flag"
ui_color: "#14b8a6"
editable: true
marketplace_eligible: true
id: "[snake_case_name]"  # Must match folder name (e.g., main_story)
entity_type: "campaign"
folder_name: "Campaigns"
file_prefix: "CAMP_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules: []
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  protagonist_characters:
    widget: entity-selector
    reference_type: character
    max_selections: 10
  supporting_characters:
    widget: entity-selector
    reference_type: character
    max_selections: 20
  antagonist_characters:
    widget: entity-selector
    reference_type: character
    max_selections: 10
  involved_factions:
    widget: entity-selector
    reference_type: faction
    max_selections: 10
  primary_locations:
    widget: entity-selector
    reference_type: location
    max_selections: 20
  secondary_locations:
    widget: entity-selector
    reference_type: location
    max_selections: 20
  starting_location:
    widget: entity-selector
    reference_type: location
    max_selections: 1

status: "active"  # active, completed, upcoming, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Campaign Display Name"
campaign_type: "main_story"  # main_story, side_story, dlc, seasonal

# STRUCTURE AND ORGANIZATION
chapter_count: 10
estimated_duration: "20-30 hours"
difficulty_level: "normal"  # easy, normal, hard, nightmare
prerequisites:
  - "tutorial_completed"
  - "level_5_minimum"

# STORY INFORMATION
narrative_summary: "Brief summary of the campaign story"
main_objectives:
  - "Find the source of the infection"
  - "Unite the survivor factions"
  - "Discover the cure"
themes:
  - "survival"
  - "redemption"
  - "sacrifice"
tone: "dark with moments of hope"  # dark, serious, humorous, mixed

# CHARACTERS AND FACTIONS INVOLVED
protagonist_characters:
  - "player_character"
  - "companion_1"
supporting_characters:
  - "gary_gasstation"
  - "sarah_techie"
antagonist_characters:
  - "general_steel"
  - "infected_scientist"
involved_factions:
  - faction_id: "survivors_alliance"
    role: "allied"
  - faction_id: "military_remnants"
    role: "antagonist"

# LOCATIONS AND SETTINGS
primary_locations:
  - "downtown_district"
  - "chemical_plant"
  - "underground_bunker"
secondary_locations:
  - "suburbs"
  - "industrial_zone"
starting_location: "safe_house_alpha"

# GAMEPLAY MECHANICS
gameplay_features:
  - "branching storylines"
  - "faction reputation system"
  - "base building"
  - "companion management"
rewards:
  - type: "achievement"
    name: "Campaign Complete"
    value: 100
  - type: "unlock"
    name: "New Game Plus"
    value: 1
branching_paths: true
multiple_endings: true

# PLAYER PROGRESSION
experience_reward: 50000
currency_reward: 10000
item_rewards:
  - item_id: "legendary_weapon"
    quantity: 1
  - item_id: "unique_armor"
    quantity: 1
skill_unlocks:
  - "master_survivor"
  - "faction_leader"

# SCHEDULING AND AVAILABILITY
seasonal_availability: false
start_date: null
end_date: null
repeatable: false

# CONTENT ORGANIZATION
quest_sequence:
  - "quest_001_escape"
  - "quest_002_first_contact"
  - "quest_003_supply_run"
optional_quests:
  - "side_quest_001"
  - "side_quest_002"
related_events:
  - "outbreak_anniversary"
  - "faction_war"

# ASSETS AND MEDIA
campaign_banner: "media/campaign_banner.png"
cutscene_files:
  - "media/intro_cutscene.mp4"
  - "media/ending_cutscene.mp4"
voice_files:
  - "media/narrator_intro.mp3"
  - "media/character_dialogue.mp3"
music_tracks:
  - "media/main_theme.mp3"
  - "media/combat_music.mp3"

# CONTENT FIELDS
description: null  # Will be in markdown below
backstory: null  # Will be in markdown below
epilogue: null  # Will be in markdown below
---