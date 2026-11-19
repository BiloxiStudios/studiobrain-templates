---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "document"
ui_icon: "Globe"
ui_color: "#0ea5e9"
generation_instructions: |
  Generate a universe that defines the top-level setting for a creative project. Establish genre, target audience, time period, technology level, and core themes. Define the primary color palette and tone. A good universe document provides the foundational rules and aesthetic that all other entities within it must respect.
editable: true
marketplace_eligible: true
id: "[snake_case_name]"  # e.g., project_name
entity_type: "universe"
folder_name: "Universes"
file_prefix: "UNIV_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules:
  - UNIVERSE_RULES.md
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  primary_colors:
    widget: color-group
    swatches:
      - key: accent_1
        label: "Accent 1"
      - key: accent_2
        label: "Accent 2"
      - key: accent_3
        label: "Accent 3"
      - key: accent_4
        label: "Accent 4"
      - key: accent_5
        label: "Accent 5"

status: "active"  # active, development, archived

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Universe Display Name"
ip_owner: "Company/Individual Name"
genre: ""  # horror, comedy, sci-fi, fantasy, or whatever this project is
target_audience: ""  # kids, teen, mature, adult
version: "1.0"

# TEMPORAL SETTING
era: ""  # modern, historical, future, alternate_timeline, or blank until the project decides
time_period: ""
technology_level: ""  # primitive, modern, advanced, mixed
key_tech_rules: []  # Devices and practices this project allows or refuses

# GEOGRAPHIC SETTING
world_type: ""  # earth, alternate_earth, fantasy_world, space
primary_locations: []  # Places that exist in this project
scope: ""  # local, regional, global, galactic

# CORE THEMES
primary_themes: []
secondary_themes: []
tone: ""
content_rating: ""

# VISUAL STYLE
art_style: ""
primary_colors: {}
lighting_style: ""
atmospheric_elements: []

# AUDIO DIRECTION
music_genre: ""
sound_design: ""
signature_tracks: []
voice_direction: ""

# NARRATIVE RULES
narrative_style: ""
perspective: ""
storytelling_principles: []

# LORE FOUNDATIONS
origin_story: null
key_events: []
power_systems: []
factions_overview: []

# ECONOMY SYSTEMS
primary_currency: ""
secondary_currency: ""
trade_systems: []
economic_principles: []

# TECHNOLOGY SYSTEMS
communication: []
transportation: []
weapons_tech: ""
special_tech: []

# CHARACTER GUIDELINES
naming_conventions: []
speech_patterns: []
species_available: []

# BRAND GUIDELINES
brand_era: ""
advertising_style: ""
product_categories: []
corporate_culture: ""

# LOCATION GUIDELINES
architectural_styles: []
biome_types: []
environmental_hazards: []

# GAMEPLAY SYSTEMS
core_mechanics: []
progression_systems: []
difficulty_options: []

# CONTENT RESTRICTIONS
prohibited_content: []
allowed_mature_content: []

# EXPANSION RULES
canon_requirements:
  - "Must not contradict lore this project has recorded"
  - "Must fit the time period this project records"
  - "Must match the tone this project records"
new_content_process:
  - "Document additions on the project's own entities"

# CROSS-MEDIA RIGHTS
game_rights: ""
film_rights: ""
merchandise_rights: ""
literary_rights: ""

# REFERENCE MATERIALS
style_guides: []
inspiration_sources: []

# CONTENT FIELDS
universe_overview: null  # Will be in markdown below
historical_timeline: null  # Will be in markdown below
world_building_notes: null  # Will be in markdown below
# NEW-ENTITY MARKDOWN SKELETON (SBAI-1857)
markdown_skeleton: |
  ## Overview

  ## History

  ## Setting

  ## Notes
---