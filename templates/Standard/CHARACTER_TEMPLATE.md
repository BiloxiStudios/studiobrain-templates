---
# METADATA
template_version: "2.0"
template_category: "entity"
editable: true
marketplace_eligible: true
id: "[snake_case_name]"
entity_type: "character"
folder_name: "Characters"
file_prefix: "CH_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "[YYYY-MM-DD]"
last_updated: "[YYYY-MM-DD]"
associated_rules:
  - CHARACTER_RULES.md
associated_skills: []
status: "active"

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC IDENTITY
name: "[Generate Full Name]"
nickname: "[Generate Nickname]"
age: "18" # Should be 18 - 85 unless specified otherwise
gender: "[male/female/non-binary]"
species: "human"

# TEMPORAL INFORMATION (Optional - extracted from backstory if not specified)
birth_year: null          # Absolute year of birth (e.g., 1985)
death_year: null          # If character is deceased
key_dates:                # Important dates in character history
  # - year: 1985
  #   event: "Got job at chemical plant"
  # - year: 1991
  #   event: "Moved to City of Brains"
current_age_reference_year: 1998  # Year the age field is accurate for (game present)

# PHYSICAL DESCRIPTION
height: "[Height in feet/inches]"
build: "[slim/average/muscular/heavyset]"
hair_color:
  name: ""
  hex: ""
eye_color:
  name: ""
  hex: ""
skin_tone:
  palette: ""
  base: ""
  midtone: ""
  shadow: ""
  highlight: ""
nail_color: ""
distinguishing_features:
  - "[Unique physical feature 1]"
  - "[Unique physical feature 2]"

# LOCATION & MOVEMENT
primary_location: "[Reference existing location ID]"
secondary_locations:
  - "[Secondary location 1]"
  - "[Secondary location 2]"

# RELATIONSHIPS
faction: "[Faction affiliation or independent]"
family:
  - "[Relationship]: [Person name/description]"
friends:
  - "[Friend name/description]": "[relationship_type]"
enemies: []
romantic:
  - "[Partner name/description]": "[relationship_status]"

# PERSONALITY & PSYCHOLOGY
personality_traits:
  - "[Core trait 1]"
  - "[Core trait 2]"
  - "[Core trait 3]"
fears:
  - "[Primary fear]"
  - "[Secondary fear]"
motivations:
  - "[Primary motivation]"
  - "[Secondary motivation]"
secrets:
  - "[Hidden secret 1]"
  - "[Hidden secret 2]"
defining_moment_summary: "[Brief one-line summary of the pivotal life event that shaped them]"

# SKILLS & ABILITIES
primary_skills:
  - "[Main skill 1]"
  - "[Main skill 2]"
secondary_skills:
  - "[Secondary skill 1]"
  - "[Secondary skill 2]"
special_abilities: []

# STORY INTEGRATION
story_function:
  - "[Role in narrative]"
  - "[Story purpose]"
inventory_items:
  - "[Item 1]"
  - "[Item 2]"
services:
  - "[Service offered 1]"
  - "[Service offered 2]"

# BRAND ASSOCIATIONS
associated_brands:
  - "[Brand name 1]"
  - "[Brand name 2]"

# JOB
job:
  - "[Reference Exisiting Job name 1]"

# NARRATIVE IMPORTANCE
narrative_importance: "[main/major/minor - story significance]"

# AI GENERATION HELPERS
ai_profile_description: "[Visual description from profile image for AI vision-to-text generation]"
ai_voice_style: "[Brief 1-2 line description of speaking style/vocal characteristics]"
ai_bio_summary: "[Concise 2-3 sentence character bio for AI context]"

# DIALOGUE SAMPLES (for AI quick reference and voice consistency)
dialogue_samples:
  - "[Example line 1 - showing their typical greeting or introduction]"
  - "[Example line 2 - showing emotion or stress response]"
  - "[Example line 3 - showing their humor or personality quirk]"
  - "[Example line 4 - showing how they give information or instructions]"
  - "[Example line 5 - showing their reaction to conflict or danger]"
---

# [Character Full Name]

## Background

[2-3 paragraphs describing the character's life before the outbreak, how they ended up in their current situation, and what shaped their personality. Include specific details about their work, family relationships, and connection to the local community.]

## Personality

[1-2 paragraphs describing how they think, act, and interact with others. Include their quirks, habits, communication style, and how their fears and motivations drive their behavior. Show their role in the dark comedy horror tone.]

## Defining Moment

[1-2 paragraphs describing the pivotal life event that fundamentally shaped who this character is. This could be a trauma, triumph, loss, discovery, betrayal, awakening, or any major turning point. Explain what happened, when it occurred, and most importantly - how it changed them. This moment should explain the core of their personality, their deepest fears or motivations, and why they are the way they are today. Make it specific and emotionally resonant.]

## Dialogue & Speech Patterns

[1-2 paragraphs describing how this character speaks and communicates. Detail their unique voice characteristics, including:]

**Voice & Delivery**: [Describe their accent, pace, tone, volume, and any speech impediments or distinctive vocal qualities]

**Vocabulary & Style**: [Explain their word choice, education level reflected in speech, formality, and whether they use technical jargon, street slang, or antiquated terms]

**Signature Patterns**: [Detail their catchphrases, repeated phrases, unique grammatical quirks, or unusual word usage - like calling all yellow things "banana-colored" or ending every statement with "right?" or "you know what I mean?"]

**Cultural & Linguistic Elements**: [Describe any language mixing (Spanglish, code-switching, etc.), cultural references they make, generation-specific slang, or regional expressions they use]

### Example Dialogue

> "[Greeting/Introduction line showing their typical opening]"

> "[Emotional response showing how they react under stress or excitement]"

> "[Casual conversation showing their humor and quirks]"

> "[Giving information or instructions - showing authority or helpfulness]"

> "[Reaction to conflict or danger - showing their true character]"

## Relationships

**[Relationship Category]**: [Description of how they relate to family, friends, romantic partners, etc. Use specific names and established cross-references when possible.]

## Story Role

[1 paragraph explaining their function in the City of Brains narrative, what they contribute to the player's experience, and how they fit into the larger outbreak storyline.]