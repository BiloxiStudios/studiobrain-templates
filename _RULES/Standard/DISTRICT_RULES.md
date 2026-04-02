---
system_prompt: Generate districts for the City of Brains universe that reflect the
  environmental and social impact of corporate negligence and zombie outbreak. Districts
  should show clear faction control, environmental contamination effects, and the
  breakdown of normal urban life. Each district should have distinct atmosphere, weather
  patterns, and survival challenges that affect gameplay and storytelling.
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
  rule: Districts should show visible signs of environmental contamination from corporate
    negligence
  validation_type: warning
  applies_to:
  - district
- id: dist_004
  category: population
  priority: medium
  rule: Population density and demographics should reflect the impact of the zombie
    outbreak
  validation_type: info
  applies_to:
  - district
- id: dist_005
  category: infrastructure
  priority: medium
  rule: Infrastructure condition should reflect the breakdown of normal urban services
  validation_type: info
  applies_to:
  - district
---


# District Creation in the City of Brains Universe

## The Urban Wasteland

Districts in City of Brains aren't just geographic areas - they're living examples of how corporate greed and environmental neglect have transformed urban life. Each district tells a story of what happens when normal city services break down and factions fight for control of the remaining resources.

### Environmental Storytelling Through Weather

Weather isn't just atmospheric - it's a character in the story. The chemical contamination has created unique weather patterns that affect everything from visibility to gameplay mechanics. Acid rain that damages equipment, toxic fog that limits movement, or radioactive dust storms that require protective gear - each district's weather tells players about the environmental damage and survival challenges they'll face.

### Faction Control and Territory

Every district has a clear power structure that affects how NPCs behave and what resources are available. Some districts are firmly controlled by one faction, others are contested territories where different groups fight for dominance. This isn't just background information - it determines what quests are available, what items can be found, and how dangerous the area is for players.

### The Contamination Legacy

Corporate negligence has left visible scars on every district. Some areas show obvious signs of chemical spills or industrial accidents. Others have more subtle contamination - unusual plant growth, strange animal behavior, or residents with mysterious health problems. These environmental details aren't just set dressing - they're clues that players can discover and use to understand the larger conspiracy.

### Population and Demographics

The zombie outbreak has dramatically changed who lives where and why. Some districts have become refugee camps for survivors. Others are controlled by factions who've driven out or converted the original residents. The population density and demographics of each district should reflect these changes and tell the story of how society has adapted (or failed to adapt) to the new reality.

### Infrastructure Breakdown

Normal city services have collapsed, but not uniformly. Some districts still have partial power or water service. Others have been completely abandoned and are falling apart. The condition of infrastructure affects what resources are available, what dangers exist, and what opportunities players might find for shelter or supplies.

## Template Integration

### District Template Alignment
When using the DISTRICT_TEMPLATE.md:
- The `district_id` field must match your folder name exactly
- The `governing_faction` should reference an existing faction
- The `district_council` should reference existing characters
- The `landmark_locations` should reference existing locations

### Cross-Reference Validation
Before finalizing any district:
- [ ] Does the `district_id` use lowercase_with_underscores format?
- [ ] Does the `governing_faction` exist in your Factions folder?
- [ ] Do any referenced character IDs exist in your Characters folder?
- [ ] Do any referenced location IDs exist in your Locations folder?
- [ ] Is the weather type specified and does it affect gameplay?
- [ ] Are there clear signs of environmental contamination?
- [ ] Does the population density reflect the outbreak's impact?
- [ ] Is the infrastructure condition consistent with the story?
- [ ] Does the faction control status affect available content?

## Implementation Examples

### For AI Generation Systems
When creating a district like "Chemical Plant District":
1. Set `district_id: "chemical_plant_district"` (matches folder name)
2. Assign `governing_faction: "corporate_remnants"` (must exist in Factions)
3. Reference `landmark_locations: ["chemical_plant_main", "worker_housing"]` (must exist in Locations)
4. Include weather effects like "acid_rain" and "toxic_fog"
5. Show contamination through environmental details

### For Human Content Creators
- Review this file before creating any district
- Use the validation checklist above
- Focus on environmental storytelling through details
- Ensure all cross-references point to existing entities
- Remember: districts are characters in the story, not just backdrops
