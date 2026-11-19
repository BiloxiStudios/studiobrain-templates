---
rules:
- id: fac_001
  category: alignment
  priority: medium
  rule: Faction threat depends on player's current faction alignment; joining one
    causes hostility from opposing sides.
  validation_type: warning
  applies_to:
  - faction
- id: fac_002
  category: voice
  priority: high
  rule: Each faction maintains distinct linguistic tone and cultural idioms based
    on geographic and social origin.
  validation_type: required
  applies_to:
  - dialogue
- id: fac_003
  category: lore
  priority: high
  rule: Factions must align with regional personality archetypes and maintain consistent
    social hierarchy and economic base.
  validation_type: consistency_check
  applies_to:
  - faction
- id: fac_004
  category: player_interaction
  priority: medium
  rule: Faction reputation modifies dialogue style, shop prices, and NPC tone. Opposing
    factions may refuse service or attack.
  validation_type: simulation
  applies_to:
  - gameplay
- id: fac_005
  category: environmental
  priority: high
  rule: "A faction's territory, when described, must use the colors, materials, and tone recorded on that faction. Do not assign a palette the faction does not have."
  validation_type: art_direction
  applies_to:
  - level_design
  - lighting
  - branding
  - environmental_storytelling
- id: fac_006
  category: territory
  priority: high
  rule: "Territory a faction controls must name districts that exist in this project. Do not assign a faction to a place the project has not recorded."
  validation_type: world_structure
  applies_to:
  - world_map
  - level_design
  - narrative
- id: fac_007
  category: economy
  priority: medium
  rule: "Industries and brands a faction controls must be entities this project has recorded. Do not invent an economic sector for them."
  validation_type: economy_integration
  applies_to:
  - trade_system
  - brand_influence
  - quest_rewards
- id: fac_008
  category: interdependence
  priority: high
  rule: "Dependencies between factions must be ones this project has recorded. Do not invent a trade the project has not recorded."
  validation_type: narrative_logic
  applies_to:
  - faction
  - economy
  - story_integration

- id: fac_009
  category: timeline_validation
  priority: critical
  rule: "formation_date, key_events, and history milestones must be in chronological order and inside the years this project uses."
  validation_type: error
  applies_to:
  - faction
  required_tools: ["check_temporal_conflicts", "calculate_duration"]

- id: fac_010
  category: entity_validation
  priority: critical
  rule: Before referencing locations (headquarters, controlled_territories), characters
    (leaders, key_members, founders), brands (allied_brands, faction_businesses),
    or districts, use validation tools to verify they exist. Use check_location_exists,
    check_character_exists, check_brand_exists, and validate_all_references. Never
    reference non-existent entities
  validation_type: error
  applies_to:
  - faction
  required_tools: ["check_location_exists", "check_character_exists", "check_brand_exists",
    "validate_all_references"]

system_prompt: "Generate a faction for this project. Follow the faction template. Give it a voice, a territory made of districts that exist here, and dependencies the project has recorded. Do not copy a faction from another setting, and do not invent a district, a trade, or a palette the project does not have."
---

# Faction guidance

These rules check structure and consistency. They do not name a setting.

A faction needs a distinct voice. Reputation may change dialogue, prices, and whether others will deal with the player. Territory must be districts that exist in this project. Colors and materials must be the ones recorded on the faction. Industries, brands, and dependencies must be ones the project has recorded. Dates must be in order and inside the project's years.

Do not assign a faction to a place, a trade, or a palette the project does not have. Do not copy a cast of factions from another world.

Fill every field the faction template asks for. Use a blank when the project has not decided a value.
