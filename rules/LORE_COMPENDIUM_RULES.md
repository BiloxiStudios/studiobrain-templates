---
system_prompt: >-
  Generate a lore compendium grounded in the project's established world.
  Keep the chronology, names, and relationships consistent and label unresolved
  questions and in-world accounts.
global: false
priority: high
entity_type: lore_compendium
template_reference: LORE_COMPENDIUM_TEMPLATE.md

rules:
- id: lore_compendium_001
  category: chronology
  priority: high
  rule: Keep timeline eras and historical_events dates in the project's calendar, and preserve established ordering when exact dates are unknown.
  validation_type: warning
  applies_to: [lore_compendium]

- id: lore_compendium_002
  category: references
  priority: high
  rule: Use consistent project names for faction relationships, connected_locations, related_entities, and related_documents. Describe each recorded connection accurately.
  validation_type: warning
  applies_to: [lore_compendium]

- id: lore_compendium_003
  category: canon
  priority: medium
  rule: Keep unconfirmed explanations in mysterious_incidents.open_questions and distinguish mythological_entities legends from established history.
  validation_type: warning
  applies_to: [lore_compendium]
---

# Lore compendium rules

Summarize recorded world events with their consequences and affected parties.
If the project contains conflicting accounts, attribute each account and keep
the disagreement visible.

Use terminology and slang_and_idioms to explain unfamiliar words in context.
Keep canonical_sources tied to sources recorded for this work.
