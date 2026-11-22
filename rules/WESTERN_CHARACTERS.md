---
system_prompt: 'This character lives on a nineteenth-century frontier in a western. Give them a trade (rancher, marshal, gambler, homesteader, railway surveyor, saloon keeper), a past they came here to escape, and a personal code. Speech is spare and dry. In visual descriptions use weathered skin, dust, sweat-stained hats, worn leather, wool and canvas, a gun belt or working tools, low sun and long shadows, and an earth palette of tan, rust, and faded blue. Keep weapons, transport, and medicine at the technology of the period.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: western_char_trade
  category: design
  priority: high
  rule: State how the character earns a living on the frontier.
  validation_type: warning
- id: western_char_past
  category: lore
  priority: medium
  rule: Say where the character came from and what they left behind.
  validation_type: suggestion
- id: western_char_code
  category: design
  priority: high
  rule: State one rule the character lives by and what would make them break it.
  validation_type: warning
- id: western_char_period_gear
  category: consistency
  priority: high
  rule: Keep clothing, weapons, and tools to what existed in the stated year.
  validation_type: warning
- id: western_char_spare_speech
  category: tone
  priority: low
  rule: Write sample dialogue in short plain sentences with little explanation.
  validation_type: suggestion
---

# Western Characters

Frontier people for a western: a trade, a past they left behind, and a code they will or will not break.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
