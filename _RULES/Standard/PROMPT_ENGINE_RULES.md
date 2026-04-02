---
# PROMPT ENGINE RULES
# Variable resolution for AI generation prompts and document template rendering.
# JIRA: SBAI-1643
system_prompt: |
  You are resolving variables inside a StudioBrain prompt template. Follow the
  variable syntax rules exactly. Fetch cross-entity values from the knowledge base
  before substituting. When a required variable cannot be resolved, raise a
  resolution error rather than inventing a value. When an optional variable cannot
  be resolved, substitute the configured fallback (default: empty string).
global: true
priority: high
entity_type: "prompt"
template_reference: "PROMPT_TEMPLATE.md"
version: "1.0"
created_by: "System"
last_updated: "2026-04-01"

rules:

  # ── Syntax ────────────────────────────────────────────────────────────────

  - id: pe_001
    category: syntax
    priority: critical
    rule: >
      Variable tokens MUST follow one of the four canonical forms:
      (1) $field — local field on the current entity context;
      (2) $type.field — cross-entity implicit (nearest entity of that type);
      (3) $type:entity_id.field — cross-entity explicit (pinned entity ID);
      (4) $type:entity_id.path.to.nested.field — explicit with arbitrary-depth
      nested dot-path traversal. Any other token form is a syntax error.
    validation_type: error
    applies_to: [prompt]

  - id: pe_002
    category: syntax
    priority: critical
    rule: >
      The `type` portion of a cross-entity token MUST be a recognised entity-type
      token: character, location, item, brand, faction, district, quest, dialogue,
      event, campaign, timeline, assembly, job, or universe. Unknown type tokens
      must be rejected with a parse error before resolution begins.
    validation_type: error
    applies_to: [prompt]

  - id: pe_003
    category: syntax
    priority: high
    rule: >
      `entity_id` in an explicit token ($type:entity_id.field) MUST be a valid
      lowercase_with_underscores identifier matching the target entity's `id`
      field. Numeric IDs and UUIDs are also accepted.
    validation_type: error
    applies_to: [prompt]

  - id: pe_004
    category: syntax
    priority: high
    rule: >
      Nested dot-path segments must each be non-empty strings containing only
      alphanumeric characters, hyphens, or underscores. Array index access via
      bracket notation (e.g. items[0]) is not supported in this version.
    validation_type: error
    applies_to: [prompt]

  # ── Resolution ────────────────────────────────────────────────────────────

  - id: pe_010
    category: resolution
    priority: critical
    rule: >
      Before substituting any cross-entity variable, the resolver MUST verify
      that the target entity exists in the database using the entity validation
      tools (check_character_exists, check_location_exists, etc.). Resolution of
      a variable that points to a non-existent entity is a resolution error.
    validation_type: error
    applies_to: [prompt]
    required_tools:
      - check_character_exists
      - check_location_exists
      - check_brand_exists
      - check_item_exists
      - validate_all_references

  - id: pe_011
    category: resolution
    priority: critical
    rule: >
      For implicit cross-entity tokens ($type.field), the resolver selects the
      entity of the given type that is most contextually relevant: the entity
      currently open in the UI, or—if no entity is active—the first entity of
      that type returned by the knowledge-base search given the prompt's domain
      context. When no entity of the requested type exists, treat as unresolvable.
    validation_type: error
    applies_to: [prompt]

  - id: pe_012
    category: resolution
    priority: high
    rule: >
      Nested dot-path fields are resolved by walking the entity's data object
      level by level. If any intermediate key is absent or null, the resolver
      must stop and treat the entire variable as unresolvable rather than
      returning a partial path or raising a JavaScript-style TypeError.
    validation_type: error
    applies_to: [prompt]

  - id: pe_013
    category: resolution
    priority: high
    rule: >
      When `strict_mode: true` is set on the prompt template, every unresolvable
      variable (required or optional) MUST cause the resolution to fail with a
      descriptive error message listing each unresolved token. Generation must not
      proceed until all variables are resolved or the prompt is fixed.
    validation_type: error
    applies_to: [prompt]

  - id: pe_014
    category: resolution
    priority: high
    rule: >
      When `strict_mode: false`, unresolvable optional variables are substituted
      with the `fallback_strategy` value defined in the prompt template:
      empty_string → "", placeholder → the original token string (e.g.
      "$character.name"), skip → the sentence containing the variable is omitted,
      error → behaves like strict_mode regardless of the flag.
    validation_type: warning
    applies_to: [prompt]

  - id: pe_015
    category: resolution
    priority: high
    rule: >
      List-valued fields (YAML sequences) resolved via a variable token must be
      serialised as a comma-separated string by default. The prompt template may
      override the serialisation format by appending a pipe modifier:
      `$type.field|join(", ")`, `$type.field|first`, `$type.field|count`.
      Modifier syntax is reserved for future versions; unknown modifiers are
      ignored and the default comma-join is used.
    validation_type: warning
    applies_to: [prompt]

  # ── Caching ───────────────────────────────────────────────────────────────

  - id: pe_020
    category: caching
    priority: medium
    rule: >
      Resolved entity values MAY be cached for the duration specified in the
      prompt template's `resolution_context.cache_ttl_seconds` field. The cache
      key is `{entity_type}:{entity_id}:{field_path}`. A TTL of 0 disables
      caching. Cached entries must be invalidated when the underlying entity is
      updated (via entity.updated events).
    validation_type: info
    applies_to: [prompt]

  - id: pe_021
    category: caching
    priority: medium
    rule: >
      The cache must be scoped per-user session. Cross-session cache sharing is
      not permitted because different users may have different permission levels
      for entity fields.
    validation_type: warning
    applies_to: [prompt]

  # ── Security ──────────────────────────────────────────────────────────────

  - id: pe_030
    category: security
    priority: critical
    rule: >
      Variable tokens must be parsed and resolved server-side before the prompt
      is forwarded to any AI provider. Resolved values must be HTML-escaped and
      truncated to a maximum of 1 000 characters per variable substitution to
      prevent prompt injection via entity field content.
    validation_type: error
    applies_to: [prompt]

  - id: pe_031
    category: security
    priority: critical
    rule: >
      The resolver must only access entity fields that the requesting user has
      read permission for. Attempting to resolve a field the user cannot read
      must return an "access denied" resolution error, not an empty string.
    validation_type: error
    applies_to: [prompt]

  # ── Universality ──────────────────────────────────────────────────────────

  - id: pe_040
    category: universality
    priority: high
    rule: >
      The prompt engine is domain-agnostic. Prompt templates that use only
      standard entity-type tokens work identically across every project domain
      (games, film, books, cooking, etc.). Domain-specific tokens are defined
      by extending the entity-type registry; they do not require changes to the
      core resolver.
    validation_type: info
    applies_to: [prompt]

  - id: pe_041
    category: universality
    priority: high
    rule: >
      Both AI generation prompts AND document template rendering share the same
      resolver. Prompts sent to AI providers and static document exports (PDF,
      Obsidian, Notion) are resolved identically; only the output handler differs.
    validation_type: info
    applies_to: [prompt]

  # ── Performance ───────────────────────────────────────────────────────────

  - id: pe_050
    category: performance
    priority: medium
    rule: >
      When a prompt template declares its variables explicitly in the `variables`
      block, the resolver MUST batch all required entity lookups into the minimum
      number of database queries (one per unique entity_id) before substitution
      begins. Fan-out to N separate queries for N variables referencing the same
      entity is a performance violation.
    validation_type: warning
    applies_to: [prompt]

  - id: pe_051
    category: performance
    priority: medium
    rule: >
      The total wall-clock time for variable resolution (excluding the downstream
      AI provider call) MUST NOT exceed 2 000 ms for prompts containing 20 or
      fewer variable tokens. Templates that exceed this budget must be flagged
      during validation and their variable list reviewed for redundant lookups.
    validation_type: warning
    applies_to: [prompt]
