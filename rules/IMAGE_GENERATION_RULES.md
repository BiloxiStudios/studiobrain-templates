---
system_prompt: Generate image prompts for the City of Brains universe with low-poly
  luxe aesthetic, 1990s retro-futuristic style, dramatic lighting with neon accents,
  and synthwave color palette. Use deep purples, electric yellows, and toxic greens.
global: false
priority: medium
entity_type: image
rules:
- id: img_001
  category: style
  priority: high
  rule: All images must use low-poly luxe aesthetic with 1990s retro-futuristic style
  validation_type: warning
  applies_to:
  - image
- id: img_002
  category: lighting
  priority: high
  rule: Use dramatic, cinematic lighting with neon accents
  validation_type: warning
  applies_to:
  - image
- id: img_003
  category: colors
  priority: high
  rule: 'Color palette: deep purples, electric yellows, toxic greens'
  validation_type: warning
  applies_to:
  - image
- id: img_004
  category: character
  priority: critical
  rule: 'Characters require: front facing, 3/4 left, 3/4 right portraits'
  validation_type: error
  applies_to:
  - character
  - image
created_by: System
last_updated: '2025-01-11'
version: '1.0'
---

# Image Generation Guidelines

## ComfyUI Workflows
- Character portraits: Use workflow_portrait_v2.json
- Environment concepts: Use workflow_environment_v1.json
- Brand logos: Use workflow_logo_clean.json

## Stable Diffusion Settings
- Model: SDXL 1.0 or custom City of Brains checkpoint
- Steps: 30-50 for quality
- CFG Scale: 7-9
- Sampler: DPM++ 2M Karras

## DALL-E 3 Format
```
[Style: Low-poly luxe, 1990s retro-futuristic]
[Lighting: Dramatic, cinematic with neon accents]
[Colors: Deep purples, electric yellows, toxic greens]
[Subject description]
```

## Midjourney Format
```
[Subject] --style raw --ar 16:9 --v 6
synthwave aesthetic, 1990s retro futuristic, low poly luxe
```

## Required Angles for Characters
- Portrait: Front facing, 3/4 left, 3/4 right
- Full body: Front, back, left profile, right profile
- Action poses: Combat ready, idle, interaction