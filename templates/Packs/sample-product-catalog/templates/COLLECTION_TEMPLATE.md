---
id: unique_lowercase_id
name: ''
template_version: '1.0'
template_category: entity
entity_type: collection
folder_name: Collections
file_prefix: COLLECTION_
ui_icon: Layers
ui_color: '#a16207'
editable: true
marketplace_eligible: true
generation_instructions: |-
  Curate a display from existing products. Use only product references supplied by the merchandiser and keep the collection’s own hero image separate from product images.
associated_rules: []
field_config:
  status:
    type: enum
    widget: select
    options:
    - value: draft
      label: Draft
    - value: featured
      label: Featured
    - value: archived
      label: Archived
  description:
    type: text
    widget: textarea
  cover_image:
    type: image
    widget: image-ref
  collection_code:
    type: string
    widget: text
  product_refs:
    type: references
    widget: entity-multiselect
    reference_type: product
  audience:
    type: string
    widget: text
  season:
    type: string
    widget: text
  featured_from:
    type: date
    widget: date
  featured_until:
    type: date
    widget: date
  display_location:
    type: string
    widget: text
  curator:
    type: string
    widget: text
  display_notes:
    type: text
    widget: textarea
status: draft
description: ''
cover_image: ''
collection_code: ''
product_refs: []
audience: ''
season: ''
featured_from: null
featured_until: null
display_location: ''
curator: ''
display_notes: ''
views:
  default: gallery
  enabled:
  - gallery
  - cards
  - table
  - calendar
  roles:
    title: name
    subtitle: audience
    badges:
    - status
    - season
    card_fields:
    - featured_from
    - featured_until
    - curator
    image: cover_image
  calendar:
    date_field: featured_from
  gallery:
    aspect: landscape
  facets:
  - status
  - season
---
# Collection
