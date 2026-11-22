---
system_prompt: 'This character lives in a specific historical period and place. State the year and country, their social rank, where their money comes from, and what is expected of someone of their sex, class, and age. The drama comes from the gap between what they want and what their society allows. Use period-accurate names, forms of address, clothing, and technology, and avoid modern attitudes stated in modern words. In visual descriptions use candle, gas, or window light, natural fabrics cut in the fashion of the stated decade, period hairstyles, and a restrained palette taken from paintings of the era.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: period_char_date_place
  category: consistency
  priority: high
  rule: State the year and country, and keep every detail consistent with them.
  validation_type: warning
- id: period_char_rank_money
  category: design
  priority: high
  rule: State the character's social rank and source of income.
  validation_type: warning
- id: period_char_constraint
  category: design
  priority: high
  rule: State one thing the character wants that their society forbids or punishes.
  validation_type: warning
- id: period_char_dress
  category: design
  priority: medium
  rule: Describe clothing and hair in the fashion of the stated decade and the character's class.
  validation_type: suggestion
- id: period_char_no_anachronism
  category: consistency
  priority: medium
  rule: Leave out objects, phrases, and ideas that did not exist in the period.
  validation_type: warning
---

# Period Drama Characters

People bound by a real historical era: rank, money, manners, and what their time would never let them say.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
