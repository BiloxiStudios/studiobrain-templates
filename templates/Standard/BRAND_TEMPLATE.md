---
id: "unique_lowercase_id"  # Must match folder name (e.g., double_dip_dog_sauce) - snake_case
name: "Brand Display Name"  # Display name shown to users

# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
ui_icon: "Building"
ui_color: "#8b5cf6"
generation_instructions: |
  Generate a brand with a clear identity, market position, and visual language. Include a tagline, founding year, industry, and color palette. Define relationships to parent companies, subsidiaries, and key personnel. A good brand feels like a real business with consistent values and recognizable style.
editable: true
marketplace_eligible: true
entity_type: "brand"
folder_name: "Brands"
file_prefix: "BR_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules:
  - BRAND_RULES.md
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
  founded:
    widget: year
    min: 1800
    max: 1998
  defunct_year:
    widget: year
    min: 1800
    max: 1998
  parent_company:
    widget: entity-selector
    reference_type: brand
    max_selections: 1
  subsidiaries:
    widget: entity-selector
    reference_type: brand
    max_selections: 20
  headquarters:
    widget: entity-selector
    reference_type: location
    max_selections: 1
  job_positions:
    widget: entity-selector
    reference_type: job
    max_selections: 20
  key_personnel:
    widget: entity-selector
    reference_type: character
    max_selections: 10
    relationship_types:
      - { value: "ceo", label: "CEO" }
      - { value: "cfo", label: "CFO" }
      - { value: "coo", label: "COO" }
      - { value: "marketing_director", label: "Marketing Director" }
      - { value: "founder", label: "Founder" }
      - { value: "board_member", label: "Board Member" }

status: "active"  # active, defunct, merged, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
tagline: "Your catchy slogan here"
founded: 1987             # Year brand was founded (integer, e.g., 1987)
industry: "food_service"  # food_service, retail, technology, healthcare, etc.
market_position: "market_leader"  # market_leader, competitor, niche, startup

# TEMPORAL INFORMATION (Optional)
defunct_year: null        # Year brand ceased operations (if applicable)
major_milestones:         # Important dates in brand history
  # - year: 1998
  #   event: "IPO and stock market debut"
  # - year: 2005
  #   event: "Expanded to national market"

# VISUAL IDENTITY
logo_files:
  primary: "media/logo_primary.png"
  alternate: "media/logo_alt.png"
  icon: "media/icon.png"
color_palette:
  primary: "#FF0000"
  secondary: "#000000"
  accent: "#FFFFFF"
typography:
  heading: "Arial Bold"
  body: "Helvetica"
  special: "Custom Font"

# AUDIO IDENTITY
jingle_file: "media/jingle.mp3"
jingle_duration: "0:15"
voice_actor: "Jane Smith"
audio_style: "upbeat and energetic"
signature_sounds:
  - "cash register ding"
  - "packaging crinkle"

# BRAND MESSAGING
brand_values:
  - "quality"
  - "affordability"
  - "convenience"
brand_personality:
  - "friendly"
  - "trustworthy"
  - "innovative"
target_audience: "middle-class families"
messaging_tone: "casual and approachable"

# CORPORATE STRUCTURE
parent_company: "parent_brand_id"  # If subsidiary
subsidiaries:
  - "sub_brand_id_1"
  - "sub_brand_id_2"
headquarters: "location_id"  # References location folder

# EMPLOYMENT & PERSONNEL
job_positions:  # Available job roles at this brand
  - "nerdent_technician"
  - "security_specialist"
  - "sales_associate"
key_personnel:  # Important individuals with their roles
  - character_id: "character_id"
    job_role: "ceo"
    status: "active"
  - character_id: "character_id"
    job_role: "marketing_director" 
    status: "active"
employee_count: 150
corporate_culture: "aggressive expansion"

# PRODUCTS & SERVICES
brand_items:  # Items/products associated with this brand
  - item_id: "sauce_001"
    relationship: "produces"
  - item_id: "sauce_002"
    relationship: "produces"
  - item_id: "branded_merchandise"
    relationship: "sells"
