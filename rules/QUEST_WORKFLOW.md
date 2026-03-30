---
version: "1.0"
name: "quest_workflow"
label: "Quest Production Workflow"
description: "Status progression for quests from concept to archived"
last_updated: "2026-03-30"
default_stage: "concept"
allow_multiple_active: false
notifications:
  on_enter:
    - type: "print"
      message: "Quest {{quest_id}} entered stage {{stage_name}}"
  on_exit:
    - type: "archive"
      target: "stage_history/quests/{{quest_id}}/{{old_stage}}"
  on_complete:
    - type: "print"
      message: "Quest {{quest_id}} completed {{stage_name}}"

# STAGES: Quest lifecycle progression
stages:
  - id: "concept"
    name: "Concept"
    description: "Initial quest idea, core objective, and basic structure"
    color: "#CCCCCC"
    order: 1
    locks:
      - field: "primary_objectives"
        reason: "Objectives defined during scripting"
      - field: "quest_giver"
        reason: "Quest giver assigned during scripting"
      - field: "reward_structure"
        reason: "Rewards determined during balancing"
    requires:
      - "name"
      - "template_type"
      - "quest_id"
    allows:
      - "transit_to:scripting"

  - id: "scripting"
    name: "Scripting"
    description: "Full narrative and quest flow - objectives, dialogues, conditions"
    color: "#FFCC00"
    order: 2
    locks:
      - field: "quest_giver"
        reason: "Quest giver finalized before balancing"
      - field: "completion_criteria"
        reason: "Completion criteria need full context"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
    allows:
      - "transit_to:balancing"
      - "transit_to:rejected"

  - id: "balancing"
    name: "Balancing"
    description: "Quest mechanics tuned - rewards, difficulty, requirements"
    color: "#FF9900"
    order: 3
    locks:
      - field: "experience_reward"
        reason: "Experience based on difficulty analysis"
      - field: "currency_reward"
        reason: "Currency based on难度 and player level"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
      - "difficulty"
      - "estimated_time"
      - "required_level"
      - "experience_reward"
      - "currency_reward"
      - "reputation_changes"
    allows:
      - "transit_to:qa"
      - "transit_to:scripting"

  - id: "qa"
    name: "QA"
    description: "Testing and validation - quest flow, dialogue, bugs, conditions"
    color: "#0066FF"
    order: 4
    locks:
      - field: "testing_notes"
        reason: "Testing notes preserved for audit"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
      - "difficulty"
      - "estimated_time"
      - "required_level"
      - "experience_reward"
      - "currency_reward"
      - "reputation_changes"
      - "testing_notes"
      - "test_results"
      - "blocking_bugs_resolved"
    allows:
      - "transit_to:final_review"
      - "transit_to:balancing"

  - id: "final_review"
    name: "Final Review"
    description: "Internal review - narrative consistency, world integration, quality"
    color: "#0099FF"
    order: 5
    locks:
      - field: "producer_notes"
        reason: "Notes preserved for audit trail"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
      - "difficulty"
      - "estimated_time"
      - "required_level"
      - "experience_reward"
      - "currency_reward"
      - "reputation_changes"
      - "testing_notes"
      - "test_results"
      - "blocking_bugs_resolved"
      - "producer_notes"
      - "reviews_complete"
    allows:
      - "transit_to:approval"
      - "transit_to:qa"

  - id: "approval"
    name: "Approval"
    description: "Producer/design lead approval - final verification before deployment"
    color: "#00CCFF"
    order: 6
    locks:
      - field: "producer_notes"
        reason: "Notes preserved for audit trail"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
      - "difficulty"
      - "estimated_time"
      - "required_level"
      - "experience_reward"
      - "currency_reward"
      - "reputation_changes"
      - "testing_notes"
      - "test_results"
      - "blocking_bugs_resolved"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "design_approved"
    allows:
      - "transit_to:published"
      - "transit_to:final_review"

  - id: "published"
    name: "Published"
    description: "Quest live in world - players can accept, track, and complete"
    color: "#00AA00"
    order: 7
    locks:
      - field: "quest_type"
        reason: "Core identity - cannot change quest type"
      - field: "quest_giver"
        reason: "World state consistency"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
      - "difficulty"
      - "estimated_time"
      - "required_level"
      - "experience_reward"
      - "currency_reward"
      - "reputation_changes"
      - "testing_notes"
      - "test_results"
      - "blocking_bugs_resolved"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "design_approved"
      - "deployment_date"
    allows:
      - "transit_to:active"
      - "transit_to:archived"

  - id: "active"
    name: "Active"
    description: "Quest fully integrated - NPCs assigned, location tracking, reward distribution"
    color: "#00FF00"
    order: 8
    locks:
      - field: "quest_type"
        reason: "World state consistency"
      - field: "quest_giver"
        reason: "World state consistency"
      - field: "trace_locations"
        reason: "Trace locations are world state"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
      - "difficulty"
      - "estimated_time"
      - "required_level"
      - "experience_reward"
      - "currency_reward"
      - "reputation_changes"
      - "testing_notes"
      - "test_results"
      - "blocking_bugs_resolved"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "design_approved"
      - "deployment_date"
      - "trace_locations"
      - "npcs_assigned"
      - "reward_distribution_setup"
    allows:
      - "transit_to:deprecated"
      - "transit_to:deleted"

  - id: "deprecated"
    name: "Deprecated"
    description: "Quest removed from active play but preserved for history"
    color: "#999999"
    order: 9
    locks:
      - field: "quest_type"
        reason: "Historical accuracy preserved"
      - field: "quest_giver"
        reason: "Historical accuracy preserved"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
      - "difficulty"
      - "estimated_time"
      - "required_level"
      - "experience_reward"
      - "currency_reward"
      - "reputation_changes"
      - "testing_notes"
      - "test_results"
      - "blocking_bugs_resolved"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "design_approved"
      - "deployment_date"
      - "deprecation_date"
      - "deprecation_reason"
      - "player_completion_count"
    allows:
      - "transit_to:archived"
      - "transit_to:active"

  - id: "archived"
    name: "Archived"
    description: "Quest permanently preserved - historical reference only"
    color: "#666666"
    order: 10
    locks:
      - all_fields: true
        reason: "Historical archive - no modifications"
    requires:
      - "name"
      - "description"
      - "quest_id"
      - "quest_type"
      - "quest_category"
      - "primary_objectives"
      - "quest_giver"
      - "dialogue_trees"
      - "narrative_context"
      - "difficulty"
      - "estimated_time"
      - "required_level"
      - "experience_reward"
      - "currency_reward"
      - "reputation_changes"
      - "testing_notes"
      - "test_results"
      - "blocking_bugs_resolved"
      - "producer_notes"
      - "producer_approval"
      - "lore_approved"
      - "design_approved"
      - "deployment_date"
      - "deprecation_date"
      - "deprecation_reason"
      - "player_completion_count"
      - "archive_date"
    allows: []

  - id: "deleted"
    name: "Deleted"
    description: "Quest removed permanently - recoverable only from backups"
    color: "#FF0000"
    order: 11
    requires:
      - "name"
      - "quest_id"
      - "deletion_reason"
      - "deleted_by"
      - "deletion_date"
    allows: []

  - id: "rejected"
    name: "Rejected"
    description: "Quest rejected feedback - requires revision before resubmission"
    color: "#FF6600"
    order: 12
    locks:
      - field: "feedback_notes"
        reason: "Feedback preserved for revision"
    requires:
      - "name"
      - "quest_id"
      - "rejection_reason"
      - "feedback_notes"
    allows:
      - "transit_to:scripting"
      - "transit_to:concept"

