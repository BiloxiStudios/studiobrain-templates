---
system_prompt: This character is designed for animation. Aim for a shape a viewer can recognise in silhouette, a palette of three to five colours, and a personality that can be read from pose alone. Describe exaggerated proportions and a signature expression or gesture. Keep details few enough to draw the character many times.
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: toon_silhouette
  category: design
  priority: high
  rule: Describe a silhouette built from one or two dominant shapes that is distinct from other characters in the project.
  validation_type: warning
- id: toon_palette
  category: design
  priority: medium
  rule: Limit the character to three to five main colours and name them.
  validation_type: warning
- id: toon_hook
  category: personality
  priority: high
  rule: Give one clear personality hook and a signature pose, expression, or catchphrase that shows it.
  validation_type: warning
- id: toon_simplicity
  category: design
  priority: medium
  rule: 'Avoid fine detail that would be hard to redraw: small patterns, many accessories, or complex textures.'
  validation_type: suggestion
- id: toon_expression_range
  category: design
  priority: low
  rule: List three expressions that are pushed further than realism would allow.
  validation_type: suggestion
---

# Animated Cartoon Characters

Characters built for animation: readable silhouette, limited palette, one clear personality hook.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
