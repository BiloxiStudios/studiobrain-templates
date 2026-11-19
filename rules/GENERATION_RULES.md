---
rules:
- id: gen_000
  category: generation
  priority: high
  rule: "Stay consistent with the entities, history, and tone this project has already recorded."
  validation_type: warning
  applies_to:
  - all
- id: gen_001
  category: generation
  priority: high
  rule: Use entity cross-references to build cohesive narrative connections
  validation_type: warning
  applies_to:
  - all
- id: gen_002
  category: generation
  priority: high
  rule: Respect character personality traits and established relationships
  validation_type: warning
  applies_to:
  - all
- id: gen_003
  category: generation
  priority: high
  rule: Incorporate location atmosphere and brand presence into content
  validation_type: warning
  applies_to:
  - all
- id: gen_004
  category: generation
  priority: high
  rule: Follow established naming conventions and ID patterns
  validation_type: warning
  applies_to:
  - all
- id: gen_005
  category: generation
  priority: high
  rule: Include specific details that enhance immersion and believability
  validation_type: warning
  applies_to:
  - all
- id: gen_006
  category: generation
  priority: high
  rule: Balance humor and seriousness according to context and entity types
  validation_type: warning
  applies_to:
  - all
- id: gen_007
  category: generation
  priority: high
  rule: "Era, technology, and institutions must match the timeline this project records."
  validation_type: warning
  applies_to:
  - all
- id: gen_008
  category: generation
  priority: high
  rule: Use markdown formatting for structured, parseable content
  validation_type: warning
  applies_to:
  - all
- id: gen_009
  category: generation
  priority: high
  rule: Include relevant cross-references to related entities when appropriate
  validation_type: warning
  applies_to:
  - all
- id: gen_010
  category: timeline_validation
  priority: high
  rule: When creating or editing entities with temporal data (birth_year, age, founded_year,
    key_events, etc.), use the available timeline validation tools (check_temporal_conflicts,
    validate_character_age, calculate_duration) to verify temporal consistency and detect
    anachronisms before finalizing content
  validation_type: warning
  applies_to:
  - all

- id: gen_011
  category: entity_validation
  priority: critical
  rule: Before referencing any entity (character, location, brand, item, faction, district)
    in generated content, use entity validation tools to verify it exists in the database.
    Use check_character_exists, check_location_exists, check_brand_exists, check_item_exists,
    or validate_all_references to prevent hallucinating non-existent entities
  validation_type: error
  applies_to:
  - all
  required_tools: ["check_character_exists", "check_location_exists", "check_brand_exists",
    "check_item_exists", "validate_all_references"]

- id: gen_012
  category: knowledge_gathering
  priority: high
  rule: Use knowledge base search tools to gather context before generating content.
    Use search_knowledge_base for semantic search, get_entity to retrieve specific
    entities, search_entities to find entities of a type, and find_similar_entities
    for relationship discovery. Rich context produces better, more integrated content
  validation_type: warning
  applies_to:
  - all
  required_tools: ["search_knowledge_base", "get_entity", "search_entities", "find_similar_entities"]

- id: gen_013
  category: content_editing
  priority: high
  rule: When editing markdown files (Fusion Wizard, refinement), use markdown editing
    tools to make changes directly. Call read_temp_file_section BEFORE editing to
    see current content, then call edit_temp_file_section to apply changes. Do not
    just describe changes - execute them using the tools
  validation_type: warning
  applies_to:
  - all
  required_tools: ["read_temp_file_section", "edit_temp_file_section", "list_temp_file_sections"]

created_by: System
last_updated: '2025-11-14'
version: '1.2'
scope: global
system_prompt: "You are generating content for this project. Follow these rules and stay consistent with entities this project has already recorded. Do not import another setting. Before you name any entity, verify it exists. Check ages and dates against the project's present year. Read related entities before you write. When editing, change the file with the editing tools instead of only describing the change."
global: true
priority: high
---

# Generation guidance

These rules apply to every entity type in this project. They do not name a setting.

Stay inside entities, dates, and tone the project has recorded. Cross-references must point at entities that exist. Check ages and dates against the project's present year before finishing. Read related entities before writing new ones. When editing, change the file with the editing tools instead of only describing the change.

Match the era the project records. Do not import another decade's devices or institutions. Use the type's own rules file for anything that type adds.
