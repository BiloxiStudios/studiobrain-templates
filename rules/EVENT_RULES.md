---
system_prompt: >-
  Design an event with a clear trigger, scope, progression, and consequences. Match its timing, affected entities, and outcomes to the project's established state.
global: false
priority: high
entity_type: event
template_reference: EVENT_TEMPLATE.md
rules:
  - id: event_001
    category: trigger
    priority: high
    rule: >-
      Make trigger_conditions meaningful for trigger_type. Use trigger_probability for a random event, schedule times for a scheduled event, and recurrence_pattern only when recurring is enabled.
    validation_type: warning
    applies_to: [event]
  - id: event_002
    category: timing
    priority: high
    rule: >-
      When both start_time and end_time are present, put the end after the start. Order event_phases in the sequence they occur and reconcile their durations with the event's stated duration.
    validation_type: warning
    applies_to: [event]
  - id: event_003
    category: scope
    priority: high
    rule: >-
      Keep affected locations, characters, and factions within event_scope. Resolve related_campaigns, related_quests, and named affected entities against existing project references.
    validation_type: warning
    applies_to: [event]
  - id: event_004
    category: outcomes
    priority: medium
    rule: >-
      Link choice_consequences to listed player_choices and make rewards and failure consequences consistent with player_participation. State how long each temporary world, character, or location change lasts.
    validation_type: warning
    applies_to: [event]
---

# Event generation rules

Explain what starts the event and, if it recurs, what defines each occurrence.
List its phases in order and reconcile their durations with the start and end
times when those are set.

Identify the affected people, locations, and factions using project references
and check that they fit the event's scope. Connect any player choices to
effects the player can observe, and say which changes expire and which remain.
