---
system_prompt: 'This location must read as a real place that a crew could scout and film. In text, give its real-world equivalent (terraced house, strip-mall office, fishing harbour), its age, and the signs of the people who use it. For images and video: photorealistic, real materials with dirt, scuffs, and repairs, light from a stated source such as overcast daylight through a window or a single streetlamp, true-to-life scale, a 24mm to 35mm lens at standing eye height, natural colour, slight lens falloff toward the corners. No impossible architecture, no perfectly clean surfaces, no fantasy lighting without a visible source.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: photoreal_loc_equivalent
  category: design
  priority: high
  rule: Name the real-world kind of place this is and the decade it was built.
  validation_type: warning
- id: photoreal_loc_light_source
  category: design
  priority: high
  rule: State every light source and whether it is daylight, tungsten, fluorescent, or screen glow.
  validation_type: warning
- id: photoreal_loc_wear
  category: design
  priority: medium
  rule: Describe three signs of use or age, such as stains, mismatched repairs, or clutter.
  validation_type: suggestion
- id: photoreal_loc_scale
  category: consistency
  priority: medium
  rule: Keep ceiling heights, door sizes, and distances at real-world measurements.
  validation_type: warning
- id: photoreal_loc_no_stylisation
  category: consistency
  priority: medium
  rule: Leave out impossible structures and light that has no visible source.
  validation_type: warning
---

# Photoreal Live-Action Locations

Places that could be scouted and filmed: real materials, motivated light, the mess of actual use.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
