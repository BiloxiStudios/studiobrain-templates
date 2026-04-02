---
id: "unique_lowercase_id"  # Must match folder name (e.g., survivors_alliance)
name: "Faction Display Name"

# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
editable: true
marketplace_eligible: true
entity_type: "faction"
folder_name: "Factions"
file_prefix: "FAC_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules:
  - FACTION_RULES.md
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  leadership:
    widget: entity-selector
    reference_type: character
    max_selections: 10
    relationship_types:
      - { value: "supreme_leader", label: "Supreme Leader" }
      - { value: "second_command", label: "Second in Command" }
      - { value: "advisor", label: "Advisor" }
      - { value: "officer", label: "Officer" }
  headquarters:
    widget: entity-selector
    reference_type: location
    max_selections: 1
  allies:
    widget: entity-selector
    reference_type: faction
    max_selections: 10
    relationship_types:
      - { value: "military_alliance", label: "Military Alliance" }
      - { value: "trade_partner", label: "Trade Partner" }
      - { value: "political_ally", label: "Political Ally" }
  enemies:
    widget: entity-selector
    reference_type: faction
    max_selections: 10
    relationship_types:
      - { value: "open_warfare", label: "Open Warfare" }
      - { value: "cold_war", label: "Cold War" }
      - { value: "rival", label: "Rival" }
  neutral:
    widget: entity-selector
    reference_type: faction
    max_selections: 10

status: "active"  # active, disbanded, underground, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
faction_type: "military"  # military, corporate, religious, criminal, civilian
founding_date: "2024-01-15"
motto: "Strength through unity"

# LEADERSHIP & HIERARCHY
leadership:
  - role: "supreme_leader"
    character_id: "character_id"
    title: "General"
  - role: "second_command"
    character_id: "character_id"
    title: "Colonel"
  - role: "advisor"
    character_id: "character_id"
    title: "Chief Strategist"
hierarchy_type: "military"  # military, democratic, oligarchy, dictatorship
chain_of_command:
  - "Supreme Leader"
  - "Council of Commanders"
  - "Regional Officers"
  - "Squad Leaders"
  - "Rank and File"

# IDEOLOGY & BELIEFS
ideology: "authoritarian survival"
core_beliefs:
  - "Only the strong survive"
  - "Order above freedom"
  - "Sacrifice for the greater good"
goals:
  - "Establish total control"
  - "Eliminate zombie threat"
  - "Rebuild civilization"
values:
  - "discipline"
  - "loyalty"
  - "strength"
taboos:
  - "showing weakness"
  - "questioning orders"
  - "fraternizing with enemies"
defining_moment_summary: "[Brief one-line summary of the pivotal event that shaped the faction's identity and purpose]"

# TERRITORY & INFLUENCE
controlled_territories:
  - "downtown_district"
  - "industrial_zone"
  - "military_base"
contested_territories:
  - "suburbs"
  - "shopping_district"
influence_level: "major"  # minor, moderate, major, dominant
expansion_strategy: "aggressive military conquest"

# MEMBERSHIP
member_count: 2500
recruitment_method: "conscription and volunteers"
membership_requirements:
  - "pass physical test"
  - "swear loyalty oath"
  - "contribute resources"
member_demographics:
  military: "40%"
  civilian: "35%"
  technical: "15%"
  other: "10%"
ranks:
  - rank: "recruit"
    count: 1000
  - rank: "soldier"
    count: 800
  - rank: "officer"
    count: 200

# RESOURCES & CAPABILITIES
resource_level: "well-supplied"  # scarce, adequate, well-supplied, abundant
primary_resources:
  - "weapons"
  - "ammunition"
  - "medical supplies"
  - "food"
special_capabilities:
  - "military training"
  - "fortified bases"
  - "vehicle fleet"
  - "communications network"
weaknesses:
  - "low morale"
  - "supply line vulnerabilities"
  - "internal power struggles"

# MILITARY STRENGTH
military_force: 1500
equipment_quality: "good"  # poor, adequate, good, excellent
combat_doctrine: "defensive strongholds with offensive raids"
special_units:
  - unit: "Elite Guard"
    size: 50
    specialty: "close protection"
  - unit: "Scavenger Teams"
    size: 200
    specialty: "resource acquisition"
vehicles:
  - type: "armored trucks"
    count: 15
  - type: "motorcycles"
    count: 30

# ECONOMY & TRADE
economic_system: "controlled distribution"
currency: "ration cards"
trade_partners:
  - faction: "merchant_guild"
    relationship: "regular trade"
  - faction: "farmers_collective"
    relationship: "food for protection"
black_market_stance: "officially prohibited, unofficially tolerated"
taxation: "mandatory contribution of resources"

# RELATIONS WITH OTHER FACTIONS
allies:
  - faction_id: "police_remnants"
    relationship: "military alliance"
    trust_level: 7  # 1-10 scale
enemies:
  - faction_id: "raiders"
    relationship: "open warfare"
    hostility_level: 10  # 1-10 scale
neutral:
  - faction_id: "merchant_guild"
    relationship: "trade only"
    trust_level: 5

