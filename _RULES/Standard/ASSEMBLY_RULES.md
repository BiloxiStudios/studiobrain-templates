---
system_prompt: "Generate and validate assembly definitions for the StudioBrain visual composition system. Assemblies are layered composite entities built from named slots organized into slot groups. They support a four-tier inheritance hierarchy (Template → Profile → Variant → Zombie), z-index driven render ordering, slot locking for protected base assets, and multi-pipeline export via named export profiles. Universal use: game sprite composition, film shot comp, design layouts, garden plot plans, recipe plating."
global: false
priority: high
entity_type: assembly
template_reference: ASSEMBLY_TEMPLATE.md

rules:

# ─── IDENTITY ───────────────────────────────────────────────────────────────
- id: asm_id_001
  category: identity
  priority: critical
  rule: Assembly IDs must use lowercase_with_underscores format (e.g. "hero_base_template")
  validation_type: error
  applies_to: [assembly]

- id: asm_id_002
  category: identity
  priority: critical
  rule: "assembly_type must be one of: character, prop, building"
  validation_type: error
  applies_to: [assembly]

- id: asm_id_003
  category: identity
  priority: high
  rule: "Every assembly must declare a hierarchy_level: template | profile | variant | zombie_variant | transformation_variant"
  validation_type: error
  applies_to: [assembly]

- id: asm_id_004
  category: identity
  priority: high
  rule: Non-template assemblies (profile/variant/zombie_variant) must supply a valid parent_assembly_id
  validation_type: error
  applies_to: [assembly]

# ─── INHERITANCE HIERARCHY ────────────────────────────────────────────────────
- id: asm_inh_001
  category: inheritance
  priority: critical
  rule: "Hierarchy is strictly Template → Profile → Variant → Zombie. A Profile must have a Template parent. A Variant must have a Profile parent. A zombie_variant must have a Variant or Profile parent."
  validation_type: error
  applies_to: [assembly]
  hierarchy_chain:
    - template        # root; no parent required
    - profile         # inherits from template
    - variant         # inherits from profile
    - zombie_variant  # inherits from variant or profile

- id: asm_inh_002
  category: inheritance
  priority: high
  rule: "inheritance_mode must be one of: full | selective | none. 'full' copies all unfilled slots from parent. 'selective' copies only explicitly listed slots. 'none' is a standalone assembly."
  validation_type: error
  applies_to: [assembly]

- id: asm_inh_003
  category: inheritance
  priority: high
  rule: "Max inheritance chain depth is 4 (Template=1, Profile=2, Variant=3, Zombie=4). Assemblies exceeding depth 4 are rejected."
  validation_type: error
  applies_to: [assembly]
  max_depth: 4

- id: asm_inh_004
  category: inheritance
  priority: medium
  rule: Children may only override slots that are not listed in the parent's locked_slots array
  validation_type: error
  applies_to: [assembly]

- id: asm_inh_005
  category: inheritance
  priority: medium
  rule: "inheritance_mode: metadata_only is not permitted — assemblies must always inherit at minimum their slot structure from their parent template"
  validation_type: error
  applies_to: [assembly]

# ─── SLOT SYSTEM ─────────────────────────────────────────────────────────────
- id: asm_slot_001
  category: slots
  priority: critical
  rule: Every slot must belong to a named slot_group. Loose slots outside a group are rejected.
  validation_type: error
  applies_to: [assembly]

- id: asm_slot_002
  category: slots
  priority: critical
  rule: "Each required slot (required: true) must be filled before an assembly can be marked status: complete or exported"
  validation_type: error
  applies_to: [assembly]

- id: asm_slot_003
  category: slots
  priority: high
  rule: Slot names within a group must be unique (no duplicate slot_name within a slot_group)
  validation_type: error
  applies_to: [assembly]

- id: asm_slot_004
  category: slots
  priority: high
  rule: "accepted_types must be a non-empty list. Allowed values: png, webp, glb, fbx, jpg, svg"
  validation_type: error
  applies_to: [assembly]

- id: asm_slot_005
  category: slots
  priority: high
  rule: "overlay_modes must be a non-empty list. Allowed values: replace, overlay, blend, multiply, screen, add"
  validation_type: error
  applies_to: [assembly]

- id: asm_slot_006
  category: slots
  priority: medium
  rule: Slot groups with allow_custom_slots set to true must also declare a default_blend_mode
  validation_type: warning
  applies_to: [assembly]

- id: asm_slot_007
  category: slots
  priority: medium
  rule: "If a slot declares variants_expected, the actual number of variant assets assigned must equal variants_expected"
  validation_type: warning
  applies_to: [assembly]

