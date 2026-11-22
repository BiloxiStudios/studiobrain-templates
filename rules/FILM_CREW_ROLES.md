---
system_prompt: 'This job is a role on a film, television, or animation production. State the department (direction, camera, lighting, grip, art, costume, hair and make-up, sound, production, post-production, animation), who the role reports to, and who it manages. Describe what the role delivers during preparation, on a shooting day, and after the shoot, and the documents it produces or relies on, such as a call sheet, shot list, or continuity report. Scale the role to the size of the production the project describes: on a small crew one person may cover several roles. Use standard industry job titles.'
global: false
priority: medium
ruleset_kind: theme
suggested_entity_type: job
rules:
- id: film_crew_department
  category: design
  priority: high
  rule: State the department and the standard job title.
  validation_type: warning
- id: film_crew_reporting
  category: design
  priority: high
  rule: State who the role reports to and who reports to it.
  validation_type: warning
- id: film_crew_deliverables
  category: design
  priority: medium
  rule: List what the role delivers in preparation, during the shoot, and in post-production.
  validation_type: suggestion
- id: film_crew_documents
  category: design
  priority: low
  rule: Name the paperwork the role creates or works from.
  validation_type: suggestion
- id: film_crew_scale
  category: consistency
  priority: medium
  rule: Match the role to the production size in the project, and say which roles are combined on a small crew.
  validation_type: suggestion
---

# Film Crew Roles

Use the job type for production crew: department, who they answer to, and what they deliver each shooting day.

How it maps onto the job type: department holds the crew department, reports to and manages hold the chain of command, collaborates with holds the roles it works beside, daily tasks and key responsibilities hold the deliverables, required skills hold the craft skills, work schedule holds shooting hours, and safety equipment and known hazards hold on-set safety.

This is a themed ruleset. Install it from the Marketplace, then choose Apply and pick the job type. Its rules and system prompt are added to the rules that type already has, so it can be combined with other themes.
