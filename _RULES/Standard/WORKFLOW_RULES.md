---
# WORKFLOW RULES
# Defines the workflow state machine system for StudioBrain templates
# Each entity type can define its own workflow with stages and transitions
# This file contains both the system definition and examples
---
# WORKFLOW SYSTEM OVERVIEW

## Purpose
Workflows enable configurable status state machines per entity template type. This allows different entity types to have different production pipelines while maintaining consistent validation and tracking.

## Key Components

### WorkflowDefinition
Top-level workflow configuration associated with a template type.

### WorkflowStage
A single state in the workflow (e.g., "concept", "draft", "review", "published").

### WorkflowTransition
 Defines how to move between stages, with validation rules and required fields.

### WorkflowTrigger
Events that can trigger transitions (manually, automatically, on meeting conditions).

## Example Workflow Types

### Game Quest Workflow
```
Concept -> Scripted -> Balanced -> QA -> Ship
```
Used for: quests, missions, levels

### Recipe/ Menu Workflow
```
Draft -> Tested -> Published
```
Used for: recipes, menu items, crafted items

### Film/TV Scene Workflow
```
Blocked -> Shooting -> Post -> Final
```
Used for: scenes, episodes, sequences

### Plant/Garden Workflow
```
Seedling -> Growing -> Harvest -> Stored
```
Used for: plants, crops, organisms

### General Content Workflow
```
Draft -> Review -> Approved -> Published -> Archived
```
Used for: documentation, articles, generic content

## Workflow Stage Properties

```yaml
workflow:
  name: "quest_workflow"
  stages:
    - id: "concept"
      name: "Concept"
      description: "Initial idea and basic concept"
      color: "#CCCCCC"
      order: 1
      locks:
        - field: "detailed_description"
          reason: "Details added in Narrative phase"
      requires:
        - "name"
        - "template_type"
      allows:
        - "transit_to:scripted"
    - id: "scripted"
      name: "Scripted"
      description: "Full narrative and script complete"
      color: "#FFCC00"
      order: 2
      locks: []
      requires:
        - "name"
        - "narrative"
        - "dialogue"
      allows:
        - "transit_to:balanced"
    - id: "balanced"
      name: "Balanced"
      description: "Values and mechanics tuned"
      color: "#00CCFF"
      order: 3
      locks: []
      requires:
        - "name"
        - "narrative"
        - "dialogue"
        - "rewards"
        - "difficulty"
      allows:
        - "transit_to:qa"
    - id: "qa"
      name: "QA"
      description: "Testing and bug fixing"
      color: "#0066FF"
      order: 4
      locks: []
      requires:
        - "name"
        - "narrative"
        - "dialogue"
        - "rewards"
        - "difficulty"
        - "testing_notes"
      allows:
        - "transit_to:ship"
    - id: "ship"
      name: "Ship"
      description: "Released to players"
      color: "#00AA00"
      order: 5
      locks:
        - field: "difficulty"
          reason: "Final value, only hotfixes allowed"
        - field: "rewards"
          reason: "Final value, only hotfixes allowed"
      requires:
        - "name"
        - "narrative"
        - "dialogue"
        - "rewards"
        - "difficulty"
        - "testing_notes"
        - "release_notes"
      allows: []
```

## Transition Validation Rules

Each transition can specify:
- Required fields that must be present
- Fields that must be locked (read-only) after transition
- Conditions that must be met (e.g., "all objectives completed")
- Notifications to send
- Roles that can approve

## Workflow Trigger Types

1. **Manual**: User initiates transition via UI
2. **Auto-On-Complete**: Transition fires when all required conditions met
3. **Schedule**: Transition fires at specific time/date
4. **Condition-Based**: Transition fires when all specified fields达到 threshold

## Template Integration

Add workflow reference to template frontmatter:

```yaml
# CHARACTER_TEMPLATE.md frontmatter
workflow:
  definition: "CHARACTER_WORKFLOW.md"
  default_stage: "draft"
  allow_multiple_active: false  # Only one stage active at a time
  notifications:
    on_enter: ["team-alerts"]
    on_exit: ["archive-notifications"]
    on_complete: ["production-complete"]
```

## Workflow File Naming Convention

