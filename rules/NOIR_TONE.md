---
system_prompt: Write in a noir tone. Everyone wants something and hides something. Favour short, concrete description, night and weather, money trouble, and choices that cost. No one is purely good.
global: false
priority: medium
ruleset_kind: theme
rules:
- id: noir_secret
  category: story
  priority: high
  rule: Give the subject a secret or a debt that someone else could use.
  validation_type: warning
- id: noir_moral_grey
  category: tone
  priority: high
  rule: Avoid purely good or purely evil. State what the subject wants and what line they have already crossed.
  validation_type: warning
- id: noir_concrete
  category: tone
  priority: medium
  rule: Prefer short concrete sentences over ornate description.
  validation_type: suggestion
- id: noir_atmosphere
  category: tone
  priority: low
  rule: Use night, weather, smoke, or artificial light in the description.
  validation_type: suggestion
---

# Noir Tone

A hard-boiled noir tone for any entity type: moral grey, secrets, rain and consequences.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick any entity type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
