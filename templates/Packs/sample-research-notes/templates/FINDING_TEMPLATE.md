---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: finding
folder_name: Findings
file_prefix: FINDING_
ui_icon: Lightbulb
ui_color: '#166534'
editable: true
marketplace_eligible: true
generation_instructions: |-
  State one finding, link the sources that support it and record where the evidence is weak or contradictory. Do not invent a source or a level of confidence.
associated_rules:
- FINDING_RULES.md
field_config:
  summary:
    type: text
    widget: textarea
  status:
    type: enum
    widget: select
    options:
    - value: proposed
      label: Proposed
    - value: reviewed
      label: Reviewed
    - value: superseded
      label: Superseded
  source_refs:
    type: references
    widget: entity-multiselect
    reference_type: source
  evidence_excerpt:
    type: text
    widget: textarea
  confidence:
    type: enum
    widget: select
    options:
    - value: low
      label: Low
    - value: moderate
      label: Moderate
    - value: high
      label: High
  limitations:
    type: text
    widget: textarea
  counterevidence:
    type: text
    widget: textarea
  question_refs:
    type: references
    widget: entity-multiselect
    reference_type: open_question
  topics:
    type: tags
    widget: tag-input
    allow_custom: true
  researcher:
    type: string
    widget: text
  reviewed_on:
    type: date
    widget: date
  next_action:
    type: text
    widget: textarea
summary: ''
status: proposed
source_refs: []
evidence_excerpt: ''
confidence: ''
limitations: ''
counterevidence: ''
question_refs: []
topics: []
researcher: ''
reviewed_on: null
next_action: ''
views:
  default: cards
  enabled:
  - cards
  - table
  - board
  roles:
    title: name
    subtitle: summary
    badges:
    - confidence
    - status
    card_fields:
    - source_refs
    - researcher
    - reviewed_on
  board:
    group_by: status
  table:
    columns:
    - key: name
    - key: confidence
    - key: source_refs
    - key: researcher
    - key: reviewed_on
  facets:
  - status
  - confidence
  - topics
---
# Finding
