---
system_prompt: 'This campaign is a story arc in a comic series or graphic novel. State the premise in one sentence, the number of issues or chapters, and a one-line summary of each issue. Each issue needs its own small conflict, a reveal or reversal, and a final-page hook that makes the reader want the next one. Give a page count per issue and plan in pages and panels: a scene is a number of pages, and a big moment earns a full page. Keep the cast, costumes, and locations consistent with the project. For cover images: one strong central figure or moment, room at the top for a title, bold flat colour, and no lettering in the artwork.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: campaign
rules:
- id: comic_arc_premise
  category: design
  priority: high
  rule: State the arc premise in one sentence.
  validation_type: warning
- id: comic_arc_issue_breakdown
  category: design
  priority: high
  rule: Give the number of issues and a one-line summary for each.
  validation_type: warning
- id: comic_arc_cliffhangers
  category: design
  priority: medium
  rule: End each issue summary with its final-page hook.
  validation_type: suggestion
- id: comic_arc_page_count
  category: design
  priority: medium
  rule: State the page count per issue and keep it the same across the arc.
  validation_type: suggestion
- id: comic_arc_cast_consistency
  category: consistency
  priority: high
  rule: Use characters and locations already recorded in the project and keep their designs unchanged.
  validation_type: warning
---

# Comic Series Arcs

Use the campaign type to plan a comic series: a story arc split into issues, each ending on a page-turn hook.

How it maps onto the campaign type: the campaign is the arc, chapter count is the number of issues, narrative summary is the premise, the quest sequence holds the issues in order, protagonist, supporting and antagonist characters hold the cast, primary locations hold the settings, and the campaign banner is the cover.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the campaign type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
