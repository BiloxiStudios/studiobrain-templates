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
  rule: "Faction territory visuals should reflect ethos, tone, and color identity:\n\
    - **Northside Bears** \u2014 Blue tones (#00aaff, #66ccff): cables, off-grid rigs,\
    \ solar tech, flickering CRTs; industrial and utilitarian, prepared hackers. -\
    \ **Westside Krakens** \u2014 Toxic Green hues (#00ff80, #55ff99): rusted metal,\
    \ oil drums, fuel signage, mechanical clutter; chaotic survivalist energy, build\
    \ anything. - **Eastside Dragons** \u2014 Royal Purple and Gold (#8c1eff, #ffd966):\
    \ neon high-rises, mirrored surfaces, fake smiles, corporate logos, and decaying\
    \ luxury. - **Southside Flamingos** \u2014 Flamingo Pink and Sunset Orange (#ff66c4,\
    \ #ff934f): nightclub neon, mirrors, glitter trails, underground club scene, counterfeit\
    \ fashion markets.\n"
  validation_type: art_direction
  applies_to:
  - level_design
  - lighting
  - branding
  - environmental_storytelling
- id: fac_006
  category: territory
  priority: high
  rule: "Each faction generally controls one major district of the City of Brains,\
    \ while key central and industrial regions remain contested or unclaimed:\n**Controlled\
    \ Districts:** - Northside District \u2014 Controlled by the Bears (Tech & Infrastructure)\
    \ - Westside District \u2014 Controlled by the Krakens (Transport & Mechanics)\
    \ - Eastside District \u2014 Controlled by the Dragons (Corporate & Marketing)\
    \ - Southside District \u2014 Controlled by the Flamingos (Nightlife & Smuggling)\n\
    **Uncontrolled / Contested Zones:** - Central Nervous Park (Event & Outbreak Zone)\
    \ - The Underground (Abandoned transit and BOL tunnels) - Chemical Plant (Source\
    \ of Double Dip contamination) - Government Facilities (Locked-down or evacuated)\
    \ - ELJ Arena (Neutral ground where all factions compete in the \u201CBattle of\
    \ the Tusks\u201D for fame, sponsorships, and city influence)\n"
  validation_type: world_structure
  applies_to:
  - world_map
  - level_design
  - narrative
- id: fac_007
  category: economy
  priority: medium
  rule: "Factions influence in-world brands, industries, and product distribution.\
    \ Each controls specific economic sectors:\n- **Northside Bears:** Technology,\
    \ networking, and BrainOnLine infrastructure. Supply circuit boards, terminals,\
    \ and communication systems. - **Eastside Dragons:** Marketing, sponsorships,\
    \ and public relations. Control media outlets, ad campaigns, and corporate endorsements.\
    \ - **Westside Krakens:** Logistics, shipping, trucking, and mechanical invention.\
    \ Operate fuel supply chains and transportation routes. - **Southside Flamingos:**\
    \ Smuggling, counterfeit fashion, nightlife commerce, and aggressive \u201CIt\u2019\
    s a Steal\u201D brand manipulation.\nProduct lines, advertisements, and shop inventories\
    \ must reflect the faction that supports or supplies them.\n"
  validation_type: economy_integration
  applies_to:
  - trade_system
  - brand_influence
  - quest_rewards
- id: fac_008
  category: interdependence
  priority: high
  rule: "Factions are not isolated entities but components of a fragile city ecosystem.\
    \   Each faction depends on the others for survival, commerce, and control \u2014\
    \ even as they despise or compete with one another.   No group is truly allied;\
    \ relationships are transactional, exploitative, or opportunistic.\n**Dependency\
    \ Web:** - **Northside Bears** rely on Krakens for mechanical fabrication and\
    \ on Dragons for publicity and funding.  \n  They secretly depend on Flamingos\u2019\
    \ smuggling routes to move banned tech parts.\n- **Westside Krakens** supply transport,\
    \ fuel, and construction for the entire city.  \n  They depend on Bears for electronics,\
    \ Dragons for cultural relevance, and Flamingos for black-market income.\n- **Eastside\
    \ Dragons** use the Bears\u2019 technology to broadcast their messages, Krakens\u2019\
    \ networks to distribute goods,  \n  and Flamingos\u2019 charisma to sell illusion\
    \ to the masses.\n- **Southside Flamingos** rely on Krakens\u2019 freight routes\
    \ to move counterfeit luxury items,  \n  Dragons\u2019 media to legitimize their\
    \ image, and Bears\u2019 power grids to keep the clubs glowing.\n\n**Post-Outbreak\
    \ Dynamic:** - Cooperation becomes transactional: fuel for power, publicity for\
    \ safety, glamour for access.   - Conflicts often erupt over scarce resources\
    \ but resolve into uneasy trades.   - The city survives only because each faction\u2019\
    s strength covers another\u2019s weakness.\n"
  validation_type: narrative_logic
  applies_to:
  - faction
  - economy
  - story_integration

- id: fac_009
  category: timeline_validation
  priority: critical
  rule: Use timeline validation tools to verify that formation_date, key_events, and faction history milestones are chronologically consistent, all events occur before or during 1998 (current game year), and temporal progression aligns with faction development narrative
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

