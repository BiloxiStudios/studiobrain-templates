---
system_prompt: "Generate a brand for this project. Give it a slogan in the voice the project uses, and connect it only to places, people, and products the project has recorded. Do not invent a disaster, a conspiracy, or a joke the project has not asked for."
global: false
priority: "high"
entity_type: "brand"
template_reference: "BRAND_TEMPLATE.md"

rules:
- id: brand_001
  category: marketing
  priority: critical
  rule: "A brand must have a slogan or short line in the voice this project records for it."
  validation_type: warning
  applies_to: [brand]

- id: brand_002
  category: timeline
  priority: critical
  rule: "Marketing must use the era and media this project records. forbidden_elements and required_elements are empty in the starter so the project can fill them."
  validation_type: warning
  applies_to: [brand]
  forbidden_elements: []
  required_elements: []
- id: brand_003
  category: conspiracy
  priority: high
  rule: "A brand's ties to places, events, and other brands must be ones this project has recorded. Do not invent a conspiracy or a disaster."
  validation_type: warning
  applies_to: [brand]

- id: brand_004
  category: humor
  priority: high
  rule: "A product name must fit the brand's voice as this project records it. Do not add humor, parody, or innuendo the project has not asked for."
  validation_type: warning
  applies_to: [brand]

- id: brand_005
  category: economy
  priority: medium
  rule: "A local business must relate to other brands only in ways this project has recorded."
  validation_type: warning
  applies_to: [brand]

- id: brand_006
  category: products
  priority: high
  rule: "A product's effects must be ones this project records for that product. Do not invent a side effect."
  validation_type: warning
  applies_to: [brand]

- id: brand_007
  category: environmental
  priority: high
  rule: "How a brand talks about the environment must match the stance this project records. Do not assume damage is celebrated or denied."
  validation_type: warning
  applies_to: [brand]

- id: brand_008
  category: faction
  priority: medium
  rule: "Marketing aimed at a faction must match that faction as this project records it. Do not invent a stereotype."
  validation_type: info
  applies_to: [brand]

- id: brand_009
  category: authenticity
  priority: medium
  rule: "A local business's risks must follow from what this project records about it."
  validation_type: info
  applies_to: [brand]

- id: brand_010
  category: references
  priority: critical
  rule: "A brand must not name a product, disaster, or campaign this project has not recorded."
  validation_type: warning
  applies_to: [brand]

- id: brand_011
  category: innuendo
  priority: high
  rule: "Wordplay in a name or slogan must match the tone this project records. Do not add innuendo the project has not asked for."
  validation_type: warning
  applies_to: [brand]

- id: brand_012
  category: absurdity
  priority: high
  rule: "A product's purpose must be one this project records. Do not invent a joke function."
  validation_type: info
  applies_to: [brand]

- id: brand_013
  category: timeline_validation
  priority: critical
  rule: "founding_year, key_milestones, and product launch dates must be in chronological order and inside the years this project uses."
  validation_type: warning
  applies_to: [brand]
  required_tools: ["check_temporal_conflicts", "calculate_duration"]

- id: brand_014
  category: entity_validation
  priority: critical
  rule: Before referencing locations (headquarters, store_locations), characters (key_personnel,
    founder, ceo, employees), items (brand_items, product_lines), or factions, use
    validation tools to verify they exist. Use check_location_exists, check_character_exists,
    check_item_exists, and validate_all_references. Never reference non-existent entities
  validation_type: warning
  applies_to: [brand]
  required_tools: ["check_location_exists", "check_character_exists", "check_item_exists",
    "validate_all_references"]
---

# Brand guidance

These rules check structure and consistency. They do not name a setting.

A brand needs a slogan in its own voice. Marketing uses the era and the media the project records. The starter's forbidden_elements and required_elements lists are empty so the project can fill them. Dates must be in order and inside the project's years.

Connections to places, people, products, factions, and events must be entities and facts the project already has. Do not invent a disaster, a conspiracy, a side effect, or a joke.

Name only entities that exist. Add the entity first when the reference is new.