# FACTION INTERDEPENDENCE
faction_interdependence:
  provides:
    - "List of essential goods, skills, or infrastructure this faction supplies."
  depends_on:
    - "List of factions or systems they rely on."
  exploits:
    - "How they manipulate, sabotage, or profit from others."
  summary: |
    [Explain how this faction fits into the city’s fragile ecosystem — what happens to the balance if they fall.]


# CULTURE & IDENTITY
symbols:
  emblem: "media/faction_emblem.png"
  flag: "media/faction_flag.png"
  colors: ["red", "black", "gold"]
uniforms:
  standard: "military fatigues with faction patch"
  elite: "black tactical gear"
  civilian: "armband with faction colors"
traditions:
  - "daily loyalty pledge"
  - "weekly combat drills"
  - "memorial services for fallen"
propaganda:
  - "Join us or perish alone"
  - "Order brings salvation"
  - "Strength in unity, death in division"

# FACTION VOICE & CULTURE
common_phrases:
  - "[Typical greeting or salute used by members]"
  - "[Common response to orders or situations]"
  - "[Phrase used when facing danger or conflict]"
  - "[Saying used to motivate or inspire members]"
  - "[Phrase used to identify fellow members]"

# OPERATIONS & ACTIVITIES
primary_operations:
  - "territory patrol"
  - "resource scavenging"
  - "refugee processing"
  - "zombie elimination"
secret_operations:
  - "spy network"
  - "assassination program"
  - "bioweapon research"
daily_routine:
  morning: "drill and training"
  afternoon: "patrol and scavenging"
  evening: "fortification and planning"

# STORY INTEGRATION
narrative_role: "major_antagonist"  # protagonist, antagonist, neutral, variable
story_significance: "primary opposition force"
key_events:
  - "formation after outbreak"
  - "battle for downtown"
  - "betrayal of allies"
faction_arc: "rise to power through brutality"
player_interaction: "hostile unless allied"

# LOCATIONS & FACILITIES
headquarters: "location_id"  # Main base of operations
outposts:
  - "checkpoint_alpha"
  - "supply_depot_bravo"
  - "observation_post_charlie"
training_facilities:
  - "boot_camp"
  - "shooting_range"
supply_depots:
  - "warehouse_district"
  - "underground_bunker"

# CONTENT FIELDS
description: null  # Will be in markdown below
history: null  # Will be in markdown below
ideology_detail: null  # Will be in markdown below
operations_detail: null  # Will be in markdown below
---

# [Faction Name]

## Description

[Comprehensive overview of the faction, their role in the world, and what makes them unique]

## History

[How the faction formed, major events in their development, key victories and defeats]

## Ideology and Beliefs

[Detailed explanation of what the faction believes, why they believe it, and how it shapes their actions]

## Defining Moment

[1-2 paragraphs describing the pivotal event that shaped this faction's identity and purpose. This could be their founding incident, a major victory or defeat, a betrayal, a discovery, or any transformative moment. Explain what happened, when it occurred, and most importantly - how it fundamentally changed the faction and defines who they are today. This moment should explain their core ideology, deepest motivations, and why they operate the way they do.]

## Leadership Structure

[Detailed breakdown of the faction's leadership, key figures, and how decisions are made]

## Territory and Control

[Description of territories under faction control, how they maintain control, expansion plans]

## Military Capabilities

[Detailed assessment of military strength, tactics, equipment, and combat effectiveness]

## Economic System

[How the faction manages resources, trade relationships, internal economy]

## Daily Life

[What life is like for faction members, daily routines, social structure]

## Recruitment and Training

[How new members join, training programs, advancement opportunities]

## Relations with Other Factions

[Detailed diplomatic status, alliances, conflicts, trade relationships]

## Faction Interdependence

[Describe how this faction’s economy and survival depend on others, how they manipulate or resist cooperation, and what collapses if they disappear.]


## Secret Operations

[Classified activities, spy networks, special projects]

## Propaganda and Public Image

[How the faction presents itself, propaganda campaigns, public perception]

## Common Phrases & Faction Voice - Aka Barks

[1-2 paragraphs describing how faction members speak and communicate. Detail the unique linguistic patterns, catchphrases, and communication style that identifies them:]

**Greetings & Salutes**: [How members greet each other, formal and informal salutations, hand signals or gestures]

**Commands & Responses**: [Common orders given, standard responses, military or organizational jargon]

**Cultural Expressions**: [Sayings that reflect their ideology, phrases used to motivate or intimidate, regional or unique slang]

**Identification Codes**: [Phrases or passwords used to identify fellow members, challenge-response protocols]

### Example Phrases

> "[Typical greeting used by members]"

> "[Response to danger or conflict situation]"

> "[Motivational phrase or battle cry]"

> "[Common saying reflecting their ideology]"

> "[Phrase used to identify fellow members]"

## Player Interactions

[How players can interact with this faction, reputation system, quest opportunities]

## Weaknesses and Vulnerabilities

[Internal conflicts, resource shortages, strategic weaknesses that players might exploit]

## Future Plans

[The faction's long-term goals and strategies]

## Developer Notes

[Implementation notes, AI behavior patterns, faction mechanics]

## Key NPCs

[Important characters within the faction and their roles]