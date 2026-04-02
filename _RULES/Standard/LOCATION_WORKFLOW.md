---
version: "1.0"
name: "location_workflow"
label: "Location Production Workflow"
description: "Status progression for locations from concept to archived"
last_updated: "2026-03-30"
default_stage: "concept"
allow_multiple_active: false
notifications:
  on_enter:
    - type: "print"
      message: "Location {{location_id}} entered stage {{stage_name}}"
  on_exit:
    - type: "archive"
      target: "stage_history/locations/{{location_id}}/{{old_stage}}"
  on_complete:
    - type: "print"
      message: "Location {{location_id}} completed {{stage_name}}"

# STAGES: Location lifecycle progression
stages:
  - id: "concept"
    name: "Concept"
    description: "Initial location idea, purpose, and basic concept art"
    color: "#CCCCCC"
    order: 1
    locks:
      - field: "district"
        reason: "District placement determined in drafting"
      - field: "biome"
        reason: "Environmental context defined in drafting"
      - field: "coordinates"
        reason: "World placement defined in drafting"
    requires:
      - "name"
      - "template_type"
      - "location_id"
    allows:
      - "transit_to:drafting"

  - id: "drafting"
    name: "Drafting"
    description: "Location details added - type, category, access, basic assets"
    color: "#FFCC00"
    order: 2
    locks:
      - field: "story_chapters"
        reason: "Narrative integration finalized in review"
      - field: "important_objects"
        reason: "Interactive elements added during layout"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
    allows:
      - "transit_to:layout"
      - "transit_to:rejected"

  - id: "layout"
    name: "Layout"
    description: "Spatial layout defined - rooms, zones, entry points, interior design"
    color: "#FF9900"
    order: 3
    locks:
      - field: "atmosphere"
        reason: "Vibe and mood finalized during rendering"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
    allows:
      - "transit_to:narrative"
      - "transit_to:drafting"

  - id: "narrative"
    name: "Narrative"
    description: "Story integration - lore, history, narrative importance, faction control"
    color: "#FF6600"
    order: 4
    locks:
      - field: "searchable_objects"
        reason: "Interactive elements added during asset integration"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
    allows:
      - "transit_to:atmosphere"
      - "transit_to:layout"

  - id: "atmosphere"
    name: "Atmosphere"
    description: "Vibe and mood - lighting, sounds, weather effects, ambient detail"
    color: "#0066FF"
    order: 5
    locks:
      - field: "interactive_features"
        reason: "Interactive elements added during asset integration"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
      - "atmosphere"
      - "lighting"
      - "ambient_sounds"
      - "weather_effects"
      - "air_quality"
    allows:
      - "transit_to:asset_integration"
      - "transit_to:narrative"

  - id: "asset_integration"
    name: "Asset Integration"
    description: "3D models, textures, sounds, and interactive elements added"
    color: "#0099FF"
    order: 6
    locks:
      - field: "validation_complete"
        reason: "Validation performed in review stage"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
      - "atmosphere"
      - "lighting"
      - "ambient_sounds"
      - "weather_effects"
      - "air_quality"
      - "model_3d"
      - "textures"
      - "interactive_features"
      - "searchable_objects"
    allows:
      - "transit_to:review"
      - "transit_to:asset_integration"

  - id: "review"
    name: "Review"
    description: "Internal review - world-building consistency, lore alignment, gameplay integration"
    color: "#00CCFF"
    order: 7
    locks:
      - field: "producer_notes"
        reason: "Notes preserved for audit trail"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
      - "atmosphere"
      - "lighting"
      - "ambient_sounds"
      - "weather_effects"
      - "air_quality"
      - "model_3d"
      - "textures"
      - "interactive_features"
      - "searchable_objects"
      - "producer_notes"
      - "reviews_complete"
    allows:
      - "transit_to:approval"
      - "transit_to:asset_integration"

  - id: "approval"
    name: "Approval"
    description: "Producer/design lead approval - final verification before deployment"
    color: "#00FFFF"
    order: 8
    locks:
      - field: "producer_notes"
        reason: "Notes preserved for audit trail"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
      - "atmosphere"
      - "lighting"
      - "ambient_sounds"
      - "weather_effects"
      - "air_quality"
      - "model_3d"
      - "textures"
      - "interactive_features"
      - "searchable_objects"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
    allows:
      - "transit_to:published"
      - "transit_to:review"

  - id: "published"
    name: "Published"
    description: "Location live in world - players can explore and interact"
    color: "#00AA00"
    order: 9
    locks:
      - field: "coordinates"
        reason: "World placement is immutable"
      - field: "faction_control"
        reason: "World state consistency"
      - field: "biome"
        reason: "Environmental consistency"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
      - "atmosphere"
      - "lighting"
      - "ambient_sounds"
      - "weather_effects"
      - "air_quality"
      - "model_3d"
      - "textures"
      - "interactive_features"
      - "searchable_objects"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
    allows:
      - "transit_to:active"
      - "transit_to:deprecated"

  - id: "active"
    name: "Active"
    description: "Location fully integrated - NPCs present, quests active, player accessible"
    color: "#00FF00"
    order: 10
    locks:
      - field: "coordinates"
        reason: "World state consistency"
      - field: "faction_control"
        reason: "World state consistency"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
      - "atmosphere"
      - "lighting"
      - "ambient_sounds"
      - "weather_effects"
      - "air_quality"
      - "model_3d"
      - "textures"
      - "interactive_features"
      - "searchable_objects"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
      - "npcs_present"
      - "quests_active"
    allows:
      - "transit_to:deprecated"
      - "transit_to:deleted"

  - id: "deprecated"
    name: "Deprecated"
    description: "Location removed from active play but preserved for lore/history"
    color: "#999999"
    order: 11
    locks:
      - field: "coordinates"
        reason: "Historical accuracy preserved"
      - field: "faction_control"
        reason: "Historical accuracy preserved"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
      - "atmosphere"
      - "lighting"
      - "ambient_sounds"
      - "weather_effects"
      - "air_quality"
      - "model_3d"
      - "textures"
      - "interactive_features"
      - "searchable_objects"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
      - "deprecation_date"
      - "deprecation_reason"
    allows:
      - "transit_to:archived"
      - "transit_to:active"

  - id: "archived"
    name: "Archived"
    description: "Location permanently preserved - historical reference only"
    color: "#666666"
    order: 12
    locks:
      - all_fields: true
        reason: "Historical archive - no modifications"
    requires:
      - "name"
      - "description"
      - "location_id"
      - "location_type"
      - "category"
      - "district"
      - "biome"
      - "coordinates"
      - "accessibility"
      - "layout"
      - "interior_zones"
      - "entrance_points"
      - "exit_points"
      - "narrative_importance"
      - "story_chapters"
      - "faction_control"
      - "historical_context"
      - "atmosphere"
      - "lighting"
      - "ambient_sounds"
      - "weather_effects"
      - "air_quality"
      - "model_3d"
      - "textures"
      - "interactive_features"
      - "searchable_objects"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
      - "deprecation_date"
      - "deprecation_reason"
      - "archive_date"
    allows: []

  - id: "deleted"
    name: "Deleted"
    description: "Location removed permanently - recoverable only from backups"
    color: "#FF0000"
    order: 13
    requires:
      - "name"
      - "location_id"
      - "deletion_reason"
      - "deleted_by"
      - "deletion_date"
    allows: []

  - id: "rejected"
    name: "Rejected"
    description: "Location rejected feedback - requires revision before resubmission"
    color: "#FF6600"
    order: 14
    locks:
      - field: "feedback_notes"
        reason: "Feedback preserved for revision"
    requires:
      - "name"
      - "location_id"
      - "rejection_reason"
      - "feedback_notes"
    allows:
      - "transit_to:drafting"
      - "transit_to:concept"

