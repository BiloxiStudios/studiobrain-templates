---
system_prompt: 'This character belongs in a mystery or detective story. For a detective, give a method of working, a field of expert knowledge, and a personal flaw. For a suspect or witness, give a relationship to the victim, a possible motive, a stated alibi, and one secret unrelated to the crime that makes them look guilty. Record what the character knows, what they say, and what is actually true as three separate things. Play fair: every fact needed for the solution must be something the audience can observe. In visual descriptions favour telling details such as worn cuffs, ink stains, or an unposted letter.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: mystery_char_role
  category: design
  priority: high
  rule: 'State the role in the case: detective, victim, suspect, witness, or accomplice.'
  validation_type: warning
- id: mystery_char_motive_alibi
  category: design
  priority: high
  rule: For a suspect, state a motive, an alibi, and whether the alibi is true.
  validation_type: warning
- id: mystery_char_secret
  category: design
  priority: medium
  rule: Give one secret that is not the crime but makes the character behave suspiciously.
  validation_type: suggestion
- id: mystery_char_knowledge
  category: consistency
  priority: high
  rule: Separate what the character knows, what they claim, and what is true, and keep these the same wherever the character appears.
  validation_type: warning
- id: mystery_char_method
  category: design
  priority: medium
  rule: For a detective, state how they work and one kind of evidence they always notice.
  validation_type: suggestion
- id: mystery_char_telling_detail
  category: design
  priority: low
  rule: Include one observable physical detail that a careful reader could use as a clue.
  validation_type: suggestion
---

# Mystery Characters

Detectives, suspects and witnesses: a method, a motive, a secret, and an alibi that can be checked.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
