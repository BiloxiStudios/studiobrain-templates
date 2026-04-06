---
id: "unique_lowercase_id"  # Must match folder name (e.g., deal_mart) - snake_case
name: "Location Display Name"  # Display name shown to users

# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
ui_icon: "MapPin"
ui_color: "#f59e0b"
editable: true
marketplace_eligible: true
entity_type: "location"
folder_name: "Locations"
file_prefix: "LOC_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules:
  - LOCATION_RULES.md
  - LOCATION_WORKFLOW.md
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  color_palette:
    widget: color-group
    swatches:
      - key: primary
        label: "Primary Color"
      - key: secondary
        label: "Secondary Color"
      - key: accent
        label: "Accent Color"
  founded_year:
    widget: year
    min: 1800
    max: 1998
  destroyed_year:
    widget: year
    min: 1800
    max: 1998
  parent_location:
    widget: entity-selector
    reference_type: district
    max_selections: 1
  faction_control:
    widget: entity-selector
    reference_type: faction
    max_selections: 1
  primary_npcs:
    widget: entity-selector
    reference_type: character
    max_selections: 20
  primary_brand:
    widget: entity-selector
    reference_type: brand
    max_selections: 1
  associated_brands:
    widget: entity-selector
    reference_type: brand
    max_selections: 10

status: "active"  # active, destroyed, quarantined, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# WORKFLOW CONFIGURATION
workflow:
  definition: "LOCATION_WORKFLOW.md"
  default_stage: "concept"
  allow_multiple_active: false
  notifications:
    on_enter:
      - type: "print"
        message: "Location entered stage {{stage_name}}"
    on_exit:
      - type: "archive"
        target: "stage_history/locations/{{location_id}}/{{old_stage}}"
    on_complete:
      - type: "print"
        message: "Location completed {{stage_name}}"
  # Note: Production status and workflow are separate systems
  # - production_status: tracks progress across domains (game, TV, etc.)
  # - workflow: tracks entity lifecycle (concept -> published -> active -> archived)

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
business_name: null  # If it's a business
location_type: "retail"  # retail, residential, industrial, recreational, etc.
category: "store"  # store, restaurant, apartment, park, etc.

# TEMPORAL INFORMATION (Optional)
founded_year: null        # Year location was established
destroyed_year: null      # Year location was destroyed/closed (if applicable)
key_events:               # Important dates in location history
  # - year: 1975
  #   event: "Grand opening"
  # - year: 1999
  #   event: "Renovation"

# GEOGRAPHIC INFORMATION
parent_location: "district_id"  # Parent district or area
coordinates_x: 100
coordinates_y: 200
coordinates_z: 0
biome: "urban"  # urban, suburban, industrial, forest, etc.
district: "downtown"  # District name
address: "123 Main Street"

# ACCESSIBILITY
enterable: true  # Can player enter?
exterior_access: true  # Accessible from outside?
entrance_points:
  - type: "main"
    location: "front door"
    status: "open"  # open, locked, barricaded
  - type: "service"
    location: "back alley"
    status: "locked"
interior_zones:
  - zone_id: "main_floor"
    accessible: true
  - zone_id: "basement"
    accessible: false

# PHYSICAL DESCRIPTION
building_type: "standalone"  # standalone, mall_shop, high_rise, etc.
architectural_style: "modern commercial"
size: "medium"  # small, medium, large, massive
condition: "damaged"  # pristine, good, damaged, ruined
notable_features:
  - "broken windows"
  - "graffiti on walls"
  - "barricaded entrance"

# ATMOSPHERE & ENVIRONMENT
lighting: "dim"  # bright, normal, dim, dark
color_palette:
  primary: "#FF0000"
  secondary: "#000000"
  accent: "#FFFFFF"
ambient_sounds:
  - "distant moaning"
  - "dripping water"
  - "creaking metal"
weather_effects:
  - "rain leaks through roof"
  - "wind through broken windows"
air_quality: "musty"  # fresh, normal, musty, toxic

