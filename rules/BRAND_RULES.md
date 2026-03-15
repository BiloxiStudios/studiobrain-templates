---
system_prompt: "Generate brands for the City of Brains universe that capture the absurd dystopia of 1990s advertising gone unchecked. Create corporate entities that sound appealing but have hilariously dark undertones, like a cleaning product that glows radioactively or a hot dog sauce that causes zombie infections. Use dark humor, innuendo, and clever wordplay to create memorable brands that would fit right into a world where corporate greed has spiraled completely out of control. Every brand, even small local ones, should have some comedic dark twist - it's corporate megalithic dystopia where even mom-and-pop shops can't escape the madness."
global: false
priority: "high"
entity_type: "brand"
template_reference: "BRAND_TEMPLATE.md"

rules:
- id: brand_001
  category: marketing
  priority: critical
  rule: All brands must have catchy, memorable jingles or slogans with deliciously dark undertones and sexual innuendo where appropriate
  validation_type: error
  applies_to: [brand]
  examples: ["Double Dip: Go ahead and double dip!", "Penetrator Drill Bits: We go deeper than anyone!", "Climax Cola: The peak of refreshment!"]

- id: brand_002
  category: timeline
  priority: critical
  rule: Marketing must reflect exaggerated 1990s advertising aesthetics with neon excess and corporate hyperbole
  validation_type: error
  applies_to: [brand]
  forbidden_elements: ["social media marketing", "viral campaigns", "hashtags", "QR codes", "influencer partnerships"]
  required_elements: ["TV commercials with cheesy effects", "radio jingles with synthesizer music", "neon billboards", "promotional giveaways", "mascot characters"]

- id: brand_003
  category: conspiracy
  priority: high
  rule: Corporate brands must have hilariously obvious connections to the chemical plant or environmental disasters
  validation_type: warning
  applies_to: [brand]
  examples: ["Glow-Fresh Cleaners", "Nuclear Family Foods", "Acid Rain Umbrella Co."]

- id: brand_004
  category: humor
  priority: high
  rule: Product names should contain dark comedy, sexual innuendo, or parodies of real brands with twisted purposes
  validation_type: warning
  applies_to: [brand]
  examples: ["Penetrator Power Tools", "Moist-Maker Food Enhancer", "Hard-On Construction Cement", "Deep Impact Mining Co.", "Climax Entertainment"]

- id: brand_005
  category: economy
  priority: medium
  rule: Local businesses should be hilariously inept at competing with mega-corps or have their own absurd dark secrets
  validation_type: warning
  applies_to: [brand]
  examples: ["Mom's Nuclear Cookies", "Family Funeral Fireworks", "Honest Abe's Dishonest Deals"]

- id: brand_006
  category: products
  priority: high
  rule: Key products must have comedically ironic side effects or unintended consequences for gameplay
  validation_type: warning
  applies_to: [brand]
  examples: ["Energy drinks that cause hallucinations", "Sleeping pills that keep you awake", "Weight loss shakes that make you heavier"]

- id: brand_007
  category: environmental
  priority: high
  rule: Brands should embrace environmental damage as a feature, not a bug, in their marketing
  validation_type: warning
  applies_to: [brand]
  examples: ["Toxic Waste Glow Sticks", "Acid Rain Car Wash", "Mutation Station Pet Shop"]

- id: brand_008
  category: faction
  priority: medium
  rule: Brands should outrageously pander to specific faction stereotypes with over-the-top targeted marketing
  validation_type: info
  applies_to: [brand]
  examples: ["Macho Motors for truckers", "Glitter Bombs for Flamingos", "Binary Beverages for hackers"]

- id: brand_009
  category: authenticity
  priority: medium
  rule: Authentic local businesses should be accidentally more dangerous than corporations through incompetence, laziness or understaffing
  validation_type: info
  applies_to: [brand]
  examples: ["Grandpa's Explosives Emporium", "Sister Sarah's Surgery Supplies", "Uncle Bob's Used Uranium"]

