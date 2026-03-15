---
# METADATA (REQUIRED)
# NOTE: Section headers (like "# METADATA") are for documentation only - DO NOT include them as literal content
template_version: "1.0"
id: "unique_lowercase_id"  # Must match folder name (e.g., nerdent_technician)
entity_type: "job"
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
status: "active"  # active, deprecated, seasonal, archived, draft

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"        # concept, in_progress, needs_work, narrative_done, art_done, complete
  game_uefn: "none"         # none, planned, in_progress, review, published, live
  tv_showrunner: "none"     # none, planned, in_progress, review, episode, current, archived
  notes: ""                 # Production notes

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Job Display Name"  # e.g., "Nerdent Technician"
job_category: "technical"  # technical, service, management, security, creative, labor, sales
description: "Detailed description of the job role and responsibilities"
department: null  # Department within organization

# EMPLOYMENT DETAILS
employment_type: "full_time"  # full_time, part_time, contract, seasonal, volunteer
experience_level: "entry"  # entry, mid, senior, executive
salary_range: "$30,000 - $45,000"  # Optional salary information
benefits: []  # List of benefits
  # - "health_insurance"
  # - "equipment_discounts"

# BRAND/ORGANIZATION ASSOCIATION
primary_brand: null  # Brand ID that primarily offers this job
associated_brands: []  # Other brands that may offer similar positions
  # - brand_id: "circuitshack"
  #   title_variation: "Tech Support Specialist"
faction_controlled: null  # If controlled by a specific faction

# REQUIREMENTS
required_skills: []  # Skills needed for this job
  # - skill: "electronics_repair"
  #   level: 5
  #   category: "technical"
required_certifications: []  # Certifications needed
education_level: "high_school"  # none, high_school, trade, associate, bachelor, master, phd
physical_requirements: []  # Physical demands
  # - "can_lift_50lbs"
  # - "comfortable_with_heights"

# JOB RESPONSIBILITIES
daily_tasks: []  # What someone in this role does daily
  # - "diagnose_hardware_issues"
  # - "assist_customers_with_technical_problems"
key_responsibilities: []  # Major responsibilities
  # - "maintain_store_equipment"
  # - "train_new_technicians"
performance_metrics: []  # How success is measured
  # - metric: "customer_satisfaction"
  #   target: "95%"

# CAREER PROGRESSION
entry_positions: []  # Jobs that lead to this one
  # - "retail_associate"
  # - "intern_technician"
advancement_paths: []  # Where this job can lead
  # - "senior_technician"
  # - "department_supervisor"
lateral_moves: []  # Similar level positions
  # - "sales_specialist"

# WORKPLACE DETAILS
work_locations: []  # Where this job is performed
  # - location_id: "circuitshack_downtown"
  #   frequency: "primary"
work_schedule: "standard_business"  # standard_business, shift_work, flexible, remote
travel_required: false
uniform_required: true
uniform_details: "Company polo shirt, khakis, safety equipment"

# HAZARDS & RISKS
safety_rating: "low"  # low, moderate, high, extreme
known_hazards: []  # Workplace dangers
  # - "electrical_equipment"
  # - "customer_confrontations"
safety_equipment: []  # Required protective gear
  # - "safety_glasses"
  # - "anti_static_wrist_strap"

# WORLD CONTEXT
cultural_status: "respectable"  # prestigious, respectable, neutral, stigmatized
job_availability: "common"  # rare, uncommon, common, abundant
automation_risk: "low"  # low, moderate, high (how likely to be replaced by AI/robots)
outbreak_impact: "essential"  # obsolete, reduced, normal, essential (post-outbreak relevance)

# NARRATIVE ELEMENTS
job_stereotypes: []  # Common perceptions about this job
  # - "tech nerds with poor social skills"
  # - "helpful problem solvers"
character_archetypes: []  # Types of characters who take this job
  # - "eager_young_graduate"
  # - "experienced_repair_veteran"
story_hooks: []  # Plot opportunities this job creates
  # - "discovers_corporate_conspiracy_through_repair_logs"
  # - "becomes_unlikely_hero_using_technical_skills"

# RELATIONSHIPS
reports_to: []  # Superior positions
  # - "store_manager"
  # - "technical_supervisor"
manages: []  # Subordinate positions
  # - "junior_technician"
  # - "repair_intern"
collaborates_with: []  # Peer positions
  # - "sales_associate"
  # - "customer_service"

# ASSETS & MEDIA
job_icon: "images/jobs/technician_icon.png"
uniform_reference: "images/uniforms/nerdent_uniform.png"
workplace_photos: []
  # - "images/workspaces/repair_station.png"

# GAME MECHANICS
unlock_requirements: []  # What's needed to access this job
  # - quest_id: "complete_orientation"
  # - skill_id: "electronics"
  #   level: 3
job_benefits_gameplay: []  # In-game benefits of having this job
  # - benefit_type: "discount"
  #   target: "electronics"
  #   amount: 15
quest_opportunities: []  # Quests available to characters with this job
  # - "corporate_espionage_mission"
  # - "customer_crisis_management"
---

## Job Description

[Write a comprehensive description of what this job entails, including:]
- **Day-to-Day Responsibilities**: What does someone in this role actually do?
- **Skills and Expertise**: What knowledge and abilities are required?
- **Work Environment**: Where and how is this work performed?
- **Cultural Context**: How is this job viewed in the City of Brains universe?

## Career Path

[Describe how someone gets into this job and where it can lead]

### Entry Requirements
- Educational background needed
- Previous experience or training
- Personality traits that help

### Advancement Opportunities
- Next level positions within the same brand
- Lateral moves to other companies
- Skills that open new career paths

## Brand Variations

[How different brands handle this same job role]

### CircuitShack Nerdents
- Company-specific training programs
- Unique uniform and equipment
- Special perks and company culture

### [Other Brand] Variations
- How other companies structure similar roles
- Different emphases or specializations

## Workplace Culture

[The social dynamics and expectations of this job]

### Team Dynamics
- How teams are structured
- Communication patterns
- Collaboration requirements

### Performance Expectations
- What success looks like
- How performance is measured
- Rewards and consequences

## Story Integration

[How this job fits into the larger narrative]

### Pre-Outbreak Role
- Economic importance
- Social dynamics
- Daily challenges

### Post-Outbreak Adaptation
- How the job changes during crisis
- New responsibilities or priorities
- Survival relevance

## Character Examples

[Examples of characters who might have this job]

### The Veteran
- Long-time employee with deep knowledge
- Mentor figure for newer workers
- Resistant to change but highly skilled

### The Newcomer
- Recent hire with fresh perspectives
- Still learning the ropes
- Eager to prove themselves

## File Structure

Each job should have:
```
Jobs/
├── {job_name}/
│   ├── JOB_{job_name}.md        # Main job sheet (this template)
│   ├── images/
│   │   ├── job_icon.png         # Job icon for UI
│   │   ├── uniform_reference.png # Uniform/dress code reference
│   │   └── workplace_photos/    # Photos of typical workplaces
│   ├── data/
│   │   └── requirements.json    # Machine-readable job requirements
│   └── comfy_workflows/         # AI generation workflows
│       └── character_generator.json
```

## Version History
- v1.0: Initial job template with brand associations and career progression

## Notes
- Always follow the naming convention: `JOB_` prefix for markdown files
- Use snake_case for all IDs and file names
- Consider how jobs change during different story phases
- Link jobs to specific brands and factions when appropriate
- Think about how automation and AI impact different roles