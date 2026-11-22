---
system_prompt: 'This event is a meal: a dinner party, a holiday feast, a weekly family supper, a tasting menu, or a picnic. State the occasion, the number of guests, and the menu as courses in serving order, using dishes already in the project where they exist. Give a timeline that works backward from the time people sit down, so the cook knows what to start when. Balance the menu: vary texture, richness, colour, and cooking method, and do not ask one oven to do two temperatures at once. For images and video: a set table seen from above or from a guest''s seat, warm low light or daylight, dishes shown family-style, hands reaching in.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: event
rules:
- id: meal_occasion_guests
  category: design
  priority: high
  rule: State the occasion and the number of guests.
  validation_type: warning
- id: meal_courses
  category: design
  priority: high
  rule: List the courses in serving order and name the dish for each.
  validation_type: warning
- id: meal_timeline
  category: design
  priority: medium
  rule: Give a preparation timeline counted back from serving time.
  validation_type: suggestion
- id: meal_balance
  category: balance
  priority: medium
  rule: Avoid repeating a main ingredient or cooking method in consecutive courses.
  validation_type: suggestion
- id: meal_dietary
  category: design
  priority: medium
  rule: State any dietary needs at the table and which dishes meet them.
  validation_type: suggestion
---

# Meals and Menus

Use the event type to plan a meal: the occasion, the courses in order, the timing and who is at the table.

How it maps onto the event type: the event is the meal, the event phases are the courses, duration and start time hold the schedule, affected characters are the guests and cook, affected locations are the kitchen and table, and the event script holds the preparation timeline. Trigger and spawn fields can be left empty.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the event type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
