---
system_prompt: 'This character is a regular in a multi-camera sitcom. In text, build them on one comic flaw that causes problems every episode, one thing they always want, and a fixed relationship to each other regular (rival, crush, parent, boss). They do not grow much: each story ends near where it began. Write dialogue as short set-ups and punchlines. For images and video: bright, even, high-key studio lighting with soft shadows, eye-level medium shots, saturated everyday wardrobe with one consistent colour per character so they are easy to tell apart in a wide shot, clean hair and make-up, standing or sitting in a three-walled studio set.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: sitcom_char_flaw
  category: design
  priority: high
  rule: State one comic flaw in a single phrase, and show how it starts trouble.
  validation_type: warning
- id: sitcom_char_want
  category: design
  priority: medium
  rule: State the one thing the character always wants and never fully gets.
  validation_type: suggestion
- id: sitcom_char_relationships
  category: consistency
  priority: high
  rule: Define the character's relationship to each other regular in the project in one line each.
  validation_type: warning
- id: sitcom_char_wardrobe_colour
  category: design
  priority: medium
  rule: Give the character a signature wardrobe colour or garment type that differs from the rest of the cast.
  validation_type: suggestion
- id: sitcom_char_voice
  category: design
  priority: medium
  rule: Include three sample lines that sound different from every other regular.
  validation_type: suggestion
- id: sitcom_char_status_quo
  category: tone
  priority: low
  rule: Avoid permanent changes such as deaths, moves, or cures for the comic flaw unless the project records them.
  validation_type: suggestion
---

# Sitcom Characters

Cast members for a multi-camera sitcom: one comic flaw, one want, and relationships that never fully resolve.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