- id: brand_010
  category: double_dip
  priority: critical
  rule: Food/chemical brands must hilariously reference or parody the Double Dip Dog Sauce apocalypse scenario
  validation_type: warning
  applies_to: [brand]
  examples: ["Triple Dip Disaster Sauce", "Quadruple Threat Condiments", "One-Dip Wonder (Guaranteed Safe!)"]

- id: brand_011
  category: innuendo
  priority: high
  rule: Brand names and slogans should include clever adult humor and double entendres that sound innocent but aren't
  validation_type: warning
  applies_to: [brand]
  examples: ["Hard Wood Lumber: We'll give you wood!", "Wet Dreams Water Park", "Big Johnson's Tool Emporium", "Ride Me Bicycles"]

- id: brand_012
  category: absurdity
  priority: high
  rule: Products should solve problems that don't exist or create new problems while solving old ones
  validation_type: info
  applies_to: [brand]
  examples: ["Silent Scream Mufflers", "Invisible Paint", "Diet Water Zero", "Solar Powered Flashlights"]

- id: brand_013
  category: timeline_validation
  priority: critical
  rule: Use timeline validation tools to verify that founding_year, key_milestones, and product_launch_dates are chronologically consistent, all dates occur before or during 1998 (current game year), and temporal progression aligns with brand evolution narrative
  validation_type: error
  applies_to: [brand]
  required_tools: ["check_temporal_conflicts", "calculate_duration"]

- id: brand_014
  category: entity_validation
  priority: critical
  rule: Before referencing locations (headquarters, store_locations), characters (key_personnel,
    founder, ceo, employees), items (brand_items, product_lines), or factions, use
    validation tools to verify they exist. Use check_location_exists, check_character_exists,
    check_item_exists, and validate_all_references. Never reference non-existent entities
  validation_type: error
  applies_to: [brand]
  required_tools: ["check_location_exists", "check_character_exists", "check_item_exists",
    "validate_all_references"]
---

# Brand Creation in the City of Brains Universe

## The Dark Comedy of Corporate Dystopia

Creating brands for City of Brains means channeling the most absurd aspects of 1990s corporate culture gone completely unchecked. These aren't just companies - they're monuments to greed, incompetence, and the kind of marketing that would make even the most cynical consumer question reality.

### The 1990s Marketing Madness

Every brand needs that perfect combination of aggressive corporate optimism and hilariously obvious problems. Think neon colors that hurt your eyes, mascots with attitude problems, and jingles that get stuck in your head for weeks. This is the era of "EXTREME!" "RADICAL!" and "MAXIMUM POWER!" - where subtlety went to die and corporate hyperbole became the norm.

### Sexual Innuendo as Marketing Strategy

The best brands work on multiple levels. What sounds innocent to kids becomes hilariously suggestive to adults. "Penetrator Drill Bits: We go deeper than anyone else can!" or "Climax Cola: Reach your peak with every sip!" - these slogans are family-friendly on the surface but make adults snicker. The key is making the innuendo obvious enough to be funny but subtle enough that parents might still buy the products.

### Environmental Destruction as a Feature

In the City of Brains universe, environmental damage isn't a bug - it's a feature. Brands market their connection to disasters with absurd pride. "Glow-Fresh Cleaners: Now with 50% more radiation for that healthy glow!" or "Acid Rain Car Wash: Strips paint AND skin!" The more obvious the connection to environmental destruction, the better.

### The Double Dip Disaster Legacy

The Double Dip Dog Sauce outbreak is the defining event of this universe, and food brands must reference it with increasingly absurd escalation. "Triple Dip Disaster Sauce: Because double wasn't enough!" or "One-Dip Wonder: Guaranteed safe! (Results not guaranteed)" - the more brands try to distance themselves from the disaster, the more they accidentally reference it.

