---
system_prompt: "Generate dialogue for the City of Brains universe that captures 1990s speech patterns, dark comedy horror tone, and faction-specific cultures. Use format [emotion] 'spoken text' *action/gesture*. Avoid modern technology references. Balance humor with genuine trauma while showing character relationships through speech patterns."
global: false
priority: high
entity_type: dialogue
template_reference: CHARACTER_TEMPLATE.md

rules:
- id: dial_001
  category: structure
  priority: critical
  rule: All dialogue must follow the format - [emotion] "spoken text" *action/gesture*
  validation_type: error
  applies_to: [dialogue, character]

- id: dial_002
  category: timeline
  priority: critical
  rule: No modern slang or technology references (this is alternate 1990s)
  validation_type: error
  applies_to: [dialogue]
  forbidden_phrases: ["google it", "text me", "DM me", "swipe right", "viral", "hashtag", "check your phone", "send me a text", "it's on social media", "streaming", "WiFi password"]
  allowed_phrases: ["check the BOL terminal", "call the payphone", "leave a message", "saw it on TV", "heard on the radio"]

- id: dial_003
  category: relationships
  priority: high
  rule: Dialogue tone must match relationship status and faction dynamics
  validation_type: warning
  applies_to: [dialogue, character]

- id: dial_004
  category: personality
  priority: medium
  rule: Speech patterns must reflect character traits, background, and faction culture
  validation_type: warning
  applies_to: [dialogue, character]

- id: dial_005
  category: infection
  priority: high
  rule: Infected characters have degraded speech based on infection stage
  validation_type: warning
  applies_to: [dialogue, character]

- id: dial_006
  category: humor
  priority: high
  rule: Dark humor should emerge naturally from situations, not forced jokes
  validation_type: warning
  applies_to: [dialogue]

- id: dial_007
  category: corporate
  priority: medium
  rule: Corporate characters use euphemisms and marketing speak to hide problems
  validation_type: info
  applies_to: [dialogue, character]

- id: dial_008
  category: environmental
  priority: medium
  rule: Characters reference environmental problems through casual observations
  validation_type: info
  applies_to: [dialogue]

- id: dial_009
  category: voice_acting
  priority: medium
  rule: Include emotional delivery notes for ElevenLabs AI voice generation
  validation_type: info
  applies_to: [dialogue]

- id: dial_010
  category: jingles
  priority: medium
  rule: Brand jingles and corporate slogans should be memorable but ominous in context
  validation_type: info
  applies_to: [dialogue, brand]
---

# DIALOGUE GENERATION RULES
## City of Brains Universe

### MANDATORY FORMAT STRUCTURE

#### 🔴 dial_001 - Standard Dialogue Format
- **Structure**: `[emotion] "spoken text" *action/gesture*`
- **Examples**:
  - `[nervous] "Did you hear that Double Dip jingle playing from the abandoned store?" *glances around warily*`
  - `[sarcastic] "Oh great, another 'family safe' product from ChemCorp." *rolls eyes while reading label*`
  - `[panicked] "The BOL terminal's going crazy with emergency broadcasts!" *frantically typing*`

#### 🔴 dial_002 - Era-Appropriate Language Only
- **Forbidden Modern Terms**: 
  - Technology: "google", "smartphone", "WiFi", "streaming", "app", "social media"
  - Slang: "lit", "yeet", "salty", "ghosting", "stan", "flex"
  - Actions: "text me", "DM me", "check your phone", "share the link"

- **Required 1990s Alternatives**:
  - "Look it up on the BOL terminal" (not "google it")
  - "Call me on the payphone" (not "text me")
  - "Leave a message on my machine" (not "send a DM")
  - "Heard it on the radio" (not "saw it online")

### DARK COMEDY INTEGRATION

#### 🟠 dial_006 - Natural Dark Humor
- **Rule**: Dark humor emerges from absurd situations, not cruelty
- **Good Examples**:
  - `[deadpan] "Well, at least the zombies are bringing the neighborhood together." *dodges zombie swipe*`
  - `[ironically cheerful] "ChemCorp: Better living through chemistry! Unless you count the zombies." *kicks empty sauce bottle*`
  - `[weary] "Remember when our biggest worry was forgetting to rewind a rental tape?" *reloads makeshift weapon*`

- **Avoid**: Mean-spirited jokes about genuine suffering or trauma

### FACTION-SPECIFIC SPEECH PATTERNS

#### Northside Modders/Hackers
**Speech Characteristics**:
- Technical precision and digital metaphors
- Collective problem-solving language
- BOL system references and connectivity terms
- "We need to debug this situation systematically."

#### Westside Truckers/Bikers  
**Speech Characteristics**:
- Practical, direct communication
- Mechanical metaphors and vehicle references
- Independence focus and self-reliance
- "This whole city's running on fumes and prayer."

#### Eastside Elites
**Speech Characteristics**:
- Refined vocabulary and proper grammar
- Status and networking references
- Passive-aggressive politeness
- "Perhaps we could arrange a mutually beneficial agreement?"

#### Southside Flamingos
**Speech Characteristics**:
- Entertainment industry slang
- Performance and style metaphors
- Dramatic flair and inclusive community language
- "Darling, this whole outbreak is just bad theater!"

### INFECTION STAGE SPEECH DEGRADATION

#### 🟠 dial_005 - Progressive Speech Loss
**Stage 0 (Healthy)**: Full coherence and vocabulary
- `[determined] "We need to find supplies before nightfall." *checks watch*`

**Stage 1 (Early Infection)**: 85% coherence, word searching, mild confusion
- `[confused] "I was... what was I saying? Something about... food?" *touches forehead*`

**Stage 2 (Progressing)**: 60% coherence, slurred speech, simple vocabulary
- `[vacant] "Head hurts... need... something..." *stumbles slightly*..Urges...`

