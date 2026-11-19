---
system_prompt: "Generate dialogue for this project. Use the format [emotion] \"spoken text\" *action/gesture*. Match each speaker's voice and the project's recorded era, technology, and tone. Do not import slang or devices from another setting."
global: false
priority: high
entity_type: dialogue
template_reference: CHARACTER_TEMPLATE.md

rules:
- id: dial_001
  category: structure
  priority: critical
  rule: All dialogue must follow the format - [emotion] "spoken text" *action/gesture*
  validation_type: error
  applies_to: [dialogue, character]

- id: dial_002
  category: timeline
  priority: critical
  rule: "Dialogue must use the speech and technology this project allows. forbidden_phrases and allowed_phrases are empty in the starter so the project can fill them. Do not ban a phrase the project has not banned."
  validation_type: error
  applies_to: [dialogue]
  forbidden_phrases: []
  allowed_phrases: []
- id: dial_003
  category: relationships
  priority: high
  rule: Dialogue tone must match relationship status and faction dynamics
  validation_type: warning
  applies_to: [dialogue, character]

- id: dial_004
  category: personality
  priority: medium
  rule: Speech patterns must reflect character traits, background, and faction culture
  validation_type: warning
  applies_to: [dialogue, character]

- id: dial_005
  category: infection
  priority: high
  rule: "If this project records a condition that changes speech, the dialogue must show that condition at the stage the project records. Do not add a condition the project has not recorded."
  validation_type: warning
  applies_to: [dialogue, character]

- id: dial_006
  category: humor
  priority: high
  rule: "When this project uses humor, it must come from the situation. Do not add a joke style the project has not recorded."
  validation_type: warning
  applies_to: [dialogue]

- id: dial_007
  category: corporate
  priority: medium
  rule: "When a character speaks for an organisation, the wording must match the voice this project records for that organisation."
  validation_type: info
  applies_to: [dialogue, character]

- id: dial_008
  category: environmental
  priority: medium
  rule: "When dialogue mentions the surroundings, it must match conditions this project has recorded."
  validation_type: info
  applies_to: [dialogue]

- id: dial_009
  category: voice_acting
  priority: medium
  rule: Include emotional delivery notes for ElevenLabs AI voice generation
  validation_type: info
  applies_to: [dialogue]

- id: dial_010
  category: jingles
  priority: medium
  rule: "A brand's slogan must match that brand as this project records it. Do not add a mood the brand does not have."
  validation_type: info
  applies_to: [dialogue, brand]
---

# Dialogue guidance

These rules check structure and consistency. They do not name a setting.

Write each line as [emotion] "spoken text" *action/gesture*. Speech must match the speaker, the relationship, and the voice of any faction or brand involved. Technology and slang must be ones this project allows. The starter's forbidden_phrases and allowed_phrases lists are empty so the project can fill them.

If the project records a condition that changes speech, show the stage it records. Do not add a condition, a joke style, or a slogan mood the project has not recorded.

Include an emotional delivery note when a voice performance needs one.
