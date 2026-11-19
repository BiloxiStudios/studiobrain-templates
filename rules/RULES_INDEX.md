# RULES INDEX
## Master rules directory

### 🎯 Purpose
This directory contains the generation and validation rules shipped with a starter pack. These rules are:
- **Machine-readable** for API/application settings
- **Human-readable** for designers and writers
- **LLM-compatible** for AI generation

### 📋 Rule Categories

| File | Purpose | Used By |
|------|---------|---------|
| [ASSEMBLY_RULES.md](ASSEMBLY_RULES.md) | Assembly slot system, inheritance hierarchy, z-index ordering, slot locking, export profiles | Assembly Composer, Export Pipeline |
| [CHARACTER_RULES.md](CHARACTER_RULES.md) | Character creation, relationships, dialogue | Character Builder, Story Generator |
| [CHARACTER_WORKFLOW.md](CHARACTER_WORKFLOW.md) | Character status state machine (11 stages) | Character Builder, QA |
| [LOCATION_RULES.md](LOCATION_RULES.md) | Location atmosphere, brands, NPCs | World Builder, Location Generator |
| [LOCATION_WORKFLOW.md](LOCATION_WORKFLOW.md) | Location status state machine (14 stages) | World Builder, QA |
| [BRAND_RULES.md](BRAND_RULES.md) | Brand identity, products, marketing | Brand Creator, Ad Generator |
| [ITEM_RULES.md](ITEM_RULES.md) | Item stats, rarity, abnormalities | Item Builder, Balance |
| [ITEM_WORKFLOW.md](ITEM_WORKFLOW.md) | Item status state machine (12 stages) | Item Builder, QA |
| [DIALOGUE_RULES.md](DIALOGUE_RULES.md) | Conversation flow, personality expression | Dialogue System, Voice AI |
| [QUEST_RULES.md](QUEST_RULES.md) | Quest structure, rewards, progression | Quest Designer, Story Builder |
| [QUEST_WORKFLOW.md](QUEST_WORKFLOW.md) | Quest status state machine (12 stages) | Quest Designer, QA |
| [IMAGE_GENERATION_RULES.md](IMAGE_GENERATION_RULES.md) | Visual style, prompts, consistency | ComfyUI, DALL-E, Stable Diffusion |
| [VOICE_GENERATION_RULES.md](VOICE_GENERATION_RULES.md) | Voice profiles, pronunciation, emotion | ElevenLabs, Voice Synthesis |
| [COMBAT_RULES.md](COMBAT_RULES.md) | Combat mechanics, damage, abilities | Game Systems, Combat AI |
| [FACTION_RULES.md](FACTION_RULES.md) | Faction dynamics, territory, loyalty | World State, Political System |
| [WORKFLOW_RULES.md](WORKFLOW_RULES.md) | Workflow system documentation and examples | All Systems |
| [PROMPT_ENGINE_RULES.md](PROMPT_ENGINE_RULES.md) | Cross-entity variable resolution syntax, pipeline, caching, and security | Prompt Engine Plugin, AI Generation, Document Renderer |

### 🔧 Application Settings Integration

```yaml
# Example application settings.yaml
rules_config:
  enforce_strict: false  # only validation_type error blocks a write
  rules_directory: "_Rules/"
  
  character_generation:
    rules_file: "CHARACTER_RULES.md"
    enforce:
      - "char_001"  # primary location; warning, does not block
      - "char_002"  # ID format; warning, does not block
      - "char_003"  # Nickname usage; warning, does not block
    
  dialogue_generation:
    rules_file: "DIALOGUE_RULES.md"
    personality_modifiers: true
    relationship_aware: true
    
  image_generation:
    rules_file: "IMAGE_GENERATION_RULES.md"
    style_preset: ""  # Fill from this project
    
  validation:
    on_create: true
    on_update: true
    on_import: true
```

### 📐 Rule Structure Standard

Every rules file follows this structure:
```yaml
# CATEGORY_RULES.md

## MANDATORY RULES
rules:
  - id: "unique_id"
    category: "subcategory"
    priority: "critical|high|medium|low"   # importance only; does not block
    validation_type: "warning"             # default. a starter pack keeps one error example
    rule: "The actual rule"
    implementation: "How to implement"

## GENERATION DEFAULTS
defaults:
  field_name: "default_value"

## VALIDATION CHECKLIST
validation:
  - "Check item 1"
  - "Check item 2"
```

### 🚀 Quick Usage

#### For LLMs/AI:
```
Load rules from _Rules/CHARACTER_RULES.md
Block a write only when validation_type is error
Record warning, info, and suggestion; they do not block
New rules default to validation_type warning
Use generation defaults for missing fields
Validate output against checklist
```

#### For Humans:
1. Open relevant rules file
2. Read mandatory rules section
3. Follow generation defaults
4. Use validation checklist before saving

#### For APIs:
```python
from rules_engine import RulesLoader

rules = RulesLoader("_Rules/CHARACTER_RULES.md")
character = rules.validate(new_character_data)
character = rules.apply_defaults(character)
```

### 🔄 Rule Updates

When updating rules:
1. Increment version in rule file header
2. Document change in CHANGELOG section
3. Test with existing content for conflicts
4. Update application settings if needed

### ⚠️ Rule level

`validation_type` is the level. Generation files that use `severity` mean the same thing.

- **error**: Blocks the write. A starter pack keeps one example, a case a new user would expect to be refused. Do not add a second.
- **warning**: Recorded on the row. Does not block. This is the default for a new rule.
- **info**: Recorded. Does not block.
- **suggestion**: Recorded. Does not block.

Unresolved references, missing optional links, and prose or style checks are `warning`. Do not ship those as `error`.

`priority` (`critical`, `high`, `medium`, `low`) is importance for generation and review. It does not block a write. A `critical` priority with `validation_type: warning` is recorded and the write succeeds.

---

## Integration Examples

### Studio settings page
```javascript
// Load available rules
const ruleCategories = loadRulesIndex('_Rules/RULES_INDEX.md');

// Settings UI
<RulesConfiguration>
  {ruleCategories.map(category => (
    <RuleToggle 
      category={category}
      enabled={settings[category].enabled}
      strictMode={settings[category].strict}
    />
  ))}
</RulesConfiguration>
```

### Story Builder Integration
```python
# When generating new story content
story_rules = load_rules([
    'CHARACTER_RULES.md',
    'DIALOGUE_RULES.md', 
    'LOCATION_RULES.md'
])

generated_content = ai_generate(
    prompt=user_prompt,
    rules=story_rules,
    block_on="error",  # warning, info, and suggestion are recorded and do not block
)
```

### Validation Pipeline
```yaml
# Pre-commit hook
validate_entity:
  - load_rules_for_type(entity_type)
  - check_mandatory_rules()
  - validate_relationships()
  - ensure_media_exists()
  - verify_cross_references()
```