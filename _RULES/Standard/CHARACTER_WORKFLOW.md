---
version: "1.0"
name: "character_workflow"
label: "Character Production Workflow"
description: "Status progression for characters from concept to archived"
last_updated: "2026-03-30"
default_stage: "concept"
allow_multiple_active: false
notifications:
  on_enter:
    - type: "print"
      message: "Character {{character_id}} entered stage {{stage_name}}"
  on_exit:
    - type: "archive"
      target: "stage_history/characters/{{character_id}}/{{old_stage}}"
  on_complete:
    - type: "print"
      message: "Character {{character_id}} completed {{stage_name}}"

# STAGES: Character lifecycle progression
stages:
  - id: "concept"
    name: "Concept"
    description: "Initial character idea, basic background, and concept art"
    color: "#CCCCCC"
    order: 1
    locks:
      - field: "faction"
        reason: "Faction alignment determined in development phase"
      - field: "skills"
        reason: "Skills defined during character development"
      - field: "appearance"
        reason: "Appearance details added during rendering"
    requires:
      - "name"
      - "template_type"
      - "character_id"
    allows:
      - "transit_to:draft"

  - id: "draft"
    name: "Draft"
    description: "Character core requirements defined - stats, skills, basic narrative"
    color: "#FFCC00"
    order: 2
    locks:
      - field: "faction_relationships"
        reason: "Relationships refined in development phase"
      - field: "dialogue_samples"
        reason: "Dialogue added during personality development"
    requires:
      - "name"
      - "description"
      - "character_id"
      - "primary_location"
      - "faction"
      - "skills"
      - "species"
    allows:
      - "transit_to:development"
      - "transit_to:rejected"

  - id: "development"
    name: "Development"
    description: "Character personality fleshed out - dialogue, relationships, backstory"
    color: "#FF9900"
    order: 3
    locks:
      - field: "core_stats"
        reason: "Core stats finalized before review"
      - field: "appearance"
        reason: "Appearance finalized before review"
    requires:
      - "name"
      - "description"
      - "character_id"
      - "primary_location"
      - "faction"
      - "skills"
      - "species"
      - "personality"
      - "backstory"
      - "faction_relationships"
    allows:
      - "transit_to:review"
      - "transit_to:draft"

  - id: "review"
    name: "Review"
    description: "Internal review - narrative consistency, lore alignment, world-building checks"
    color: "#0066FF"
    order: 4
    locks:
      - field: "dialogue_samples"
        reason: "Dialogue finalized before approval"
    requires:
      - "name"
      - "description"
      - "character_id"
      - "primary_location"
      - "faction"
      - "skills"
      - "species"
      - "personality"
      - "backstory"
      - "faction_relationships"
      - "dialogue_samples"
      - "sprite_reference"
      - "voice_actor"
    allows:
      - "transit_to:approval"
      - "transit_to:development"

  - id: "approval"
    name: "Approval"
    description: "Producer/design lead approval - final verification before deployment"
    color: "#00CCFF"
    order: 5
    locks:
      - field: "pre_approval_notes"
        reason: "Notes preserved for audit trail"
    requires:
      - "name"
      - "description"
      - "character_id"
      - "primary_location"
      - "faction"
      - "skills"
      - "species"
      - "personality"
      - "backstory"
      - "faction_relationships"
      - "dialogue_samples"
      - "sprite_reference"
      - "voice_actor"
      - "producer_approval"
      - "lore_approved"
    allows:
      - "transit_to:published"
      - "transit_to:review"
      - "transit_to:rejected"

  - id: "published"
    name: "Published"
    description: "Character live in the game - appearing in locations, having dialogue"
    color: "#00AA00"
    order: 6
    locks:
      - field: "faction"
        reason: "Core identity - only faction migration allowed"
      - field: "species"
        reason: "Core identity - permanent"
      - field: "primary_location"
        reason: "World placement - changes require location team"
    requires:
      - "name"
      - "description"
      - "character_id"
      - "primary_location"
      - "faction"
      - "skills"
      - "species"
      - "personality"
      - "backstory"
      - "faction_relationships"
      - "dialogue_samples"
      - "sprite_reference"
      - "voice_actor"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
    allows:
      - "transit_to:active"
      - "transit_to:retired"

  - id: "active"
    name: "Active"
    description: "Character fully integrated - NPCs respond, quest givers, interactable"
    color: "#00FF00"
    order: 7
    locks:
      - field: "faction"
        reason: "World state consistency"
      - field: "primary_location"
        reason: "World state consistency"
    requires:
      - "name"
      - "description"
      - "character_id"
      - "primary_location"
      - "faction"
      - "skills"
      - "species"
      - "personality"
      - "backstory"
      - "faction_relationships"
      - "dialogue_samples"
      - "sprite_reference"
      - "voice_actor"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
      - "active_since"
      - "quest_giver"
    allows:
      - "transit_to:retired"
      - "transit_to:deleted"

  - id: "retired"
    name: "Retired"
    description: "Character removed from active play but preserved for lore/history"
    color: "#999999"
    order: 8
    locks:
      - field: "faction"
        reason: "Preserved for historical accuracy"
      - field: "primary_location"
        reason: "Preserved for historical accuracy"
    requires:
      - "name"
      - "description"
      - "character_id"
      - "primary_location"
      - "faction"
      - "skills"
      - "species"
      - "personality"
      - "backstory"
      - "faction_relationships"
      - "dialogue_samples"
      - "sprite_reference"
      - "voice_actor"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
      - "retired_date"
      - "retirement_reason"
    allows:
      - "transit_to:archived"
      - "transit_to:active"

  - id: "archived"
    name: "Archived"
    description: "Character permanently preserved - historical reference only"
    color: "#666666"
    order: 9
    locks:
      - all_fields: true
        reason: "Historical archive - no modifications"
    requires:
      - "name"
      - "description"
      - "character_id"
      - "primary_location"
      - "faction"
      - "skills"
      - "species"
      - "personality"
      - "backstory"
      - "faction_relationships"
      - "dialogue_samples"
      - "sprite_reference"
      - "voice_actor"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
      - "retired_date"
      - "retirement_reason"
      - "archive_date"
    allows: []

  - id: "deleted"
    name: "Deleted"
    description: "Character removed - only recoverable from backups"
    color: "#FF0000"
    order: 10
    requires:
      - "name"
      - "character_id"
      - "deletion_reason"
      - "deleted_by"
      - "deletion_date"
    allows: []

  - id: "rejected"
    name: "Rejected"
    description: "Character rejected feedback - requires rework before resubmission"
    color: "#FF6600"
    order: 11
    locks:
      - field: "feedback_notes"
        reason: "Feedback preserved for revision"
    requires:
      - "name"
      - "character_id"
      - "rejection_reason"
      - "feedback_notes"
    allows:
      - "transit_to:draft"
      - "transit_to:concept"

