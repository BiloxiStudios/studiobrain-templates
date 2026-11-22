---
system_prompt: 'This event is one scene in a film or episode. Give a scene heading (interior or exterior, set, day or night), the characters present, and what each one wants. Write the scene as beats in order, with a turn where the balance shifts, and end as soon as the point is made. State what the audience knows after the scene that they did not know before. Add shooting notes that image and video models can use: shot sizes (wide, medium, close-up), camera movement, lens, lighting mood, and estimated screen time. Use only sets, characters, and props that exist in the project, and keep time of day and wardrobe consistent with the scenes on either side.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: event
rules:
- id: film_scene_heading
  category: design
  priority: high
  rule: Give a scene heading with interior or exterior, the set, and day or night.
  validation_type: warning
- id: film_scene_wants
  category: design
  priority: high
  rule: State what each character in the scene wants.
  validation_type: warning
- id: film_scene_turn
  category: design
  priority: high
  rule: Identify the beat where the scene turns and what has changed by the end.
  validation_type: warning
- id: film_scene_shots
  category: design
  priority: medium
  rule: List the key shots with size and camera movement.
  validation_type: suggestion
- id: film_scene_screen_time
  category: design
  priority: low
  rule: Estimate screen time in seconds or script pages.
  validation_type: suggestion
- id: film_scene_continuity
  category: consistency
  priority: high
  rule: Keep time of day, wardrobe, and props consistent with the scenes before and after.
  validation_type: warning
---

# Film Scenes

Use the event type for a film scene: who wants what, the beats in order, and how it will be shot.

How it maps onto the event type: the event is the scene, affected locations hold the set, affected characters hold the cast, event phases hold the beats, duration holds screen time, the event script holds dialogue and action, visual effects and audio changes hold shooting and sound notes, and story consequences hold what the scene changes.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the event type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
