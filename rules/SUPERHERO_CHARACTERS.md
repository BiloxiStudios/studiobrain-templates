---
system_prompt: 'This character is a superhero or supervillain. Give one clear power set with a source, a limit, and a weakness that an opponent could use. Give a costume with a two or three colour scheme and one emblem, and a private life that the powers make harder. A villain needs a goal that makes sense from their side. In visual descriptions use bold primary or strongly contrasting colours, an athletic heroic stance, a clear emblem on the chest or back, and dramatic low camera angles. Keep the power level in line with other powered characters in the project, and make every name, power, and costume original.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: super_char_power_set
  category: design
  priority: high
  rule: State the power set in one sentence and where it comes from.
  validation_type: warning
- id: super_char_weakness
  category: balance
  priority: high
  rule: State a limit on the power and a weakness that can be exploited.
  validation_type: warning
- id: super_char_costume
  category: design
  priority: medium
  rule: Describe a costume with two or three colours and one emblem.
  validation_type: suggestion
- id: super_char_private_life
  category: design
  priority: medium
  rule: Describe the life outside the costume and one way the powers damage it.
  validation_type: suggestion
- id: super_char_power_scale
  category: consistency
  priority: high
  rule: Keep the power level consistent with other powered characters the project records.
  validation_type: warning
- id: super_char_original
  category: consistency
  priority: high
  rule: Do not reuse the name, costume, or exact power set of an existing published hero or villain.
  validation_type: warning
---

# Superhero Characters

Heroes and villains with powers: one clear power set, a real weakness, a costume and a life behind the mask.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
