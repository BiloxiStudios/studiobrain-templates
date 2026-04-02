---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "core"
editable: false
marketplace_eligible: false
id: "[snake_case_name]"  # Must match folder name (e.g., find_the_cure)
entity_type: "quest"
folder_name: "Quests"
file_prefix: "QUEST_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
status: "active"  # active, disabled, completed, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Quest Display Name"
quest_type: "main"  # main, side, daily, faction, hidden

# ORGANIZATION
parent_campaign: "campaign_id"  # If part of a campaign
quest_category: "story"  # story, combat, exploration, social, survival
priority_level: "high"  # low, medium, high, critical
estimated_time: "30-45 minutes"

# REQUIREMENTS AND PREREQUISITES
required_level: 10
required_skills:
  - "lockpicking_3"
  - "combat_5"
required_items:
  - "keycard_alpha"
  - "hazmat_suit"
prerequisite_quests:
  - "quest_001"
  - "quest_002"

# OBJECTIVES AND TASKS
primary_objectives:
  - objective_id: "obj_001"
    description: "Reach the laboratory"
    type: "location"
    target: "chemical_plant_lab"
    completed: false
  - objective_id: "obj_002"
    description: "Find the research notes"
    type: "collect"
    target: "research_notes"
    quantity: 5
    completed: false
secondary_objectives:
  - objective_id: "sec_001"
    description: "Save trapped survivors"
    type: "rescue"
    target: "survivor_group"
    optional: true
    completed: false
failure_conditions:
  - "player death"
  - "time limit exceeded"
  - "key npc dies"
completion_criteria:
  - "all primary objectives complete"
  - "return to quest giver"

# CHARACTERS AND ENTITIES INVOLVED
quest_giver: "character_id"
key_npcs:
  - "scientist_jones"
  - "guard_captain"
target_characters:
  - "infected_researcher"
  - "rogue_soldier"
involved_factions:
  - faction_id: "scientists_guild"
    role: "ally"
  - faction_id: "military_remnants"
    role: "hostile"

# LOCATIONS AND MOVEMENT
starting_location: "safe_house"
quest_locations:
  - "chemical_plant_entrance"
  - "laboratory_wing_a"
  - "underground_tunnel"
destination_location: "extraction_point"
travel_requirements:
  - "vehicle_required"
  - "radiation_protection"

# DIALOGUE AND INTERACTION
dialogue_trees:
  - tree_id: "quest_start"
    character: "quest_giver"
  - tree_id: "mid_quest"
    character: "scientist_jones"
interaction_types:
  - "persuasion"
  - "intimidation"
  - "bribery"
social_challenges:
  - challenge: "convince_guard"
    difficulty: "medium"
    skill_check: "charisma"

# COMBAT AND CHALLENGES
combat_encounters:
  - encounter_id: "lab_zombies"
    enemy_type: "infected_scientist"
    count: 10
    difficulty: "medium"
  - encounter_id: "boss_fight"
    enemy_type: "mutated_researcher"
    count: 1
    difficulty: "hard"
puzzle_elements:
  - puzzle_id: "door_code"
    type: "combination"
    difficulty: "medium"
skill_challenges:
  - challenge: "hack_terminal"
    skill: "hacking"
    difficulty: 7
environmental_hazards:
  - hazard: "radiation_zone"
    damage_type: "radiation"
    severity: "moderate"

# REWARDS AND CONSEQUENCES
experience_reward: 5000
currency_reward: 1000
item_rewards:
  - item_id: "cure_sample"
    quantity: 1
    rarity: "legendary"
  - item_id: "lab_keycard"
    quantity: 1
    rarity: "rare"
reputation_changes:
  - faction_id: "scientists_guild"
    change: 100
  - faction_id: "military_remnants"
    change: -50
story_consequences:
  - consequence: "unlocks_new_area"
    description: "Opens access to secret lab"
  - consequence: "npc_relationship"
    description: "Scientist becomes ally"

# BRANCHING AND CHOICES
player_choices:
  - choice_id: "save_or_data"
    description: "Save survivors or retrieve data"
    options:
      - "save_survivors"
      - "get_data"
choice_consequences:
  - choice: "save_survivors"
    result: "gain ally, lose research"
  - choice: "get_data"
    result: "gain cure progress, survivors die"
alternative_solutions:
  - solution: "stealth"
    description: "Sneak past all enemies"
  - solution: "diplomacy"
    description: "Negotiate with faction"

# TIME AND SCHEDULING
time_limit: "72 hours"  # In-game time
time_sensitive: true
seasonal_quest: false
daily_reset: false

# ASSETS AND MEDIA
quest_icon: "media/quest_icon.png"
cutscene_files:
  - "media/quest_intro.mp4"
  - "media/quest_complete.mp4"
voice_files:
  - "media/quest_dialogue.mp3"
sound_effects:
  - "media/alarm_sound.mp3"
  - "media/explosion.mp3"

# CONTENT FIELDS
description: null  # Will be in markdown below
detailed_walkthrough: null  # Will be in markdown below
hints_and_tips: null  # Will be in markdown below
developer_notes: null  # Will be in markdown below
---