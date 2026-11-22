---
system_prompt: 'This campaign is for a tabletop roleplaying game run by a game master for a group of players. State the starting level or experience of the characters, the number of sessions expected, and the hook that gives a mixed party a reason to act together. Outline it as situations, not a script: for each stage give a location, who is there and what they want, what happens if the players do nothing, and at least two ways through. Give the antagonist a plan with a timetable. Include rewards and one decision point where the players change the ending. Stay rules-neutral unless the project names a game system, and do not reproduce any published adventure.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: campaign
rules:
- id: ttrpg_campaign_hook
  category: design
  priority: high
  rule: State a hook that gives every kind of player character a reason to take part.
  validation_type: warning
- id: ttrpg_campaign_scope
  category: design
  priority: medium
  rule: State the starting level or experience and the expected number of sessions.
  validation_type: suggestion
- id: ttrpg_campaign_situations
  category: design
  priority: high
  rule: Describe each stage as a situation with people and goals, not a fixed sequence of player actions.
  validation_type: warning
- id: ttrpg_campaign_villain_plan
  category: design
  priority: high
  rule: Give the antagonist a goal and the steps that happen if nobody stops them.
  validation_type: warning
- id: ttrpg_campaign_choice
  category: design
  priority: medium
  rule: Include at least one decision that leads to different endings.
  validation_type: suggestion
- id: ttrpg_campaign_system
  category: consistency
  priority: medium
  rule: Use the game system the project names, or stay rules-neutral if it names none.
  validation_type: warning
---

# Tabletop RPG Campaigns

Campaigns a game master can run at the table: a hook, sessions, choices that matter and room to improvise.

How it maps onto the campaign type: narrative summary holds the hook, chapter count holds the number of sessions or acts, difficulty level and prerequisites hold the starting level, the quest sequence holds the adventures in order, optional quests hold side adventures, antagonist characters and involved factions hold the opposition, branching paths and multiple endings hold the player choices, and rewards hold treasure and advancement.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the campaign type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
