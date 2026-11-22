---
system_prompt: 'This character belongs in a film made and set in the 1980s. In text, use period-accurate jobs, slang, music taste, and technology, and give the character a direct, earnest goal. For images and video: 35mm film grain, slightly soft focus, warm skin tones, strong backlight with haze, coloured gels in pink, teal, and amber, anamorphic lens flare. Wardrobe from the decade: shoulder pads, high-waisted denim, bomber or varsity jackets, leg warmers, bright sportswear, big-framed glasses. Hair is large, feathered, permed, or held with spray. Props are analogue: cassette tapes, corded phones, wristwatches with digital faces. No smartphones, no flat screens, no modern fabrics or haircuts.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: character
rules:
- id: eighties_char_wardrobe
  category: design
  priority: high
  rule: Describe an outfit and hairstyle that existed in the 1980s, naming at least three specific garments or accessories.
  validation_type: warning
- id: eighties_char_no_anachronism
  category: consistency
  priority: high
  rule: 'Leave out anything invented after 1989: mobile phones, the web, modern slang, modern brands of technology.'
  validation_type: warning
- id: eighties_char_year
  category: consistency
  priority: medium
  rule: State the year within the decade and keep age, music, and fashion consistent with that year.
  validation_type: suggestion
- id: eighties_char_prop
  category: design
  priority: medium
  rule: Give the character one analogue object they always carry or use.
  validation_type: suggestion
- id: eighties_char_goal
  category: tone
  priority: low
  rule: State the goal in one plain sentence, the way a film poster of the period would.
  validation_type: suggestion
---

# 1980s Film Characters

Characters who look and talk like a 1980s movie: period wardrobe, period hair, period problems.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the character type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
