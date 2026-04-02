---
system_prompt: "Generate jobs for the City of Brains universe that reflect the economic reality of a 1990s retro-futuristic dystopia. Create employment opportunities that are grounded in the world's technology level, corporate culture, and post-outbreak survival needs. Jobs should feel authentic to the setting while incorporating the dark humor and absurdity of corporate excess. Consider how each job contributes to the faction ecosystem, brand identity, and character motivations."
global: false
priority: "high"
entity_type: "job"
template_reference: "JOB_TEMPLATE.md"

rules:
- id: job_001
  category: era_consistency
  priority: critical
  rule: Jobs must reflect 1990s technology and work culture - no social media managers, app developers, or roles requiring post-2000s technology
  validation_type: error
  applies_to: [job]
  forbidden_elements: ["smartphone apps", "social media", "cloud computing", "cryptocurrency", "streaming services"]
  required_elements: ["paper filing", "fax machines", "analog processes", "in-person service", "manual systems"]

- id: job_002
  category: brand_association
  priority: high
  rule: Jobs must be associated with existing brands or factions, and job responsibilities must align with brand values and business model
  validation_type: error
  applies_to: [job]
  examples: ["CircuitShack Nerdent - technical support", "Double Dip Vendor - food service", "Kraken Mechanic - vehicle repair"]

- id: job_003
  category: salary_realism
  priority: medium
  rule: Salary ranges must reflect 1990s economic reality and job hierarchy - entry level jobs pay less, corporate positions pay more, but adjusted for dystopian inflation
  validation_type: warning
  applies_to: [job]
  examples: ["Entry retail: $15k-25k", "Mid technical: $30k-50k", "Senior management: $60k-100k", "Corporate executive: $100k+"]

- id: job_004
  category: career_progression
  priority: medium
  rule: Career progression paths must be logical and realistic - advancement requires skill development, lateral moves should be to similar-level positions
  validation_type: warning
  applies_to: [job]
  examples: ["Retail Associate → Senior Associate → Department Manager", "Junior Technician → Technician → Senior Technician → Technical Supervisor"]

- id: job_005
  category: faction_alignment
  priority: high
  rule: Jobs controlled by factions must reflect faction ideology, resources, and territory - Bears control tech jobs, Krakens control mechanics, Dragons control corporate, Flamingos control nightlife/smuggling
  validation_type: warning
  applies_to: [job]
  faction_specializations:
    bears: ["technology", "infrastructure", "network administration", "power grid maintenance"]
    krakens: ["mechanics", "transport", "logistics", "construction"]
    dragons: ["marketing", "public relations", "corporate management", "media"]
    flamingos: ["entertainment", "fashion", "smuggling", "nightlife"]

- id: job_006
  category: outbreak_adaptation
  priority: high
  rule: Jobs must specify outbreak_impact - how does this role change after the Double Dip disaster? Essential jobs become more dangerous, luxury jobs become obsolete
  validation_type: warning
  applies_to: [job]
  impact_levels: ["obsolete - job no longer exists", "reduced - fewer positions available", "normal - business as usual", "essential - critical for survival"]

- id: job_007
  category: workplace_hazards
  priority: medium
  rule: Safety ratings and hazards must be realistic for the dystopian setting - even "safe" jobs have risks due to corporate negligence and outbreak dangers
  validation_type: info
  applies_to: [job]
  examples: ["Office work: moderate (poor ventilation, zombie customers)", "Mechanic: high (chemical exposure, equipment failure)", "Security: extreme (combat, infection risk)"]

- id: job_008
  category: automation_risk
  priority: medium
  rule: Automation risk should reflect 1990s technology capabilities - robots are primitive, AI is limited, most jobs still require human workers
  validation_type: info
  applies_to: [job]
  low_risk: ["creative work", "customer service", "management", "skilled trades"]
  moderate_risk: ["assembly line", "data entry", "basic calculations", "inventory management"]
  high_risk: ["repetitive manual tasks", "dangerous work", "24/7 monitoring"]

- id: job_009
  category: cultural_status
  priority: medium
  rule: Job cultural status should reflect City of Brains social hierarchy and corporate values - corporate jobs are prestigious, manual labor is stigmatized, creative work depends on brand association
  validation_type: info
  applies_to: [job]
  examples: ["Corporate executive: prestigious", "Brand manager: respectable", "Retail worker: neutral", "Waste disposal: stigmatized"]

