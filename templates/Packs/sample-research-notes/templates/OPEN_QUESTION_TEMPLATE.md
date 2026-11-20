---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: open_question
folder_name: OpenQuestions
file_prefix: OPEN_QUESTION_
ui_icon: CircleHelp
ui_color: '#92400e'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Frame one answerable question, describe why it matters and list the evidence that would resolve it. Keep tentative explanations separate from findings.
associated_rules: []
field_config:
  status:
    type: enum
    widget: select
    options:
    - value: open
      label: Open
    - value: investigating
      label: Investigating
    - value: answered
      label: Answered
    - value: parked
      label: Parked
  context:
    type: text
    widget: textarea
  research_owner:
    type: string
    widget: text
  priority_level:
    type: enum
    widget: select
    options:
    - value: low
      label: Low
    - value: normal
      label: Normal
    - value: high
      label: High
  working_hypothesis:
    type: text
    widget: textarea
  method:
    type: text
    widget: textarea
  source_refs:
    type: references
    widget: entity-multiselect
    reference_type: source
  finding_refs:
    type: references
    widget: entity-multiselect
    reference_type: finding
  resolution_criteria:
    type: text
    widget: textarea
  next_review:
    type: date
    widget: date
  opened_on:
    type: date
    widget: date
  topics:
    type: tags
    widget: tag-input
    allow_custom: true
status: open
context: ''
research_owner: ''
priority_level: ''
working_hypothesis: ''
method: ''
source_refs: []
finding_refs: []
resolution_criteria: ''
next_review: null
opened_on: null
topics: []
views:
  default: board
  enabled:
  - board
  - cards
  - table
  - calendar
  roles:
    title: name
    subtitle: research_owner
    badges:
    - status
    - priority_level
    card_fields:
    - method
    - next_review
    - finding_refs
  board:
    group_by: status
  calendar:
    date_field: next_review
  table:
    columns:
    - key: name
    - key: status
    - key: priority_level
    - key: research_owner
    - key: next_review
  facets:
  - status
  - priority_level
---
# Open Question
