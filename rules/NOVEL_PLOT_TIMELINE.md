---
system_prompt: 'This timeline entry is one scene or plot beat in a novel. State whose point of view it is told from, what that character wants in the scene, what stands in the way, and how things are different at the end. Every beat must be caused by an earlier one and must cause a later one: use therefore and but, never and then. Mark the major structural beats (opening image, inciting incident, midpoint reversal, lowest point, climax, resolution) and keep the story order and the in-world date separate when they differ.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: timeline
rules:
- id: novel_plot_pov
  category: design
  priority: high
  rule: Name the point-of-view character for the beat.
  validation_type: warning
- id: novel_plot_goal_obstacle
  category: design
  priority: high
  rule: State what the point-of-view character wants in this scene and what opposes them.
  validation_type: warning
- id: novel_plot_change
  category: design
  priority: high
  rule: 'State what has changed by the end of the beat: a fact, a relationship, or a decision.'
  validation_type: warning
- id: novel_plot_causality
  category: consistency
  priority: high
  rule: Link the beat to the earlier beat that causes it and the later beat it makes possible.
  validation_type: warning
- id: novel_plot_structure_mark
  category: design
  priority: low
  rule: Label the beat if it is a major structural point such as the inciting incident, midpoint, or climax.
  validation_type: suggestion
---

# Novel Plot Timeline

Use the timeline type to outline a novel: each entry is a scene or beat with a cause, a change and a cost.

How it maps onto the timeline type: each entry is a scene or beat, sequence order is its place in the book, timestamp is the in-world date, prerequisites and enables hold cause and effect, characters and locations involved hold the cast and setting, relationship changes and consequences analysis hold what the beat changes, and importance level marks the major turning points.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the timeline type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
