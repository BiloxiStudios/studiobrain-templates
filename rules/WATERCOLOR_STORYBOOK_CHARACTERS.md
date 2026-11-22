---
system_prompt: 'Design this character for a watercolour picture book. In text, use short plain sentences that can be read aloud, give the character one simple wish and one small worry, and describe them with two or three details a young child would notice. For images and video: transparent watercolour washes with soft bleeding edges, a loose pencil or fine ink outline that does not close every shape, visible paper grain, plenty of white paper left around the figure, a muted warm palette with one bright accent, rounded simple body shapes, dot eyes and a small expressive mouth. No hard digital edges, no heavy black outline, no dark or frightening imagery.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: storybook_char_simple_details
  category: design
  priority: high
  rule: Describe the character with two or three concrete details a small child would notice first.
  validation_type: warning
- id: storybook_char_wish
  category: design
  priority: medium
  rule: State one simple wish and one small worry in a sentence each.
  validation_type: suggestion
- id: storybook_char_read_aloud
  category: tone
  priority: high
  rule: Keep sentences under fifteen words and use everyday vocabulary.
  validation_type: warning
- id: storybook_char_accent_colour
  category: design
  priority: medium
  rule: Give the character one bright accent colour item, such as a red scarf or yellow boots, that appears on every page.
  validation_type: suggestion
- id: storybook_char_gentle
  category: tone
  priority: medium
  rule: Leave out anything frightening, violent, or cynical.
  validation_type: warning
---

# Watercolour Storybook Characters

Gentle picture-book characters: soft washes, loose pencil line, simple shapes and kind faces.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
