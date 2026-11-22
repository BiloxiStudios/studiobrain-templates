---
system_prompt: 'This character is for a preschool audience aged two to five. Give them one main personality trait, one thing they love, and small everyday problems such as sharing, bedtime, or trying something new. They name their feelings out loud and solve problems by asking for help, trying again, or being kind. Speech is short, positive, and repeats key phrases. In visual descriptions use big round shapes, a large head and eyes, a thick soft outline, three or four bright flat colours, a simple smiling face, and no sharp points, weapons, or frightening features.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: preschool_char_one_trait
  category: design
  priority: high
  rule: State one main personality trait and one favourite thing.
  validation_type: warning
- id: preschool_char_simple_speech
  category: tone
  priority: high
  rule: Write sample lines of eight words or fewer using words a three-year-old knows.
  validation_type: warning
- id: preschool_char_feelings
  category: design
  priority: medium
  rule: Show the character naming a feeling and what they do about it.
  validation_type: suggestion
- id: preschool_char_round_design
  category: design
  priority: medium
  rule: Describe the body with round shapes and three or four bright colours.
  validation_type: suggestion
- id: preschool_char_safe
  category: tone
  priority: high
  rule: Leave out violence, weapons, scary imagery, sarcasm, and insults.
  validation_type: warning
---

# Preschool Show Characters

Friendly characters for ages two to five: simple shapes, one feeling at a time, problems a small child knows.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
