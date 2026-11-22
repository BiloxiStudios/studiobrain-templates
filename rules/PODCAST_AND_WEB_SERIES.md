---
system_prompt: 'This campaign is one season of a podcast or web series. State the premise in one sentence, the audience, whether it is fiction, interview, documentary, or tutorial, the number of episodes, and the target length of each. Define the repeating episode format: cold open, intro, segments, sign-off. Give every episode a title, a one-line summary, and one thing the listener or viewer takes away. For audio, describe hosts'' voices, music, and sound design, and never rely on something that must be seen. For video, state the aspect ratio, the set or backdrop, the framing of the hosts, and the look of titles and thumbnails. Keep hosts and recurring segments consistent across the season.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: campaign
rules:
- id: series_premise_audience
  category: design
  priority: high
  rule: State the premise in one sentence and who the series is for.
  validation_type: warning
- id: series_episode_format
  category: design
  priority: high
  rule: Define the repeating structure of an episode and the target length.
  validation_type: warning
- id: series_episode_list
  category: design
  priority: high
  rule: Give each episode a title and a one-line summary.
  validation_type: warning
- id: series_hook
  category: design
  priority: medium
  rule: 'State what makes someone come back for the next episode: an open question, a running story, or a regular segment.'
  validation_type: suggestion
- id: series_medium_fit
  category: consistency
  priority: medium
  rule: For audio, do not rely on visuals. For video, state the aspect ratio and framing.
  validation_type: warning
- id: series_host_consistency
  category: consistency
  priority: medium
  rule: Keep the hosts, their voices, and recurring segments the same across episodes.
  validation_type: suggestion
---

# Podcast and Web Series

Use the campaign type to plan a season of a podcast or web series: a format, an episode list and a reason to come back.

How it maps onto the campaign type: the campaign is the season, chapter count is the number of episodes, narrative summary is the premise, estimated duration is the episode length, the quest sequence holds the episodes in order, protagonist and supporting characters are the hosts and guests, primary locations are the studio or sets, music tracks hold the theme music, and voice files hold recordings.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the campaign type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
