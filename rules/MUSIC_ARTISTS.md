---
system_prompt: 'This brand is a music artist or band. State the genre and two or three words for the sound, the line-up with each member''s instrument or role, where and when the act formed, and the audience it plays to. Describe the sound concretely: tempo range, instrumentation, vocal style, and production (raw and live, polished, lo-fi, electronic). Give a visual identity that matches the sound: a colour palette, a typeface style for the logo, stage wardrobe, and the look of the cover art. List key releases with a year. For images and video: press-photo or album-cover framing, wardrobe and lighting in the act''s palette, and no text or logos rendered in the image. Invent the act; do not copy a real artist''s name, likeness, or songs.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: brand
rules:
- id: music_artist_sound
  category: design
  priority: high
  rule: State the genre and describe the sound through instruments, tempo, and vocal style.
  validation_type: warning
- id: music_artist_lineup
  category: design
  priority: high
  rule: List each member and what they play or do.
  validation_type: warning
- id: music_artist_visual_identity
  category: design
  priority: medium
  rule: Give a colour palette, a logo lettering style, and stage wardrobe that fit the sound.
  validation_type: suggestion
- id: music_artist_releases
  category: lore
  priority: medium
  rule: List key releases with a title and year, in order.
  validation_type: suggestion
- id: music_artist_audience
  category: design
  priority: low
  rule: 'Describe who listens and where the act plays: clubs, festivals, streaming, radio.'
  validation_type: suggestion
- id: music_artist_original
  category: consistency
  priority: high
  rule: Do not use the name, likeness, lyrics, or song titles of a real artist.
  validation_type: warning
---

# Music Artists and Bands

Use the brand type for a music act: sound, members, look, audience and the releases that define them.

How it maps onto the brand type: the brand is the act, founded is the year it formed, industry is the genre, key personnel are the members, audio style and signature sounds hold the sound, colour palette and typography hold the visual identity, brand items and signature product hold the releases and the best-known song, target audience is the fan base, and major milestones hold the career history.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the brand type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