system_prompt: "You are the Faction Generation Engine for the \u201CCity of Brains\u201D\
  \ universe.  \nYour role is to create new, lore-consistent factions that fit within\
  \ the City of Brains IP \u2014 a 1990s retro-futuristic survival-horror world blending\
  \ neon industrial aesthetics, corporate collapse, counter-culture rebellion, and\
  \ environmental decay. Follow ALL of these instructions exactly. Ensure compliance\
  \ with all provided rule.\n\n### TEMPLATE COMPLIANCE\nAll output MUST conform 100%\
  \ to the official **FACTION_TEMPLATE.md** structure.  \nEvery field and markdown\
  \ body section listed below must be included, in order, even if a placeholder value\
  \ is used.\n\n### GENERATION INSTRUCTIONS\nWhen generating a new faction:\n1. Read\
  \ the FACTION_RULES.md to understand faction balance, ecosystem, and dependencies.\
  \  \n2. Assign a unique color scheme, tone, and archetype (industrial, luxury, rebel,\
  \ tech, religious, etc).  \n3. Define one **Defining Moment** that shaped their\
  \ power or downfall.  \n4. Define their **Faction Voice** \u2014 how they speak,\
  \ what slang they use, and how they sound over radio/VO.  \n5. Integrate faction\
  \ economics and interdependence so no group exists in isolation.  \n6. Ensure all\
  \ sections are filled \u2014 do not skip or summarize any required fields."
---


# Faction Rules

## Validation Rules

Each faction’s **color identity**, **territory**, and **economic specialty** define their influence within the City of Brains.



### Color Associations

| Faction | Primary Color | Secondary Color | Symbolism |
|----------|----------------|-----------------|------------|
| Northside Bears | Electric Blue (#00aaff) | Pale Cyan (#66ccff) | Precision, technology, unity |
| Westside Krakens | Toxic Green (#00ff80) | Diesel Rust (#55ff99) | Chaos, adaptability, fuel economy |
| Eastside Dragons | Royal Purple (#8c1eff) | Gold Accent (#ffd966) | Decadence, pride, influence |
| Southside Flamingos | Flamingo Pink (#ff66c4) | Sunset Orange (#ff934f) | Glamour, vanity, danger |



### District Control Overview

| Zone | Control Status | Primary Influence | Notes |
|------|----------------|-------------------|-------|
| **Northside District** | Controlled | Bears | Power grids, off-grid labs, BOL servers |
| **Westside District** | Controlled | Krakens | Trucking routes, scrapyards, mechanics |
| **Eastside District** | Controlled | Dragons | Corporate plazas, PR towers, luxury housing |
| **Southside District** | Controlled | Flamingos | Nightclubs, counterfeit markets, shipping ports |
| **Central Nervous Park** | Contested | All | Carnival grounds, outbreak origin |
| **Underground** | Uncontrolled | None | Old BOL tunnels, smugglers’ routes |
| **Chemical Plant / Mountains** | Contested | None | Pollution epicenter, high-value research site |
| **Government Facilities** | Uncontrolled | None | Locked-down relics of pre-outbreak order |
| **ELJ Arena** | Neutral | All | Tournament zone for “Battle of the Tusks” competition |


## Voice & Tone Guidelines

### 🧊 Northside Bears (Blue)
**Tone:** Analytical, nerdy, paranoid.  
**Speech:** Technical and communal, favoring collective language (“we,” “our”).  
**Example:** “We reprogrammed the relay to reroute clean power. Efficiency keeps us alive.”

### 🛢 Westside Krakens (Green)
**Tone:** Fast, chaotic, gritty.  
**Speech:** Trucker-meets-pirate slang with improvised metaphors.  
**Example:** “She’s leaking oil and luck — better patch both before sunrise!”

### 💼 Eastside Dragons (Purple)
**Tone:** Corporate charm masking vanity.  
**Speech:** Polished, persuasive, always selling a dream.  
**Example:** “Survival’s just branding, darling — and we *own* the logo.”

### 💄 Southside Flamingos (Pink-Orange)
**Tone:** Dramatic, flamboyant, dangerous.  
**Speech:** Fashion jargon mixed with veiled threats and theatrical delivery.  
**Example:** “Buy the look, live the fantasy — or don’t live at all.”


### Faction Ecosystem Overview

| Faction | Provides | Depends On | Exploits |
|----------|-----------|------------|-----------|
| **Northside Bears** | Technology, energy grids | Krakens (construction), Dragons (media), Flamingos (smuggling circuits) | Krakens’ labor |
| **Westside Krakens** | Fuel, freight, mechanical work | Bears (tech), Dragons (contracts), Flamingos (black market) | Flamingos’ connections |
| **Eastside Dragons** | Advertising, propaganda, finance | Bears (hardware), Krakens (distribution), Flamingos (style) | Everyone’s image |
| **Southside Flamingos** | Fashion, nightlife, smuggling | Krakens (shipping), Bears (power), Dragons (influence) | Public perception |

No faction can stand alone — even domination leads to collapse of supply lines, power grids, or morale.


## Implementation Notes

- District-based color grading, signage, and lighting should immediately convey faction control.  
- Uncontrolled regions (Chemical Plant, Government, Underground) should feature **neutral greys, flickering fluorescents, or polluted greens** to distinguish them.  
- Brand tie-ins (ads, billboards, vending machines) should favor faction colors and slogans.  
- ELJ Arena events dynamically mix all faction aesthetics — color lighting changes per round.  
- NPC dialogue and trade offers must reflect the faction’s industrial specialization.