**Stage 3 (Advanced)**: 30% coherence, mostly groans, single words
- `[feral] "HUNGRY... NEED... YES..." *lunges forward with clumsy movements*`

**Stage 4 (Full Zombie)**: No coherent speech, only growls and screams
- `*inhuman shriek* *gnashing teeth and wild gestures*`

### CORPORATE DOUBLESPEAK

#### 🟡 dial_007 - Marketing Language Corruption
Corporate characters use euphemisms to hide environmental damage:
- "Temporary water discoloration" (chemical contamination)
- "Enhanced preservation formula" (toxic additives)
- "Accelerated biodegradation" (things dissolving from chemicals)
- "Consumer excitement incidents" (people getting sick)

### ENVIRONMENTAL STORYTELLING THROUGH DIALOGUE

#### 🟡 dial_008 - Casual Environmental References
Characters notice environmental problems through offhand comments:
- `[disgusted] "This water tastes like hot dogs and cotton candy again." *makes face*`
- `[worried] "My mom's roses have been growing those weird purple spots." *points to garden*`
- `[matter-of-fact] "Yeah, the fish in the lake glow now. Pretty but probably not good." *shrugs*`

### MEMORABLE JINGLES AND SLOGANS

#### 🟡 dial_010 - Corporate Audio Branding
**Double Dip Dog Sauce Jingle**: "Double dip, double dip, go ahead and double dip! Double the pleasure, double the fun!"
- Becomes ominous when characters realize the connection to infection

**ChemCorp Slogan**: "ChemCorp: Better living through chemistry!"
- Ironically referenced as environmental damage becomes obvious

**Glow-Fresh Cleaners**: "Glow-Fresh makes everything brighter!"
- Products literally glow due to radioactive contamination

### VOICE ACTING DIRECTION FOR AI

#### 🟡 dial_009 - ElevenLabs Performance Notes
**Breathing Patterns**:
- `[breathing heavily]` for panicked characters
- `[calm breathing]` for composed characters
- `[wheezing]` for infected or injured

**Environmental Effects**:
- `[echo]` for warehouse/large spaces
- `[muffled]` for characters wearing masks
- `[distant]` for characters across the street

**Emotional Layers**:
- `[surface_angry, underlying_scared]` for complex emotions
- `[fake_cheerful]` for corporate characters hiding problems
- `[exhausted_but_determined]` for survivor characters

### RELATIONSHIP-APPROPRIATE DIALOGUE

#### Trust Levels and Addressing
**Stranger**: Formal tone, "Sir/Ma'am" or full names
- `[wary] "I don't know you, mister. State your business." *hand near weapon*`

**Acquaintance**: Polite but guarded, first names only
- `[neutral] "Oh, it's you again, Jake. Find anything useful out there?" *continues sorting supplies*`

**Friend**: Warm and supportive, nicknames if available
- `[relieved] "Thank god you're okay, Sparky! I was starting to worry." *quick hug*`

**Enemy**: Hostile and threatening, last names or insults
- `[cold] "Well, well. If it isn't Morrison. You've got some nerve showing up here." *steps forward menacingly*`

### CONVERSATION FLOW TECHNIQUES

#### Interruptions and Overlaps
- **Sudden Cut**: "Wait, I— *stops mid-sentence as zombie appears*"
- **Trailing Off**: "But I thought we were going to... *voice fades as realization hits*"
- **Talking Over**: `[both characters] "We need to—" "Let's get—" *both stop and laugh nervously*`

#### Silence and Tension
- `[uncomfortable silence as both avoid mentioning the missing neighbor]`
- `[tense silence as they listen for zombie sounds]`
- `[long pause to process the loss]`

### ERA-APPROPRIATE LANGUAGE GUIDELINES

#### Acceptable 1990s Slang
- **Positive**: "rad", "gnarly", "tight", "wicked", "phat", "fresh", "dope"
- **Negative**: "bogus", "bummer", "harsh", "weak sauce", "lame"
- **General**: "whatever", "as if", "talk to the hand", "psych", "not"

#### Communication References
- "Call me on the payphone"
- "Leave a message on my answering machine" 
- "Check the BOL terminal for updates"
- "Page me if it's urgent"
- "I saw it on the news"

### SPECIAL DIALOGUE SITUATIONS

#### Dying Words
Emotional weight with unfinished business or revelations:
- `[weakening] "Tell Sarah... tell her I kept my promise..." *coughs blood*`

#### First Meeting
Establish personality and faction allegiance:
- `[cautious] "You're not from around here. That makes you either useful or dangerous."`

#### Betrayal Reveal
Emotional intensity with relationship destruction:
- `[cold] "You never understood. This was always about survival, not friendship."`

#### Reunion
Emotional recognition with time passage acknowledgment:
- `[shocked] "My god... is that really you? We thought you were dead!"`

### VALIDATION CHECKLIST

Before finalizing dialogue:
- [ ] Uses proper format: [emotion] "speech" *action*
- [ ] Contains only 1990s-appropriate language and references
- [ ] Matches character's faction speech patterns
- [ ] Reflects appropriate relationship dynamics
- [ ] Includes environmental storytelling details
- [ ] Balances dark humor with genuine emotion
- [ ] Incorporates infection stage if applicable
- [ ] Provides clear voice acting direction
- [ ] Serves narrative or character development purpose
- [ ] Avoids modern technology or slang references

### USAGE EXAMPLES

#### For AI Generation:
Use this document as context for generating natural, period-appropriate dialogue that serves the dark comedy horror narrative.

#### For Voice Directors:
Reference emotion tags and environmental effects to guide AI voice generation through ElevenLabs.

#### For Writers:
Follow relationship matrices and faction speech patterns to create authentic character voices.
