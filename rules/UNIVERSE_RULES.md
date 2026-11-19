---
# UNIVERSE CONFIGURATION METADATA
system_prompt: "You are creating content for this project. Follow the universe entity this project records. Do not invent a setting, an era, a technology ban, a catastrophe, or a visual style the project has not recorded. A place must exist as an entity before other content names it."
global: true
priority: "critical"
universe_id: "project"
applies_to: ["character", "location", "brand", "faction", "dialogue", "story", "item", "quest"]

# UNIVERSE CORE SPECIFICATIONS
universe_name: ""
genre: ""
era: ""
time_period: ""
technology_level: ""
art_style: ""
tone: ""
content_rating: ""

# CRITICAL UNIVERSE RULES
rules:
  - id: "universe_001"
    category: "technology"
    priority: "critical"
    rule: "Technology references must stay inside the limits recorded on this project. forbidden_tech and allowed_tech are empty in the starter so the project can fill them. Do not invent a device ban the project has not recorded."
    validation_type: "warning"
    forbidden_tech: []
    allowed_tech: []
  - id: "universe_002"
    category: "timeline"
    priority: "critical"
    rule: "Cultural and technology references must match the era this project records. Do not import a later era's devices, slang, or institutions."
    validation_type: "warning"
    
  - id: "universe_003"
    category: "narrative"
    priority: "critical"
    rule: "Narrative events must stay consistent with the history this project records. Do not invent a central catastrophe the project has not established."
    validation_type: "warning"
    
  - id: "universe_004"
    category: "geography"
    priority: "critical"
    rule: "A place named in content must be an entity this project already has, or be added as its own entity before anything else names it."
    validation_type: "warning"
    
  - id: "universe_005"
    category: "tone"
    priority: "critical"
    rule: "Tone must match the tone this project records. Do not shift genre or humor unless the project asks for it."
    validation_type: "warning"
    
  - id: "universe_006"
    category: "visual"
    priority: "high"
    rule: "Visual descriptions must match the art style this project records."
    validation_type: "warning"
---

# Universe guidance

This file is the project's top-level consistency check. It does not define a setting.

Read the project's universe entity and follow it. Technology, era, tone, visual style, and history are whatever that entity records. The starter leaves forbidden_tech and allowed_tech empty so the project can fill them.

Do not add a device ban, a central catastrophe, a map, or an art style the project has not recorded. A new place is added as its own entity before other content names it.
