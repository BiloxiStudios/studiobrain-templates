---
system_prompt: 'Design this character for a 3D computer-animated feature film. In text, give stylised proportions as ratios (head to body, eye size, hand size), one clear shape idea for the whole figure, and the materials each part is made of. For images and video: stylised anatomy with large expressive eyes and simplified features, smooth sculpted forms, believable materials (soft skin with light passing through the ears and fingers, groomed hair or fur in clumps, stitched cloth with a visible weave), warm key light with a coloured rim light, soft bounced fill, shallow depth of field, a saturated but controlled palette. Keep the face clearly stylised, never a near-photographic human.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: cg_char_proportions
  category: design
  priority: high
  rule: 'State the proportions as numbers: how many heads tall, and which features are enlarged or reduced.'
  validation_type: warning
- id: cg_char_shape_idea
  category: design
  priority: high
  rule: Give one shape idea for the whole figure, such as round and soft, tall and angular, or top-heavy.
  validation_type: warning
- id: cg_char_materials
  category: design
  priority: medium
  rule: Name the material of skin, hair or fur, and each main costume piece, including how worn or new it is.
  validation_type: suggestion
- id: cg_char_stylised_face
  category: consistency
  priority: high
  rule: Keep the face stylised. Do not describe photographic human skin, realistic teeth, or true-to-life eye size.
  validation_type: warning
- id: cg_char_acting
  category: design
  priority: low
  rule: 'Describe how the character moves: weight, speed, and one habitual gesture an animator can use.'
  validation_type: suggestion
---

# 3D Animated Feature Characters

Stylised 3D characters for an animated feature: appealing proportions, rich materials, cinematic light.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
