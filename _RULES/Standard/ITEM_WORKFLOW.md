---
version: "1.0"
name: "item_workflow"
label: "Item Production Workflow"
description: "Status progression for items from concept to archived"
last_updated: "2026-03-30"
default_stage: "concept"
allow_multiple_active: false
notifications:
  on_enter:
    - type: "print"
      message: "Item {{item_id}} entered stage {{stage_name}}"
  on_exit:
    - type: "archive"
      target: "stage_history/items/{{item_id}}/{{old_stage}}"
  on_complete:
    - type: "print"
      message: "Item {{item_id}} completed {{stage_name}}"

# STAGES: Item lifecycle progression
stages:
  - id: "concept"
    name: "Concept"
    description: "Initial item idea, basic purpose, and visual concept"
    color: "#CCCCCC"
    order: 1
    locks:
      - field: "item_type"
        reason: "Item type determined during drafting"
      - field: "rarity"
        reason: "Rarity determined based on stats and value"
      - field: "damage"
        reason: "Combat stats defined in drafting"
    requires:
      - "name"
      - "template_type"
      - "item_id"
    allows:
      - "transit_to:draft"

  - id: "draft"
    name: "Draft"
    description: "Item core properties defined - type, stats, base mechanics"
    color: "#FFCC00"
    order: 2
    locks:
      - field: "procedural_stats"
        reason: "Procedural generation details added during testing"
      - field: "crafting_recipe"
        reason: "Crafting requires complete recipe definition"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
    allows:
      - "transit_to:testing"
      - "transit_to:rejected"

  - id: "testing"
    name: "Testing"
    description: "Item mechanics validated - damage, defense, effects, usage"
    color: "#FF9900"
    order: 3
    locks:
      - field: "rarity"
        reason: "Rarity based on test results"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
      - "base_stats"
      - "usage_properties"
      - "effects"
      - "testing_results"
    allows:
      - "transit_to:balancing"
      - "transit_to:draft"

  - id: "balancing"
    name: "Balancing"
    description: "Values tuned for game balance - damage, defense, rarity adjustments"
    color: "#FF6600"
    order: 4
    locks:
      - field: "base_price"
        reason: "Price set during balance"
      - field: "value"
        reason: "Value tied to rarity and stats"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
      - "base_stats"
      - "usage_properties"
      - "effects"
      - "balancing_notes"
      - "balance_calculation"
      - "sensitivity_analysis"
    allows:
      - "transit_to:review"
      - "transit_to:testing"

  - id: "review"
    name: "Review"
    description: "Internal review - game balance, lore integration, design consistency"
    color: "#0066FF"
    order: 5
    locks:
      - field: "producer_notes"
        reason: "Notes preserved for audit trail"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
      - "base_stats"
      - "usage_properties"
      - "effects"
      - "balancing_notes"
      - "balance_calculation"
      - "sensitivity_analysis"
      - "producer_notes"
      - "reviews_complete"
    allows:
      - "transit_to:approval"
      - "transit_to:balancing"

  - id: "approval"
    name: "Approval"
    description: "Producer/design lead approval - final verification before deployment"
    color: "#0099FF"
    order: 6
    locks:
      - field: "producer_notes"
        reason: "Notes preserved for audit trail"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
      - "base_stats"
      - "usage_properties"
      - "effects"
      - "balancing_notes"
      - "balance_calculation"
      - "sensitivity_analysis"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
    allows:
      - "transit_to:published"
      - "transit_to:review"

  - id: "published"
    name: "Published"
    description: "Item live in game - can be looted, crafted, purchased, equipped"
    color: "#00CC00"
    order: 7
    locks:
      - field: "item_type"
        reason: "Core identity - cannot change item type"
      - field: "rarity"
        reason: "World state consistency"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
      - "base_stats"
      - "usage_properties"
      - "effects"
      - "balancing_notes"
      - "balance_calculation"
      - "sensitivity_analysis"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
    allows:
      - "transit_to:active"
      - "transit_to:archived"

  - id: "active"
    name: "Active"
    description: "Item fully integrated - spawn locations defined, vendor pricing set"
    color: "#00FF00"
    order: 8
    locks:
      - field: "item_type"
        reason: "World state consistency"
      - field: "rarity"
        reason: "World state consistency"
      - field: "drop_sources"
        reason: "Drop tables are world state"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
      - "base_stats"
      - "usage_properties"
      - "effects"
      - "balancing_notes"
      - "balance_calculation"
      - "sensitivity_analysis"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "deployment_date"
      - "spawn_locations"
      - "vendor_pricing"
      - "drop_sources"
    allows:
      - "transit_to:deprecated"
      - "transit_to:deleted"

  - id: "deprecated"
    name: "Deprecated"
    description: "Item removed from active play but preserved for history"
    color: "#999999"
    order: 9
    locks:
      - field: "item_type"
        reason: "Historical accuracy preserved"
      - field: "rarity"
        reason: "Historical accuracy preserved"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
      - "base_stats"
      - "usage_properties"
      - "effects"
      - "balancing_notes"
      - "balance_calculation"
      - "sensitivity_analysis"
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
    description: "Item permanently preserved - historical reference only"
    color: "#666666"
    order: 10
    locks:
      - all_fields: true
        reason: "Historical archive - no modifications"
    requires:
      - "name"
      - "description"
      - "item_id"
      - "item_type"
      - "category"
      - "rarity"
      - "value"
      - "weight"
      - "tags"
      - "base_stats"
      - "usage_properties"
      - "effects"
      - "balancing_notes"
      - "balance_calculation"
      - "sensitivity_analysis"
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
    description: "Item removed permanently - recoverable only from backups"
    color: "#FF0000"
    order: 11
    requires:
      - "name"
      - "item_id"
      - "deletion_reason"
      - "deleted_by"
      - "deletion_date"
    allows: []

  - id: "rejected"
    name: "Rejected"
    description: "Item rejected feedback - requires revision before resubmission"
    color: "#FF6600"
    order: 12
    locks:
      - field: "feedback_notes"
        reason: "Feedback preserved for revision"
    requires:
      - "name"
      - "item_id"
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
        condition: "all_required_fields_filled(['name', 'description', 'item_id', 'item_type', 'category'])"
    permissions:
      roles: ["game_designer", "producer", "artist"]
    notifications:
      on_execute:
        - type: "print"
          message: "Item concept approved for {{item_id}}"

  - from: "draft"
    to: "testing"
    triggers:
      - type: "manual"
    permissions:
      roles: ["game_designer", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Item {{item_id}} entered testing phase"

  - from: "testing"
    to: "balancing"
    triggers:
      - type: "auto"
        condition: "all_tests_passed AND_all_effects_validated"
    permissions:
      roles: ["game_designer", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Item {{item_id}} entered balancing phase"

  - from: "balancing"
    to: "review"
    triggers:
      - type: "auto"
        condition: "sensitivity_analysis_complete AND_balance_report_final"
    permissions:
      roles: ["game_designer", "producer", "balance_master"]
    notifications:
      on_execute:
        - type: "print"
          message: "Item {{item_id}} balancing complete, ready for review"

  - from: "review"
    to: "approval"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "producer_notes_filled AND_reviews_complete"
    permissions:
      roles: ["producer", "design_lead", "balance_master"]
    notifications:
      on_execute:
        - type: "print"
          message: "Item {{item_id}} entered approval stage"

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
          message: "Item {{item_id}} deployed to game"

  - from: "published"
    to: "active"
    triggers:
      - type: "auto"
        condition: "spawn_locations_defined AND_vendor_pricing_set"
    permissions:
      roles: ["producer", "game_designer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Item {{item_id}} is now active"

  - from: "active"
    to: "deprecated"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "item_usage_reached_zero AND_30_days_inactive"
    permissions:
      roles: ["producer", "balance_master"]
    notifications:
      on_execute:
        - type: "print"
          message: "Item {{item_id}} deprecated"

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
          message: "Item {{item_id}} archived"

# TRANSITION VALIDATION RULES
validation_rules:
  - id: "item_wf_001"
    category: "core_identity"
    rule: "Item ID must remain consistent across all stages"
    validation_type: "error"
    applies_to: ["concept", "draft", "testing", "balancing", "review", "approval", "published", "active", "deprecated", "archived", "deleted", "rejected"]

  - id: "item_wf_002"
    category: "item_type_consistency"
    rule: "Item type must be valid enum value (weapon, consumable, key_item, material, collectible, cosmetic, currency)"
    validation_type: "error"
    applies_to: ["draft", "testing", "balancing", "review", "approval", "published", "active", "deprecated", "archived"]

  - id: "item_wf_003"
    category: "rarity_consistency"
    rule: "Rarity must match item_type category standards"
    validation_type: "warning"
    applies_to: ["draft", "testing", "balancing"]

  - id: "item_wf_004"
    category: "fallback_required"
    rule: "Weapons must have fallback damage value defined before active"
    validation_type: "error"
    applies_to: ["review", "approval", "published", "active", "deprecated", "archived"]

  - id: "item_wf_005"
    category: "consumable_balance"
    rule: "Consumables must have duration and cooldown defined before active"
    validation_type: "error"
    applies_to: ["review", "approval", "published", "active", "deprecated", "archived"]

  - id: "item_wf_006"
    category: "key_item_uniqueness"
    rule: "Key items must not be tradeable or storable"
    validation_type: "error"
    applies_to: ["draft", "testing", "balancing", "review", "approval", "published", "active", "deprecated", "archived"]

  - id: "item_wf_007"
    category: "base_price_validation"
    rule: "Base price must be positive integer before active"
    validation_type: "error"
    applies_to: ["review", "approval", "published", "active", "deprecated", "archived"]

  - id: "item_wf_008"
    category: "lore_integration"
    rule: "Lore significant items require lore master approval"
    validation_type: "warning"
    applies_to: ["approval", "published", "active", "deprecated", "archived"]

  - id: "item_wf_009"
    category: "spawn_location_valid"
    rule: "Spawn locations must reference existing location entities"
    validation_type: "error"
    applies_to: ["active", "deprecated", "archived"]

  - id: "item_wf_010"
    category: "identifier_consistency"
    rule: "Item ID must match folder name exactly"
    validation_type: "error"
    applies_to: ["draft", "testing", "balancing", "review", "approval", "published", "active", "deprecated", "archived", "deleted", "rejected"]

  - id: "item_wf_011"
    category: "crafting_valid"
    rule: "Crafting recipe must reference valid item IDs"
    validation_type: "error"
    applies_to: ["testing", "balancing", "review", "approval", "published", "active", "deprecated", "archived"]

# META-FIELDS for workflow tracking
meta_fields:
  workflow_version: "1.0"
  workflow_name: "item_workflow"
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
    balance_master_approval: "boolean"
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
      - "Initial item workflow definition"
      - "12 stages: concept -> draft -> testing -> balancing -> review -> approval -> published -> active -> deprecated -> archived, plus deleted and rejected"
      - "Explicit transition definitions with triggers and permissions"
      - "Validation rules for core identity, item type consistency, rarity, fallbacks, consumables, key items, pricing, lore, spawn locations, crafting"
    breaking_changes: []

# EXAMPLES
examples:
  standard_item:
    item_id: "item_neural_sword_mk2"
    stages:
      - stage: "concept"
        days: 1
        notes: "Initial idea - advanced melee weapon with neural damage"
      - stage: "draft"
        days: 3
        notes: "Added item_type, category, rarity, base_stats, effects"
      - stage: "testing"
        days: 5
        notes: "Added testing_results for damage, defense, effects"
      - stage: "balancing"
        days: 7
        notes: "Added balancing_notes, balance_calculation, sensitivity_analysis"
      - stage: "review"
        days: 3
        notes: "Producer notes recorded"
      - stage: "approval"
        days: 1
        notes: "Producer and lore approval granted"
      - stage: "published"
        days: 0
        notes: "Deployed to game"
      - stage: "active"
        days: 0
        notes: "Fully integrated with spawn locations and vendors"

  weapon_revision:
    item_id: "item_shotgun_reaper"
    stages:
      - stage: "concept"
        days: 2
      - stage: "draft"
        days: 4
      - stage: "testing"
        days: 6
        notes: "Feedback: Damage too high for range"
      - stage: "balancing"
        days: 8
        notes: "Revision: Adjusted damage and added range modifiers"
      - stage: "review"
        days: 3
      - stage: "approval"
        days: 1
      - stage: "published"
        days: 0

  crafting_recipe_item:
    item_id: "item_energy_cell_advanced"
    stages:
      - stage: "concept"
        days: 1
        notes: "Initial idea - advanced power cell for energy weapons"
      - stage: "draft"
        days: 3
        notes: "Added item_type=material, crafting_station=workbench"
      - stage: "testing"
        days: 5
        notes: "Added crafting_recipe with required_items"
      - stage: "balancing"
        days: 5
        notes: "Added value, crafting_time, yield"
      - stage: "review"
        days: 2
      - stage: "approval"
        days: 1
      - stage: "published"
        days: 0

---
# Item Workflow in Practice

## For Game Designers

1. **Concept Stage**: Start with item idea - name, basic purpose, visual concept
2. **Draft Stage**: Define core properties - type, stats, rarity, value
3. **Testing Stage**: Validate mechanics - damage, defense, effects, usage
4. **Balancing Stage**: Tune values for game balance
5. **Review Stage**: Get feedback - balance, lore integration
6. **Approval Stage**: Get producer approval - final verification
7. **Published Stage**: Item is live in game
8. **Active Stage**: Fully integrated with spawn locations and vendors

## For Artists

- Create visual concepts during concept stage
- Review balance during testing stage
- No direct involvement required after published

## For Producers

- Approve transitions from approval -> published
- Monitor stage durations for workflow efficiency
- Archive deprecated items after 7 days

## Common Workflows

### New Item Creation (Standard)
```
concept -> draft -> testing -> balancing -> review -> approval -> published -> active
```

### New Item Creation (Crafting)
```
concept -> draft -> testing (add crafting_recipe) -> balancing -> review -> approval -> published -> active
```

### Item Revision
```
active -> testing (adjust stats) -> balancing -> review -> approval -> published -> active
```

### Item Deprecation
```
active -> deprecated -> archived
```

### Item Deletion (Emergency)
```
active -> deleted (permanent, recoverable only from backup)
```

## Workflow Metrics

Track these metrics for workflow health:
- Average days per stage
- Re-work rate (transitions back to earlier stages)
- Approval time by producer
- Balance changes between stages

## Rarity Guidelines

| Rarity | Value Range | Item Type Examples |
|--------|-------------|-------------------|
| Common | 10-100 | Basic weapons, consumables |
| Uncommon | 100-500 | Better weapons, tools |
| Rare | 500-1000 | High-end weapons, rare materials |
| Epic | 1000-5000 | Legendary weapons, special items |
| Legendary | 5000+ | Unique items, story-critical |
| Unique | Custom | One-of-a-kind items |
