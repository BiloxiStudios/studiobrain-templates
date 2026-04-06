---
# METADATA
template_version: "1.0"
template_category: "system"
ui_icon: "Sparkles"
ui_color: "#d946ef"
editable: true
marketplace_eligible: false
id: "[snake_case_prompt_id]"
entity_type: "prompt"
folder_name: "Prompts"
file_prefix: "PROMPT_"
asset_subfolders: []
created_date: "[YYYY-MM-DD]"
last_updated: "[YYYY-MM-DD]"
associated_rules:
  - PROMPT_ENGINE_RULES.md

# FIELD WIDGET CONFIGURATION
# No non-default widgets required for prompt template fields.
# All fields use standard string, boolean, and structured-object inputs.
field_config: {}

status: "active"   # active, draft, deprecated, archived

# PRODUCTION STATUS TRACKING
production_status:
  general: "concept"   # concept, in_progress, needs_work, complete
  notes: ""

# PROMPT IDENTITY
name: "[Human-readable prompt name]"
description: "[What this prompt does and when to use it]"
prompt_type: "generation"   # generation | document | composite

# DOMAIN — which entity types or domains this prompt serves
# (universal means the prompt works across all domains)
domain: "universal"   # universal | character | location | item | dialogue | quest | faction | brand | …

# TEMPLATE BODY
# Write the prompt text here. Use variable syntax to inject live entity data:
#
#   $field_name                        — local field on the current entity
#   $type.field                        — cross-entity implicit: nearest entity of
#                                        type `type`, accesses `field`
#   $type:entity_id.field              — cross-entity explicit: specific entity
#   $type:entity_id.nested.path.field  — nested dot-path traversal (arbitrary depth)
#
# Supported entity type tokens: character, location, item, brand, faction, district,
#   quest, dialogue, event, campaign, timeline, assembly, job, universe
#
# Examples:
#   "Write a scene where $character.name visits $location.name."
#   "Describe $character:rusty_mcdaniels.name working at $location:rustys_auto_repair.name."
#   "Generate flavor text for $item.name worth $item.stats.value gold."
#   "Create a recipe using $ingredient.name with $technique.method."
template_body: |
  [Write your prompt here. Use $variable syntax for cross-entity resolution.]

# VARIABLE DECLARATIONS
# Explicitly declare variables used in template_body. This enables the resolver
# to pre-validate that all required fields exist before running generation.
variables:
  - name: "[variable_name]"
    syntax: "$[type].[field]"          # one of the four syntax forms
    entity_type: "[entity_type]"       # resolved entity type
    field_path: "[field]"              # dot-separated path within the entity
    required: true                     # if true, resolution fails on missing value
    default: null                      # fallback value when required: false
    description: "[What this variable represents]"

# RESOLUTION CONTEXT
# Controls how the resolver fetches cross-entity values at generation time.
resolution_context:
  cache_ttl_seconds: 300              # how long resolved values are cached (0 = no cache)
  strict_mode: true                   # true = error on unresolved variable; false = leave placeholder
  fallback_strategy: "empty_string"   # empty_string | placeholder | skip | error

# OUTPUT CONFIGURATION
output:
  format: "markdown"                  # markdown | plain | json | yaml
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9

# USAGE EXAMPLES
# Show how this prompt is invoked via the API or UI.
usage_examples:
  - description: "[Example description]"
    invocation:
      entity_type: "[entity_type]"
      entity_id: "[entity_id]"
      prompt_id: "[snake_case_prompt_id]"
      extra_context: {}

# VERSIONING
version_history:
  - version: "1.0"
    date: "[YYYY-MM-DD]"
    author: "[Author]"
    notes: "Initial version"
# NEW-ENTITY MARKDOWN SKELETON (SBAI-1857)
markdown_skeleton: |
  ## Purpose

  ## Prompt Text

  ## Usage Notes
---

# [Prompt Name]

## Purpose

[Describe the goal of this prompt and the generation task it performs.]

## Variable Reference

| Variable | Syntax | Entity Type | Field Path | Required |
|----------|--------|-------------|------------|----------|
| `$[name]` | `$[type].[field]` | [entity_type] | [field_path] | Yes/No |

## Resolution Examples

### Implicit Cross-Entity (nearest match)

```
$character.name    → resolves to the name field of the nearest character in context
$location.name     → resolves to the name field of the active location
```

### Explicit Cross-Entity (pinned entity ID)

```
$character:rusty_mcdaniels.name    → "Russell 'Rusty' McDaniels"
$location:rustys_auto_repair.name  → "Rusty's Auto Repair"
```

### Nested Dot-Path

```
$character:rusty_mcdaniels.appearance.hair_color.name  → "gray_brown"
$item.stats.damage.base                                → traverses stats → damage → base
```

### Local Field (current entity context)

```
$name      → current entity's name field
$status    → current entity's status field
```

## Notes

[Any additional context, limitations, or integration notes for this prompt.]
