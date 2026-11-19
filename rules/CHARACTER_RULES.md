---
system_prompt: "Generate a character for this project. Follow the character template. Use only places, factions, brands, and people that exist in the project. Match the project's recorded era, technology, and tone. Do not invent a setting."
global: false
priority: high
entity_type: character
template_reference: CHARACTER_TEMPLATE.md

rules:
- id: char_001
  category: identity
  priority: critical
  rule: Every character MUST have a primary_location or they will be flagged as homeless
  validation_type: warning
  applies_to: [character]

- id: char_002
  category: naming
  priority: critical
  rule: Character IDs must use lowercase_with_underscores format
  validation_type: warning
  applies_to: [character]

- id: char_003
  category: relationships
  priority: high
  rule: Friends always use nicknames when available, never full names in dialogue
  validation_type: warning
  applies_to: [character]

- id: char_004
  category: timeline
  priority: critical
  rule: "Technology named on a character must match the limits this project has recorded. forbidden_tech and allowed_tech are empty in the starter so the project can fill them. Do not invent a ban the project has not recorded."
  validation_type: warning
  applies_to: [character]
  forbidden_tech: []
  allowed_tech: []
- id: char_005
  category: tone
  priority: high
  rule: "A character's tone must match the tone this project has recorded."
  validation_type: warning
  applies_to: [character]

- id: char_006
  category: infection
  priority: high
  rule: "If this project records a condition that changes speech or behavior, show that condition consistently. Do not add a condition the project has not recorded."
  validation_type: warning
  applies_to: [character]

- id: char_007
  category: faction
  priority: medium
  rule: Characters should reflect their faction's culture and speech patterns
  validation_type: warning
  applies_to: [character]

- id: char_008
  category: skills
  priority: medium
  rule: "A character's skills must fit the role this project gives them. Do not assume which skills the world values."
  validation_type: info
  applies_to: [character]

- id: char_009
  category: corporate
  priority: medium
  rule: "What a character knows must follow from the position and events this project has already recorded."
  validation_type: info
  applies_to: [character]

- id: char_010
  category: environmental
  priority: medium
  rule: "A character's physical condition must follow from the environment this project has recorded. Do not add contamination the project has not recorded."
  validation_type: info
  applies_to: [character]

- id: char_011
  category: timeline_validation
  priority: critical
  rule: "birth_year must agree with age against the present year this project records. key_dates must be in order. death_year, when set, must fall after birth. Temporal data must be internally consistent."
  validation_type: warning
  applies_to: [character]
  required_tools: ["validate_character_age", "check_temporal_conflicts", "calculate_duration"]

- id: char_012
  category: entity_validation
  priority: critical
  rule: Before referencing locations (primary_location, home_location), factions, brands
    (associated_brands), or other characters (relationships, allies, enemies), use
    validation tools to verify they exist. Use check_location_exists for locations,
    check_brand_exists for brands, check_character_exists for character relationships.
    Never reference non-existent entities
  validation_type: warning
  applies_to: [character]
  required_tools: ["check_location_exists", "check_brand_exists", "check_character_exists",
    "validate_all_references"]

- id: char_013
  category: physical
  priority: high
  rule: "skin_tone, eye_color, and hair_color must be set, and each value must be one this project's style guide allows. Do not invent a palette the project has not recorded."
  validation_type: warning
  applies_to: [character]
---

# Character guidance

These rules check structure and consistency. They do not name a setting.

A character needs a primary location that exists in this project, and an id in lowercase_with_underscores. Dates must agree with the project's present year. References to other people, places, factions, and brands must be entities that already exist.

Technology, tone, skills, and what the character knows come from the project. The starter does not forbid devices and does not require a palette. Fill forbidden_tech only when the project has a technology limit. Use the project's style guide for skin, eye, and hair color.

Write the character as someone who already lives in this project. Leave a field blank rather than borrowing a person, a place, or a disaster from another world.
