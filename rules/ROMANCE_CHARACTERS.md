---
system_prompt: 'This character is a lead, love interest, or rival in a romance or romantic comedy. State what they want from life, what they believe about love and why, and the specific obstacle that keeps them from the other lead. Give them a life outside the relationship: work, friends, family. Attraction should come from behaviour and conversation as much as looks. For a comedy, add one habit that causes embarrassing situations. In visual descriptions use warm flattering light, soft focus, inviting everyday settings, and expressive faces. Keep both leads adults with equal say in the relationship.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: romance_char_belief
  category: design
  priority: high
  rule: State what the character believes about love and the experience that taught them that.
  validation_type: warning
- id: romance_char_obstacle
  category: design
  priority: high
  rule: State the specific reason this character and the other lead cannot simply be together.
  validation_type: warning
- id: romance_char_own_life
  category: design
  priority: medium
  rule: Give the character a job, a friend, and a goal that have nothing to do with the romance.
  validation_type: suggestion
- id: romance_char_appeal
  category: design
  priority: medium
  rule: Name two things about how the character behaves that make them attractive to the other lead.
  validation_type: suggestion
- id: romance_char_adults
  category: consistency
  priority: high
  rule: Keep romantic leads adults who both choose the relationship freely.
  validation_type: warning
---

# Romance Characters

Leads and rivals for romance and romantic comedy: what they want, what they fear, why it cannot be easy.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
