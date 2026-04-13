---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "document"
ui_icon: "BookText"
ui_color: "#A855F7"
editable: true
marketplace_eligible: true
id: "[snake_case_name]"  # Must match universe_id
entity_type: "story_bible"
folder_name: "Story Bibles"
file_prefix: "STORY_"
asset_subfolders:
  - images
  - concept_art
  - reference_scripts
universe_id: "universe_id"  # References universe configuration
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules: []
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  narrative_type:
    widget: dropdown
    options: ["Linear", "Branching", "Episodic", "Environmental", "Non-linear"]
  tonal_quality:
    widget: dropdown
    options: ["Dark", "Light", "Horror", "Comedic", "Dramatic", "Whimsical", "Grim", "Hopeful"]
  target_audience_age:
    widget: dropdown
    options: ["Everyone", "Teen", "Mature 17+", "Adult 18+"]

status: "active"  # active, development, archived

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Story Bible Display Name"
version: "1.0"
primary_medium: "video_game"  # video_game, film, animation, literature, mixed

# LOGLINE
logline: ""  # One-sentence hook
premise: null  # 1-2 paragraph core concept
themes:
  - null
motifs:
  - null

# SYNOPSIS
act_one_setup: null
act_one_conflict: null
act_two_rising_action: null
act_two_climax: null
act_three_resolution: null
after_credits: null  # Post-credits or sequel hooks

# CHARACTERS
protagonists:
  - name: null
    description: null
    backstory: null
    arc: null
    visual_reference: null
antagonists:
  - name: null
    description: null
    motivation: null
    weakness: null
    visual_reference: null
supporting_characters:
  - name: null
    role: null  # Mentor, Comic relief, Love interest, Ally, Neutral
    relationship_to_protagonist: null

# PLOT ARCS
main_arc: null
sub_arcs:
  - arc_name: null
    description: null
    resolution: null
character_arcs:
  - character: null
    starting_point: null
    transformation: null
    resolution: null

# SETTING
time_period: null  # Historical, Future, Contemporary, Fantasy, Sci-Fi
locations:
  - name: null
    significance: null
    atmosphere: null
world_building_notes: null

# DIALOGUE STYLE
tone_guidelines: null
dialect_speech_patterns: null
narrative_voice: null  # First person, Third person limited, Omniscient
exposition_handling: null  # Cutscenes, Environmental, Dialogue, Logs/Journals

# THEMATIC ELEMENTS
core_conflicts: null
moral_ambiguity: null  # Black & white, Shades of gray, Player choice
endings: null  # Single, Multiple, Player-determined

# NARRATIVE STRUCTURE
branching_strategy: null  # None, Key choices, Permutations, Emergent
player_agency_level: null  # None, Minor, Significant, Defining
lore_delivery_method: null  # Direct, Environmental, Collectible, Unlockable

# CONTENT FIELDS
character_profiles: null  # Will be in markdown below
detailed_synopsis: null  # Will be in markdown below
dialogue_samples: null  # Will be in markdown below
narrative_notes: null  # Will be in markdown below
---
