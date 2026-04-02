---
# BIOME GENERATION METADATA
system_prompt: "Generate a biome for a creative project following the biome template exactly. Create ecologically consistent environments with believable weather patterns, terrain, flora, fauna, and hazards. Ensure sensory details are vivid and interconnected. Biomes must feel like living ecosystems, not lists of features. Respect the climate logic: what grows, lives, and happens in this biome must make physical and biological sense."
global: false
priority: "high"
entity_type: "biome"
template_reference: "BIOME_TEMPLATE.md"

# BIOME VALIDATION RULES
rules:
- id: bio_001
  category: naming
  priority: critical
  rule: Biome IDs must use lowercase_with_underscores format
  validation_type: error
  applies_to:
  - biome

- id: bio_002
  category: naming
  priority: critical
  rule: Biome files must use BIO_ prefix (e.g., BIO_frozen_tundra.md)
  validation_type: error
  applies_to:
  - biome

- id: bio_003
  category: ecology
  priority: critical
  rule: Flora must be climatically appropriate for the biome type and temperature range.
    Cacti do not grow in tundra. Tropical ferns do not thrive in deserts. Coniferous
    forests do not appear in volcanic wastelands. If a biome has unusual flora, provide
    an in-world explanation (magical influence, artificial cultivation, mutation).
  validation_type: error
  applies_to:
  - biome

- id: bio_004
  category: ecology
  priority: critical
  rule: Fauna must be ecologically consistent with the biome's flora, climate, and
    food chain. Predator populations must be smaller than prey populations. Aquatic
    species require water features. Large herbivores require sufficient vegetation.
    Desert fauna must have adaptations for heat and water scarcity.
  validation_type: error
  applies_to:
  - biome

- id: bio_005
  category: weather
  priority: high
  rule: Weather patterns must be consistent with the stated climate and geographic
    position. Tropical biomes have monsoons, not blizzards. Tundra has permafrost,
    not droughts. Precipitation, humidity, and temperature range must align. If a biome
    has anomalous weather, provide an in-world explanation.
  validation_type: error
  applies_to:
  - biome

- id: bio_006
  category: transitions
  priority: high
  rule: Connected biomes must have plausible transitions. A forest does not border
    a desert without an intermediate zone (savanna, scrubland, steppe). A tundra does
    not border a tropical jungle. Mountain biomes can border most types due to elevation
    gradients. Ocean biomes connect to coastal variants of any type. Valid transition
    chains include forest-savanna-desert, tundra-taiga-temperate forest, mountain-foothills-plains,
    swamp-wetland-river-forest.
  validation_type: warning
  applies_to:
  - biome

- id: bio_007
  category: seasons
  priority: high
  rule: Seasonal changes must be internally consistent. If winter brings heavy snow,
    spring must account for snowmelt and flooding. If summer is a dry season, autumn
    should show the return of moisture. Flora and fauna behavior must shift with seasons
    (migration, dormancy, blooming, breeding). Equatorial biomes may have wet/dry
    cycles instead of four seasons.
  validation_type: warning
  applies_to:
  - biome

- id: bio_008
  category: resources
  priority: medium
  rule: Natural resources must be appropriate to the biome type. Timber requires forests.
    Minerals require rocky or mountainous terrain. Freshwater requires rainfall or
    water features. Fertile soil requires appropriate climate and vegetation cycles.
    Resources drive economic and narrative value of the biome.
  validation_type: warning
  applies_to:
  - biome

- id: bio_009
  category: hazards
  priority: high
  rule: Every biome MUST have at least one environmental hazard. Hazards must be
    consistent with the biome type and climate. Avalanches require mountains or steep
    terrain. Wildfires require dry vegetation. Flooding requires water features and
    rainfall. Toxic gas requires volcanic or swamp terrain. Hazard severity should
    correlate with threat_level.
  validation_type: warning
  applies_to:
  - biome

- id: bio_010
  category: atmosphere
  priority: medium
  rule: Sensory details (ambient_sounds, ambient_smells, dominant_colors, visibility,
    light_quality) must be consistent with the biome type and current season. A dense
    forest has dappled light and limited visibility. A desert has harsh light and high
    visibility. A swamp has dim light and poor visibility. Sounds must match the fauna
    and weather described.
  validation_type: warning
  applies_to:
  - biome

- id: bio_011
  category: spatial
  priority: medium
  rule: Biomes should reference a parent_location when they exist within a larger
    geographic context. Sub_regions should be distinct areas within the biome, each
    with their own character. Area_size should be proportional to the biome type and
    the scale of the project.
  validation_type: suggestion
  applies_to:
  - biome

- id: bio_012
  category: completeness
  priority: medium
  rule: A biome should have at least 3 flora entries, 3 fauna entries, and 1 natural
    resource to be considered minimally complete. Incomplete biomes should remain in
    draft status until populated.
  validation_type: suggestion
  applies_to:
  - biome

- id: bio_013
  category: entity_validation
  priority: critical
  rule: Before referencing locations (parent_location) or other biomes (connected_biomes),
    use validation tools to verify they exist. Never reference non-existent entities.
    Use check_location_exists for parent locations and check_biome_exists for connected
    biomes.
  validation_type: error
  applies_to:
  - biome
  required_tools: ["check_location_exists", "check_biome_exists", "validate_all_references"]

