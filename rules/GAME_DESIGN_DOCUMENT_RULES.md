---
system_prompt: >-
  Generate a game design document for the project's chosen medium. Describe
  what players do, how the systems respond, and how the team can test the design.
  Preserve existing decisions and identify unresolved choices.
global: false
priority: high
entity_type: game_design_document
template_reference: GAME_DESIGN_DOCUMENT_TEMPLATE.md

rules:
- id: game_design_document_001
  category: gameplay
  priority: high
  rule: Connect core_loop_description to player_goals, observable feedback, and the applicable victory_conditions or failure_conditions.
  validation_type: warning
  applies_to: [game_design_document]

- id: game_design_document_002
  category: mechanics
  priority: high
  rule: Keep core_systems, interaction_model, and progression_system consistent with the medium and explain how one player action changes the game state.
  validation_type: warning
  applies_to: [game_design_document]

- id: game_design_document_003
  category: planning
  priority: medium
  rule: Pair material risks with mitigations and keep target_platforms and engine_requirements consistent with the project's confirmed scope.
  validation_type: warning
  applies_to: [game_design_document]
---

# Game design document rules

Use prototyping_notes to identify a small test of the core loop and describe
what a designer should observe. Separate that first playable slice from later
features so readers can see which decisions depend on the test.

Describe technical, schedule, and market risks in their respective fields.
Leave platform targets, multiplayer, or monetization open when the project has
yet to decide them.
