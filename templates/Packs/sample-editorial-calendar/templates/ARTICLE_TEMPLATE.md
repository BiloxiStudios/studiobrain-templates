---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: article
folder_name: Articles
file_prefix: ARTICLE_
ui_icon: Newspaper
ui_color: '#9f1239'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Draft the article for the named channel and audience. Write a usable headline and summary, use supplied references, and leave unpublished dates or assignments empty until agreed.
associated_rules:
- ARTICLE_RULES.md
field_config:
  summary:
    type: text
    widget: textarea
  article_copy:
    type: markdown
    widget: rich-text
  primary_image:
    type: image
    widget: image-ref
  status:
    type: enum
    widget: select
    options:
    - value: pitch
      label: Pitch
    - value: drafting
      label: Drafting
    - value: editing
      label: Editing
    - value: scheduled
      label: Scheduled
    - value: published
      label: Published
  publish_date:
    type: date
    widget: date
  channel_ref:
    type: reference
    widget: entity-selector
    reference_type: channel
  author_ref:
    type: reference
    widget: entity-selector
    reference_type: author
  editor_name:
    type: string
    widget: text
  audience:
    type: string
    widget: text
  topic_tags:
    type: tags
    widget: tag-input
    allow_custom: true
  source_links:
    type: text
    widget: textarea
  call_to_action:
    type: text
    widget: textarea
  review_notes:
    type: text
    widget: textarea
summary: ''
article_copy: ''
primary_image: ''
status: pitch
publish_date: null
channel_ref: ''
author_ref: ''
editor_name: ''
audience: ''
topic_tags: []
source_links: ''
call_to_action: ''
review_notes: ''
views:
  default: calendar
  enabled:
  - calendar
  - cards
  - table
  - gallery
  - board
  roles:
    title: name
    subtitle: summary
    badges:
    - status
    - topic_tags
    card_fields:
    - publish_date
    - channel_ref
    - author_ref
    image: primary_image
  board:
    group_by: status
  calendar:
    date_field: publish_date
  gallery:
    aspect: landscape
  table:
    columns:
    - key: name
    - key: status
    - key: channel_ref
    - key: author_ref
    - key: publish_date
  facets:
  - status
  - topic_tags
---
# Article
