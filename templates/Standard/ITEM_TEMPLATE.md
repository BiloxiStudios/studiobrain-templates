---
id: "unique_lowercase_id"  # Must match folder name (e.g., neural_sword_mk2)
name: "Item Display Name"

# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
ui_icon: "Package"
ui_color: "#10b981"
editable: true
marketplace_eligible: true
entity_type: "item"
folder_name: "Items"
file_prefix: "ITEM_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules:
  - ITEM_RULES.md
  - ITEM_WORKFLOW.md
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  brand_id:
    widget: entity-selector
    reference_type: brand
    max_selections: 1
  spawn_locations:
    widget: entity-selector
    reference_type: location
    max_selections: 20
  vendors:
    widget: entity-selector
    reference_type: character
    max_selections: 20

status: "active"  # active, deprecated, prototype, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# WORKFLOW CONFIGURATION
workflow:
  definition: "ITEM_WORKFLOW.md"
  default_stage: "concept"
  allow_multiple_active: false
  notifications:
    on_enter:
      - type: "print"
        message: "Item entered stage {{stage_name}}"
    on_exit:
      - type: "archive"
        target: "stage_history/items/{{item_id}}/{{old_stage}}"
    on_complete:
      - type: "print"
        message: "Item completed {{stage_name}}"
  # Note: Production status and workflow are separate systems
  # - production_status: tracks progress across domains (game, TV, etc.)
  # - workflow: tracks entity lifecycle (concept -> published -> active -> archived)

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)

item_type: "weapon"  # weapon, consumable, key_item, material, collectible, cosmetic, currency
description: "A detailed description of the item and its purpose"
tagline: "Short catchy description with emojis 🗡️"

# CATEGORIZATION
category: "melee"  # Subcategory based on item type
rarity: "common"  # common, uncommon, rare, epic, legendary, unique
stack_size: 1
weight: "2.5kg"  # Optional weight for realism
value: 100  # Base monetary value

# VERSE/GAME INTEGRATION
game_id: null  # Maps to Verse resource ID (1-999: Currency, 1000-1999: Weapons, etc.)
base_price: 100  # Game currency value  
texture_path: "textures/weapons/sword_neural.png"  # Reference to game asset
max_stack_size: 1  # Maximum stack size in inventory
storage_type: "inventory"  # inventory, bank, pet, closet

# STORAGE CONFIGURATION
storage_settings:
  requires_physical_removal: true  # Must be physically removed from storage
  can_be_stored: true  # Can be stored in containers
  storage_restrictions: []  # Special storage requirements

# VERSE DEVICE CONFIGURATION (for game items)
item_granter_config:
  auto_grant: false
  grant_on_start: false
  max_count: 1
is_removable_config:
  removable: true
  destroy_on_remove: false
power_up_device: null  # Power-up effects configuration (dict object when used)
  # device_type: "consumable_boost"
  # auto_activate: true
collectible_device: null  # Collectible achievement data (dict object when used)

# BRAND ASSOCIATION
brand_id: null  # Associated brand (e.g., flameys_kitchen)
product_line: null  # Product line within brand

# WORLD INTEGRATION
spawn_locations: []  # Location IDs where this item can be found
  # - "neon_district"
  # - "garys_gas_station_chain"
vendors: []  # Character IDs that sell this item
  # - "merchant_joe"
  # - "club_promoter_neuro"
drop_sources: []  # Source IDs that drop this item
  # - "cyber_grunt"
  # - "choke_vend_unit"

# ITEM MECHANICS
crafting_recipe:
  craftable: false
  required_items: []
  # - item_id: "metal_scrap"
  #   quantity: 3
  # - item_id: "neural_chip"
  #   quantity: 1
  crafting_station: null  # "workbench", "forge", etc.

# USAGE PROPERTIES
usable: false
consumable: false
effects: []  # Status effects when used
  # - effect_type: "heal"
  #   magnitude: 50
  #   duration: null
duration: null  # How long consumable effects last
cooldown: null  # Cooldown between uses

# COMBAT STATS (if applicable)
damage: 0  # Base damage for weapons
defense: 0  # Defense value for armor
special_properties: []  # Special abilities or effects (dict objects)
  # - property_type: "piercing"
  #   description: "Ignores armor protection"
  # - property_type: "lightning_damage"
  #   description: "Deals electrical damage over time"
ammo_type: null  # For weapons that use ammo

# QUEST INTEGRATION
quest_item: false
required_quests: []  # Quests needed to unlock/use this item
unlocks: []  # What this item unlocks
  # - quest_id: "find_the_sword"
  # - location_id: "secret_chamber"
lore_significance: null  # Importance to game lore

# DISPLAY DATA
thumbnail: "neural_sword_icon.png"  # Icon for UI display
model_3d: null  # 3D model path if applicable
ui_category: "weapons"  # UI categorization
ui_sort_order: 100  # Sort order in inventory

# RESTRICTIONS
level_requirement: null  # Minimum level to use
class_restrictions: []  # Classes that can use item
faction_restrictions: []  # Factions that can use item
bound: false  # Binds to character on pickup
tradeable: true  # Can be traded between players

# NFT DATA (if tokenized)
nft_metadata:
  collection: null
  token_id: null
  minted: false
  blockchain: null

# AUDIO/VISUAL
sound_effects:
  pickup: null
  use: null
  drop: null
visual_effects:
  pickup: null
  equipped: null
  active: null

# STATUS EFFECTS
buffs: []  # Positive effects
debuffs: []  # Negative effects
auras: []  # Area effects

# TAGS & SEARCH
tags: []
  # - "weapon"
  # - "melee"
  # - "sword"
search_keywords: []
  # - "blade"
  # - "neural"
  # - "cyber"

# VENDOR PRICING (override defaults)
vendor_overrides: []
  # - vendor_id: "merchant_joe"
  #   price_multiplier: 0.8
  #   always_available: true

# PROCEDURAL GENERATION
procedural_stats:
  can_generate: false
  stat_ranges: {}
  rarity_weights: {}

# ANALYTICS
analytics_id: null
track_usage: false
track_trades: false

# METADATA
notes: ""
designer_notes: ""
balance_notes: ""
---

# [Item Name] - Complete Documentation

## Overview
[Provide a comprehensive overview of the item, its purpose, and role in the game world]

## Physical Description
[Detailed description of the item's appearance, materials, and construction]

## Lore & History
[Background story, origin, and significance in the game world]

## Mechanics & Usage
[How the item works in gameplay, special abilities, and usage instructions]

## Acquisition Methods
[Where and how players can obtain this item]

## Crafting Information
[If craftable, detailed recipe and requirements]

## Market Analysis
[Economic impact, trading value, and market dynamics]

## Strategic Value
[Tips for using the item effectively]

## Related Items
[Links to similar or complementary items]

## Version History
[Track changes and updates to the item]

## AI Generation Notes
This template provides the structure for generating item content. When creating items:
1. Consider the item's role in the game economy
2. Balance stats with rarity and acquisition difficulty
3. Create interesting lore that fits the world
4. Ensure vendor and spawn locations make narrative sense
5. Use consistent naming conventions for IDs
6. Consider the item's visual and audio feedback
7. Think about player progression and power scaling

## Template Usage
- Replace all placeholder values with appropriate content
- Remove unused sections that don't apply to your item type
- Ensure all IDs reference existing entities in the system
- Use snake_case for all ID fields
- Maintain consistency with existing items in the same category