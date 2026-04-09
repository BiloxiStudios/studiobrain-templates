---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
ui_icon: "Calendar"
ui_color: "#ec4899"
generation_instructions: |
  Generate an event that represents a significant occurrence in the world. Define event type, trigger conditions, duration, and affected entities (locations, characters, factions). Describe consequences, escalation stages, and resolution conditions. A good event creates narrative momentum and has meaningful ripple effects across the world.
editable: true
marketplace_eligible: true
id: "[snake_case_name]"  # Must match folder name (e.g., zombie_horde_attack)
entity_type: "event"
folder_name: "Events"
file_prefix: "EVENT_"
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
  affected_locations:
    widget: entity-selector
    reference_type: location
    max_selections: 20
  affected_characters:
    widget: entity-selector
    reference_type: character
    max_selections: 20
  affected_factions:
    widget: entity-selector
    reference_type: faction
    max_selections: 10
  related_campaigns:
    widget: entity-selector
    reference_type: campaign
    max_selections: 5
  related_quests:
    widget: entity-selector
    reference_type: quest
    max_selections: 20

status: "active"  # active, disabled, completed, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Event Display Name"
event_type: "world"  # world, local, personal, faction, seasonal

# TIMING AND TRIGGERS
trigger_type: "scheduled"  # scheduled, random, conditional, manual
trigger_conditions:
  - condition: "time_passed"
    value: "7_days"
  - condition: "player_level"
    value: "10+"
trigger_probability: "25%"  # If random
duration: "3 hours"  # How long event lasts

# SCHEDULING
start_time: "2024-06-01T12:00:00"  # ISO format or null
end_time: "2024-06-01T15:00:00"  # ISO format or null
recurring: true
recurrence_pattern: "weekly"  # daily, weekly, monthly, seasonal

# LOCATION AND SCOPE
event_scope: "district"  # global, region, district, location, personal
affected_locations:
  - "downtown_district"
  - "industrial_zone"
affected_characters:
  - "all_outdoor_npcs"
  - "faction_guards"
affected_factions:
  - "survivors_alliance"
  - "military_remnants"

# EVENT MECHANICS
event_phases:
  - phase: 1
    name: "Warning Phase"
    duration: "30 minutes"
    description: "Sirens sound, NPCs take cover"
  - phase: 2
    name: "Main Attack"
    duration: "2 hours"
    description: "Zombie hordes spawn and attack"
  - phase: 3
    name: "Aftermath"
    duration: "30 minutes"
    description: "Cleanup and recovery"
player_participation: "optional"  # required, optional, automatic
participation_rewards:
  - reward: "experience"
    amount: 1000
  - reward: "faction_reputation"
    amount: 50
failure_consequences:
  - consequence: "location_damage"
    severity: "moderate"
  - consequence: "npc_deaths"
    severity: "high"

# STORY INTEGRATION
narrative_importance: "moderate"  # minor, moderate, major, critical
story_consequences:
  - consequence: "faction_power_shift"
    description: "Weakened faction loses territory"
  - consequence: "new_quest_available"
    description: "Rescue mission unlocked"
related_campaigns:
  - "main_story"
  - "faction_wars"
related_quests:
  - "defend_the_district"
  - "evacuation_protocol"

# WORLD STATE CHANGES
world_state_changes:
  - change: "zombie_density"
    value: "increased_50%"
    duration: "permanent"
  - change: "resource_scarcity"
    value: "moderate"
    duration: "7_days"
character_state_changes:
  - character: "all_civilians"
    change: "frightened"
    duration: "24_hours"
location_state_changes:
  - location: "safe_zones"
    change: "overcrowded"
    duration: "48_hours"
economy_effects:
  - effect: "price_increase"
    items: ["ammunition", "medical_supplies"]
    percentage: 25
    duration: "3_days"

# PLAYER INTERACTION
player_choices:
  - choice: "help_defend"
    description: "Join the defense forces"
  - choice: "evacuate_civilians"
    description: "Help civilians escape"
  - choice: "profit"
    description: "Loot abandoned areas"
choice_consequences:
  - choice: "help_defend"
    result: "faction_reputation_gain"
  - choice: "evacuate_civilians"
    result: "moral_reputation_gain"
  - choice: "profit"
    result: "items_but_reputation_loss"
dialogue_options:
  - npc: "faction_commander"
    option: "volunteer_to_help"
  - npc: "scared_civilian"
    option: "offer_shelter"

# VISUAL AND AUDIO
visual_effects:
  - effect: "weather_change"
    type: "dark_clouds"
  - effect: "lighting_change"
    type: "emergency_red"
audio_changes:
  - change: "ambient_music"
    track: "tension_theme"
  - change: "sound_effects"
    add: ["sirens", "distant_screams"]
environmental_changes:
  - change: "spawn_rates"
    enemy_type: "zombie"
    multiplier: 3
  - change: "loot_quality"
    modifier: "reduced"

# NOTIFICATIONS AND UI
notification_text: "WARNING: Massive zombie horde detected approaching the district!"
ui_changes:
  - element: "minimap"
    change: "show_horde_markers"
  - element: "hud"
    change: "display_event_timer"
hud_indicators:
  - indicator: "event_progress"
    type: "progress_bar"
  - indicator: "threat_level"
    type: "color_coded"

# SPAWNING AND ENEMIES
enemy_spawns:
  - enemy_type: "common_zombie"
    count: 100
    spawn_points: ["north_gate", "south_bridge"]
  - enemy_type: "special_infected"
    count: 10
    spawn_points: ["random"]
special_spawns:
  - spawn: "boss_zombie"
    probability: "10%"
    location: "district_center"

# ASSETS AND MEDIA
event_icon: "media/event_icon.png"
cutscene_files:
  - "media/event_intro.mp4"
audio_files:
  - "media/siren.mp3"
  - "media/horde_approaching.mp3"
image_files:
  - "media/event_banner.png"

# CONTENT FIELDS
description: null  # Will be in markdown below
background_lore: null  # Will be in markdown below
event_script: null  # Will be in markdown below
# NEW-ENTITY MARKDOWN SKELETON (SBAI-1857)
markdown_skeleton: |
  ## Summary

  ## Details

  ## Aftermath

  ## Notes
---