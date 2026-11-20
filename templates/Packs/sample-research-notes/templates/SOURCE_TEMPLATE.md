---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: source
folder_name: Sources
file_prefix: SOURCE_
ui_icon: Library
ui_color: '#155e75'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Describe the original source and how to locate it. Preserve exact quotations and distinguish the speaker’s words from the researcher’s observations.
associated_rules:
- SOURCE_RULES.md
field_config:
  source_kind:
    type: enum
    widget: select
    options:
    - value: interview
      label: Interview
    - value: document
      label: Document
    - value: dataset
      label: Dataset
    - value: observation
      label: Observation
    - value: publication
      label: Publication
  summary:
    type: text
    widget: textarea
  source_url:
    type: url
    widget: url
  citation:
    type: text
    widget: textarea
  creator_name:
    type: string
    widget: text
  published_on:
    type: date
    widget: date
  accessed_on:
    type: date
    widget: date
  collected_by:
    type: string
    widget: text
  topics:
    type: tags
    widget: tag-input
    allow_custom: true
  locator:
    type: string
    widget: text
  access_notes:
    type: text
    widget: textarea
  source_notes:
    type: text
    widget: textarea
source_kind: ''
summary: ''
source_url: ''
citation: ''
creator_name: ''
published_on: null
accessed_on: null
collected_by: ''
topics: []
locator: ''
access_notes: ''
source_notes: ''
views:
  default: table
  enabled:
  - table
  - cards
  - calendar
  roles:
    title: name
    subtitle: creator_name
    badges:
    - source_kind
    - topics
    card_fields:
    - accessed_on
    - citation
  calendar:
    date_field: accessed_on
  table:
    columns:
    - key: name
    - key: source_kind
    - key: creator_name
    - key: published_on
    - key: accessed_on
  facets:
  - source_kind
  - topics
---
# Source
