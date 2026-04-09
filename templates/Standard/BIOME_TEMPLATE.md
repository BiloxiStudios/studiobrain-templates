---
id: "unique_lowercase_id"  # Must match folder name (e.g., frozen_tundra)
name: "Biome Display Name"

# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
ui_icon: "Trees"
ui_color: "#22c55e"
generation_instructions: |
  Generate a biome with distinct environmental characteristics. Define climate, temperature, precipitation, and weather patterns. List flora, fauna, natural resources, and hazards specific to this biome. A good biome feels ecologically coherent and provides rich context for locations and characters within it.
editable: true
marketplace_eligible: true
entity_type: "biome"
folder_name: "Biomes"
file_prefix: "BIO_"
asset_subfolders:
  - images
  - audio
  - video
  - maps
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules:
  - BIOME_RULES.md
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  biome_type:
    widget: select
    options:
      - { value: "forest", label: "Forest" }
      - { value: "desert", label: "Desert" }
      - { value: "tundra", label: "Tundra" }
      - { value: "ocean", label: "Ocean" }
      - { value: "mountain", label: "Mountain" }
      - { value: "swamp", label: "Swamp" }
      - { value: "plains", label: "Plains" }
      - { value: "volcanic", label: "Volcanic" }
      - { value: "urban", label: "Urban" }
      - { value: "custom", label: "Custom" }
  dominant_colors:
    widget: color-group
    swatches:
      - key: primary
        label: "Primary Color"
      - key: secondary
        label: "Secondary Color"
      - key: accent
        label: "Accent Color"
      - key: sky
        label: "Sky / Atmosphere Color"
  parent_location:
    widget: entity-selector
    reference_type: location
    max_selections: 1
  connected_biomes:
    widget: entity-selector
    reference_type: biome
    max_selections: 10
    relationship_types:
      - { value: "borders", label: "Borders" }
      - { value: "transitions_to", label: "Transitions To" }
      - { value: "contained_within", label: "Contained Within" }
      - { value: "overlaps", label: "Overlaps" }
  flora:
    widget: tag-list
    allow_custom: true
    suggestions:
      - "deciduous trees"
      - "coniferous trees"
      - "grasses"
      - "mosses"
      - "fungi"
      - "flowering plants"
      - "aquatic plants"
      - "cacti"
      - "vines"
      - "ferns"
  fauna:
    widget: tag-list
    allow_custom: true
    suggestions:
      - "mammals"
      - "birds"
      - "reptiles"
      - "amphibians"
      - "insects"
      - "fish"
      - "crustaceans"
      - "mollusks"
  natural_resources:
    widget: tag-list
    allow_custom: true
    suggestions:
      - "timber"
      - "freshwater"
      - "minerals"
      - "fertile soil"
      - "medicinal plants"
      - "game animals"
      - "fish"
      - "stone"
      - "clay"
      - "peat"
  hazards:
    widget: tag-list
    allow_custom: true
    suggestions:
      - "flooding"
      - "wildfire"
      - "avalanche"
      - "quicksand"
      - "toxic gas"
      - "predators"
      - "extreme cold"
      - "extreme heat"
      - "volcanic eruption"
      - "landslide"

status: "active"  # active, archived, draft, deprecated

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# WORKFLOW CONFIGURATION
workflow:
  definition: "BIOME_WORKFLOW.md"
  default_stage: "concept"
  allow_multiple_active: false
  notifications:
    on_enter:
      - type: "print"
        message: "Biome entered stage {{stage_name}}"
    on_exit:
      - type: "archive"
        target: "stage_history/biomes/{{biome_id}}/{{old_stage}}"
    on_complete:
      - type: "print"
        message: "Biome completed {{stage_name}}"

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC IDENTITY
biome_name: "[Biome Name]"
biome_type: "forest"        # forest, desert, tundra, ocean, mountain, swamp, plains, volcanic, urban, custom

