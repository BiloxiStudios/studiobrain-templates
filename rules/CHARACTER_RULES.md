---
system_prompt: "Generate a character for the City of Brains universe, a dark comedy horror set in an alternate 1990s during a zombie outbreak. Characters should reflect the era's culture while showing impact of corporate environmental neglect. Balance humor with genuine trauma, avoid modern technology references, and connect to established locations/factions. Use faction-appropriate speech patterns and show how ordinary people cope with extraordinary circumstances."
global: false
priority: high
entity_type: character
template_reference: CHARACTER_TEMPLATE.md

rules:
- id: char_001
  category: identity
  priority: critical
  rule: Every character MUST have a primary_location or they will be flagged as homeless
  validation_type: error
  applies_to: [character]

- id: char_002
  category: naming
  priority: critical
  rule: Character IDs must use lowercase_with_underscores format
  validation_type: error
  applies_to: [character]

- id: char_003
  category: relationships
  priority: high
  rule: Friends always use nicknames when available, never full names in dialogue
  validation_type: warning
  applies_to: [character]

- id: char_004
  category: timeline
  priority: critical
  rule: No modern technology references - this is alternate 1990s
  validation_type: error
  applies_to: [character]
  forbidden_tech: ["cell phones", "social media", "internet search", "GPS", "ride sharing", "streaming"]
  allowed_tech: ["payphones", "BOL terminals", "VHS", "newspapers", "dial-up", "pagers"]

- id: char_005
  category: tone
  priority: high
  rule: Characters must balance dark humor with genuine trauma responses
  validation_type: warning
  applies_to: [character]

- id: char_006
  category: infection
  priority: high
  rule: Infected characters show progressive degradation in speech and behavior
  validation_type: warning
  applies_to: [character]

- id: char_007
  category: faction
  priority: medium
  rule: Characters should reflect their faction's culture and speech patterns
  validation_type: warning
  applies_to: [character]

- id: char_008
  category: skills
  priority: medium
  rule: Practical real-world skills (plumbing, electrical, mechanical) are highly valued
  validation_type: info
  applies_to: [character]

- id: char_009
  category: corporate
  priority: medium
  rule: Characters' awareness of conspiracy varies by position and exposure
  validation_type: info
  applies_to: [character]

- id: char_010
  category: environmental
  priority: medium
  rule: Characters should show signs of living in a chemically contaminated environment
  validation_type: info
  applies_to: [character]

- id: char_011
  category: timeline_validation
  priority: critical
  rule: Use timeline validation tools to verify that birth_year matches age (current year is 1998), key_dates are chronologically ordered, death_year (if applicable) occurs after birth, and all temporal data is internally consistent
  validation_type: error
  applies_to: [character]
  required_tools: ["validate_character_age", "check_temporal_conflicts", "calculate_duration"]

- id: char_012
  category: entity_validation
  priority: critical
  rule: Before referencing locations (primary_location, home_location), factions, brands
    (associated_brands), or other characters (relationships, allies, enemies), use
    validation tools to verify they exist. Use check_location_exists for locations,
    check_brand_exists for brands, check_character_exists for character relationships.
    Never reference non-existent entities
  validation_type: error
  applies_to: [character]
  required_tools: ["check_location_exists", "check_brand_exists", "check_character_exists",
    "validate_all_references"]

- id: char_013
  category: physical
  priority: high
  rule: Characters MUST have skin_tone set to one of the three approved palettes
        (Light-Medium Warm Beige, Medium-Deep Rich Brown, Deep Cool Ebony).
        eye_color MUST use an approved value (Dark Blue, Dark Brown, Indigo, Grey,
        Dark Green, Dark Teal, Mocha, Honey, Blue, Green, Zombie).
        hair_color MUST use an approved value (Black, Dark Brown, Medium Brown,
        Light Brown, Auburn, Red, Dark Blonde, Blonde, Platinum Blonde, Grey,
        White, Strawberry Blonde). nail_color should default from the skin_tone
        palette unless intentionally overridden.
  validation_type: warning
  applies_to: [character]
---

# Character Creation in the City of Brains Universe

## The Dark Comedy Horror Balance

Creating characters for City of Brains means walking a tightrope between absurd corporate dystopia and genuine human trauma. Every character should feel like they could have existed in the real 1990s, but now they're dealing with zombie outbreaks and corporate conspiracies that would make even the most cynical consumer question everything.

### Why Location Matters

In a world where safe spaces are rare and contested, every character needs a home base. Whether it's a fortified gas station, a hidden basement apartment, or a faction-controlled district, the `primary_location` field isn't just metadata - it's survival. Characters without locations are literally homeless in a zombie apocalypse, which affects everything from their mental state to their available resources.

### The 1990s Time Capsule

This isn't just "retro" - it's an alternate timeline where the internet never became mainstream, cell phones are still luxury items, and people communicate through payphones and pagers. When creating dialogue or backstories, think about how people actually lived in 1995: VHS rentals, newspaper classifieds, dial-up modems that tied up phone lines, and the last generation to grow up without constant digital connectivity.

### Faction Identity Through Speech

Each faction has developed its own survival culture, and characters should reflect this in their speech patterns:

