---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: author
folder_name: Authors
file_prefix: AUTHOR_
ui_icon: PenLine
ui_color: '#6d28d9'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Use the author’s preferred byline and approved biography. Record their expertise and availability as supplied and leave unknown contact details blank.
associated_rules: []
field_config:
  status:
    type: enum
    widget: select
    options:
    - value: active
      label: Active
    - value: on_leave
      label: On leave
    - value: alumni
      label: Alumni
  byline:
    type: string
    widget: text
  biography:
    type: text
    widget: textarea
  portrait:
    type: image
    widget: image-ref
  beats:
    type: tags
    widget: tag-input
    allow_custom: true
  channel_refs:
    type: references
    widget: entity-multiselect
    reference_type: channel
  editor_name:
    type: string
    widget: text
  availability:
    type: string
    widget: text
  next_available:
    type: date
    widget: date
  contact_email:
    type: email
    widget: email
  portfolio_url:
    type: url
    widget: url
  assignment_notes:
    type: text
    widget: textarea
status: active
byline: ''
biography: ''
portrait: ''
beats: []
channel_refs: []
editor_name: ''
availability: ''
next_available: null
contact_email: ''
portfolio_url: ''
assignment_notes: ''
views:
  default: cards
  enabled:
  - cards
  - table
  - gallery
  - calendar
  roles:
    title: name
    subtitle: byline
    badges:
    - status
    - beats
    card_fields:
    - editor_name
    - availability
    - next_available
    image: portrait
  calendar:
    date_field: next_available
  gallery:
    aspect: landscape
  table:
    columns:
    - key: name
    - key: byline
    - key: beats
    - key: editor_name
    - key: availability
---
# Author
