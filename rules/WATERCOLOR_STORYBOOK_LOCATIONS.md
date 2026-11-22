---
system_prompt: 'Describe this location as a watercolour illustration for a picture book. In text, use short sentences that can be read aloud, say what the place smells and sounds like, and hide three or four small things a child can find on the page. For images and video: loose transparent watercolour washes that bleed into each other, visible paper texture, soft pencil line, pale skies with wet-on-wet clouds, a muted natural palette with a warm light source, edges that fade into white paper as a vignette, simplified buildings and trees with slightly wobbly lines. No sharp digital edges, no deep black shadows, no crowded detail in every corner.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: storybook_loc_find_details
  category: design
  priority: medium
  rule: Include three or four small findable things, such as a snail on the gate or a kite in a tree.
  validation_type: suggestion
- id: storybook_loc_senses
  category: design
  priority: medium
  rule: Describe one sound and one smell in plain words.
  validation_type: suggestion
- id: storybook_loc_read_aloud
  category: tone
  priority: high
  rule: Keep sentences under fifteen words and use everyday vocabulary.
  validation_type: warning
- id: storybook_loc_white_space
  category: design
  priority: medium
  rule: Say where the picture fades to empty paper so text can sit there.
  validation_type: suggestion
- id: storybook_loc_safe
  category: tone
  priority: high
  rule: Keep the place safe and welcoming, even at night or in bad weather.
  validation_type: warning
---

# Watercolour Storybook Locations

Picture-book places painted in watercolour: soft light, room to breathe, small things to find on each page.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
