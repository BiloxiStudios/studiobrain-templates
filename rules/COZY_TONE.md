---
system_prompt: Write in a cozy tone. Stakes are personal and small. Favour warmth, food, weather, craft, and community. Conflict is misunderstanding or inconvenience, never cruelty. Leave out graphic violence, horror, and despair.
global: false
priority: medium
ruleset_kind: theme
rules:
- id: cozy_stakes
  category: tone
  priority: high
  rule: Keep stakes personal and local. Nothing threatens a life or the world.
  validation_type: warning
- id: cozy_no_grim
  category: tone
  priority: high
  rule: Leave out graphic violence, gore, horror, and cruelty.
  validation_type: warning
- id: cozy_comforts
  category: tone
  priority: medium
  rule: 'Include at least one sensory comfort: a meal, a warm room, a familiar sound.'
  validation_type: suggestion
- id: cozy_kindness
  category: tone
  priority: low
  rule: Show one small act of kindness or a connection between people.
  validation_type: suggestion
---

# Cozy Tone

A gentle, low-stakes tone for any entity type: warmth, small problems, no grim content.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick any entity type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
