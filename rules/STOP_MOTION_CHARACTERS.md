---
system_prompt: 'Design this character as a physical puppet for stop-motion animation. In text, say what the puppet is made of (modelling clay, felt, silicone over a wire frame, wood, knitted wool), how tall it is in centimetres, and how its face changes expression. For images and video: a handmade miniature figure with visible fingerprints, tool marks, or stitching, slightly oversized head and hands, simple bead or painted eyes, real fabric at miniature scale with a coarse weave, real light on a real object with soft shadows, shallow depth of field from a macro lens, slightly uneven movement at twelve frames a second. No smooth computer-generated surfaces and no motion blur.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: stopmo_char_material
  category: design
  priority: high
  rule: Name the materials of the body, hair, and clothes.
  validation_type: warning
- id: stopmo_char_handmade
  category: design
  priority: high
  rule: 'Describe at least one visible sign of being handmade: fingerprints, seams, brush strokes, or uneven edges.'
  validation_type: warning
- id: stopmo_char_face
  category: design
  priority: medium
  rule: 'Say how expressions are made: swapped mouth shapes, sculpted clay, or moving brows.'
  validation_type: suggestion
- id: stopmo_char_buildable
  category: consistency
  priority: medium
  rule: 'Keep the design something a model maker could build and pose: no floating parts, flowing liquid hair, or glowing effects without a stated practical method.'
  validation_type: warning
- id: stopmo_char_scale
  category: design
  priority: low
  rule: State the puppet height and keep props in proportion to it.
  validation_type: suggestion
---

# Stop-Motion Characters

Puppet characters for stop-motion and claymation: handmade materials, simple faces, visible touch of the maker.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
