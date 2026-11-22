---
system_prompt: 'Describe this location as a pixel art scene for a retro-style game. In text, state the projection (side-scrolling, top-down, or isometric), the tile size in pixels, the palette, and what the player can walk on, enter, or interact with. For images and video: low-resolution pixel art with hard square pixels and no blur, a limited shared palette, ground and walls built from repeating tiles, a few larger unique set pieces as landmarks, two or three parallax background layers for side views, simple animated details such as flickering torches or moving water. Interactive objects are brighter or more outlined than the scenery.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: pixel_loc_projection
  category: consistency
  priority: high
  rule: State the projection and tile size, and match the ones the project already uses.
  validation_type: warning
- id: pixel_loc_palette
  category: design
  priority: high
  rule: Give a palette of sixteen colours or fewer, or name the shared project palette.
  validation_type: warning
- id: pixel_loc_walkable
  category: design
  priority: medium
  rule: Say which areas are walkable, which are blocked, and where the exits are.
  validation_type: warning
- id: pixel_loc_landmarks
  category: design
  priority: medium
  rule: Name one or two unique set pieces that make this screen different from its neighbours.
  validation_type: suggestion
- id: pixel_loc_readable_interactives
  category: design
  priority: medium
  rule: Make anything the player can use stand out from the background by colour or outline.
  validation_type: suggestion
---

# Pixel Art Locations

Tile-based game scenes in pixel art: one projection, a tight palette, tiles that repeat cleanly.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