- id: job_010
  category: narrative_hooks
  priority: high
  rule: Jobs should create story opportunities - access to restricted areas, knowledge of secrets, connection to key characters, involvement in conspiracies
  validation_type: warning
  applies_to: [job]
  examples: ["Technician discovers corporate cover-up through repair logs", "Security guard witnesses illegal experiments", "Janitor finds evidence of conspiracy", "Sales associate becomes unlikely hero"]

- id: job_011
  category: timeline_validation
  priority: critical
  rule: Verify that job availability dates, historical context, and career progression timelines are chronologically consistent and occur before or during 1998 (current game year)
  validation_type: error
  applies_to: [job]
  required_tools: ["check_temporal_conflicts", "calculate_duration"]

- id: job_012
  category: entity_validation
  priority: critical
  rule: Before referencing brands (primary_brand, associated_brands), locations (work_locations), characters (example employees, managers), or factions (faction_controlled), use validation tools to verify they exist. Use check_brand_exists, check_location_exists, check_character_exists, and validate_all_references. Never reference non-existent entities
  validation_type: error
  applies_to: [job]
  required_tools: ["check_brand_exists", "check_location_exists", "check_character_exists", "validate_all_references"]

- id: job_013
  category: skills_realism
  priority: medium
  rule: Required skills and certifications must be appropriate for 1990s setting - no coding bootcamps or online certifications, focus on trade schools, apprenticeships, and on-the-job training
  validation_type: warning
  applies_to: [job]
  era_appropriate: ["high school diploma", "trade school certificate", "company training program", "apprenticeship", "college degree"]
  era_inappropriate: ["online certification", "coding bootcamp", "social media marketing degree", "app development course"]

- id: job_014
  category: dark_humor
  priority: medium
  rule: Job descriptions should incorporate City of Brains dark humor - corporate doublespeak, absurd requirements, hilariously dangerous conditions presented as normal
  validation_type: info
  applies_to: [job]
  examples: ["Must be comfortable working with mildly radioactive materials", "Occasional zombie encounters (PPE provided)", "Competitive salary (for hazard pay)", "Great benefits (if you survive probation)"]
---

# Job Creation in the City of Brains Universe

## The Employment Landscape

Jobs in the City of Brains reflect a world where corporate excess meets survival horror. The 1990s retro-futuristic setting means technology is primitive by modern standards but advanced by period standards. The Double Dip outbreak has fundamentally altered what work means - some jobs become obsolete, others become essential, and many become significantly more dangerous.

### Era-Appropriate Employment

This is a world of:
- **Fax machines and filing cabinets**, not cloud storage
- **In-person customer service**, not chatbots
- **Manual inventory systems**, not automated warehouses
- **Analog processes**, not digital workflows
- **Trade skills**, not app development

### The 1990s Work Culture

Jobs must capture the corporate culture of the 1990s:
- Rigid hierarchies with clear reporting structures
- Dress codes and uniform requirements
- Time clocks and punch cards
- Employee handbooks thick with policies
- Performance reviews based on arbitrary metrics
- Corporate jargon and mission statements
- "Team building" that's thinly veiled surveillance

### Brand-Specific Employment

Every major brand has its own employment culture:

**CircuitShack (Tech Retail)**:
- "Nerdents" provide technical support with condescending expertise
- Dress code: Polo shirt, khakis, name badge, fake smile
- Training: Memorize product specs, upsell techniques, customer pacification
- Perks: Employee discount on obsolete technology

**Double Dip (Food Service)**:
- Vendors operate carts and stands selling contaminated condiments
- Dress code: Company apron, hairnet, thousand-yard stare
- Training: Food handling (ignore expiration dates), crisis management (zombie customers)
- Perks: Free hot dogs (not recommended)

**Kraken Transport (Mechanics & Logistics)**:
- Mechanics keep vehicles running through improvisation and prayers
- Dress code: Grease-stained coveralls, steel-toed boots, creative swearing
- Training: On-the-job learning, apprenticeship under veterans, inventive problem-solving
- Perks: Access to stolen parts and black market connections

**Dragon Corporate (Marketing & Media)**:
- Brand managers craft propaganda with a smile
- Dress code: Business suits, polished shoes, empty soul
- Training: Corporate doublespeak, manipulation techniques, moral flexibility
- Perks: Expense account (for client schmoozing), company car (if you hit quota)