# CLIMATE & WEATHER
climate: "[Tropical / Temperate / Arid / Continental / Polar / Mediterranean / Subarctic]"
temperature_range:
  low: "[Lowest typical temperature, e.g. -10C / 14F]"
  high: "[Highest typical temperature, e.g. 35C / 95F]"
  unit: "C"                 # C or F
humidity: "[Low / Moderate / High / Variable]"
precipitation: "[Rainfall/snowfall description, e.g. Heavy monsoon rains June-September]"
weather_patterns:
  - "[Primary weather pattern, e.g. Afternoon thunderstorms in summer]"
  - "[Secondary weather pattern, e.g. Dense fog at dawn]"

# TERRAIN & GEOGRAPHY
terrain_description: "[Describe the ground, landforms, and physical geography]"
elevation: "[Elevation range, e.g. 500m - 2000m above sea level]"
water_features:
  - "[Rivers, lakes, ponds, waterfalls, springs, etc.]"
soil_type: "[Sandy / Clay / Loam / Rocky / Peat / Volcanic ash / Permafrost]"

# ECOLOGY
flora:
  - "[Dominant plant species or type 1]"
  - "[Dominant plant species or type 2]"
  - "[Dominant plant species or type 3]"
fauna:
  - "[Dominant animal species or type 1]"
  - "[Dominant animal species or type 2]"
  - "[Dominant animal species or type 3]"
natural_resources:
  - "[Resource 1, e.g. timber]"
  - "[Resource 2, e.g. freshwater]"
  - "[Resource 3, e.g. medicinal herbs]"
ecosystem_health: "stable"  # thriving, stable, declining, endangered, collapsed

# HAZARDS
hazards:
  - "[Environmental hazard 1, e.g. flash flooding]"
  - "[Environmental hazard 2, e.g. venomous wildlife]"
threat_level: "moderate"    # safe, low, moderate, high, extreme

# SEASONAL CHANGES
seasonal_changes:
  spring: "[How the biome changes in spring / wet season]"
  summer: "[How the biome changes in summer / dry season]"
  autumn: "[How the biome changes in autumn / transition]"
  winter: "[How the biome changes in winter / cold season]"

# SENSORY PROFILE
atmosphere: "[Overall mood and feel of being in this biome]"
dominant_colors:
  primary: "#2D5016"        # Main color impression
  secondary: "#8B6914"      # Supporting color
  accent: "#4A90D9"         # Highlight / contrast color
  sky: "#87CEEB"            # Sky and atmosphere color
ambient_sounds:
  - "[Sound 1, e.g. wind through canopy]"
  - "[Sound 2, e.g. birdsong]"
  - "[Sound 3, e.g. rushing water]"
ambient_smells:
  - "[Smell 1, e.g. damp earth]"
  - "[Smell 2, e.g. pine resin]"
visibility: "[Clear / Hazy / Foggy / Dense canopy / Open sky]"
light_quality: "[Dappled / Harsh / Soft / Dim / Variable]"

# SPATIAL RELATIONSHIPS
parent_location: "[Reference existing location ID, e.g. northern_continent]"
connected_biomes:
  - "[Adjacent biome ID 1]"
  - "[Adjacent biome ID 2]"
sub_regions:
  - "[Named sub-area 1 within this biome]"
  - "[Named sub-area 2 within this biome]"
area_size: "[Approximate area, e.g. 500 sq km / vast / small pocket]"

# NARRATIVE INTEGRATION
narrative_importance: "major"  # minor, moderate, major, critical
story_function:
  - "[Role in narrative, e.g. contested territory between factions]"
  - "[Story purpose, e.g. source of rare ingredient for main quest]"
cultural_significance: "[How inhabitants or travelers view this biome]"
historical_events:
  - "[Significant event that shaped this biome]"

