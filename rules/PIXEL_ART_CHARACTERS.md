---
system_prompt: 'Design this character as a pixel art sprite for a retro-style game. In text, state the sprite height in pixels, the palette size, the viewing angle (side-on, top-down, or three-quarter), and the two or three features that must survive at that size. For images and video: low-resolution pixel art with hard square pixels, no blur and no smooth gradients, a limited palette of eight to sixteen colours, a one-pixel dark outline, shading in two or three steps per colour with optional dithering, a large head relative to the body, a clear silhouette against a plain background, simple looping idle and walk frames. Keep the pixel grid consistent across every sprite.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: pixel_char_size
  category: design
  priority: high
  rule: State the sprite height in pixels and keep it the same as other characters of the same kind in the project.
  validation_type: warning
- id: pixel_char_palette
  category: design
  priority: high
  rule: State the number of colours and name the main ones.
  validation_type: warning
- id: pixel_char_key_features
  category: design
  priority: high
  rule: Name two or three features that identify the character at sprite size, such as hat shape, hair colour, or cape.
  validation_type: warning
- id: pixel_char_view
  category: consistency
  priority: medium
  rule: State the viewing angle and match the angle the project already uses.
  validation_type: warning
- id: pixel_char_animation
  category: design
  priority: low
  rule: List the animation states needed, such as idle, walk, attack, and hurt, with a frame count for each.
  validation_type: suggestion
---

# Pixel Art Characters

Sprite characters for retro-style games: tiny canvas, limited palette, readable in a handful of pixels.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