# TRANSITIONS: Explicit transition definitions with requirements and permissions
transitions:
  - from: "concept"
    to: "drafting"
    triggers:
      - type: "auto"
        condition: "all_required_fields_filled(['name', 'description', 'location_id', 'location_type', 'category', 'district'])"
    permissions:
      roles: ["world_builder", "designer", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location concept approved for {{location_id}}"

  - from: "drafting"
    to: "layout"
    triggers:
      - type: "manual"
    permissions:
      roles: ["world_builder", "designer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} entered layout phase"

  - from: "layout"
    to: "narrative"
    triggers:
      - type: "auto"
        condition: "all_interior_zones_complete AND all_entrance_points_defined"
    permissions:
      roles: ["world_builder", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} entered narrative phase"

  - from: "narrative"
    to: "atmosphere"
    triggers:
      - type: "manual"
    permissions:
      roles: ["world_builder", "artist"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} entered atmosphere phase"

  - from: "atmosphere"
    to: "asset_integration"
    triggers:
      - type: "manual"
    permissions:
      roles: ["artist", "sound_designer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} entered asset integration phase"

  - from: "asset_integration"
    to: "review"
    triggers:
      - type: "auto"
        condition: "all_textures_loaded AND all_models_built AND all_sounds_added"
    permissions:
      roles: ["artist", "sound_designer", "world_builder"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} ready for review"

  - from: "review"
    to: "approval"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "producer_notes_filled AND reviews_complete"
    permissions:
      roles: ["producer", "design_lead", "world_leader"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} entered approval stage"

  - from: "approval"
    to: "published"
    triggers:
      - type: "manual"
        required_roles: ["producer"]
    permissions:
      roles: ["producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} deployed to world"

  - from: "published"
    to: "active"
    triggers:
      - type: "auto"
        condition: "npcs_assigned AND_quests_connected"
    permissions:
      roles: ["producer", "game_designer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} is now active"

  - from: "active"
    to: "deprecated"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "player_visit_count_reached_zero AND_7_days_inactive"
    permissions:
      roles: ["producer", "world_leader"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} deprecated"

  - from: "deprecated"
    to: "archived"
    triggers:
      - type: "auto"
        condition: "7_days_deprecated"
    permissions:
      roles: ["producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Location {{location_id}} archived"

# TRANSITION VALIDATION RULES
validation_rules:
  - id: "loc_wf_001"
    category: "core_identity"
    rule: "Location ID must remain consistent across all stages"
    validation_type: "error"
    applies_to: ["concept", "drafting", "layout", "narrative", "atmosphere", "asset_integration", "review", "approval", "published", "active", "deprecated", "archived", "deleted", "rejected"]

  - id: "loc_wf_002"
    category: "district_placement"
    rule: "District assignment requires district metadata file to exist"
    validation_type: "error"
    applies_to: ["drafting", "layout", "narrative", "atmosphere", "asset_integration", "review", "approval", "published", "active", "deprecated", "archived"]

  - id: "loc_wf_003"
    category: "faction_control"
    rule: "Faction control assignment requires faction metadata file to exist"
    validation_type: "error"
    applies_to: ["narrative", "atmosphere", "asset_integration", "review", "approval", "published", "active", "deprecated", "archived"]

  - id: "loc_wf_004"
    category: "biome_consistency"
    rule: "Biome must be consistent with district environment and climate"
    validation_type: "warning"
    applies_to: ["drafting", "layout", "narrative", "atmosphere"]

  - id: "loc_wf_005"
    category: "interior_zones"
    rule: "At least one interior zone must be defined before asset integration"
    validation_type: "error"
    applies_to: ["review", "approval", "published", "active", "deprecated", "archived"]

  - id: "loc_wf_006"
    category: "navigation"
    rule: "All interior zones must have connection points defined"
    validation_type: "error"
    applies_to: ["layout", "narrative", "atmosphere", "asset_integration", "review", "approval", "published", "active", "deprecated", "archived"]

  - id: "loc_wf_007"
    category: "model_reference"
    rule: "3D model reference must exist before published stage"
    validation_type: "warning"
    applies_to: ["asset_integration", "review", "approval", "published", "active", "deprecated", "archived"]

  - id: "loc_wf_008"
    category: "lore_approval"
    rule: "Lore master approval required before published stage for major locations"
    validation_type: "error"
    applies_to: ["approval", "published", "active", "deprecated", "archived"]

  - id: "loc_wf_009"
    category: "identifier_consistency"
    rule: "Location ID must match folder name exactly"
    validation_type: "error"
    applies_to: ["drafting", "layout", "narrative", "atmosphere", "asset_integration", "review", "approval", "published", "active", "deprecated", "archived", "deleted", "rejected"]

  - id: "loc_wf_010"
    category: "interactive_elements"
    rule: "Interactive elements must reference valid objects or locations"
    validation_type: "error"
    applies_to: ["asset_integration", "review", "approval", "published", "active", "deprecated", "archived"]

# META-FIELDS for workflow tracking
meta_fields:
  workflow_version: "1.0"
  workflow_name: "location_workflow"
  last_stage_update: "timestamp"
  stage_transitions:
    - stage: "concept"
      entered: "timestamp"
      exited: "timestamp"
      duration_seconds: "number"
    - stage: "drafting"
      entered: "timestamp"
      exited: "timestamp"
      duration_seconds: "number"
  approvals:
    producer_approval: "boolean"
    lore_approval: "boolean"
    world_leader_approval: "boolean"
  metadata:
    created_by: "user_id"
    created_date: "timestamp"
    last_modified_by: "user_id"
    last_modified_date: "timestamp"
    revision_count: "number"

# VERSION HISTORY
version_history:
  - version: "1.0"
    date: "2026-03-30"
    author: "system"
    changes:
      - "Initial location workflow definition"
      - "14 stages: concept -> drafting -> layout -> narrative -> atmosphere -> asset_integration -> review -> approval -> published -> active -> deprecated -> archived, plus deleted and rejected"
      - "Explicit transition definitions with triggers and permissions"
      - "Validation rules for core identity, district placement, faction control, biome consistency, interior zones, navigation, model references, lore approval, identifier consistency, and interactive elements"
    breaking_changes: []

# EXAMPLES
examples:
  standard_location:
    location_id: "loc_rusty_auto_repair"
    stages:
      - stage: "concept"
        days: 1
        notes: "Initial idea - auto repair shop in a post-apocalyptic world"
      - stage: "drafting"
        days: 3
        notes: "Added location_type, category, district, biome, coordinates"
      - stage: "layout"
        days: 5
        notes: "Added interior_zones, entrance_points, layout structure"
      - stage: "narrative"
        days: 4
        notes: "Added story_chapters, faction_control, historical_context"
      - stage: "atmosphere"
        days: 3
        notes: "Added atmosphere, lighting, ambient_sounds"
      - stage: "asset_integration"
        days: 7
        notes: "Added 3D model, textures, interactive features"
      - stage: "review"
        days: 2
        notes: "Producer notes recorded"
      - stage: "approval"
        days: 1
        notes: "Producer and lore approval granted"
      - stage: "published"
        days: 0
        notes: "Deployed to world"
      - stage: "active"
        days: 0
        notes: "Fully integrated with NPCs and quests"

  location_revision:
    location_id: "loc_deal_mart"
    stages:
      - stage: "concept"
        days: 2
      - stage: "drafting"
        days: 3
      - stage: "layout"
        days: 5
      - stage: "narrative"
        days: 4
      - stage: "atmosphere"
        days: 3
      - stage: "asset_integration"
        days: 6
      - stage: "review"
        days: 2
        notes: "Feedback: Need more interactive elements"
      - stage: "asset_integration"
        days: 8
        notes: "Revision: Added more searchable objects and interactive features"
      - stage: "review"
        days: 2
      - stage: "approval"
        days: 1
      - stage: "published"
        days: 0

---
# Location Workflow in Practice

## For World Builders

1. **Concept Stage**: Start with location idea - name, purpose, basic concept
2. **Drafting Stage**: Define core requirements - type, category, district, coordinates
3. **Layout Stage**: Add spatial structure - rooms, zones, entrances, exits
4. **Narrative Stage**: Add story integration - lore, history, faction control
5. **Atmosphere Stage**: Add vibe - lighting, sounds, weather effects
6. **Asset Integration Stage**: Add 3D models, textures, interactive elements
7. **Review Stage**: Get feedback - world consistency, gameplay integration
8. **Approval Stage**: Get producer approval - final verification
9. **Published Stage**: Location is live in world
10. **Active Stage**: Fully integrated with NPCs and quests

## For Artists

- Add 3D models and textures during asset integration
- Ensure all interactive features are functional
- Check consistency with narrative and atmosphere

## For Producers

- Approve transitions from approval -> published
- Monitor stage durations for workflow efficiency
- Archive deprecated locations after 7 days

## Common Workflows

### New Location Creation
```
concept -> drafting -> layout -> narrative -> atmosphere -> asset_integration -> review -> approval -> published -> active
```

### Location Revision
```
active -> asset_integration -> review -> approval -> published -> active
```

### Location Deprecation
```
active -> deprecated -> archived
```

### Location Deletion (Emergency)
```
active -> deleted (permanent, recoverable only from backup)
```

## Workflow Metrics

Track these metrics for workflow health:
- Average days per stage
- Re-work rate (transitions back to earlier stages)
- Approval time by producer
- Stage transition types (manual vs auto)
