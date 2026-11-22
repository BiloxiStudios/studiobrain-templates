---
system_prompt: 'This character belongs in a sports story. State the sport, their position or event, their level (school, amateur, professional), and their record so far. Give them one strength and one weakness in how they play, a reason they compete, and a rival or a teammate who pushes them. Use the sport''s real rules, positions, and terms correctly. In visual descriptions use an athletic build suited to the sport, team kit with a number and team colours, sweat, tape, and worn equipment, stadium floodlights or training-ground daylight, and frozen moments of peak action.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: sports_char_position
  category: design
  priority: high
  rule: State the sport, the position or event, and the level of competition.
  validation_type: warning
- id: sports_char_strength_weakness
  category: balance
  priority: high
  rule: State one strength and one weakness in how the character plays.
  validation_type: warning
- id: sports_char_why
  category: design
  priority: medium
  rule: State what the character is playing for beyond winning.
  validation_type: suggestion
- id: sports_char_rival
  category: design
  priority: medium
  rule: Name a rival or teammate from the project and what the contest between them is about.
  validation_type: suggestion
- id: sports_char_accuracy
  category: consistency
  priority: high
  rule: Use the sport's real rules, scoring, and terms, and a body type that fits the position.
  validation_type: warning
---

# Sports Characters

Athletes, coaches and rivals: a position, a strength, a weakness in their game, and what they play for.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
