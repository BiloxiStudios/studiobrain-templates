---
system_prompt: >-
  Design a quest with a clear reason to act, achievable objectives, and observable outcomes. Use the project's references and make prerequisites, branching choices, and rewards fit the intended progression.
global: false
priority: high
entity_type: quest
template_reference: QUEST_TEMPLATE.md
rules:
  - id: quest_001
    category: objectives
    priority: high
    rule: >-
      Give primary_objectives observable completion criteria and distinguish secondary_objectives from actions required for completion. Make failure_conditions consistent with any alternatives or time_limit.
    validation_type: warning
    applies_to: [quest]
  - id: quest_002
    category: prerequisites
    priority: high
    rule: >-
      Use prerequisite_quests, required_skills, and required_items that the player can obtain before starting. Avoid cycles among prerequisite quests, and keep required_level and estimated_time consistent with the challenge.
    validation_type: warning
    applies_to: [quest]
  - id: quest_003
    category: references
    priority: high
    rule: >-
      Link the quest giver, characters, factions, and locations to existing project references. Make travel from starting_location to quest_locations and destination_location consistent with travel_requirements.
    validation_type: warning
    applies_to: [quest]
  - id: quest_004
    category: outcomes
    priority: medium
    rule: >-
      Link choice_consequences to listed player_choices and give alternative_solutions a clear requirement. Keep promised rewards and story_consequences consistent with the completion path that earns them.
    validation_type: warning
    applies_to: [quest]
---

# Quest generation rules

Describe the quest's stakes, then give each required objective a visible sign
of completion. Mark optional tasks clearly and check that prerequisite quests,
items, and skills can be obtained before the player starts.

Use project references for quest givers and destinations. For alternative
solutions, explain the requirement and result of each route. Tie rewards and
failure consequences to the outcomes that trigger them.
