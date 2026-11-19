---
system_prompt: >-
  Generate a color guide for the project's medium and existing art direction.
  Give swatches distinct roles, document how they combine, and distinguish
  measured accessibility results from proposed checks.
global: false
priority: high
entity_type: color_guide
template_reference: COLOR_GUIDE_TEMPLATE.md

rules:
- id: color_guide_001
  category: palette
  priority: high
  rule: Where a swatch has both hex and rgb values, keep them equivalent and give it a usage that distinguishes its role.
  validation_type: warning
  applies_to: [color_guide]

- id: color_guide_002
  category: accessibility
  priority: high
  rule: Assess each documented text and background pairing against contrast_minimum_ratio. Record unsuitable pairs and the reason in inaccessible_pairs.
  validation_type: warning
  applies_to: [color_guide]

- id: color_guide_003
  category: accessibility
  priority: medium
  rule: Mark colorblind_tested only when the applicable modes have been checked. Capture findings and mitigations in colorblind_simulation_notes and known_issues.
  validation_type: warning
  applies_to: [color_guide]
---

# Color guide rules

Group primary, secondary, and neutral colors by how they are used. Connect
component_application to named swatches so the examples can be reproduced.

When defining success, warning, error, and info colors, pair color with a label
or icon so the states remain distinguishable without hue. Review the actual
foreground and background combinations, including any dark or high-contrast
variants the project uses.