**Flamingo Nightlife (Entertainment & Smuggling)**:
- Performers and service workers maintain the glamorous facade
- Dress code: Sequins, leather, attitude, questionable legality
- Training: Crowd management, cocktail mixing, looking the other way
- Perks: Tips in cash (untraceable), connections to underground networks

### Post-Outbreak Employment Reality

The Double Dip outbreak changed everything:

**Obsolete Jobs**:
- Tourism guide (who's touring a zombie-infested city?)
- Luxury goods retail (survival trumps status symbols)
- Event planning (parties are survival prep now)

**Reduced Jobs**:
- Restaurant server (most restaurants closed)
- Office administrator (companies downsized)
- Sales representative (fewer customers, less buying)

**Normal Jobs**:
- Retail clerk (people still need supplies)
- Technician (equipment still breaks)
- Mechanic (vehicles still need repair)

**Essential Jobs**:
- Security guard (protection is everything)
- Medical staff (injuries and infections constant)
- Supply chain workers (food and medicine critical)
- Utility maintenance (power and water are survival)

### Workplace Hazards in a Dystopia

Even "safe" jobs have risks:

**Low Risk** (Office Work):
- Poor ventilation systems spreading illness
- Zombie customers making unreasonable demands
- Electrical hazards from faulty equipment
- Psychological stress from corporate culture

**Moderate Risk** (Retail/Service):
- Customer confrontations (some customers are zombies)
- Chemical exposure (cleaning supplies, product leaks)
- Physical strain (long hours, heavy lifting)
- Infection risk (handling contaminated goods)

**High Risk** (Technical/Mechanical):
- Equipment failure (safety systems don't exist)
- Chemical burns (toxic materials everywhere)
- Electrical shock (nothing is properly grounded)
- Industrial accidents (OSHA is a joke here)

**Extreme Risk** (Security/Emergency):
- Combat situations (zombie encounters)
- Radiation exposure (cleaning up contamination)
- Biological hazards (constant infection risk)
- Violent confrontations (faction warfare)

### Career Progression in the Dystopia

Career advancement follows predictable but cruel patterns:

**Entry Level** → **Competent Worker** → **Experienced Professional** → **Supervisor/Specialist** → **Management** → **Corporate**

But advancement requires:
- Surviving long enough to gain experience
- Avoiding being scapegoated when things go wrong
- Navigating office politics and faction loyalties
- Accepting moral compromises for promotions
- Sacrificing work-life balance (what life?)

### Automation and Job Security

1990s automation is primitive but threatening:
- **Robots exist** but are expensive, unreliable, and need constant maintenance
- **Computers handle** basic calculations and data storage
- **Automated systems** control some manufacturing and utilities
- **But humans are still cheaper** for most jobs

Jobs at risk:
- Repetitive manufacturing tasks
- Simple data entry and calculations
- Basic inventory tracking
- Dangerous work (if robots can handle it)

Jobs that are safe:
- Complex problem-solving
- Customer service requiring empathy
- Skilled trades requiring adaptability
- Creative work and decision-making

### Job Cultural Status

The City of Brains has its own social hierarchy:

**Prestigious** (Envied):
- Corporate executives at major brands
- Media personalities and brand spokespersons
- High-level faction leadership
- Specialized professionals with rare skills

**Respectable** (Acceptable):
- Middle management positions
- Skilled technicians and mechanics
- Sales professionals hitting quotas
- Government administrators

**Neutral** (Invisible):
- Retail workers and service staff
- Entry-level employees
- Administrative assistants
- Security guards

**Stigmatized** (Looked Down Upon):
- Waste disposal workers
- Janitors and cleaners
- Manual laborers
- Anything involving bodily fluids

### Dark Humor in Job Descriptions

City of Brains jobs should include hilariously horrifying elements:

**Absurd Requirements**:
- "Must be comfortable working in mildly radioactive environment"
- "Occasional zombie encounters (PPE provided upon request)"
- "Ability to lift 50 lbs and maintain composure during apocalypse"
- "Strong communication skills and willingness to sign NDA about workplace 'incidents'"

**Corporate Doublespeak**:
- "Competitive salary" (competitive with starvation wages)
- "Fast-paced environment" (constant chaos and panic)
- "Self-starter" (we won't train you or help you)
- "Wear many hats" (do three jobs for one salary)

**Benefits That Aren't**:
- "Comprehensive health insurance" (doesn't cover zombie bites)
- "Generous PTO policy" (if you're alive to use it)
- "Employee discount" (on products that cause mutations)
- "Retirement plan" (assuming you live that long)

## Story Integration Opportunities

Every job should create narrative hooks:

### Access to Information
- Technicians see repair logs revealing corporate secrets
- Janitors overhear confidential conversations
- Security guards witness restricted area activities
- Administrative assistants handle incriminating documents

### Connection to Conflict
- Retail workers caught between faction territories
- Mechanics working for multiple competing brands
- Corporate employees forced to choose loyalties
- Service workers seeing both sides of class divide

### Personal Transformation
- Unlikely heroes emerging from mundane positions
- Workers becoming radicalized by corporate abuse
- Employees discovering hidden talents under pressure
- Characters finding purpose beyond their job title

### Moral Dilemmas
- Following orders vs. doing what's right
- Protecting the company vs. protecting people
- Career advancement vs. personal ethics
- Loyalty to brand vs. loyalty to faction

## Template Integration

### Required Fields
When using JOB_TEMPLATE.md:
- `id` must match folder name (snake_case)
- `primary_brand` must reference existing brand ID
- `work_locations` must reference existing location IDs
- `faction_controlled` must reference existing faction ID

### Cross-Reference Validation
Before finalizing any job:
- [ ] Does the `id` use snake_case format matching folder name?
- [ ] Does `primary_brand` exist in Brands folder?
- [ ] Do all `work_locations` exist in Locations folder?
- [ ] Does `faction_controlled` exist in Factions folder?
- [ ] Are required skills appropriate for 1990s setting?
- [ ] Does salary range match job level and era?
- [ ] Is outbreak_impact specified and logical?
- [ ] Do career progression paths make sense?
- [ ] Are workplace hazards realistically dangerous?
- [ ] Does the job create story opportunities?

## Implementation Examples

### Technical Job (CircuitShack Nerdent)
```yaml
id: "circuitshack_nerdent"
name: "Nerdent Technician"
job_category: "technical"
primary_brand: "circuitshack"
employment_type: "full_time"
experience_level: "entry"
salary_range: "$28,000 - $42,000"
faction_controlled: "bears"  # Northside Bears control tech sector
required_skills:
  - skill: "electronics_repair"
    level: 5
  - skill: "customer_service"
    level: 3
outbreak_impact: "essential"  # Tech support critical post-outbreak
safety_rating: "moderate"
known_hazards:
  - "electrical_equipment"
  - "zombie_customers"
  - "corporate_negligence"
```

### Service Job (Double Dip Vendor)
```yaml
id: "double_dip_vendor"
name: "Hot Dog Cart Vendor"
job_category: "service"
primary_brand: "double_dip"
employment_type: "full_time"
experience_level: "entry"
salary_range: "$18,000 - $25,000"
outbreak_impact: "reduced"  # Fewer customers post-outbreak
safety_rating: "high"  # Contaminated products
known_hazards:
  - "chemical_exposure"
  - "food_contamination"
  - "zombie_customers"
  - "faction_violence"
```

### Corporate Job (Marketing Manager)
```yaml
id: "brand_marketing_manager"
name: "Brand Marketing Manager"
job_category: "management"
primary_brand: "various_corporate"
employment_type: "full_time"
experience_level: "senior"
salary_range: "$65,000 - $95,000"
faction_controlled: "dragons"  # Eastside Dragons control marketing
outbreak_impact: "normal"  # Propaganda still needed
safety_rating: "low"
cultural_status: "prestigious"
```

## For AI Generation Systems

When generating jobs:
1. Verify era consistency (no post-2000s technology)
2. Check brand/faction alignment
3. Validate all cross-references
4. Ensure salary matches job level
5. Specify outbreak impact
6. Include appropriate hazards
7. Create story hooks
8. Use dark humor in descriptions

## For Human Content Creators

- Review this file before creating any job
- Use the validation checklist above
- Focus on dark humor emerging from corporate absurdity
- Ensure all cross-references point to existing entities
- Remember: even mundane jobs are dangerous in this dystopia
- Consider how the job changes pre- vs. post-outbreak
- Think about faction control and brand identity
- Create opportunities for character stories
