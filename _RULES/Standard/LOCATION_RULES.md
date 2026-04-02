---
# LOCATION GENERATION METADATA
system_prompt: "Generate a location for the City of Brains universe following the location template exactly. Create atmospheric descriptions that show environmental storytelling, corporate influence, and outbreak impact. Include specific details about faction control, brand presence, and how the location serves the narrative."
global: false
priority: "high"
entity_type: "location"
template_reference: "LOCATION_TEMPLATE.md"

# LOCATION VALIDATION RULES
rules:
- id: loc_001
  category: structure
  priority: critical
  rule: Every location MUST belong to a district
  validation_type: error
  applies_to:
  - location
- id: loc_002
  category: atmosphere
  priority: critical
  rule: Locations must blend 1990s nostalgia with post-apocalyptic decay
  validation_type: error
  applies_to:
  - location
- id: loc_003
  category: brands
  priority: high
  rule: Minimum 2 brand presences per commercial location
  validation_type: warning
  applies_to:
  - location
- id: loc_004
  category: hazards
  priority: high
  rule: Every location needs at least one environmental hazard
  validation_type: warning
  applies_to:
  - location
- id: loc_005
  category: general
  priority: medium
  rule: Locations must be set in a District in order to be considered accessible to
    players and characters. Locations without a district should be set as Unincorporated
    which can include historical locations (ones that no longer exist in world but
    the story and characters remember them), or locations that are not yet built (like
    coming soon, or did you see that new casino on the outskirts they are building?)
  validation_type: warning
  applies_to:
  - location

- id: loc_006
  category: timeline_validation
  priority: critical
  rule: Use timeline validation tools to verify that founded_year and key_events are chronologically consistent, all events occur before or during 1998 (current game year), destruction_date (if applicable) occurs after founding, and temporal progression is logical
  validation_type: error
  applies_to:
  - location
  required_tools: ["check_temporal_conflicts", "calculate_duration"]

- id: loc_007
  category: entity_validation
  priority: critical
  rule: Before referencing characters (primary_npcs, owner, staff), brands (associated_brands,
    vendors), factions (faction_control), or districts, use validation tools to verify
    they exist. Use check_character_exists for NPCs, check_brand_exists for brands,
    validate_all_references for bulk validation. Never reference non-existent entities
  validation_type: error
  applies_to:
  - location
  required_tools: ["check_character_exists", "check_brand_exists", "validate_all_references"]
---


# LOCATION GENERATION RULES
## City of Brains Universe

### Context and Guidelines

This document provides rules and context for generating locations in the City of Brains universe. The YAML frontmatter above contains machine-enforceable validation rules, while this section provides creative context and guidelines for human designers and AI generation.

### LOCATION TYPES
```yaml
location_categories:
  commercial:
    required:
      - "Cash registers (broken or looted)"
      - "Shopping carts/baskets"
      - "Price tags with 1990s prices"
      - "Brand signage"
    atmosphere: "Former consumer paradise, now picked clean"
    
  residential:
    required:
      - "Personal belongings scattered"
      - "Family photos"
      - "Signs of hasty evacuation"
    atmosphere: "Intimate tragedy, frozen moments"
    
  industrial:
    required:
      - "Heavy machinery"
      - "Safety warnings"
      - "Worker belongings in lockers"
    atmosphere: "Dangerous, utilitarian, abandoned mid-shift"
    
  recreational:
    required:
      - "Entertainment remnants"
      - "Ticket booths"
      - "Concession stands"
    atmosphere: "Eerie contrast of fun and horror"
```

### VISUAL DETAILS
```yaml
environmental_storytelling:
  mandatory_elements:
    - "Clues about what happened here during outbreak"
    - "Signs of survivor activity (camps, barricades)"
    - "Nature reclaiming spaces (vines, animals)"
    
  lighting:
    - "Dramatic shadows from broken windows"
    - "Neon signs flickering intermittently"
    - "Emergency lighting still running on backup power"
    
  sound_design:
    - "Distant infected groans"
    - "Structural creaking"
    - "1990s music still playing on loop"
```

### NPC PLACEMENT
```yaml
npc_rules:
  density:
    safe_zones: "5-10 NPCs"
    contested: "2-5 NPCs"
    dangerous: "0-2 NPCs"
    
  behavior:
    - "NPCs must have reason for being there"
    - "Faction allegiance affects placement"
    - "Time of day affects NPC presence"
```

### LOOT & RESOURCES
```yaml
resource_distribution:
  scavenged_level:
    untouched: "Full shelves, locked doors"
    partial: "Some supplies remain, picked over"
    cleaned_out: "Empty, only hidden caches"
    
  item_placement:
    logical: "Medicine in pharmacies, food in kitchens"
    hidden: "Survivor caches in unexpected places"
    trapped: "Valuable items may be booby-trapped"
```

### ATMOSPHERIC REQUIREMENTS

Every location should blend:
- **1990s nostalgia**: Period-appropriate technology, brands, and cultural references
- **Post-apocalyptic decay**: Evidence of the outbreak and abandonment
- **Environmental storytelling**: Visual clues about what happened

### DISTRICT INTEGRATION

Locations must respect their district's characteristics:
- **Downtown**: Dense, vertical, lots of neon
- **Suburbs**: Spread out, residential, white picket fences gone wrong
- **Industrial**: Factories, warehouses, chemical hazards
- **Waterfront**: Docks, boats, aquatic dangers

### BRAND PRESENCE

Commercial locations should feature:
- Multiple brand advertisements and products
- Both intact and destroyed brand signage
- Products that tell a story (half-eaten Double Dip Dog Sauce)

### HAZARD DESIGN

Environmental hazards should be:
- Logical for the location type
- Avoidable with skill/knowledge
- Tied to the outbreak narrative
- Varying in danger level

---

## Usage Notes

### For AI Generation:
Pass this entire document as context. The YAML rules are enforced by the validation system, while the markdown body provides creative guidelines.

### For Human Designers:
- Check YAML rules for validation requirements
- Use markdown sections for creative inspiration
- Remember the 1990s alternate timeline setting
- Consider how each location tells part of the outbreak story

### For Web App:
- YAML frontmatter = Validation rules (add/edit/delete/enforce)
- Markdown body = Context editor (rich text editing for guidelines)