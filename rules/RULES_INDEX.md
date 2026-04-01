# RULES INDEX
## City of Brains Universe - Master Rules Directory

### 🎯 Purpose
This directory contains ALL generation and validation rules for the City of Brains universe. These rules are:
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

### 🔧 Application Settings Integration

```yaml
# Example application settings.yaml
rules_config:
  enforce_strict: true
  rules_directory: "_Rules/"
  
  character_generation:
    rules_file: "CHARACTER_RULES.md"
    enforce:
      - "char_001"  # Must have location
      - "char_002"  # ID format
      - "char_003"  # Nickname usage
    
  dialogue_generation:
    rules_file: "DIALOGUE_RULES.md"
    personality_modifiers: true
    relationship_aware: true
    
  image_generation:
    rules_file: "IMAGE_GENERATION_RULES.md"
    style_preset: "city_of_brains_v2"
    
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
    priority: "critical|high|medium|low"
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
Apply mandatory rules with priority: critical
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

### ⚠️ Priority Levels

- **CRITICAL**: System will reject if not followed
- **HIGH**: Warning issued, should fix
- **MEDIUM**: Suggestion, recommended
- **LOW**: Nice to have, optional

---

## Integration Examples

### City of Brains Studio Settings Page
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
    enforce_critical=True
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