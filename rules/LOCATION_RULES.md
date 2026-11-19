---
# LOCATION GENERATION METADATA
system_prompt: "Generate a location for this project. Follow the location template. Belong to a district that exists here, or mark the place unincorporated. Match the atmosphere the project records for that district. Name only brands, people, and factions that exist."
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
  validation_type: warning
  applies_to:
  - location
- id: loc_002
  category: atmosphere
  priority: critical
  rule: "A location's atmosphere must match the atmosphere recorded for its district and for this project. Do not add a decay, era, or mood the project has not recorded."
  validation_type: warning
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
  rule: "founded_year and key_events must be in chronological order. A destruction date, when set, must fall after founding. Dates must sit inside the years this project uses."
  validation_type: warning
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
  validation_type: warning
  applies_to:
  - location
  required_tools: ["check_character_exists", "check_brand_exists", "validate_all_references"]
---

# Location guidance

These rules check structure and consistency. They do not name a setting.

Every location belongs to a district that exists in this project, or it is marked unincorporated (a place the story remembers, or a place that is not built yet). A location needs at least one hazard. A commercial location that names brands must name brands that exist. Dates must sit inside the project's years.

Atmosphere comes from the district and from the project. Do not add nostalgia, decay, or a mood the project has not recorded.

Name only people, brands, and factions that exist. Add the entity first when the reference is new.
