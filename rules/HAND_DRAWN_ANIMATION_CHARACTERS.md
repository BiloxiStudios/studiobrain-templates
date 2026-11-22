---
system_prompt: 'Design this character for traditional 2D hand-drawn animation. In text, describe the body as shapes an artist can repeat (one head shape, one body shape, three or four costume pieces) and show personality through poses and actions, not inner monologue. For images and video: clean confident outlines of even or gently tapered weight, flat colour fills with one shadow tone and at most one highlight tone, a palette of four to six colours, simple hands, a face built for broad readable expressions, squash and stretch in motion, soft painted backgrounds behind the figure. No photographic texture, no skin pores or fabric weave, no 3D render shading.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: anim2d_char_shapes
  category: design
  priority: high
  rule: Name the head shape and the body shape (circle, pear, rectangle, triangle) and keep every later description on those shapes.
  validation_type: warning
- id: anim2d_char_palette
  category: design
  priority: high
  rule: List four to six flat colours for the character, each tied to a named part such as hair, skin, top, or shoes.
  validation_type: warning
- id: anim2d_char_costume
  category: design
  priority: medium
  rule: 'Limit the costume to pieces that can be redrawn quickly: no fine patterns, lace, chain mail, or small repeated details.'
  validation_type: warning
- id: anim2d_char_expression
  category: design
  priority: medium
  rule: Describe one signature expression and one signature pose that show the personality without dialogue.
  validation_type: suggestion
- id: anim2d_char_no_realism
  category: consistency
  priority: medium
  rule: Leave out photographic detail such as pores, wrinkles, realistic hair strands, and cloth texture.
  validation_type: suggestion
---

# Hand-Drawn Animation Characters

Characters for traditional 2D animation: clean outlines, flat colour, shapes an artist can redraw a thousand times.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
