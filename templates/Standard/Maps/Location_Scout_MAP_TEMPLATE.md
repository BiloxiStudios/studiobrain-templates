---
template_category: map
template_name: Location Scout
template_id: location-scout
description: Real-world geographic map for location scouting with address search, route planning, and geo-fencing.
icon: globe
renderer: geo-leaflet
renderer_config:
  center: [34.0522, -118.2437]
  default_zoom: 12
  span: 1.0
layers:
  - id: entities
    label: Locations
    type: entity-pins
    pin_types: [filming, reference, logistics]
    default_visible: true
  - id: routes
    label: Routes
    type: line-overlay
    default_visible: true
  - id: zones
    label: Zones
    type: overlay
    default_visible: true
pin_types:
  filming:
    icon: video
    color: "#3b82f6"
    entity_types: [location]
  reference:
    icon: image
    color: "#8b5cf6"
    entity_types: [location]
  logistics:
    icon: truck
    color: "#eab308"
    entity_types: [location]
fields:
  project_name:
    type: text
    label: Project Name
    required: true
  shoot_date:
    type: date
    label: Shoot Date
  permit_status:
    type: select
    label: Permit Status
    options: [pending, approved, denied, not-required]
  notes:
    type: textarea
    label: Scout Notes
tags:
  - film-tv
  - location-scouting
  - production
---

# Location Scout

A geographic map for scouting real-world filming locations. Search addresses, plan routes between locations, and draw geo-fence zones for permit boundaries.
