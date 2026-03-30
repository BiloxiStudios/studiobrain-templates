---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "entity"
editable: true
marketplace_eligible: false
id: "[snake_case_name]"
entity_type: "quest"
folder_name: "Quests"
file_prefix: "QST_"
asset_subfolders:
  - images
  - audio
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
status: "active"
workflow:
  definition: "QUEST_WORKFLOW.md"
  default_stage: "concept"
  allow_multiple_active: false
  notifications:
    on_enter:
      - type: "print"
        message: "Quest entered stage {{stage_name}}"
    on_exit:
      - type: "archive"
        target: "stage_history/quests/{{quest_id}}/{{old_stage}}"
    on_complete:
      - type: "print"
        message: "Quest completed {{stage_name}}"
  # Note: Production status and workflow are separate systems
  # - production_status: tracks progress across domains (game, TV, etc.)
  # - workflow: tracks entity lifecycle (concept -> published -> active -> archived)

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"
  game_uefn: "none"
  tv_showrunner: "none"
  notes: ""

# PRIMARY IMAGE
primary_image: ""

# BASIC INFORMATION (REQUIRED)
name: "Quest Display Name"
quest_type: "side"

# ORGANIZATION
parent_campaign: "campaign_id"
quest_category: "investigation"
priority_level: "normal"
estimated_time: "1-2 hours"

# REQUIREMENTS AND PREREQUISITES
required_level: 1
required_skills:
  - "survival"
required_items: []
prerequisite_quests: []

# OBJECTIVES AND TASKS
primary_objectives:
  - objective: "Find the missing person"
    type: "investigation"
secondary_objectives:
  - objective: "Collect evidence"
    type: "collect"
failure_conditions:
  - "Player character dies"
completion_criteria:
  - "Return to quest giver"

# CHARACTERS AND ENTITIES INVOLVED
quest_giver: "character_id"
key_npcs:
  - "npc_id"
target_characters:
  - "target_id"
involved_factions:
  - faction_id: "faction_id"
    role: "allied"

# LOCATIONS AND MOVEMENT
starting_location: "location_id"
quest_locations:
  - "location_id"
destination_location: "location_id"
travel_requirements:
  - "vehicle_required"

# DIALOGUE AND INTERACTION
dialogue_trees:
  - tree_id: "dialogue_id"
    trigger: "quest_start"
interaction_types:
  - "conversation"
  - "investigation"
social_challenges:
  - challenge: "persuade_guard"
    skill: "charisma"

# COMBAT AND CHALLENGES
combat_encounters:
  - encounter: "ambush_point"
    difficulty: "normal"
puzzle_elements:
  - puzzle: "code_lock"
    solution_type: "observation"
skill_challenges:
  - skill: "lockpicking"
    difficulty: 50
environmental_hazards:
  - hazard: "toxic_zone"
    severity: "moderate"

# REWARDS AND CONSEQUENCES
experience_reward: 500
currency_reward: 200
item_rewards:
  - item_id: "item_id"
    quantity: 1
reputation_changes:
  - faction_id: "faction_id"
    change: 10
story_consequences:
  - consequence: "unlocks_new_area"
    trigger: "completion"

# BRANCHING AND CHOICES
player_choices:
  - choice: "spare_enemy"
    outcome: "mercy_path"
choice_consequences:
  - choice: "spare_enemy"
    consequence: "faction_approval"
alternative_solutions:
  - solution: "stealth_approach"
    requirement: "stealth_skill"

# TIME AND SCHEDULING
time_limit: null
time_sensitive: false
seasonal_quest: false
daily_reset: false

# ASSETS AND MEDIA
quest_icon: ""
cutscene_files: []
voice_files: []
sound_effects: []

# CONTENT
description: null
detailed_walkthrough: null
hints_and_tips: null
developer_notes: null
---

# Quest: [Quest Display Name]

Quest description and narrative context.
