---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "core"
editable: false
marketplace_eligible: false
id: "unique_lowercase_id"  # Must match folder name (e.g., quest_001_intro)
entity_type: "dialogue"
folder_name: "Dialogues"
file_prefix: "DIAL_"
asset_subfolders:
  - images
  - audio
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
status: "draft"  # draft, active, archived

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Dialogue Tree Display Name"
tree_type: "conversation"  # conversation, interrogation, negotiation, cutscene, internal_monologue

# CONTEXT AND RELATIONSHIPS
quest_id: "quest_id"        # If part of a quest
campaign_id: "campaign_id"  # If part of a campaign  
event_id: "event_id"        # If triggered by an event
location_id: "location_id"  # Where this dialogue takes place

# PARTICIPANTS
participants:
  - "character_id1"
  - "character_id2"
  - "player"
primary_speaker: "character_id1"  # Main character or "player"

# TREE CONFIGURATION
branching_complexity: "medium"  # simple, medium, complex
estimated_duration: "5-10 minutes"
max_depth: 8  # Maximum number of dialogue exchanges
multiple_paths: true  # Whether dialogue has branching paths

# CONDITIONAL LOGIC
prerequisites:
  - condition: "quest_progress"
    value: "started"
  - condition: "character_relationship"
    character: "character_id1"
    value: "friendly"
  - condition: "player_level"
    value: "10+"

unlock_conditions:
  - condition: "faction_reputation"
    faction: "scientists_guild"
    value: "50+"
    unlocks: ["diplomatic_path"]
  - condition: "has_item"
    item: "evidence_folder"
    unlocks: ["accusation_path"]

# WORLD INTEGRATION
atmosphere: "tense"  # casual, tense, formal, hostile, friendly, mysterious
background_music: "tension_theme_01"
lighting: "dim_amber"  # Lighting mood for the scene
camera_style: "close_up"  # close_up, medium_shot, wide_shot

# GAME MECHANICS
skill_checks:
  - skill: "persuasion"
    difficulty: 7
    success_path: "convince_guard"
    failure_path: "guard_suspicious"
  - skill: "intimidation"  
    difficulty: 5
    success_path: "guard_backs_down"
    failure_path: "guard_calls_backup"

reputation_effects:
  - faction: "scientists_guild"
    path: "help_scientists"
    change: 25
  - faction: "military_remnants"
    path: "report_to_military"
    change: 15

item_requirements:
  - path: "show_evidence"
    required_items: ["evidence_folder", "witness_statement"]
  - path: "bribe_guard"
    required_items: ["currency:500"]

# DIALOGUE STRUCTURE
root_node: "greeting"  # Starting node ID
node_count: 15  # Total number of dialogue nodes
choice_count: 8  # Total number of player choices
ending_count: 4  # Number of possible endings

# VISUAL AND AUDIO
visual_effects:
  - node: "revelation_moment"
    effect: "screen_flash"
  - node: "dramatic_pause"
    effect: "zoom_in"

voice_acting:
  character_id1:
    voice_actor: "actor_name"
    voice_style: "gruff_veteran"
    emotional_range: ["angry", "sad", "determined"]
  character_id2:
    voice_actor: "actor_name"
    voice_style: "nervous_scientist"
    emotional_range: ["worried", "excited", "fearful"]

# EXPORT AND VERSIONING
auto_export: true  # Automatically export to markdown on save
json_backup: true  # Keep JSON structure backup
localization_ready: false  # Ready for translation

# CONTENT FIELDS
description: null  # Will be in markdown below
dialogue_script: null  # Will be in markdown below
implementation_notes: null  # Will be in markdown below
---

# Dialogue Tree Description

[High-level description of this dialogue tree, its purpose in the story, and what outcomes it can lead to]

## Context and Setup

[Description of the situation that leads to this dialogue. What has happened before this conversation begins?]

## Dialogue Flow

### Node: greeting
**Speaker**: Character Name (emotion: neutral)
**Text**: "Welcome to our facility. I wasn't expecting visitors today."
**Type**: statement
**Position**: (0, 0)  <!-- Visual editor coordinates -->

