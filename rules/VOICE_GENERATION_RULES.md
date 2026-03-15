---
system_prompt: Generate voice samples and dialogue for City of Brains characters.
  Ensure voice matches character personality, age, and background. Include emotional
  variations and character catchphrases.
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

# Voice Generation Guidelines

## ElevenLabs Settings
- Model: Eleven Multilingual v2
- Stability: 0.5-0.7 (natural variation)
- Similarity Boost: 0.75
- Style: 0.2-0.3 (for character emotion)

## Pronunciation Guide Format
```yaml
pronunciations:
  - word: "BOL"
    phonetic: "bowl"
    ipa: "/boʊl/"
  - word: "NeuroNuggets"
    phonetic: "NEW-row-NUG-ets"
    emphasis: "first syllable"
```

## Voice Sample Requirements
- 3-5 minutes of clean audio
- Multiple emotional states (neutral, happy, angry, scared)
- Include character catchphrases
- 44.1kHz, 16-bit WAV format

## Dialogue Tags
- `[pause]` - 0.5 second pause
- `[emphasis]` - Stress next word
- `[whisper]` - Lower volume/intensity
- `[shout]` - Increase volume/intensity
- `[sarcastic]` - Tonal shift