- `ENTITYTYPE_WORKFLOW.md` (e.g., CHARACTER_WORKFLOW.md, QUEST_WORKFLOW.md)
- Templates in `templates/Standard/` have corresponding workflow files in `rules/`
- Optional: `ENTITYTYPE_WORKFLOW_[VARIANT].md` for variants (e.g., CHARACTER_WORKFLOW npc.md)

## Versioning

Include version in workflow definition:

```yaml
workflow:
  version: "1.0"
  name: "quest_workflow"
  last_updated: "2024-03-30"
  breaking_changes: []
  deprecated_stages: []
```

## Cross-Workflow References

For shared stages/transitions:

```yaml
# Use a shared workflow stage by reference
workflow:
  stages:
    - include: "WORKFLOWS_SHARED/common_stages.yml"
    - id: "custom_phase"
      name: "Custom Phase"
      # ... custom definition
```

## Workflow Assignment

Assign workflow to entity type in template:

```yaml
# In CHARACTER_TEMPLATE.md
workflow_definition: "CHARACTER_WORKFLOW.md"

# In quest documentation
workflow_definition: "QUEST_WORKFLOW.md"
```

## Default Workflows by Entity Type

| Entity Type | Default Workflow | Stages |
|-------------|-----------------|--------|
| Character | CHARACTER_WORKFLOW | draft -> active -> retired |
| Location | LOCATION_WORKFLOW | concept -> drafted -> reviewed -> published |
| Item | ITEM_WORKFLOW | draft -> tested -> published |
| Quest | QUEST_WORKFLOW | concept -> scripted -> balanced -> qa -> ship |
| Dialogue | DIALOGUE_WORKFLOW | draft -> reviewed -> finalized |
|Assembly | ASSEMBLY_WORKFLOW | component -> assembled -> tested -> released |
|Timeline | TIMELINE_WORKFLOW | pending -> scheduled -> active -> archived |
| Univer se | UNIVERSE_WORKFLOW | concept -> planned ->展开 -> maintained |
| Faction | FACTION_WORKFLOW | concept -> organized -> established -> active |
| Story | STORY_WORKFLOW | outline -> draft -> reviewed -> published |

## Validation Tools

When a workflow transition is attempted, validate:

1. User has permission for source and target stages
2. All required fields for target stage are present
3. No locked fields are being modified
4. Transition conditions are met
5. Any required external dependencies exist

## Notifications System

```yaml
workflow:
  notifications:
    on_enter:
      - type: "email"
        to: ["producer@studio.com"]
        template: "stage_entered"
        context: ["entity_name", "source_stage", "target_stage"]
      - type: "slack"
        channel: "#production-alerts"
        message: "Entity {{entity_name}} entered stage {{target_stage}}"
    on_exit:
      - type: "archive"
        target: "stage_history/{{entity_type}}/{{entity_id}}/{{stage_id}}"
    on_complete:
      - type: "webhook"
        url: "https://hooks.production.com/workflow/complete"
        method: "POST"
        body: "{{entity_json}}"
```

## Schema Reference

```yaml
# Full workflow definition schema
workflow:
  version: "string"  #_semver
  name: "string"     # unique identifier
  label: "string"    # human-readable name
  description: "string"  # what this workflow represents
  default_stage: "string"  # initial stage
  allow_multiple_active: "boolean"  # can entity be in multiple stages?
  lock_entity_on_transition: "boolean"  # lock during transition
  stages:
    - id: "string"           # unique within workflow
      name: "string"         # display name
      description: "string"  # what this stage means
      color: "string"        # hex color for UI
      order: "number"        # sort order
      locks:                 # fields that cannot be modified
        - field: "string"    # field path
          reason: "string"   # why it's locked
      requires:              # fields that must be present
        - "field_name"
        - "nested.field.name"
      allows:                # transitions available from this stage
        - "transit_to:target_stage_id"
        - "transit_to:another_stage_id"
      triggers:              # automatic triggers
        - type: "auto"
          conditions:
            - field: "field_name"
              operator: "gt"
              value: 100
          target_stage: "next_stage"
      notifications:         # on-enter notifications
        - type: "email"
          to: ["list@example.com"]
  transitions:               # global transition definitions
    - from: "stage_a"
      to: "stage_b"
      requires:             # additional requirements for this transition
        - "field_a"
      permissions:
        roles: ["producer", "editor"]
        teams: ["production"]  # optional teams that can approve
    - from: "stage_b"
      to: "stage_c"
      # ...
  metadata:
    last_updated: "YYYY-MM-DD"
    owner: "team_name"
    version_history:
      - version: "1.0"
        date: "YYYY-MM-DD"
        changes: ["Initial version"]
```

