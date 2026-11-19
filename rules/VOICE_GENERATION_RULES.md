---
system_prompt: "Generate voice samples and dialogue for characters in this project. Match the character's personality, age, and background as recorded. Include more than one emotional state, and any catchphrase the character already has."
global: false
priority: medium
entity_type: voice
rules:
- id: voice_001
  category: quality
  priority: critical
  rule: Voice samples must be 44.1kHz, 16-bit WAV format
  validation_type: error
  applies_to:
  - voice
  - character
- id: voice_002
  category: duration
  priority: high
  rule: Provide 3-5 minutes of clean audio for voice cloning
  validation_type: warning
  applies_to:
  - voice
- id: voice_003
  category: emotion
  priority: high
  rule: 'Include multiple emotional states: neutral, happy, angry, scared'
  validation_type: warning
  applies_to:
  - voice
  - character
created_by: System
last_updated: '2025-01-11'
version: '1.0'
---

# Voice guidance

Voice samples are 44.1 kHz, 16-bit WAV, with several minutes of clean audio and more than one emotional state.

Match the character as this project records them: age, background, and any catchphrase they already use. Pronounce names the way the project spells them. Do not import another setting's jargon into the sample script.