- id: asm_slot_008
  category: slots
  priority: medium
  rule: "If a slot declares variant_keys, each key must be a non-empty string with no spaces (use underscores)"
  validation_type: error
  applies_to: [assembly]

- id: asm_slot_009
  category: slots
  priority: medium
  rule: "A slot that declares mirror_of must also declare mirror_strategy (flip_x | flip_y | rotate_180)"
  validation_type: error
  applies_to: [assembly]

# ─── Z-INDEX ORDERING ────────────────────────────────────────────────────────
- id: asm_zidx_001
  category: z_index
  priority: high
  rule: "z_index values must be integers in range 1–999. Values outside this range are clamped with a warning."
  validation_type: warning
  applies_to: [assembly]
  z_index_min: 1
  z_index_max: 999

- id: asm_zidx_002
  category: z_index
  priority: medium
  rule: "No two slots in the same assembly may share an identical z_index (within the same composite canvas). Duplicates produce a warning."
  validation_type: warning
  applies_to: [assembly]

- id: asm_zidx_003
  category: z_index
  priority: medium
  rule: "Overlay slots (overlay_modes containing 'overlay', 'multiply', or 'blend') must use z_index ≥ 80 to prevent base-layer occlusion."
  validation_type: warning
  applies_to: [assembly]
  overlay_z_index_min: 80

- id: asm_zidx_004
  category: z_index
  priority: low
  rule: Infection/damage overlay slots should use z_index in range 88–99 so they composite above all base layers
  validation_type: suggestion
  applies_to: [assembly]

# ─── SLOT LOCKING ────────────────────────────────────────────────────────────
- id: asm_lock_001
  category: locking
  priority: high
  rule: "locked_slots entries must reference existing slot_group.slot_name paths (e.g. 'head.head_base'). Invalid references are flagged as errors."
  validation_type: error
  applies_to: [assembly]

- id: asm_lock_002
  category: locking
  priority: high
  rule: A child assembly must not assign an asset to any slot path listed in any ancestor's locked_slots
  validation_type: error
  applies_to: [assembly]

- id: asm_lock_003
  category: locking
  priority: medium
  rule: "Locking is additive down the chain: if Template locks 'head.head_base' and Profile locks 'body.torso_base', a Variant inherits both locks."
  validation_type: error
  applies_to: [assembly]

# ─── AUTO-SLOT DETECTION ─────────────────────────────────────────────────────
- id: asm_auto_001
  category: auto_slot_detection
  priority: medium
  rule: "When ai_validation.auto_validate_on_slot_assign is true, the AI validator must check the assigned image against the slot's description and accepted_types before confirming the assignment."
  validation_type: warning
  applies_to: [assembly]

- id: asm_auto_002
  category: auto_slot_detection
  priority: medium
  rule: "slot_detection_confidence_threshold defaults to 0.75. Assignments with confidence below threshold should prompt user confirmation, not auto-reject."
  validation_type: warning
  applies_to: [assembly]
  default_threshold: 0.75

- id: asm_auto_003
  category: auto_slot_detection
  priority: low
  rule: "parent_similarity_threshold defaults to 0.70. Profile/variant assets that score below this against the parent template's corresponding slot asset generate a style consistency warning."
  validation_type: suggestion
  applies_to: [assembly]
  default_threshold: 0.70

# ─── EXPORT PROFILES ─────────────────────────────────────────────────────────
- id: asm_exp_001
  category: export
  priority: high
  rule: "Every assembly must declare at least one export profile in export_profile_files (or inherit one from its parent template)."
  validation_type: warning
  applies_to: [assembly]

- id: asm_exp_002
  category: export
  priority: high
  rule: "export_profile_files entries must reference files that exist under templates/Standard/ExportProfiles/. Missing profile files block export."
  validation_type: error
  applies_to: [assembly]

- id: asm_exp_003
  category: export
  priority: medium
  rule: "Export is only allowed when all required slots (required: true) are filled. Partial exports for optional slots are allowed but must be flagged in the export manifest."
  validation_type: error
  applies_to: [assembly]

- id: asm_exp_004
  category: export
  priority: medium
  rule: "color_variants list must contain at least 'default'. Additional variant names must be non-empty strings."
  validation_type: error
  applies_to: [assembly]

- id: asm_exp_005
  category: export
  priority: low
  rule: "zombie_stages list (when export.zombie_stages is declared) must be integers in ascending order starting from 0."
  validation_type: warning
  applies_to: [assembly]

# ─── INFECTION / ZOMBIE SYSTEM ───────────────────────────────────────────────
- id: asm_zomb_001
  category: zombie_system
  priority: critical
  rule: "Zombie overlay assets must only use green, purple/black color palettes. NO red blood anywhere. Fluids must be green or dark purple/black."
  validation_type: error
  applies_to: [assembly]
  palette_restriction:
    allowed_hues:
      green: [80, 160]
      purple: [260, 320]
    allowed_values:
      black_max_v: 20
    max_saturation_exception: 15