## Version History

- v1.0 (2024-03-30): Initial workflow system definition

---
# ENTITY-SPECIFIC WORKFLOWS

## Character Workflow Example

Used for: Characters, NPCs, player characters

### Stages
1. **Concept** - Character idea, background sketch
2. **Draft** - Character requirements and stats defined
3. **Refinement** - Dialogue and personality fleshed out
4. **Approval** - Internal review and approvals
5. **Published** - Live in game/system
6. **Retired** - Removed or archived

### Transitions
- Concept -> Draft: Add character_stats, skills, faction
- Draft -> Refinement: Add dialogue_samples, personality
- Refinement -> Approval: Complete all required assets
- Approval -> Published: Final review and deployment
- Published -> Retired: Archive assets and documentation

---

## Location Workflow Example

Used for: Locations, districts, buildings, points of interest

### Stages
1. **Concept** - Basic location idea and purpose
2. **Drafting** - Location details and metadata added
3. **Layout** - Spatial layout and zoning defined
4. **Review** - Internal review and feedback
5. **Finalizing** - Final polish and asset integration
6. **Published** - Live in world
7. **Deprecated** - Archived or removed

### Transitions
- Concept -> Drafting: Add location_type, category, district
- Drafting -> Layout: Add coordinates, interior_zones, entry_points
- Layout -> Review: Complete description and atmosphere
- Review -> Finalizing: Add final assets and validation
- Finalizing -> Published: Production deployment
- Published -> Deprecated: Archive with notes

---

## Item Workflow Example

Used for: Items, weapons, consumables, equipment

### Stages
1. **Concept** - Item idea and basic purpose
2. **Draft** - Item properties and stats defined
3. **Testing** - Item mechanics validated
4. **Balancing** - Values tuned for game balance
5. **Review** - Design review and feedback
6. **Final** - Final approval and integration
7. **Published** - Live in game
8. **Archived** - Deprecated item

### Transitions
- Concept -> Draft: Add item_type, rarity, base_stats
- Draft -> Testing: Add crafting_recipe, uses, effects
- Testing -> Balancing: Complete all stat tuning
- Balancing -> Review: Final metadata and documentation
- Review -> Final: Production approval
- Final -> Published:Deploy to game
- Published -> Archived: Remove from active use

---

## Quest Workflow Example

Used for: Quests, missions, objectives

### Stages
1. **Concept** - Quest idea and basic structure
2. **Scripting** - Full narrative and dialogue written
3. **Balancing** - Rewards, difficulty, requirements tuned
4. **QA** - Testing and validation
5. **Publish-ready** - Final polish and deployment
6. **Published** - Live for players
7. **Archived** - Historical record

### Transitions
- Concept -> Scripting: Add primary_objectives, description
- Scripting -> Balancing: Add experience_reward, currency_reward
- Balancing -> QA: Add testing_notes, validation checklist
- QA -> Publish-ready: Final review and sign-off
- Publish-ready -> Published: Deploy to world
- Published -> Archived: Archive with version note

---

## Dialogue Workflow Example

Used for: Dialogue trees, conversations, NPC interactions

### Stages
1. **Draft** - Initial dialogue content
2. **Branching** - All branches and options added
3. **Testing** - All paths validated
4. **Final** - Final polish and integration
5. **Published** - Live in game
6. **Archived** - Historical record

### Transitions
- Draft -> Branching: Add all decision branches
- Branching -> Testing: Validate all paths
- Testing -> Final: Final review
- Final -> Published: Deploy
- Published -> Archived: Archive

---

## Assembly Workflow Example

Used for: Assemblies, component combinations, recipes

### Stages
1. **Design** - Assembly design and component list
2. **Component-Gathering** - Source all required components
3. **Prototyping** - Test assembly mechanics
4. **Validation** - Validate design requirements
5. **Production** - Finalize for production
6. **Published** - Live for use
7. **Retired** - Archived