- **Northside Bears** speak like early computer enthusiasts - precise, technical, and collaborative. They use "we" more than "I" because survival requires teamwork. Hot wires, off grid doesn't trust the corporations they work for, always in Plan B surivival mode.
- **Westside Krakens** fast talkers, irriational at times, nonsense slag cross of desert rat / sea shanty style of people who work with their hands and depend on each other.
- **Eastside Dragons** maintain the refined speech patterns of people who used to network at corporate events and socialite parties, influencers before they existed now pushing brands for survival.
- **Southside Flamingos** bring entertainment industry energy to everything - they're used to performing and know how to make even the darkest situation glamourous, or else... With a cat walk cut-throat side.

### The Infection Progression

Zombie infection isn't instant - it's a slow degradation that affects speech and behavior. Early stages show confusion and word-searching as the brain chemistry changes. Later stages reduce vocabulary and eventually eliminate speech entirely. This progression should be reflected in dialogue trees and character interactions.

### Environmental Contamination as Character Development

Living in a chemically contaminated environment affects everyone differently. Some develop unusual hair colors or skin conditions. Others become sensitive to certain foods or chemicals. These aren't just cosmetic details - they're evidence of corporate negligence that characters can discover and use in their quest for truth and survival.

### Practical Skills in a Post-Apocalyptic World

The outbreak has flipped the value system. Skills that were once considered "blue collar" or "working class" are now essential for survival. A plumber who can fix water systems is more valuable than a marketing executive who can't repair anything. This creates interesting character dynamics where former corporate employees must learn practical skills or find other ways to contribute.

### Corporate Conspiracy Awareness Levels

Not everyone knows the truth about the outbreak. Characters' awareness of corporate conspiracy varies dramatically:

- **Insiders** (corporate brand employees, executives, government) know the truth but may be complicit or trapped by their knowledge
- **Suspicious** (local business owners, journalists) have pieced together clues but lack definitive proof
- **Naive** (teenagers, average consumers) are still processing the outbreak and haven't connected it to corporate malfeasance
- **Victims** (those directly affected by contamination) are learning the truth through personal experience

### Character Creation Defaults

When creating new characters, consider these baseline assumptions:
- Most characters are between 16-75 years old, representing the full spectrum of society
- Default to human species unless specifically creating infected or mutated characters
- New characters start "active" but with "stressed" mental state - the outbreak affects everyone
- Faction alignment choose one based on their history, home or work location (district), social influences or business factors to side with one over the other.

## Speech Patterns and Communication

### Era-Appropriate Language

Characters should sound authentically 1990s without being caricatures. Use slang that feels natural to the era:

**Positive expressions**: "rad", "gnarly", "tight", "wicked", "phat", "fresh", "dope"
**Negative expressions**: "bogus", "bummer", "harsh", "weak sauce", "lame"  
**General expressions**: "whatever", "as if", "talk to the hand", "psych", "not"

**Avoid modern slang**: "lit", "fam", "yeet", "ghosting", "salty", "stan", "flex", "lowkey", "highkey"

### Communication Technology

Characters communicate through 1990s technology:
- "Call me on the payphone" (not "text me")
- "Leave a message on my answering machine" (not "DM me")
- "I saw it on the news" (not "I saw it online")
- "Check the BOL terminal for updates" (not "check your phone")
- "Page me if it's urgent" (not "send me a link")

## Character Backstory Development

### Pre-Outbreak Life
Every character needs a foundation in the "before times":
- What was their job or school situation?
- Who were their family and close relationships?
- What was their daily routine and biggest concerns?
- How were they exposed to corporate products or contamination?

### The Outbreak Experience
The moment everything changed:
- Where were they during the concert/eclipse that started it all?
- How did they first learn about the infection?
- What were their initial survival decisions?
- What losses and trauma did they experience?

### Current Survival Situation
How they've adapted to the new world:
- What survival strategies and skills have they developed?
- Who are their current allies and enemies?
- What resources do they have access to?
- What are their goals and motivations moving forward?

## Template Integration

### Character Template Alignment
When using the CHARACTER_TEMPLATE.md:
- The `character_id` field must match your folder name exactly
- The `primary_location` must reference an existing location in your Locations folder
- The `faction` field should reference an existing faction if applicable
- The `associated_brands` list should reference brands from your Brands folder

### Cross-Reference Validation
Before finalizing any character:
- [ ] Does the `primary_location` exist in your Locations folder?
- [ ] Do any referenced faction IDs exist in your Factions folder?
- [ ] Do any associated brand IDs exist in your Brands folder?
- [ ] Does the `character_id` use lowercase_with_underscores format?
- [ ] Are all technology references limited to 1990s era?
- [ ] Does the speech pattern match the character's faction and background?
- [ ] Is dark humor balanced with genuine trauma responses?
- [ ] Do practical skills match the survival situation?
- [ ] Are environmental contamination effects subtle but present?
- [ ] Does the backstory connect to the Double Dip Dog Sauce outbreak?
- [ ] Do relationships and dialogue patterns feel authentic?

## Implementation Examples

### For AI Generation Systems
When creating a character named "Jake Morrison":
1. Set `character_id: "jake_morrison"` (matches folder name)
2. Assign `primary_location: "downtown_district"` (must exist in Locations)
3. If he's friends with "gary_gasstation", Gary calls him "Jake" not "Mr. Morrison"
4. Include only 1990s technology references
5. Generate portraits with synthwave aesthetic

### For Human Content Creators
- Review this file before creating any character
- Use the validation checklist above
- Follow social dynamics for dialogue writing
- Reference only era-appropriate elements
- Ensure all cross-references point to existing entities
