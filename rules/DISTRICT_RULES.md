---
system_prompt: "Generate a district for this project. Record weather, who controls it, and the condition of its services in line with the history this project already has. Do not assume a disaster, a contamination, or a collapse the project has not recorded."
global: false
priority: medium
entity_type: district
template_reference: DISTRICT_TEMPLATE.md
rules:
- id: dist_001
  category: environment
  priority: medium
  rule: Weather type should be included for each district as this affects environmental
    and game modes as well as art and audio
  validation_type: info
  applies_to:
  - district
- id: dist_002
  category: faction_control
  priority: high
  rule: Each district must have clear faction control or contested status that affects
    NPC behavior and player interactions
  validation_type: warning
  applies_to:
  - district
- id: dist_003
  category: contamination
  priority: high
  rule: "If this project records an environmental condition, the district must show it. Do not add contamination the project has not recorded."
  validation_type: warning
  applies_to:
  - district
- id: dist_004
  category: population
  priority: medium
  rule: "Population and demographics must follow from events this project has recorded. Do not assume a disaster the project has not recorded."
  validation_type: info
  applies_to:
  - district
- id: dist_005
  category: infrastructure
  priority: medium
  rule: "Infrastructure condition must match the history this project records for the district. Do not assume services have collapsed."
  validation_type: info
  applies_to:
  - district
---

# District guidance

These rules check structure and consistency. They do not name a setting.

Record a weather type. If factions exist here, say who controls the district or that it is contested, and name a faction that exists. Population, infrastructure, and any environmental condition must follow from events the project has already recorded. Do not assume contamination, an outbreak, or a collapse of services.

Name only places and groups that exist in this project.