### Transitions
- Design -> Component-Gathering: Add all required_components
- Component-Gathering -> Prototyping: Add test_results
- Prototyping -> Validation: Complete validation checklist
- Validation -> Production: Production approval
- Production -> Published: Deploy
- Published -> Retired: Archive with notes

---

## Timeline Workflow Example

Used for: Timelines, schedules, event sequences

### Stages
1. **Pending** - Timeline idea only
2. **Scheduling** - Events added and ordered
3. **Validation** - Temporal consistency checked
4. **Review** - Internal review
5. **Active** - Timeline running
6. **Completed** - All events completed
7. **Archived** - Historical record

### Transitions
- Pending -> Scheduling: Add all timeline_events
- Scheduling -> Validation: Temporal validation
- Validation -> Review: Review and feedback
- Review -> Active: Activate timeline
- Active -> Completed: All events finish
- Completed -> Archived: Archive

---

## Universe Workflow Example

Used for: universes, worlds, dimension settings

### Stages
1. **Concept** - Universe concept and theme
2. **Planning** - Universe parameters defined
3. **World-Building** - Geography, lore, factions added
4. **Content-Creation** - Entities and assets added
5. **Testing** - Universe mechanics validated
6. **Review** - Internal review
7. **Published** - Active universe
8. **Archived** - Historical record

### Transitions
- Concept -> Planning: Add universe_parameters
- Planning -> World-Building: Add lore, geography
- World-Building -> Content-Creation: Add initial content
- Content-Creation -> Testing: Validate mechanics
- Testing -> Review: Review and feedback
- Review -> Published: Activate universe
- Published -> Archived: Archive

---

## Faction Workflow Example

Used for: Factions, organizations, groups

### Stages
1. **Concept** - Faction idea and purpose
2. **Organization** - Structure and leadership defined
3. **Establishment** - Base, resources, members added
4. **Active** - Faction active in world
5. **Dominant** - Faction has major influence
6. **Archived** - Historical record

### Transitions
- Concept -> Organization: Add faction_structure, leadership
- Organization -> Establishment: Add base, resources
- Establishment -> Active: Add members, activities
- Active -> Dominant: Add major influence events
- Dominant -> Archived: Archive with final status

---

## Story Workflow Example

Used for: Stories, narratives, arcs

### Stages
1. **Outline** - Story structure and plot points
2. **Draft** - Full narrative written
3. **Review** - Feedback and revisions
4. **Final** - Final polish
5. **Published** - Live for readers
6. **Archived** - Historical record

### Transitions
- Outline -> Draft: Add full narrative content
- Draft -> Review: Add revision_history
- Review -> Final: Final approval
- Final -> Published: Publish story
- Published -> Archived: Archive

---

# IMPLEMENTATION NOTES

## For Template Creators

1. Create workflow file in `rules/` named `ENTITYTYPE_WORKFLOW.md`
2. Add `workflow_definition` field to template frontmatter
3. Reference workflow file in template metadata
4. Follow naming conventions for stages and transitions

## For AI Generation

When generating entities:
1. Load workflow definition for entity type
2. Default to default_stage
3. Validate that generated content can enter the stage
4. Respect stage locks and requirements
5. Only allow valid transitions

## For validators

When validating entities:
1. Load entity's current workflow and stage
2. Load workflow definition
3. Check that current stage is valid
4. Verify all required fields for current stage are present
5. Check that no locked fields have been modified
6. Confirm all transition conditions are met

## For Notifications

When workflow triggers notifications:
1. Determine notification type (on_enter, on_exit, on_complete)
2. Load notification configuration for transition
3. Render notification template with context
4. Send to all configured destinations
5. Log notification event for audit trail

---

# CHANGELOG

## 2024-03-30 (v1.0)
- Initial workflow system definition
- Added entity-specific workflow examples
- Defined validation and notification systems

---
# FAQ

## Q: Can an entity be in multiple stages simultaneously?
A: By default, no. Set `allow_multiple_active: true` in workflow definition to enable.

## Q: How do I rename a stage?
A: Create a new stage, migrate existing entities, deprecate old stage in metadata.

## Q: Can I remove a stage?
A: Archive entities in that stage first, then add to deprecated_stages in metadata.

## Q: What happens when a workflow is updated?
A: Existing entities keep their current workflow version. New entities use latest.

## Q: Can I create custom workflows for specific projects?
A: Yes, place in `rules/Custom/` or template-specific folder.
