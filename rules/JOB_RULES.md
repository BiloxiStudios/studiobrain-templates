---
system_prompt: "Generate a job for this project. Match the technology, economy, and factions this project records. Name only brands, places, and factions that exist. Do not assume a decade or a disaster the project has not recorded."
global: false
priority: "high"
entity_type: "job"
template_reference: "JOB_TEMPLATE.md"

rules:
- id: job_001
  category: era_consistency
  priority: critical
  rule: "A job's tools and duties must match the technology this project records. forbidden_elements and required_elements are empty in the starter so the project can fill them. Do not ban a role the project has not banned."
  validation_type: error
  applies_to: [job]
  forbidden_elements: []
  required_elements: []
- id: job_002
  category: brand_association
  priority: high
  rule: "A job that names a brand or a faction must name one that exists in this project, and the duties must match that brand or faction as recorded."
  validation_type: error
  applies_to: [job]

- id: job_003
  category: salary_realism
  priority: medium
  rule: "Pay must be consistent with the economy and the job's rank as this project records them."
  validation_type: warning
  applies_to: [job]

- id: job_004
  category: career_progression
  priority: medium
  rule: Career progression paths must be logical and realistic - advancement requires skill development, lateral moves should be to similar-level positions
  validation_type: warning
  applies_to: [job]

- id: job_005
  category: faction_alignment
  priority: high
  rule: "A job tied to a faction must match the work this project records for that faction."
  validation_type: warning
  applies_to: [job]
- id: job_006
  category: outbreak_adaptation
  priority: high
  rule: "If this project records a disruption that changes work, say how this job changes, using one of obsolete, reduced, normal, or essential. Do not assume a disaster the project has not recorded."
  validation_type: warning
  applies_to: [job]
  impact_levels: ["obsolete - job no longer exists", "reduced - fewer positions available", "normal - business as usual", "essential - critical for survival"]

- id: job_007
  category: workplace_hazards
  priority: medium
  rule: "Hazards must follow from the work and the conditions this project records. Do not add a danger the project has not recorded."
  validation_type: info
  applies_to: [job]

- id: job_008
  category: automation_risk
  priority: medium
  rule: "Automation risk must match the technology this project records. Do not assume a particular decade's machines."
  validation_type: info
  applies_to: [job]
  low_risk: ["creative work", "customer service", "management", "skilled trades"]
  moderate_risk: ["assembly line", "data entry", "basic calculations", "inventory management"]
  high_risk: ["repetitive manual tasks", "dangerous work", "24/7 monitoring"]

- id: job_009
  category: cultural_status
  priority: medium
  rule: "How a job is regarded must match the social order this project records. Do not assume which work is prestigious."
  validation_type: info
  applies_to: [job]

- id: job_010
  category: narrative_hooks
  priority: high
  rule: "Story access a job grants must follow from the duties this project records for it. Do not invent a secret."
  validation_type: warning
  applies_to: [job]

- id: job_011
  category: timeline_validation
  priority: critical
  rule: "Availability dates and career steps must be in chronological order and inside the years this project uses."
  validation_type: error
  applies_to: [job]
  required_tools: ["check_temporal_conflicts", "calculate_duration"]

- id: job_012
  category: entity_validation
  priority: critical
  rule: Before referencing brands (primary_brand, associated_brands), locations (work_locations), characters (example employees, managers), or factions (faction_controlled), use validation tools to verify they exist. Use check_brand_exists, check_location_exists, check_character_exists, and validate_all_references. Never reference non-existent entities
  validation_type: warning
  applies_to: [job]
  required_tools: ["check_brand_exists", "check_location_exists", "check_character_exists", "validate_all_references"]

- id: job_013
  category: skills_realism
  priority: medium
  rule: "Skills and certifications must be ones this project's era would actually teach. era_appropriate and era_inappropriate are empty in the starter so the project can fill them."
  validation_type: warning
  applies_to: [job]
  era_appropriate: []
  era_inappropriate: []
- id: job_014
  category: dark_humor
  priority: medium
  rule: "The voice of a job description must match the tone this project records. Do not add humor the project has not asked for."
  validation_type: info
  applies_to: [job]
---

# Job guidance

These rules check structure and consistency. They do not name a setting.

A job's tools, duties, pay, training, and standing must match the technology, economy, and social order this project records. The starter's forbidden_elements, required_elements, era_appropriate, and era_inappropriate lists are empty so the project can fill them. A job that names a brand, a faction, or a workplace must name one that exists, and the duties must match that entity.

Career steps must be in a believable order. If the project records a disruption, mark the job obsolete, reduced, normal, or essential. Do not assume a disaster. Story access must follow from the duties as recorded.

Dates must sit inside the project's years.
