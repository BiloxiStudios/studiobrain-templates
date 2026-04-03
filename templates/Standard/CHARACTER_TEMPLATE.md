---
# METADATA
template_version: "2.0"
template_category: "entity"
ui_icon: "Users"
ui_color: "#6366f1"
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
  - CHARACTER_WORKFLOW.md
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  hair_color:
    widget: color-palette
    options:
      - { label: "Black", hex: "#1A1A1A" }
      - { label: "Dark Brown", hex: "#3B2314" }
      - { label: "Medium Brown", hex: "#6B4226" }
      - { label: "Light Brown", hex: "#A0724A" }
      - { label: "Auburn", hex: "#922724" }
      - { label: "Red", hex: "#B7410E" }
      - { label: "Dark Blonde", hex: "#C2A868" }
      - { label: "Blonde", hex: "#E8D44D" }
      - { label: "Platinum Blonde", hex: "#F0E6D3" }
      - { label: "Grey", hex: "#8A8A8A" }
      - { label: "White", hex: "#F0F0F0" }
      - { label: "Strawberry Blonde", hex: "#D4A76A" }
  eye_color:
    widget: color-palette
    options:
      - { label: "Dark Blue", hex: "#1A3A5C" }
      - { label: "Dark Brown", hex: "#3D2B1F" }
      - { label: "Indigo", hex: "#2E0854" }
      - { label: "Grey", hex: "#6B7B8D" }
      - { label: "Dark Green", hex: "#1A4D2E" }
      - { label: "Dark Teal", hex: "#1A5C5C" }
      - { label: "Mocha", hex: "#6B4226" }
      - { label: "Honey", hex: "#B8860B" }
      - { label: "Blue", hex: "#4A90D9" }
      - { label: "Green", hex: "#2E8B57" }
      - { label: "Zombie", hex: "#A8B820" }
  skin_tone:
    widget: color-palette
    multi_swatch: true
    options:
      - { label: "Light-Medium Warm Beige", description: "Warm beige tones with peachy undertones", base: "#C9A58C", midtone: "#A67C63", shadow: "#7A5440", highlight: "#E8C9B4" }
      - { label: "Medium-Deep Rich Brown", description: "Rich brown tones with warm red undertones", base: "#A8554A", midtone: "#8B453D", shadow: "#5C2E28", highlight: "#D49A8A" }
      - { label: "Deep Cool Ebony", description: "Deep ebony tones with cool undertones", base: "#5D3C33", midtone: "#422822", shadow: "#2A1814", highlight: "#8A6558" }
  nail_color:
    widget: color-picker
  family:
    widget: entity-selector
    reference_type: character
    max_selections: 10
    relationship_types:
      - { value: "parent", label: "Parent" }
      - { value: "child", label: "Child" }
      - { value: "sibling", label: "Sibling" }
      - { value: "spouse", label: "Spouse" }
      - { value: "cousin", label: "Cousin" }
      - { value: "grandparent", label: "Grandparent" }
      - { value: "grandchild", label: "Grandchild" }
  friends:
    widget: entity-selector
    reference_type: character
    max_selections: 15
    relationship_types:
      - { value: "close", label: "Close Friend" }
      - { value: "casual", label: "Casual Friend" }
      - { value: "acquaintance", label: "Acquaintance" }
      - { value: "best_friend", label: "Best Friend" }
  enemies:
    widget: entity-selector
    reference_type: character
    max_selections: 10
    relationship_types:
      - { value: "rival", label: "Rival" }
      - { value: "nemesis", label: "Nemesis" }
      - { value: "antagonist", label: "Antagonist" }
      - { value: "hostile", label: "Hostile" }
  romantic:
    widget: entity-selector
    reference_type: character
    max_selections: 5
    relationship_types:
      - { value: "partner", label: "Partner" }
      - { value: "ex", label: "Ex" }
      - { value: "crush", label: "Crush" }
      - { value: "complicated", label: "Complicated" }
  primary_location:
    widget: entity-selector
    reference_type: location
    max_selections: 1
  faction:
    widget: entity-selector
    reference_type: faction
    max_selections: 1
  job:
    widget: entity-selector
    reference_type: job
    max_selections: 1
  associated_brands:
    widget: entity-selector
    reference_type: brand
    max_selections: 5
    relationship_types:
      - { value: "employee", label: "Employee" }
      - { value: "customer", label: "Customer" }
      - { value: "owner", label: "Owner" }
      - { value: "sponsor", label: "Sponsor" }
      - { value: "ambassador", label: "Ambassador" }
  birth_year:
    widget: year
    min: 1900
    max: 1998
  death_year:
    widget: year
    min: 1900
    max: 1998

status: "active"

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# WORKFLOW CONFIGURATION
workflow:
  definition: "CHARACTER_WORKFLOW.md"
  default_stage: "concept"
  allow_multiple_active: false
  notifications:
    on_enter:
      - type: "print"
        message: "Character entered stage {{stage_name}}"
    on_exit:
      - type: "archive"
        target: "stage_history/characters/{{character_id}}/{{old_stage}}"
    on_complete:
      - type: "print"
        message: "Character completed {{stage_name}}"
  # Note: Production status and workflow are separate systems
  # - production_status: tracks progress across domains (game, TV, etc.)
  # - workflow: tracks entity lifecycle (concept -> published -> active -> archived)

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