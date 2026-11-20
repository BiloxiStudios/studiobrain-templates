---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: channel
folder_name: Channels
file_prefix: CHANNEL_
ui_icon: Radio
ui_color: '#1d4ed8'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Describe where and how this channel publishes. Record its actual audience, cadence and submission requirements without guessing a platform limit.
associated_rules: []
field_config:
  status:
    type: enum
    widget: select
    options:
    - value: active
      label: Active
    - value: paused
      label: Paused
    - value: retired
      label: Retired
  description:
    type: text
    widget: textarea
  channel_kind:
    type: enum
    widget: select
    options:
    - value: website
      label: Website
    - value: newsletter
      label: Newsletter
    - value: social
      label: Social
    - value: print
      label: Print
    - value: audio
      label: Audio
  public_url:
    type: url
    widget: url
  audience:
    type: string
    widget: text
  voice_notes:
    type: text
    widget: textarea
  cadence:
    type: string
    widget: text
  channel_owner:
    type: string
    widget: text
  headline_limit:
    type: integer
    widget: number
    min: 0
  submission_notes:
    type: text
    widget: textarea
  next_review:
    type: date
    widget: date
  topics:
    type: tags
    widget: tag-input
    allow_custom: true
status: active
description: ''
channel_kind: ''
public_url: ''
audience: ''
voice_notes: ''
cadence: ''
channel_owner: ''
headline_limit: null
submission_notes: ''
next_review: null
topics: []
views:
  default: table
  enabled:
  - table
  - cards
  roles:
    title: name
    subtitle: audience
    badges:
    - channel_kind
    - status
    card_fields:
    - cadence
    - channel_owner
  table:
    columns:
    - key: name
    - key: channel_kind
    - key: audience
    - key: cadence
    - key: channel_owner
  facets:
  - status
  - channel_kind
---
# Channel