signature_product: "sauce_001"
quality_tier: "mid_range"  # budget, mid_range, premium, luxury

# MARKET PRESENCE
geographic_reach:
  - "downtown_district"
  - "suburbs"
  - "industrial_zone"
store_count: 47
franchise_model: true
distribution_channels:
  - "retail stores"
  - "online delivery"
  - "vending machines"
market_share: "35%"

# REPUTATION & PUBLIC PERCEPTION
public_opinion: "mixed"  # beloved, positive, mixed, negative, hated
controversy_level: "moderate"  # none, low, moderate, high, extreme
reputation_factors:
  - "affordable prices"
  - "questionable ingredients"
  - "aggressive marketing"
consumer_loyalty: "moderate"  # low, moderate, high, fanatic

# STORY INTEGRATION
narrative_role: "major_antagonist"  # background, minor, moderate, major, central
story_significance: "infection vector"
dark_secrets:
  - "uses chemical plant runoff"
  - "executives knew about side effects"
  - "planned obsolescence in products"
conspiracy_connections:
  - "chemical plant experiments"
  - "government contracts"
  - "eclipse research funding"

# MARKETING CAMPAIGNS
active_campaigns:
  - campaign_id: "double_dip_promo"
    type: "social media"
    message: "Double the dip, double the fun!"
  - campaign_id: "family_values"
    type: "television"
    message: "Bringing families together"
slogans:
  - "Double dip, double dip, go ahead and double dip!"
  - "The sauce that makes everything better"
  - "Lighting up your taste buds"

# LOCATIONS & FACILITIES
retail_locations:
  - "location_id_1"
  - "location_id_2"
manufacturing:
  - "chemical_plant_district"
  - "industrial_zone_factory"
warehouses:
  - "warehouse_district_a"

# RELATIONSHIPS
competitor_brands:
  - "brand_id_1"
  - "brand_id_2"
partner_brands:
  - "brand_id_3"
  - "brand_id_4"
affiliated_characters:
  - character_id: "character_id"
    relationship: "spokesperson"
  - character_id: "character_id"
    relationship: "employee"

# CONTENT FIELDS
brand_overview: null  # Will be in markdown below
corporate_history: null  # Will be in markdown below
marketing_strategy: null  # Will be in markdown below
conspiracy_details: null  # Will be in markdown below

# AI GENERATION HELPERS
ai_brand_voice: "[Brand's distinctive communication style and tone for AI content generation]"
ai_visual_identity: "[Key visual elements and style for AI image generation]"
ai_marketing_summary: "[Brief brand positioning for AI marketing content]"
# NEW-ENTITY MARKDOWN SKELETON (SBAI-1857)
markdown_skeleton: |
  ## Overview

  ## Identity & Values

  ## Products & Services

  ## Notes
---

# [Brand Name]

## Brand Overview

[Comprehensive description of what the brand is, what it stands for, and its place in the City of Brains universe]

## Corporate History

[The story of how the brand was founded, major milestones, expansions, acquisitions, etc.]

## Products and Services

[Detailed description of what the brand offers, flagship products, quality, pricing strategy]

## Marketing Strategy

[How the brand markets itself, target demographics, advertising channels, brand voice]

## Public Perception

[How the general public views the brand, any controversies, loyal customer base, critics]

## Dark Secrets and Conspiracies

[Hidden information about the brand that players might discover, connections to the outbreak, unethical practices]

## The Infection Connection

[For brands connected to the zombie outbreak, explain their role in detail]

## Notable Marketing Campaigns

### "Double Dip" Campaign
[Description of the campaign, when it ran, impact on sales and culture]

### "Family Values" Campaign
[Description of the campaign, target audience, effectiveness]

## Facilities and Operations

[Where the brand operates, manufacturing facilities, distribution network]

## Key Personnel

[Important people associated with the brand and their roles]

## Competition and Market Position

[How the brand competes, market share, competitive advantages and disadvantages]

## Developer Notes

[Technical notes for implementing the brand in-game, asset requirements, audio cues]

## Brand Assets

[List of required assets: logos, audio files, marketing materials, in-game advertisements]