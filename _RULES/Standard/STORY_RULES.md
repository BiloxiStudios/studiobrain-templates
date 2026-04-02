---
rule_category: "story"
rule_version: "1.0"
priority: "high"
applies_to: ["campaign", "quest", "event"]
created_date: "2025-01-11"
last_updated: "2025-01-11"
---

# Story Management Rules

## Campaign Rules

### Campaign Structure
- **campaign_id**: Must be lowercase with underscores (e.g., "main_story_arc")
- **campaign_name**: Human-readable display name
- **campaign_type**: Must be one of ["main_story", "side_campaign", "event_chain", "seasonal", "faction"]
- **chapter_count**: Must be between 1 and 20
- **estimated_duration**: Format as "X hours" or "X-Y hours"

### Campaign Relationships
- **protagonist_characters**: Array of valid character_ids
- **supporting_characters**: Array of valid character_ids  
- **antagonist_characters**: Array of valid character_ids
- **primary_locations**: Array of valid location_ids
- **quest_sequence**: Array of quest_ids in chronological order
- **related_events**: Array of event_ids that occur during campaign

### Campaign Validation
- At least one protagonist character required
- Starting location must be valid location_id
- All character references must exist in database
- Campaign cannot reference itself in prerequisites

## Quest Rules

### Quest Structure
- **quest_id**: Must be lowercase with underscores
- **quest_name**: Clear, actionable title
- **quest_type**: Must be one of ["main", "side", "daily", "faction", "hidden", "tutorial"]
- **parent_campaign**: Must reference existing campaign_id if specified
- **estimated_time**: Format as "X-Y minutes" or "X hours"

### Quest Objectives
- **primary_objectives**: At least one objective required
- **objective_id**: Unique within the quest
- **objective_type**: Must be one of ["location", "collect", "eliminate", "escort", "interact", "survive"]
- **completion_criteria**: Must specify measurable success conditions

### Quest Dependencies
- **prerequisite_quests**: Array of quest_ids that must be completed first
- **required_level**: Minimum player level (1-100)
- **required_skills**: Array of skill requirements with minimum levels
- **required_items**: Array of item_ids needed to start quest

### Quest NPCs and Locations
- **quest_giver**: Must be valid character_id
- **key_npcs**: Array of character_ids involved in quest
- **starting_location**: Must be valid location_id
- **quest_locations**: Array of location_ids used during quest

### Quest Rewards
- **experience_reward**: Must be positive integer
- **currency_reward**: Must be non-negative integer
- **item_rewards**: Array with item_id, quantity, and rarity
- **reputation_changes**: Must specify faction_id and change amount

## Event Rules

### Event Structure
- **event_id**: Must be lowercase with underscores
- **event_name**: Descriptive title for the event
- **event_type**: Must be one of ["world", "local", "personal", "faction", "seasonal"]
- **event_scope**: Must be one of ["global", "region", "district", "location", "personal"]

### Event Timing
- **trigger_type**: Must be one of ["scheduled", "random", "conditional", "manual"]
- **trigger_time**: ISO 8601 format if scheduled
- **duration**: Specify how long event lasts
- **recurring**: Boolean for repeating events
- **recurrence_pattern**: Required if recurring is true

### Event Impact
- **affected_locations**: Array of location_ids impacted by event
- **affected_characters**: Array of character_ids involved
- **world_state_changes**: Array of changes with type, value, and duration
- **spawn_modifications**: Changes to enemy/NPC spawning

## Cross-Reference Validation Rules

### Character References
- All character_ids must exist in Characters table
- Character roles must be appropriate for their involvement
- Character availability must align with event timing

### Location References  
- All location_ids must exist in Locations table
- Location capacity must accommodate event requirements
- Location access restrictions must be considered

### Faction References
- All faction_ids must exist in Factions table
- Faction relationships must be logically consistent
- Reputation changes must be within reasonable bounds (-100 to +100)

## Narrative Consistency Rules

### Story Continuity
- Events must occur in logical chronological order
- Character development must be consistent across quests
- World state changes must be permanent unless explicitly temporary
- Dead characters cannot appear in future content

### Tone and Theme
- Content must maintain consistent tone within campaigns
- Themes must align with overall world setting
- Dialogue must match established character voices
- Violence level must be appropriate for target audience

### Pacing Rules
- Main story campaigns: 10-20 hours total
- Side campaigns: 2-8 hours total  
- Individual quests: 15-90 minutes
- Daily quests: 5-15 minutes
- Events: 30 minutes to 4 hours

## Technical Implementation Rules

### Database Constraints
- IDs must be unique within their entity type
- JSON arrays must contain valid entity references
- Timestamps must use UTC timezone
- Status values must be from approved enums

### Performance Guidelines
- Limit objectives per quest: maximum 10 primary, 5 secondary
- Limit NPCs per quest: maximum 20 key NPCs
- Limit locations per quest: maximum 15 locations
- Event duration should not exceed 24 hours real-time

### Asset Requirements
- Campaigns require banner image (campaign_banner)
- Important quests require icon (quest_icon)
- Major events require visual assets
- All dialogue must have backup text versions

## AI Generation Guidelines

### Content Generation Rules
- Generate content that fits established world lore
- Maintain character personality consistency
- Create meaningful choices with consequences
- Balance challenge with player progression

### Cross-Reference Integration
- Always check for existing relationships when generating
- Prefer building on existing characters over creating new ones
- Maintain geographical consistency in location references
- Respect established faction relationships and conflicts

### Quality Standards
- Generated quests must have clear objectives
- Events must have meaningful impact on world state
- Dialogue must advance plot or character development
- All content must serve narrative purpose

## Validation Checklist

### Before Creating Story Content
- [ ] All referenced entities exist in database
- [ ] Timing and scheduling conflicts resolved
- [ ] Prerequisites and dependencies mapped
- [ ] Resource requirements feasible
- [ ] Narrative consistency maintained

### Before Publishing Story Content
- [ ] All objectives tested and completable
- [ ] Rewards balanced and appropriate
- [ ] Dialogue flows tested for all paths
- [ ] Audio/visual assets integrated
- [ ] Localization considerations addressed

### Content Review Process
- [ ] Lore consistency check
- [ ] Character voice validation
- [ ] Technical implementation review  
- [ ] Player experience testing
- [ ] Performance impact assessment