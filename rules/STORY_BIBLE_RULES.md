---
system_prompt: >-
  Generate a story bible for the project's medium, audience, and established
  setting. Connect the central conflict to character choices and consequences,
  and keep continuity across the synopsis and individual arcs.
global: false
priority: high
entity_type: story_bible
template_reference: STORY_BIBLE_TEMPLATE.md

rules:
- id: story_bible_001
  category: narrative
  priority: high
  rule: Keep logline, premise, main_arc, and the chosen synopsis beats aligned around the same central conflict and stakes.
  validation_type: warning
  applies_to: [story_bible]

- id: story_bible_002
  category: continuity
  priority: high
  rule: Tie each character_arcs transformation to events or choices in the story and use the same character and location names throughout.
  validation_type: warning
  applies_to: [story_bible]

- id: story_bible_003
  category: structure
  priority: medium
  rule: Keep endings consistent with branching_strategy and player_agency_level where those fields apply. Make the consequences of branch choices explicit.
  validation_type: warning
  applies_to: [story_bible]
---

# Story bible rules

Use themes and motifs to connect repeat appearances to story events. Check
that resolutions follow from choices and pressures established earlier in the
synopsis, including for any sub_arcs included in the draft.

Keep dialogue_samples consistent with narrative_voice and tone_guidelines.
Preserve the project's recorded time_period and locations when adding detail.