### Corporate Hierarchy of Evil

**Major Corporations** (ChemCorp Subsidiaries) represent the pinnacle of corporate evil:
- Overwhelming marketing presence that's impossible to escape
- Products that create the problems they claim to solve
- Slogans that become increasingly ominous over time
- Mascots with dead eyes and forced smiles

**Regional Chains** are desperately trying to be as evil as the big corporations:
- Cutting corners in hilariously dangerous ways
- Marketing that tries too hard to be edgy
- Products that are knock-offs of corporate disasters

**Local Businesses** represent authentic incompetence:
- Family recipes that are accidentally toxic
- Personal service that's personally dangerous
- Fighting corporate pressure by being worse than corporations

**Underground Brands** (Faction Black Market) have their own creative chaos:
- Homemade products with creative naming
- Modified corporate goods with added "features"
- Quality that varies wildly from batch to batch

### Absurd Product Concepts

The best brands solve problems that don't exist or create bigger problems while solving smaller ones. Think "Silent Scream Mufflers" or "Diet Water Zero" - products that are so obviously useless they become hilarious. Or products with hilariously ironic side effects: energy drinks that make you sleepy, sleeping pills that cause insomnia, weight loss shakes that make you gain weight.

### Faction-Specific Pandering

Brands should ridiculously over-pander to faction stereotypes:
- **Northside Bears**: "Binary Beverages: 1 or 0, there is no maybe!"
- **Westside Krakens**: "Macho Motors: Real trucks for real men with real chest hair!"
- **Eastside Dragons**: "Snooty Soufflé: Too good for you, but we'll sell it anyway!"
- **Southside Flamingos**: "Glitter Bombs: Explode with fabulousness!"

### Brand Evolution Through Crisis

Brands must adapt their messaging as the world changes:

**Pre-Outbreak**: Aggressively cheerful corporate optimism
**During Outbreak**: Tone-deaf corporate damage control  
**Post-Outbreak**: Products repurposed for zombie apocalypse survival

Example: "Hard-On Construction Cement"
- Pre: "We stay up all night to get the job done!"
- During: "Our concrete barriers will protect you!"
- Post: "Cement zombies in place permanently!"

## Template Integration

### Brand Template Alignment
When using the BRAND_TEMPLATE.md:
- The `brand_id` field must match your folder name exactly
- The `headquarters` field should reference an existing location
- The `key_personnel` list should reference existing characters
- The `brand_items` list should reference items from your Items folder

### Cross-Reference Validation
Before finalizing any brand:
- [ ] Does the `brand_id` use lowercase_with_underscores format?
- [ ] Does the `headquarters` location exist in your Locations folder?
- [ ] Do any referenced character IDs exist in your Characters folder?
- [ ] Do any referenced item IDs exist in your Items folder?
- [ ] Does the name have at least one possible sexual interpretation?
- [ ] Is the connection to environmental destruction hilariously obvious?
- [ ] Would parents buy this for kids without realizing the implications?
- [ ] Does the product solve a problem by creating a bigger problem?
- [ ] Can the slogan be sung ominously during zombie attacks?
- [ ] Does the humor emerge from the absurdity rather than cruelty?

## Implementation Examples

### For AI Generation Systems
When creating a brand like "Penetrator Power Tools":
1. Set `brand_id: "penetrator_power_tools"` (matches folder name)
2. Assign `headquarters: "industrial_district_warehouse"` (must exist in Locations)
3. Reference `key_personnel: ["bob_penetrator"]` (must exist in Characters)
4. Include products like `"penetrator_drill_bits"` in brand_items
5. Create slogans that work on multiple levels

### For Human Content Creators
- Review this file before creating any brand
- Use the validation checklist above
- Focus on dark comedy that emerges from absurdity, not cruelty
- Ensure all cross-references point to existing entities
- Remember: no marketing idea is too stupid in this universe