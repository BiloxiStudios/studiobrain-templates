---
system_prompt: 'This location is a standing set for a multi-camera sitcom, built with three walls and open on the fourth side toward the cameras and audience. In text, state the entrances and where each leads, the central piece of furniture scenes play around (sofa, kitchen island, bar, desk), and which characters treat the place as home. For images and video: seen straight on from the open side at eye level, bright even studio lighting with no deep shadows, warm saturated set dressing, everything important visible in one wide shot, furniture angled toward the camera, a backdrop visible through any window. The layout never changes between episodes.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: sitcom_set_three_walls
  category: design
  priority: high
  rule: 'Describe the set from one open side: left wall, back wall, right wall. Do not describe a fourth wall.'
  validation_type: warning
- id: sitcom_set_entrances
  category: design
  priority: high
  rule: List every door, stair, or archway and say where it leads.
  validation_type: warning
- id: sitcom_set_anchor
  category: design
  priority: medium
  rule: Name the central furniture piece that most scenes are played around.
  validation_type: warning
- id: sitcom_set_fixed_layout
  category: consistency
  priority: high
  rule: Keep the layout identical to any earlier description of this set in the project.
  validation_type: warning
- id: sitcom_set_owner
  category: lore
  priority: low
  rule: Say whose place it is and one object in it that tells a running joke or a piece of history.
  validation_type: suggestion
---

# Sitcom Sets

Standing sets for a multi-camera sitcom: three walls, clear entrances, a sofa or counter to play scenes around.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
