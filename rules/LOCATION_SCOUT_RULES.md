---
system_prompt: >-
  Prepare a geographic scout for this production. Organize locations, routes, constraints, and shoot logistics around information the project can verify, and flag open questions for follow-up.
global: false
priority: high
entity_type: location_scout
template_reference: Location_Scout_MAP_TEMPLATE.md
rules:
  - id: location_scout_001
    category: locations
    priority: high
    rule: >-
      Use filming, reference, and logistics pins for their respective purposes. Use verified coordinates or addresses for placement and mark uncertain positions in notes for confirmation.
    validation_type: warning
    applies_to: [location_scout]
  - id: location_scout_002
    category: permits
    priority: high
    rule: >-
      Record permit_status using the template options. Keep unconfirmed permissions pending, and use notes for boundaries, access restrictions, and dates that the production still needs to confirm.
    validation_type: warning
    applies_to: [location_scout]
  - id: location_scout_003
    category: logistics
    priority: medium
    rule: >-
      Connect known stops in the routes layer, and use zones for known geographic boundaries. Tie timing and access notes to shoot_date when available and distinguish estimates from confirmed arrangements.
    validation_type: warning
    applies_to: [location_scout]
---

# Location scout generation rules

Group confirmed stops by filming, reference, or logistics purpose. Use
verified addresses or coordinates for pins, and put unconfirmed locations in
the scout notes for follow-up.

Map known routes and permit boundaries where available. Record pending
permissions, access limits, and route estimates in the notes so the crew can
see what needs confirmation before the shoot date.
