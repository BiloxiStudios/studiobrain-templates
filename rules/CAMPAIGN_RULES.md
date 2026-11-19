---
system_prompt: >-
  Design a campaign with clear objectives, an ordered progression, and a resolution that follows from the project's themes and stakes. Connect its quests, events, locations, and characters through the template fields.
global: false
priority: high
entity_type: campaign
template_reference: CAMPAIGN_TEMPLATE.md
rules:
  - id: campaign_001
    category: progression
    priority: high
    rule: >-
      Order quest_sequence so prerequisites can be met before dependent quests. Keep optional_quests separate from required progression, and make chapter_count and estimated_duration consistent with the proposed scope.
    validation_type: warning
    applies_to: [campaign]
  - id: campaign_002
    category: narrative
    priority: high
    rule: >-
      Connect main_objectives to the narrative_summary and show how later chapters follow from earlier outcomes. Describe the branches or conclusions that justify branching_paths and multiple_endings when enabled.
    validation_type: warning
    applies_to: [campaign]
  - id: campaign_003
    category: references
    priority: high
    rule: >-
      Use project references for named quests, events, factions, characters, and locations. Set starting_location to the place where the opening objective begins when that location is known.
    validation_type: warning
    applies_to: [campaign]
  - id: campaign_004
    category: availability
    priority: medium
    rule: >-
      When the campaign has seasonal availability, keep start_date before end_date and consistent with related events. Choose repeatable and reward values that fit the intended progression.
    validation_type: warning
    applies_to: [campaign]
---

# Campaign generation rules

Order the required quests so players can meet each prerequisite. Give optional
quests their own list, and choose a chapter count and duration that reflect
the main sequence. Connect the opening objective to the starting location.

Describe how the objectives raise the stakes. If there are branches or
multiple endings, explain the choices that lead to them and their consequences.
Use existing project references for quests, events, people, and places, and
check the campaign dates against any related events.