# TRANSITIONS: Explicit transition definitions with requirements and permissions
transitions:
  - from: "concept"
    to: "draft"
    triggers:
      - type: "auto"
        condition: "all_required_fields_filled(['name', 'description', 'primary_location', 'faction', 'species'])"
    permissions:
      roles: ["writer", "designer", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Concept approved for character {{character_id}}"

  - from: "draft"
    to: "development"
    triggers:
      - type: "auto"
        condition: "personality_defined AND backstory_complete"
    permissions:
      roles: ["writer", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Character {{character_id}} entered development phase"

  - from: "development"
    to: "review"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "dialogue_samples_complete AND faction_relationships_final"
    permissions:
      roles: ["writer", "producer", "editor"]
    notifications:
      on_execute:
        - type: "print"
          message: "Character {{character_id}} ready for review"

  - from: "review"
    to: "approval"
    triggers:
      - type: "manual"
        required_roles: ["producer", "design_lead"]
    permissions:
      roles: ["producer", "design_lead", "lore_master"]
    notifications:
      on_execute:
        - type: "print"
          message: "Character {{character_id}} entered approval stage"

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
          message: "Character {{character_id}} deployed to game"

  - from: "published"
    to: "active"
    triggers:
      - type: "auto"
        condition: "npc_enabled_in_engine AND dialogue_loaded"
    permissions:
      roles: ["producer", "engineer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Character {{character_id}} is now interactable"

  - from: "active"
    to: "retired"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "character_usage_reached_zero AND 30_days_inactive"
    permissions:
      roles: ["producer", "design_lead"]
    notifications:
      on_execute:
        - type: "print"
          message: "Character {{character_id}} retired"

  - from: "retired"
    to: "archived"
    triggers:
      - type: "auto"
        condition: "7_days_retired"
    permissions:
      roles: ["producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Character {{character_id}} archived"

  - from: "active"
    to: "deleted"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "critical_lore_error AND无法_restore"
    permissions:
      roles: ["producer", "design_lead", "tech_lead"]
    notifications:
      on_execute:
        - type: "print"
          message: "Character {{character_id}} marked for deletion"

# TRANSITION VALIDATION RULES
# These rules are checked when any transition is attempted
validation_rules:
  - id: "char_wf_001"
    category: "core_identity"
    rule: "Character ID must remain consistent across all stages"
    validation_type: "error"
    applies_to: ["concept", "draft", "development", "review", "approval", "published", "active", "retired", "archived", "deleted"]

  - id: "char_wf_002"
    category: "faction_alignment"
    rule: "Faction assignment requires faction metadata file to exist"
    validation_type: "error"
    applies_to: ["draft", "development", "review", "approval", "published", "active", "retired", "archived"]

  - id: "char_wf_003"
    category: "primary_location"
    rule: "Primary location assignment requires location entity to exist"
    validation_type: "error"
    applies_to: ["draft", "development", "review", "approval", "published", "active", "retired", "archived"]

  - id: "char_wf_004"
    category: "species_consistency"
    rule: "Species change requires lore approval and affects faction compatibility"
    validation_type: "warning"
    applies_to: ["draft", "development"]

  - id: "char_wf_005"
    category: "skills_required"
    rule: "Character must have at least one skill assigned before published stage"
    validation_type: "error"
    applies_to: ["review", "approval", "published", "active", "retired", "archived"]

  - id: "char_wf_006"
    category: "dialogue_valid"
    rule: "Dialogues must reference valid scenario IDs before published stage"
    validation_type: "error"
    applies_to: ["review", "approval", "published", "active", "retired", "archived"]

  - id: "char_wf_007"
    category: "faction_relationships"
    rule: "All faction relationships must reference existing factions"
    validation_type: "error"
    applies_to: ["development", "review", "approval", "published", "active", "retired", "archived"]

  - id: "char_wf_008"
    category: "sprite_reference"
    rule: "Sprite reference path must exist before published stage"
    validation_type: "warning"
    applies_to: ["review", "approval", "published", "active", "retired", "archived"]

  - id: "char_wf_009"
    category: "voice_actor"
    rule: "Voice actor must be specified for main characters before published"
    validation_type: "warning"
    applies_to: ["approval", "published", "active", "retired", "archived"]

  - id: "char_wf_010"
    category: "lore_approval"
    rule: "Lore master approval required before published stage"
    validation_type: "error"
    applies_to: ["approval", "published", "active", "retired", "archived"]

# META-FIELDS for workflow tracking
meta_fields:
  workflow_version: "1.0"
  workflow_name: "character_workflow"
  last_stage_update: "timestamp"
  stage_transitions:
    - stage: "concept"
      entered: "timestamp"
      exited: "timestamp"
      duration_seconds: "number"
    - stage: "draft"
      entered: "timestamp"
      exited: "timestamp"
      duration_seconds: "number"
  approvals:
    producer_approval: "boolean"
    lore_approval: "boolean"
    design_approval: "boolean"
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
      - "Initial character workflow definition"
      - "11 stages: concept -> draft -> development -> review -> approval -> published -> active -> retired -> archived, plus rejected and deleted"
      - "Explicit transition definitions with triggers and permissions"
      - "Validation rules for core identity, faction alignment, location, species, skills, dialogue, relationships, sprite references, voice actors, and lore approval"
    breaking_changes: []

# EXAMPLES
examples:
  concept_to_published:
    character_id: "ch_rusty_mcdaniels"
    stages:
      - stage: "concept"
        days: 1
        notes: "Initial idea - mechanic with rusty aesthetic"
      - stage: "draft"
        days: 3
        notes: "Added skills: Mechanical Repair, Automotive Knowledge; faction: Krakens"
      - stage: "development"
        days: 5
        notes: "Added backstory, personality, dialogue samples"
      - stage: "review"
        days: 2
        notes: "Internal review - faction alignment verified"
      - stage: "approval"
        days: 1
        notes: "Producer approval granted, lore approved"
      - stage: "published"
        days: 0
        notes: "Deployed to Rusty's Auto Repair location"

  repeated_development:
    character_id: "ch_mysterious_stranger"
    stages:
      - stage: "concept"
        days: 2
      - stage: "draft"
        days: 3
      - stage: "development"
        days: 4
      - stage: "review"
        days: 2
        notes: "Feedback: Need more backstory depth"
      - stage: "development"
        days: 7
        notes: "Revision: Added complete backstory"
      - stage: "review"
        days: 3
      - stage: "approval"
        days: 1
      - stage: "published"
        days: 0

---
# Character Workflow in Practice

## For Writers

1. **Concept Stage**: Start with character idea - name, core concept, basic background
2. **Draft Stage**: Define core requirements - location, faction, species, key skills
3. **Development Stage**: Add personality, backstory, relationships, dialogue
4. **Review Stage**: Wait for feedback - narrative consistency, lore alignment
5. **Approval Stage**: Get producer approval - final verification
6. **Published Stage**: Character is live in game

## For Producers

- Approve transitions from approval -> published
- Monitor stage durations for workflow efficiency
- Archive retired characters after 7 days

## For Lore Masters

- Approve lore consistency before published stage
- Verify faction assignments are world-appropriate
- Check primary location assignments

## Common Workflows

### New Character Creation
```
concept -> draft -> development -> review -> approval -> published -> active
```

### Character Revision
```
published -> development -> review -> approval -> published
```

### Character Retirement
```
active -> retired -> archived
```

### Character Deletion (Emergency)
```
active -> deleted (permanent, recoverable only from backup)
```

## Workflow Metrics

Track these metrics for workflow health:
- Average days per stage
- Re-work rate (transitions back to earlier stages)
- Approval time by producer
- Stage transition types (manual vs auto)
