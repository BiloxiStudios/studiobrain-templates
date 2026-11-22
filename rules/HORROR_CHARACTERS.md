---
system_prompt: 'This character belongs in a horror story. For a human, give a private fear, something they are hiding or grieving, and one blind spot that will put them in danger. For a monster or killer, give rules: what draws it, what it cannot do, and what it leaves behind. Suggest more than you show. In visual descriptions use low light, hard shadow, cold or sickly colour, and one detail that is slightly wrong rather than a pile of gore. Keep the threat consistent with what the project has already established.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: horror_char_fear
  category: design
  priority: high
  rule: For a human character, state one specific fear and where it came from.
  validation_type: warning
- id: horror_char_blind_spot
  category: design
  priority: medium
  rule: State the flaw or belief that will lead this character into danger.
  validation_type: suggestion
- id: horror_char_threat_rules
  category: consistency
  priority: high
  rule: For a monster or killer, state what attracts it, what limits it, and one sign that it is near.
  validation_type: warning
- id: horror_char_wrong_detail
  category: design
  priority: medium
  rule: Include one small, specific detail that is wrong or unsettling instead of general gore.
  validation_type: suggestion
- id: horror_char_restraint
  category: tone
  priority: medium
  rule: Describe injury and death by implication and aftermath unless the project's content rating allows more.
  validation_type: warning
---

# Horror Characters

Victims, survivors and monsters for horror: a private fear, a fatal blind spot, a threat with rules.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
