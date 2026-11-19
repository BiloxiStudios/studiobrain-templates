---
system_prompt: >-
  Generate a style bible that translates the project's chosen art direction
  into reproducible guidance for its medium and platforms. Keep examples,
  technical targets, and accessibility options grounded in project decisions.
global: false
priority: high
entity_type: style_bible
template_reference: STYLE_BIBLE_TEMPLATE.md

rules:
- id: style_bible_001
  category: art_direction
  priority: high
  rule: Keep lighting_philosophy, material_types, and recurring_motifs consistent with art_direction, rendering_style, and the recorded palette.
  validation_type: warning
  applies_to: [style_bible]

- id: style_bible_002
  category: performance
  priority: medium
  rule: Align texture_resolution, polygon_budget, and effect_quality with target_platform and performance_target where those fields apply.
  validation_type: warning
  applies_to: [style_bible]

- id: style_bible_003
  category: accessibility
  priority: high
  rule: Document how contrast_options, motion_reduction, and subtitle_styling affect the relevant interface, camera, or effects guidance.
  validation_type: warning
  applies_to: [style_bible]
---

# Style bible rules

Use visual_examples to show how a collaborator can apply the selected palette,
lighting, and shape language to a new asset. Describe which choices carry
across platforms and where a platform adaptation is needed.

Keep typography, icons, and UI colors consistent with the project’s visual
hierarchy. Use implementation_notes to explain how reduced-motion and
high-contrast alternatives preserve the same cues.