- id: asm_zomb_002
  category: zombie_system
  priority: high
  rule: "Infection stages 0–3 are OVERLAY-BASED (additive overlays on the base character). Stage 4 (full zombie) requires a dedicated zombie_variant assembly with full slot replacement."
  validation_type: error
  applies_to: [assembly]

- id: asm_zomb_003
  category: zombie_system
  priority: high
  rule: A zombie_variant assembly must either (a) override all required base slots, or (b) declare zombie_mode "overlay_only" to treat it as a maxed-out stage-3 composite
  validation_type: error
  applies_to: [assembly]

- id: asm_zomb_004
  category: zombie_system
  priority: medium
  rule: Gore in zombie overlays must be stylized, not photorealistic. Photorealistic gore is rejected by the content validator.
  validation_type: error
  applies_to: [assembly]

# ─── PRODUCTION STATUS ───────────────────────────────────────────────────────
- id: asm_prod_001
  category: production
  priority: medium
  rule: "production_status.general must be one of: concept, in_progress, needs_work, art_done, complete"
  validation_type: error
  applies_to: [assembly]

- id: asm_prod_002
  category: production
  priority: low
  rule: "An assembly may only transition to production_status.general: complete when all required slots are filled and no validation errors remain."
  validation_type: error
  applies_to: [assembly]

defaults:
  hierarchy_level: "template"
  inheritance_mode: "full"
  assembly_type: "character"
  z_index_min: 1
  z_index_max: 999
  overlay_z_index_min: 80
  slot_detection_confidence_threshold: 0.75
  parent_similarity_threshold: 0.70
  style_consistency_threshold: 0.80
  default_color_variants: ["default"]
  export_profile_default: "showrunner_v1"

validation:
  - "Does the assembly have a valid assembly_type (character | prop | building)?"
  - "Is hierarchy_level set and does it conform to the Template→Profile→Variant→Zombie chain?"
  - "Does every non-template assembly supply a valid parent_assembly_id?"
  - "Are all locked_slots references valid slot_group.slot_name paths?"
  - "Are all required slots filled before marking status: complete?"
  - "Are z_index values unique and within 1–999?"
  - "Do overlay slots use z_index ≥ 80?"
  - "Are export_profile_files references resolvable on disk?"
  - "Do zombie overlay assets comply with the green/purple/black palette restriction?"
  - "Do variant_keys contain no spaces or special characters?"
---

# Assembly Rules

## Purpose

These rules govern the StudioBrain **Assembly** system — the visual composition layer that
combines named slot assets into a layered composite image or mesh. Assemblies are universal:
they can represent game sprites, film shot comps, design layouts, garden plot plans, or
recipe plating diagrams.

## Inheritance Hierarchy

Every assembly belongs to one of four tiers:

| Tier | `hierarchy_level` | Parent Required |
|------|-------------------|-----------------|
| Template | `template` | No — root definition |
| Profile | `profile` | Yes — must be a `template` |
| Variant | `variant` | Yes — must be a `profile` |
| Zombie / Transformation | `zombie_variant` | Yes — must be a `variant` or `profile` |

Maximum chain depth is **4**. A Template counts as depth 1.

## Slot System

Slots are organized into **slot groups** (e.g. `head`, `body`, `accessories`). Each slot defines:

- `required` — whether the slot must be filled before export
- `z_index` — render layer order (1 = back, 999 = front)
- `overlay_modes` — how the asset composites (`replace`, `overlay`, `blend`, `multiply`, etc.)
- `accepted_types` — allowed file extensions
- `variants_expected` / `variant_keys` — for multi-frame or multi-pose slot sets

## Z-Index Ordering

- Base layers: z_index 1–79
- Clothing/accessory layers: z_index 30–70
- Overlay layers (damage, infection): z_index 80–99
- Infection overlays: z_index 88–99

## Slot Locking

Add slot paths to `locked_slots` (e.g. `"head.head_base"`) to prevent child assemblies from
overriding them. Locks are inherited additively down the chain.

## Export Profiles

Export profiles translate slot assets into pipeline-specific folder structures and filenames.
Profiles are defined as YAML files under `templates/Standard/ExportProfiles/`. An assembly
references one or more profiles via `export_profile_files`. Export is blocked until all
`required: true` slots are filled.

## Zombie / Infection System

Stages 0–3 are overlay-based (add infection overlays to the base character).
Stage 4 (full zombie) requires a dedicated `zombie_variant` assembly.

**Palette restriction:** All zombie/infection overlay assets must use **only green, purple, and black**.
No red blood. Gore must be stylized, not photorealistic.
