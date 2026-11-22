---
system_prompt: 'Design this character for a comic book or graphic novel. In text, give a costume or outfit simple enough to draw in every panel, a two or three colour scheme, and one emblem, shape, or prop that identifies the character even in silhouette. Write how they speak in short lines that fit a speech balloon. For images and video: bold black ink outlines with varied line weight, areas of solid black shadow, flat colour with halftone dots or simple gradients, dynamic foreshortened poses, strong facial expressions, dramatic angles from below or above, visible hatching for texture. No photographic rendering and no soft airbrushed shading.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: comic_char_silhouette
  category: design
  priority: high
  rule: Describe the silhouette and the one element that makes it recognisable in solid black.
  validation_type: warning
- id: comic_char_colours
  category: design
  priority: high
  rule: Limit the costume to two or three main colours and name them.
  validation_type: warning
- id: comic_char_drawable
  category: design
  priority: medium
  rule: 'Keep costume detail low enough to redraw in dozens of panels: no fine patterns or many small parts.'
  validation_type: suggestion
- id: comic_char_balloon_voice
  category: design
  priority: medium
  rule: Include sample lines of no more than twenty-five words each.
  validation_type: suggestion
- id: comic_char_model_consistency
  category: consistency
  priority: high
  rule: 'Match any earlier appearance in the project: same emblem, same colours, same proportions.'
  validation_type: warning
---

# Comic Book Characters

Characters drawn for comics: bold ink, a costume that reads in one panel, a silhouette you know in shadow.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
