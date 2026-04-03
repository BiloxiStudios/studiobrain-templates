---
id: "unique_lowercase_id"  # Must match folder name (e.g., downtown_district) - snake_case
name: "District Display Name"  # Display name shown to users

# METADATA (REQUIRED)
template_version: "1.0"
ui_icon: "Map"
ui_color: "#f97316"
entity_type: "district"
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
status: "active"  # active, quarantined, destroyed, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
district_type: "commercial"  # commercial, residential, industrial, mixed

# GEOGRAPHIC INFORMATION
parent_location: "city_name"  # Parent city or region
boundaries:
  - point: "north"
    description: "Highway 101"
  - point: "south"
    description: "River Street"
  - point: "east"
    description: "Industrial Canal"
  - point: "west"
    description: "Mountain Ridge"
size_category: "large"  # small, medium, large, massive
population_density: "high"  # low, medium, high, overcrowded

# ADMINISTRATION
governing_faction: "faction_id"  # Which faction controls the district
district_council:
  - role: "district_leader"
    character_id: "character_id"
  - role: "security_chief"
    character_id: "character_id"
laws_regulations:
  - "curfew at 10pm"
  - "mandatory ID checks"
  - "no unauthorized gatherings"
tax_rate: "15%"
services:
  - "basic utilities"
  - "emergency medical"
  - "security patrols"

# ECONOMY
primary_industries:
  - "retail"
  - "entertainment"
  - "finance"
economic_status: "declining"  # thriving, stable, declining, collapsed
unemployment_rate: "12%"
major_employers:
  - "megamart"
  - "chemical_plant"
  - "city_government"

# INFRASTRUCTURE
transportation:
  public_transit: "limited bus service"
  road_condition: "poor"
  parking: "scarce"
utilities:
  power: "intermittent"
  water: "contaminated"
  sewage: "backed up"
  internet: "sporadic"
emergency_services:
  police: "understaffed"
  fire: "one station"
  medical: "overwhelmed"
education:
  schools: 3
  condition: "abandoned"

# DEMOGRAPHICS
population_count: 45000
age_demographics:
  children: "15%"
  adults: "60%"
  elderly: "25%"
species_demographics:
  human: "70%"
  infected: "25%"
  other: "5%"
cultural_groups:
  - "locals"
  - "refugees"
  - "corporate workers"

# SECURITY AND SAFETY
crime_rate: "high"  # low, moderate, high, extreme
security_presence: "heavy"  # none, light, moderate, heavy
common_crimes:
  - "looting"
  - "assault"
  - "black market trading"
safe_zones:
  - "police station"
  - "fortified mall"
danger_zones:
  - "abandoned subway"
  - "old hospital"

# ENVIRONMENT AND ATMOSPHERE
air_quality: "poor"  # excellent, good, moderate, poor, hazardous
noise_level: "loud"  # quiet, moderate, loud, deafening
cleanliness: "dirty"  # pristine, clean, average, dirty, squalid
architecture_style: "modern commercial"
landmark_locations:
  - "city_hall"
  - "central_park"
  - "megamart_headquarters"

# POST-OUTBREAK STATUS
outbreak_impact: "severe"  # minimal, moderate, severe, catastrophic
current_status: "partially controlled"  # safe, contested, dangerous, lost
survivor_population: 12000
zombie_density: "moderate"  # none, low, moderate, high, extreme

# STORY INTEGRATION
narrative_importance: "major"  # minor, moderate, major, central
key_events:
  - event: "first_outbreak"
    date: "2024-01-15"
    impact: "catastrophic"
  - event: "faction_takeover"
    date: "2024-03-20"
    impact: "moderate"
story_chapters:
  - "chapter_1"
  - "chapter_4"
  - "chapter_7"
faction_relations:
  faction_1: "allied"
  faction_2: "hostile"
  faction_3: "neutral"

# ASSETS & MEDIA
district_map: "media/district_map.png"
concept_art:
  - "media/skyline.jpg"
  - "media/street_view.jpg"
screenshots:
  - "media/ingame_1.png"
  - "media/ingame_2.png"

# CONTENT FIELDS
description: null  # Will be in markdown below
history: null  # Will be in markdown below
notable_features: null  # Will be in markdown below
current_situation: null  # Will be in markdown below

# AI GENERATION HELPERS
ai_district_ambiance: "[Overall mood and atmosphere for AI environmental generation]"
ai_architectural_style: "[Key visual and structural elements for AI image generation]"
ai_cultural_summary: "[Brief cultural and social context for AI content creation]"
---