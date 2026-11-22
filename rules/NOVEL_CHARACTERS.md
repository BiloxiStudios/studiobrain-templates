---
system_prompt: 'This character is for a novel. Give them a conscious want that drives the plot, a deeper need they do not yet see, and a past wound that explains the gap between the two. State where they start, the turning point that forces a choice, and who they are at the end. Write a distinct voice: vocabulary, rhythm, what they notice, and what they avoid saying. Describe appearance through a few details another character would observe, not a list. If images are generated, treat them as cover or chapter illustration: one figure, one mood, no text.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: novel_char_want_need
  category: design
  priority: high
  rule: State what the character wants and, separately, what they need.
  validation_type: warning
- id: novel_char_wound
  category: lore
  priority: medium
  rule: State the past event that shaped the character's flaw or false belief.
  validation_type: suggestion
- id: novel_char_arc
  category: design
  priority: high
  rule: State the character at the start, the turning point, and the character at the end.
  validation_type: warning
- id: novel_char_voice
  category: design
  priority: medium
  rule: Include sample lines that show a vocabulary and rhythm different from the rest of the cast.
  validation_type: suggestion
- id: novel_char_observed_detail
  category: design
  priority: low
  rule: Describe appearance with three details another character would notice, not a full inventory.
  validation_type: suggestion
- id: novel_char_pov
  category: consistency
  priority: medium
  rule: State whether the character is a point-of-view character and keep what they can know limited to that.
  validation_type: suggestion
---

# Novel Characters

Characters built for prose fiction: a want, a need, a wound and an arc that changes them by the last chapter.

How it maps onto the character type: motivations hold the want and the need, fears and secrets hold the wound, the defining moment summary holds the turning point, story function holds the role in the plot, and dialogue samples hold the voice.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
