---
system_prompt: 'This character must read as a real person filmed with a real camera. In text, give a plausible age, body, job, income, and wardrobe, and describe the face with ordinary human asymmetry and at least one imperfection. For images and video: photorealistic, natural skin texture with pores and fine lines, real hair with flyaways, clothing with creases, wear, and correct fit, light motivated by a window or a practical lamp, a 50mm to 85mm lens at eye level, shallow depth of field, neutral colour grade. No airbrushed skin, no perfectly symmetrical features, no exaggerated anatomy, no costume that a real wardrobe department could not buy or make.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: photoreal_char_plausible
  category: design
  priority: high
  rule: Give height, build, and age that are ordinary for a human, and say how the body shows the life the character has led.
  validation_type: warning
- id: photoreal_char_imperfection
  category: design
  priority: high
  rule: 'Include at least one natural imperfection: a scar, uneven teeth, tired eyes, a receding hairline.'
  validation_type: warning
- id: photoreal_char_wardrobe
  category: design
  priority: medium
  rule: Describe clothes the character could afford and would choose, including their condition.
  validation_type: suggestion
- id: photoreal_char_no_stylisation
  category: consistency
  priority: high
  rule: Leave out stylised features such as oversized eyes, unnatural hair colour without dye, or impossible proportions.
  validation_type: warning
- id: photoreal_char_casting_note
  category: design
  priority: low
  rule: Write one casting line that describes the presence wanted, without naming any real person.
  validation_type: suggestion
---

# Photoreal Live-Action Characters

People who could be cast and filmed: plausible bodies, real wardrobe, natural light on real skin.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
