---
system_prompt: 'This campaign is a music video. Name the song, artist, running time, and tempo, then state the concept in one sentence and whether it is performance, narrative, abstract, or a mix. Break the song into sections (intro, verse, chorus, bridge, outro) with timecodes and say what is on screen in each; the chorus should return to a recognisable image. Write a visual treatment that image and video models can follow: aspect ratio, palette, lighting, lens and camera movement, wardrobe, and editing pace tied to the beat. List locations and performers from the project. Keep the look constant across every shot unless a change is part of the concept.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: campaign
rules:
- id: music_video_concept
  category: design
  priority: high
  rule: 'State the concept in one sentence and the type: performance, narrative, abstract, or mixed.'
  validation_type: warning
- id: music_video_song_sections
  category: design
  priority: high
  rule: Break the song into sections with timecodes and describe the visuals for each.
  validation_type: warning
- id: music_video_treatment
  category: design
  priority: high
  rule: State aspect ratio, colour palette, lighting, and camera movement for the whole video.
  validation_type: warning
- id: music_video_chorus_image
  category: design
  priority: medium
  rule: Give the chorus one repeating image or set-up the viewer will remember.
  validation_type: suggestion
- id: music_video_edit_pace
  category: design
  priority: medium
  rule: Tie cutting speed to the tempo, such as a cut every two or four beats.
  validation_type: suggestion
- id: music_video_continuity
  category: consistency
  priority: medium
  rule: Keep wardrobe, palette, and performer appearance the same in every shot of the same set-up.
  validation_type: warning
---

# Music Video Shoots

Use the campaign type to plan a music video: concept, visual treatment and a shot plan cut to the song.

How it maps onto the campaign type: the campaign is the video, narrative summary is the concept, music tracks hold the song, estimated duration is the running time, the quest sequence holds the song sections in order, primary locations are the sets, protagonist and supporting characters are the performers, and tone and themes hold the treatment.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the campaign type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