# AI GENERATION HELPERS
ai_atmosphere_description: "[Brief atmospheric description for AI scene generation]"
ai_visual_style: "[Visual style and mood for AI image generation]"
ai_ambient_summary: "[Key environmental elements for AI context]"
# NEW-ENTITY MARKDOWN SKELETON (SBAI-1857)
markdown_skeleton: |
  ## Description

  ## Flora & Fauna

  ## Climate

  ## Notes
---

# [Biome Name]

## Background

[2-3 paragraphs describing the biome's formation, history, and current state. How did this environment come to be? What geological, magical, or industrial forces shaped it? What role does it play in the broader world? Include the biome's reputation among those who live near or within it.]

## Ecology

[2-3 paragraphs detailing the web of life within this biome. Describe the dominant plant species and how they create the landscape -- canopy layers, ground cover, aquatic vegetation. Explain the food chains: what the herbivores eat, what hunts them, and what apex predators rule the territory. Note any symbiotic relationships, invasive species, or ecological pressures threatening the balance. For non-natural biomes (urban, volcanic), describe whatever fills the ecological niche -- scavengers in ruins, extremophile organisms near vents.]

### Flora Highlights

- **[Plant/vegetation 1]**: [Brief description and ecological role]
- **[Plant/vegetation 2]**: [Brief description and ecological role]
- **[Plant/vegetation 3]**: [Brief description and ecological role]

### Fauna Highlights

- **[Animal/creature 1]**: [Brief description, behavior, and danger level]
- **[Animal/creature 2]**: [Brief description, behavior, and danger level]
- **[Animal/creature 3]**: [Brief description, behavior, and danger level]

## Hazards & Challenges

[1-2 paragraphs describing the dangers of traveling through or living in this biome. Include both environmental hazards (weather, terrain, natural disasters) and biological threats (predators, poisonous plants, disease). Explain how these hazards change with the seasons or time of day. Note any areas that are particularly dangerous and why.]

### Known Hazards

| Hazard | Severity | Frequency | Season |
|--------|----------|-----------|--------|
| [Hazard 1] | [Low/Medium/High/Extreme] | [Rare/Occasional/Common/Constant] | [When it occurs] |
| [Hazard 2] | [Low/Medium/High/Extreme] | [Rare/Occasional/Common/Constant] | [When it occurs] |
| [Hazard 3] | [Low/Medium/High/Extreme] | [Rare/Occasional/Common/Constant] | [When it occurs] |

## Seasonal Cycles

[1-2 paragraphs describing how the biome transforms across seasons. What does the landscape look like in each season? How do animal behaviors shift -- migrations, hibernation, breeding? Which seasons bring abundance and which bring scarcity? For biomes without traditional seasons (tropical, underground), describe whatever cyclical patterns exist -- monsoons, tidal cycles, eruption intervals.]

## Sensory Details

**Sight**: [What travelers see -- the landscape at different times of day, weather conditions, notable visual features. Describe the quality of light, the depth of the sky, the textures of the terrain.]

**Sound**: [The soundscape -- what fills the air at dawn, midday, dusk, and midnight. Silence itself can be a defining sound. Describe layered audio: distant, mid-range, and close sounds.]

**Smell**: [The dominant scents -- soil, vegetation, water, decay, mineral. How smells change with weather and season. What you smell before you see.]

**Touch**: [What the air feels like on skin -- humidity, temperature, wind. The ground underfoot. Textures of the vegetation. The bite of insects or the sting of plants.]

## Cultural Impact

[1-2 paragraphs describing how this biome affects the people, creatures, or civilizations that live near or within it. What resources does it provide? What industries or traditions depend on it? How do local cultures view the biome -- with reverence, fear, pragmatism? Are there territorial disputes over it? Does it serve as a boundary between nations or factions?]

## Developer Notes

[Technical notes for world builders, level designers, and environmental artists. Include guidance on rendering priorities, ambient audio loops, particle effects, lighting setups, and any gameplay mechanics tied to the biome (movement speed, visibility range, resource gathering rates).]