---

# Prompt Engine Rules
## Cross-Entity Variable Resolution for AI Generation

### Overview

The Prompt Engine provides a universal variable-substitution layer that resolves
live entity data into prompt templates before they are sent to an AI provider or
rendered into a document. It is the single source of truth for cross-entity
references across all StudioBrain domains.

### Variable Syntax Reference

| Form | Example | Resolves to |
|------|---------|-------------|
| Local field | `$name` | Current entity's `name` field |
| Cross-entity implicit | `$character.name` | `name` of the nearest character in context |
| Cross-entity explicit | `$character:rusty_mcdaniels.name` | `name` of the entity with `id: rusty_mcdaniels` |
| Nested dot-path | `$character:rusty_mcdaniels.appearance.hair_color.hex` | Deep field traversal |

### Resolution Pipeline

```
Template text
     │
     ▼
1. PARSE    — tokenise all $… tokens; validate syntax (pe_001–pe_004)
     │
     ▼
2. PLAN     — deduplicate entity lookups; batch into minimum DB queries (pe_050)
     │
     ▼
3. FETCH    — retrieve entities; verify existence (pe_010, pe_011)
     │
     ▼
4. RESOLVE  — walk nested dot-paths; apply fallback strategy (pe_012–pe_015)
     │
     ▼
5. SANITISE — HTML-escape, truncate to 1 000 chars per value (pe_030)
     │
     ▼
6. SUBSTITUTE — replace tokens in template text with resolved values
     │
     ▼
Resolved prompt string  →  AI provider  OR  document renderer
```

### Supported Entity Type Tokens

`character` · `location` · `item` · `brand` · `faction` · `district` ·
`quest` · `dialogue` · `event` · `campaign` · `timeline` · `assembly` ·
`job` · `universe`

### Fallback Strategies

| Strategy | Behaviour when variable cannot be resolved |
|----------|--------------------------------------------|
| `empty_string` *(default)* | Substitute `""` |
| `placeholder` | Leave the original token (e.g. `$character.name`) in the output |
| `skip` | Remove the sentence containing the unresolved token |
| `error` | Abort resolution and return an error regardless of `strict_mode` |

### Domain-Agnostic Examples

**Game / Narrative**
```
Write a scene where $character.name visits $location.name.
Describe $character:rusty_mcdaniels.name working at $location:rustys_auto_repair.name.
```

**Film / TV**
```
Draft a cold-open where $character.name discovers $item.name inside $location.name.
```

**Cooking**
```
Create a recipe using $ingredient.name with $technique.method, cooked at $location.name.
```

**Universal document template**
```
# $name — Profile Sheet
**Age:** $age  |  **Location:** $primary_location
**Faction:** $faction
```

### Integration with Generation Rules

Rule `gen_011` (GENERATION_RULES.md) already requires entity existence validation
before any cross-reference is used in generated content. The Prompt Engine's
`pe_010` rule enforces the same constraint automatically at resolution time,
preventing hallucinated entity references before they reach an AI provider.

### Cache Invalidation

Entity update events (`entity.updated`) emitted by the backend automatically
invalidate all cache entries whose key matches the updated entity's
`{entity_type}:{entity_id}` prefix. This ensures stale resolved values are never
used after an entity is edited.

### See Also

- `PROMPT_TEMPLATE.md` — template definition for authoring new prompts
- `GENERATION_RULES.md` — global AI generation rules (gen_011, gen_012)
- Plugin: `prompt-engine` — REST API and UI for resolving and testing prompts
