---
system_prompt: 'This location is a set for a film made and set in the 1980s. In text, dress it with period furniture, signage, vehicles, and technology, and say who hangs out there. For images and video: shot on 35mm film with visible grain, practical light sources in frame (neon tubes, fluorescent strips, table lamps, sodium street lights), smoke or haze so light beams show, wet streets at night, a palette of teal, magenta, amber, and brown. Interiors have wood panelling, patterned carpet, venetian blinds, and bulky cathode-ray televisions. Exteriors have boxy cars, shopping malls, video arcades, diners, and phone booths. Nothing digital, flat-screen, or LED-lit.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: location
rules:
- id: eighties_loc_dressing
  category: design
  priority: high
  rule: List at least five period set-dressing items, including one piece of technology and one piece of signage.
  validation_type: warning
- id: eighties_loc_no_anachronism
  category: consistency
  priority: high
  rule: Leave out flat screens, LED lighting, modern cars, and any device with a touch screen.
  validation_type: warning
- id: eighties_loc_practical_light
  category: design
  priority: medium
  rule: Name the light sources visible in the scene and their colours.
  validation_type: warning
- id: eighties_loc_regulars
  category: lore
  priority: low
  rule: Say which group of people uses the place and what they do there.
  validation_type: suggestion
- id: eighties_loc_sound
  category: design
  priority: low
  rule: 'Name what is playing or humming in the background: a radio, an arcade cabinet, a ceiling fan.'
  validation_type: suggestion
---

# 1980s Film Locations

Sets dressed for a 1980s movie: neon, wood panelling, analogue technology and haze in the light.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the location type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