#### Player Choices:
1. **[Polite Introduction]** → Node: polite_response
   - Text: "I'm here on official business. May I speak with you?"
   - Requirements: None
   - Consequences: reputation_change(scientists_guild, +5)

2. **[Demanding Entry]** → Node: aggressive_response  
   - Text: "I need to get inside immediately. This is urgent."
   - Requirements: None
   - Consequences: relationship_change(character_id, -10)

3. **[Show Credentials]** → Node: official_response
   - Text: "Here are my credentials. I'm investigating the recent incidents."
   - Requirements: has_item(official_badge)
   - Consequences: unlock_path(investigation_branch)

### Node: polite_response
**Speaker**: Character Name (emotion: pleased)
**Text**: "Of course! I appreciate your courtesy. What can I help you with?"
**Type**: statement
**Position**: (-200, 100)

#### Player Choices:
1. **[Ask about incidents]** → Node: incident_discussion
2. **[Request facility tour]** → Node: tour_offer
3. **[Inquire about security]** → Node: security_concerns

### Node: aggressive_response
**Speaker**: Character Name (emotion: defensive)
**Text**: "Hold on there! You can't just demand entry. Who do you think you are?"
**Type**: question
**Position**: (200, 100)

#### Skill Check: Intimidation (Difficulty 6)
- **Success** → Node: intimidation_success
- **Failure** → Node: intimidation_failure

[Continue with all dialogue nodes...]

## Dialogue Endings

### Ending 1: Peaceful Resolution
- **Requirements**: Maintained positive relationships
- **Outcome**: Gained ally, received key information
- **Reputation**: Scientists Guild +25
- **Items Gained**: facility_access_card

### Ending 2: Forced Entry
- **Requirements**: Failed diplomatic options
- **Outcome**: Gained entry but made enemies
- **Reputation**: Scientists Guild -15
- **Consequences**: security_alert_triggered

### Ending 3: Compromise Solution
- **Requirements**: Mixed diplomatic success
- **Outcome**: Limited access granted
- **Reputation**: Scientists Guild +10
- **Items Gained**: temporary_visitor_pass

### Ending 4: Complete Failure
- **Requirements**: All diplomatic options failed
- **Outcome**: Denied entry, must find alternate route
- **Reputation**: Scientists Guild -25
- **Quest Update**: investigate_alternate_entrance

## Character Development

### [Character Name]
[How this dialogue reveals or develops this character's personality, motivations, or background]

### Player Character
[What the player can learn about their character through the dialogue choices available]

## Branching Analysis

### Key Decision Points:
1. **Initial Approach** (Node: greeting)
   - Sets the tone for the entire conversation
   - Affects all subsequent relationship modifiers

2. **Evidence Revelation** (Node: show_evidence)
   - Only available with specific items
   - Dramatically changes available paths

3. **Final Negotiation** (Node: final_offer)
   - Player's reputation determines available options
   - Multiple paths to similar outcomes

### Narrative Paths:
- **Diplomatic Path**: High charisma, respectful choices
- **Aggressive Path**: Intimidation and force
- **Investigative Path**: Evidence-based approach
- **Sneaky Path**: Deception and misdirection

## Implementation Notes

### Technical Requirements:
- Skill check system integration
- Item inventory checking
- Reputation tracking
- Character relationship system

### Performance Considerations:
- Pre-load voice files for smoother playback
- Cache frequently accessed dialogue branches
- Optimize UI updates during long conversations

### Testing Checklist:
- [ ] All dialogue paths lead to valid endings
- [ ] Skill checks function correctly
- [ ] Item requirements properly validated
- [ ] Reputation changes apply correctly
- [ ] Visual positioning works in editor
- [ ] Voice acting synchronized with text
- [ ] Localization strings properly tagged

## AI Generation Notes

[Guidelines for AI systems on how to use this dialogue tree, what themes to emphasize, and how it connects to other story elements]

## Writer Notes

[Internal notes for writers and designers about this dialogue tree's role in the larger narrative]