# TRANSITIONS: Explicit transition definitions with requirements and permissions
transitions:
  - from: "concept"
    to: "scripting"
    triggers:
      - type: "auto"
        condition: "all_required_fields_filled(['name', 'description', 'quest_id', 'quest_type', 'primary_objectives'])"
    permissions:
      roles: ["quest_designer", "writer", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Quest concept approved for {{quest_id}}"

  - from: "scripting"
    to: "balancing"
    triggers:
      - type: "manual"
    permissions:
      roles: ["quest_designer", "writer", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Quest {{quest_id}} entered balancing phase"

  - from: "balancing"
    to: "qa"
    triggers:
      - type: "auto"
        condition: "all_rewards_defined AND_required_levels_set"
    permissions:
      roles: ["quest_designer", "producer", "balance_master"]
    notifications:
      on_execute:
        - type: "print"
          message: "Quest {{quest_id}} balancing complete, ready for QA"

  - from: "qa"
    to: "final_review"
    triggers:
      - type: "auto"
        condition: "blocking_bugs_resolved AND_all_path_validated"
    permissions:
      roles: ["quest_designer", "qa_lead", "producer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Quest {{quest_id}} QA complete, ready for review"

  - from: "final_review"
    to: "approval"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "producer_notes_filled AND_reviews_complete"
    permissions:
      roles: ["producer", "design_lead", "quest_lead"]
    notifications:
      on_execute:
        - type: "print"
          message: "Quest {{quest_id}} entered approval stage"

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
          message: "Quest {{quest_id}} deployed to world"

  - from: "published"
    to: "active"
    triggers:
      - type: "auto"
        condition: "quest_giver_assigned AND_trace_locations_set"
    permissions:
      roles: ["producer", "quest_designer"]
    notifications:
      on_execute:
        - type: "print"
          message: "Quest {{quest_id}} is now active"

  - from: "active"
    to: "deprecated"
    triggers:
      - type: "manual"
      - type: "auto"
        condition: "player_completion_count_zero AND_30_days_inactive"
    permissions:
      roles: ["producer", "quest_lead"]
    notifications:
      on_execute:
        - type: "print"
          message: "Quest {{quest_id}} deprecated"

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
          message: "Quest {{quest_id}} archived"

# TRANSITION VALIDATION RULES
validation_rules:
  - id: "quest_wf_001"
    category: "core_identity"
    rule: "Quest ID must remain consistent across all stages"
    validation_type: "error"
    applies_to: ["concept", "scripting", "balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived", "deleted", "rejected"]

  - id: "quest_wf_002"
    category: "quest_type_valid"
    rule: "Quest type must be valid enum (side, main, daily, weekly, event, tutorial)"
    validation_type: "error"
    applies_to: ["scripting", "balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

  - id: "quest_wf_003"
    category: "quest_giver_exists"
    rule: "Quest giver must reference existing character ID"
    validation_type: "error"
    applies_to: ["scripting", "balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

  - id: "quest_wf_004"
    category: "primary_objectives_required"
    rule: "At least one primary objective must be defined before QA"
    validation_type: "error"
    applies_to: ["balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

  - id: "quest_wf_005"
    category: "dialogue_valid"
    rule: "Dialogue trees must reference valid dialogue IDs"
    validation_type: "error"
    applies_to: ["scripting", "balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

  - id: "quest_wf_006"
    category: "reward_consistency"
    rule: "Experience reward must be proportional to difficulty and estimated_time"
    validation_type: "warning"
    applies_to: ["balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

  - id: "quest_wf_007"
    category: "reputation_changes"
    rule: "All factions in reputation_changes must exist"
    validation_type: "error"
    applies_to: ["balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

  - id: "quest_wf_008"
    category: "trace_locations_valid"
    rule: "Trace locations must reference existing location IDs"
    validation_type: "error"
    applies_to: ["active", "deprecated", "archived"]

  - id: "quest_wf_009"
    category: "level_scaling"
    rule: "Required level must be positive integer before active"
    validation_type: "error"
    applies_to: ["qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

  - id: "quest_wf_010"
    category: "identifier_consistency"
    rule: "Quest ID must match folder name exactly"
    validation_type: "error"
    applies_to: ["scripting", "balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived", "deleted", "rejected"]

  - id: "quest_wf_011"
    category: "prerequisites_valid"
    rule: "All prerequisite quests must exist"
    validation_type: "error"
    applies_to: ["scripting", "balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

  - id: "quest_wf_012"
    category: "completion_criteria_valid"
    rule: "Completion criteria must be achievable within quest scope"
    validation_type: "warning"
    applies_to: ["scripting", "balancing", "qa", "final_review", "approval", "published", "active", "deprecated", "archived"]

# META-FIELDS for workflow tracking
meta_fields:
  workflow_version: "1.0"
  workflow_name: "quest_workflow"
  last_stage_update: "timestamp"
  stage_transitions:
    - stage: "concept"
      entered: "timestamp"
      exited: "timestamp"
      duration_seconds: "number"
    - stage: "scripting"
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
      - "Initial quest workflow definition"
      - "12 stages: concept -> scripting -> balancing -> qa -> final_review -> approval -> published -> active -> deprecated -> archived, plus deleted and rejected"
      - "Explicit transition definitions with triggers and permissions"
      - "Validation rules for core identity, quest type, quest giver, objectives, dialogue, rewards, reputation, trace locations, level scaling, prerequisites, completion criteria"
    breaking_changes: []

# EXAMPLES
examples:
  standard_quest:
    quest_id: "quest_find_the_circuitshack_erd"
    stages:
      - stage: "concept"
        days: 1
        notes: "Initial idea - find missing CircuitShack employee"
      - stage: "scripting"
        days: 5
        notes: "Added quest_type, dialogue_trees, narrative_context"
      - stage: "balancing"
        days: 3
        notes: "Added difficulty, estimated_time, experience_reward"
      - stage: "qa"
        days: 4
        notes: "Added testing_notes, test_results"
      - stage: "final_review"
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
        notes: "Fully integrated with quest giver and trace locations"

  major_quest_revision:
    quest_id: "quest_double_dip_origin"
    stages:
      - stage: "concept"
        days: 2
      - stage: "scripting"
        days: 8
        notes: "Expanded for major story beat"
      - stage: "balancing"
        days: 4
        notes: "Adjusted rewards and difficulty for major quest"
      - stage: "qa"
        days: 6
        notes: "Feedback: Quest flow needs adjustment"
      - stage: "scripting"
        days: 5
        notes: "Revision: Adjusted dialogue flow and objectives"
      - stage: "balancing"
        days: 3
      - stage: "qa"
        days: 5
      - stage: "final_review"
        days: 2
      - stage: "approval"
        days: 1
      - stage: "published"
        days: 0

  side_quest_to_main_quest:
    quest_id: "quest_faction_nexus"
    stages:
      - stage: "concept"
        days: 1
        notes: "Initial as side quest for faction relationship"
      - stage: "scripting"
        days: 3
      - stage: "balancing"
        days: 2
      - stage: "qa"
        days: 3
      - stage: "published"
        days: 7
        notes: "Deployed as side quest for testing"
      - stage: "active"
        days: 14
        notes: "Player feedback indicates potential as main quest"
      - stage: "scripting"
        days: 10
        notes: "Revision: Expanded to main quest with branching"
      - stage: "balancing"
        days: 5
        notes: "Adjusted rewards for main quest status"
      - stage: "qa"
        days: 7
      - stage: "final_review"
        days: 3
      - stage: "approval"
        days: 1
      - stage: "published"
        days: 0
        notes: "Promoted to main quest"

---
# Quest Workflow in Practice

## For Quest Designers

1. **Concept Stage**: Start with quest idea - name, core objective, basic structure
2. **Scripting Stage**: Write full narrative - objectives, dialogues, conditions
3. **Balancing Stage**: Tune mechanics - rewards, difficulty, requirements
4. **QA Stage**: Test and validate - quest flow,-dialogue, bugs, conditions
5. **Final Review Stage**: Get feedback - narrative consistency, world integration
6. **Approval Stage**: Get producer approval - final verification
7. **Published Stage**: Quest is live in world
8. **Active Stage**: Fully integrated with quest givers and tracking

## For Producers

- Approve transitions from approval -> published
- Monitor stage durations for workflow efficiency
- Archive deprecated quests after 7 days
- Track quest completion rates

## For Writers

- Create dialogue trees during scripting stage
- Write narrative context during scripting stage
- No direct involvement required after published

## Common Workflows

### New Side Quest
```
concept -> scripting -> balancing -> qa -> final_review -> approval -> published -> active
```

### Main Quest
```
concept -> scripting (expanded scope) -> balancing (higher rewards) -> qa -> final_review -> approval -> published -> active
```

### Quest Revision
```
active -> scripting (adjust objectives) -> balancing -> qa -> final_review -> approval -> published -> active
```

### Quest Deprecation
```
active -> deprecated -> archived
```

### Quest Deletion (Emergency)
```
active -> deleted (permanent, recoverable only from backup)
```

### Side Quest to Main Quest
```
published (as side) -> active -> scripting (expand) -> balancing -> qa -> approval -> published (as main)
```

## Workflow Metrics

Track these metrics for workflow health:
- Average days per stage
- Re-work rate (transitions back to earlier stages)
- Approval time by producer
- Quest completion rates by stage
- Stage transition types (manual vs auto)

## Quality Gates

### Scripting Completion Checklist
- [ ] All primary objectives defined
- [ ] All dialogue trees complete
- [ ] Narrative context written
- [ ] Quest giver assigned
- [ ] Branching paths designed

### Balancing Completion Checklist
- [ ] Reward structure approved
- [ ] Difficulty curve validated
- [ ] Level scaling correct
- [ ] Reputation changes set
- [ ] Estimated time accurate

### QA Completion Checklist
- [ ] All paths tested
- [ ] All blocking bugs fixed
- [ ] All NPCs present
- [ ] All locations accessible

## Quest Type Notes

**Side Quests**: Smaller scope, simpler rewards, one-time completion
**Main Quests**: Larger scope, significant rewards, may have multiple stages
**Daily Quests**: Repeatable, daily reset, modest rewards
**Weekly Quests**: Repeatable, weekly reset, better rewards
**Event Quests**: Time-limited, special rewards
**Tutorial Quests**: Progressive difficulty, comprehensive guidance