# STORY INTEGRATION
narrative_importance: "major"  # minor, moderate, major, critical
story_chapters:
  - "chapter_1"
  - "chapter_3"
faction_control: "faction_id"  # Which faction controls it
faction_relationship: "headquarters"  # headquarters, outpost, contested, neutral

# INTERACTIVE ELEMENTS
searchable_objects:
  - object: "cash register"
    loot_table: "store_register"
    searched: false
  - object: "storage room"
    loot_table: "store_supplies"
    searched: false
vendors:
  - vendor_id: "character_id"
    vendor_type: "general_store"
    hours: "24/7"
minigames:
  - game_id: "lock_picking"
    difficulty: "medium"
interactive_features:
  - "workbench"
  - "save_point"
  - "fast_travel"

# NPCS & POPULATION
primary_npcs:
  - character_id: "gary_gasstation"
    role: "vendor"
    schedule: "night_shift"
background_npcs:
  - type: "survivor"
    count: 5
    behavior: "passive"
npc_density: "low"  # none, low, medium, high
crowd_behavior: "scattered"  # scattered, grouped, panicked, hostile

# ECONOMY & SERVICES
business_type: "convenience_store"
operating_hours: "24/7"  # or specific hours
currency_accepted:
  - "credits"
  - "barter"
services_offered:
  - "buy items"
  - "sell items"
  - "repair equipment"
price_range: "budget"  # budget, moderate, expensive, luxury

# BRAND ASSOCIATIONS
primary_brand: "brand_id"  # Main brand if applicable
associated_brands:
  - brand_id: "megamart"
    presence: "signage"
  - brand_id: "double_dip_dog_sauce"
    presence: "products"
advertising_presence:
  - "neon signs"
  - "billboards"
  - "product displays"

# SAFETY & HAZARDS
threat_level: "moderate"  # safe, low, moderate, high, extreme
hazards:
  - type: "zombies"
    frequency: "occasional"
    severity: "moderate"
  - type: "structural"
    frequency: "constant"
    severity: "low"
zombie_risk: "medium"  # none, low, medium, high, extreme
infection_status: "contaminated"  # clean, contaminated, infected, quarantined

# CONTENT FIELDS
description: null  # Brief description (also in markdown below for details)
atmosphere: null  # Atmosphere description (also in markdown below for details)
hidden_secrets: []  # Hidden elements players can discover
historical_context: null  # Will be in markdown below
gameplay_notes: null  # Will be in markdown below

# AI GENERATION HELPERS
ai_atmosphere_description: "[Brief atmospheric description for AI scene generation]"
ai_visual_style: "[Visual style and mood for AI image generation]"
ai_ambient_summary: "[Key environmental elements for AI context]"
# NEW-ENTITY MARKDOWN SKELETON (SBAI-1857)
markdown_skeleton: |
  ## Location Description

  ## History

  ## Notable Features

  ## Notes
---

# [Location Name]

## Description

[Detailed description of the location. What does it look like? What's the general vibe? What would a player first notice when approaching?]

## Atmosphere

[Describe the mood and feeling of the location. Is it tense? Peaceful? Creepy? How does it make people feel?]

## Historical Context

[What was this place before the outbreak? What happened here? Any significant events?]

## Layout

[Describe the physical layout. Where are the entrances? What are the main areas? How do they connect?]

## Points of Interest

### Main Floor
- Cash register area (searchable)
- Product shelves (mostly empty)
- Storage room (locked)

### Back Room
- Employee break area
- Manager's office (locked safe inside)
- Loading dock (barricaded)

## NPC Interactions

[Describe the NPCs found here and how players can interact with them]

## Loot and Resources

[What valuable items can be found here? What makes it worth visiting?]

## Hazards and Threats

[Detailed description of dangers players might face]

## Story Significance

[How does this location tie into the main narrative? Any quests or events?]

## Developer Notes

[Technical notes for level designers, environmental artists, sound designers, etc.]

## Secrets

[Hidden areas, easter eggs, or secret loot that players can discover]