---
system_prompt: "Generate image prompts for this project. Match the art style, lighting, and palette the project records. For characters, include front, three-quarter left, and three-quarter right portraits when the template asks for them."
global: false
priority: medium
entity_type: image
rules:
- id: img_001
  category: style
  priority: high
  rule: "Images must match the art style this project records."
  validation_type: warning
  applies_to:
  - image
- id: img_002
  category: lighting
  priority: high
  rule: "Lighting must match the lighting this project records."
  validation_type: warning
  applies_to:
  - image
- id: img_003
  category: colors
  priority: high
  rule: "Colors must match the palette this project records."
  validation_type: warning
  applies_to:
  - image
- id: img_004
  category: character
  priority: critical
  rule: 'Characters require: front facing, 3/4 left, 3/4 right portraits'
  validation_type: error
  applies_to:
  - character
  - image
created_by: System
last_updated: '2025-01-11'
version: '1.0'
---

# Image guidance

Match the art style, lighting, and palette recorded on this project. Do not apply a style the project has not chosen.

When the request is a character, produce the angles the template asks for: front, three-quarter left, and three-quarter right. Full-body and action views follow the same style guide.

Name the subject's existing details. Do not invent a costume, a skyline, or a color grade from another world.