- id: bio_014
  category: universal
  priority: high
  rule: Biomes are domain-agnostic. Do not assume a fantasy or game setting unless
    the project specifies one. A biome template works equally for a game world, a
    nature documentary, a sci-fi planet, a cooking project (regional ingredients),
    or a gardening project (growing zones). Keep descriptions adaptable.
  validation_type: info
  applies_to:
  - biome
---

# Biome Creation Rules

## Ecological Consistency

The single most important rule for biomes: **everything must make ecological sense together**. A biome is an interconnected system, not a grab bag of features. The climate drives the vegetation. The vegetation supports the herbivores. The herbivores feed the predators. The terrain shapes the weather. The weather erodes the terrain. Every element connects.

When generating a biome, start with the climate and work outward:

1. **Climate** determines what can grow (temperature range, precipitation, humidity)
2. **Flora** follows from climate (what survives and thrives in these conditions)
3. **Fauna** follows from flora (what the food chain can support)
4. **Resources** follow from all three (what humans or inhabitants can extract)
5. **Hazards** emerge from the system (what the environment does when it's hostile)

If any element contradicts this chain, the biome needs revision or an in-world explanation.

## Weather Pattern Logic

Weather is not random decoration. It follows from geography and climate:

- **Elevation** affects temperature (roughly -6.5C per 1000m altitude)
- **Proximity to water** increases humidity and moderates temperature
- **Wind patterns** carry moisture and affect precipitation
- **Latitude** (or equivalent) determines seasonal variation
- **Terrain** creates rain shadows, funnels wind, and traps cold air

A mountain biome on the windward side gets heavy rain. The leeward side is dry. A coastal biome has milder winters and cooler summers than an inland one. These patterns should be reflected in the weather_patterns and seasonal_changes fields.

## Connected Biome Transitions

Biomes do not change abruptly in nature. Transitions follow gradients:

| From | Valid Neighbors | Invalid Without Transition |
|------|----------------|---------------------------|
| Forest | Savanna, Plains, Mountain, Swamp, Forest (different type) | Desert, Tundra, Volcanic |
| Desert | Savanna, Scrubland, Mountain, Plains (arid) | Forest, Tundra, Swamp, Ocean |
| Tundra | Taiga, Mountain, Ocean (arctic) | Desert, Tropical Forest, Swamp |
| Ocean | Coast (any type), Swamp (coastal), Mountain (cliff) | Desert (interior), Forest (interior) |
| Mountain | Any (via elevation gradient) | Ocean (without coast) |
| Swamp | Forest, Plains, River delta, Coast | Desert, Tundra, Mountain (high) |
| Plains | Forest, Desert, Savanna, Mountain (foothills) | Ocean, Tundra (without gradient) |
| Volcanic | Mountain, Desert, Ocean (island), Plains (ash) | Tundra, Swamp, Forest (dense) |
| Urban | Any (human settlement overrides natural biome) | N/A |

When a project requires an implausible transition, use the `connected_biomes` relationship type `transitions_to` and describe the transition zone in the biome's Background section.

## Seasonal Cycle Consistency

Seasons form a closed loop. What happens in one season must set up the next:

- **Spring snowmelt** follows **winter snow accumulation**
- **Summer drought** leads to **autumn wildfire risk**
- **Autumn leaf fall** creates **winter ground cover and soil nutrients**
- **Monsoon rains** produce **post-monsoon flooding and lush growth**

Fauna behavior must track seasons: migration out in autumn means migration back in spring. Hibernation in winter means increased activity in spring. Breeding season timing must allow offspring to mature before the harshest season.

## Resource Availability

Resources are what make biomes strategically important in a narrative:

| Biome Type | Common Resources | Rare Resources |
|------------|-----------------|----------------|
| Forest | Timber, game, medicinal plants, freshwater | Rare hardwoods, truffles, amber |
| Desert | Minerals, gems, solar exposure, hardy spices | Oasis water, date palms, salt |
| Tundra | Permafrost cores, hardy lichens, Arctic game | Ice crystals, rare minerals, ivory |
| Ocean | Fish, shellfish, salt, pearls, coral | Deep-sea minerals, ambergris, bioluminescent algae |
| Mountain | Stone, minerals, crystal, mountain herbs | Rare ores, high-altitude plants, glacier water |
| Swamp | Peat, clay, reeds, freshwater fish | Bog iron, rare orchids, medicinal leeches |
| Plains | Fertile soil, grazing land, wind energy | Prairie herbs, flint, ancient bones |
| Volcanic | Obsidian, pumice, geothermal energy, ash soil | Rare metals, sulfur, heat-resistant crystals |
| Urban | Salvage, infrastructure, stored goods | Technology, archives, hidden caches |

## Checklist

Before finalizing any biome:
- [ ] Does the flora survive in the stated climate and temperature range?
- [ ] Does the fauna have a viable food chain within this ecosystem?
- [ ] Are weather patterns consistent with geography and climate?
- [ ] Do connected biomes have plausible transition zones?
- [ ] Do seasonal changes form a consistent cycle?
- [ ] Are hazards appropriate to the biome type?
- [ ] Does the sensory profile match the physical description?
- [ ] Are natural resources consistent with terrain and vegetation?
- [ ] Does the biome have at least one clear narrative purpose?
- [ ] Is the biome_type field set correctly?
- [ ] Does the parent_location reference an existing entity?
- [ ] Do all connected_biomes reference existing entities?
