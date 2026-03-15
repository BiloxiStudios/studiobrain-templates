# City of Brains - Standardized Templates

## ✅ THESE ARE THE OFFICIAL TEMPLATES

Use these templates for ALL entity creation, whether through the app or external LLMs.

## 📋 Template List

| Entity Type | Template File | Folder Prefix | File Prefix |
|------------|--------------|---------------|-------------|
| Character | [CHARACTER_TEMPLATE.md](CHARACTER_TEMPLATE.md) | `Characters/[character_id]/` | `CH_` |
| Location | [LOCATION_TEMPLATE.md](LOCATION_TEMPLATE.md) | `Locations/[location_id]/` | `LOC_` |
| Brand | [BRAND_TEMPLATE.md](BRAND_TEMPLATE.md) | `Brands/[brand_id]/` | `BR_` |
| District | [DISTRICT_TEMPLATE.md](DISTRICT_TEMPLATE.md) | `Districts/[district_id]/` | `DIST_` |
| Faction | [FACTION_TEMPLATE.md](FACTION_TEMPLATE.md) | `Factions/[faction_id]/` | `FAC_` |
| Campaign | [CAMPAIGN_TEMPLATE.md](CAMPAIGN_TEMPLATE.md) | `Campaigns/[campaign_id]/` | `CAMP_` |
| Quest | [QUEST_TEMPLATE.md](QUEST_TEMPLATE.md) | `Quests/[quest_id]/` | `QUEST_` |
| Event | [EVENT_TEMPLATE.md](EVENT_TEMPLATE.md) | `Events/[event_id]/` | `EVENT_` |

## 🚀 Quick Start

### Creating a New Entity

1. **Choose the appropriate template** from the list above
2. **Copy the template** to create your new entity
3. **Follow naming conventions**:
   - Entity ID: `lowercase_with_underscores`
   - Folder name must match entity ID
   - File name: `PREFIX_entityid.md`
4. **Fill in required fields** (marked as REQUIRED in template)
5. **Add narrative content** in markdown section below YAML
6. **Place media files** in `media/` subfolder

### Example: Creating a Character

```bash
# 1. Create folder structure
Characters/
└── john_survivor/
    ├── CH_john_survivor.md    # Main file
    └── media/
        ├── portrait.png
        └── voice_greeting.mp3

# 2. File content structure
---
template_version: "1.0"
character_id: "john_survivor"
created_date: "2024-06-01"
last_updated: "2024-06-01"
status: "active"
full_name: "John 'Lucky' Sullivan"
# ... rest of YAML fields
---

# John "Lucky" Sullivan

## Background Story
[Narrative content here...]
```

## ⚠️ Critical Rules

### IDs and Naming
- **ALL IDs**: Must be `lowercase_with_underscores`
- **NO SPACES**: Never use spaces in IDs or folder names
- **CONSISTENCY**: Folder name = entity_id in YAML
- **PREFIXES**: Always use the correct file prefix

### Field Standards
- **Required Fields**: Cannot be null or missing
- **Lists**: Use proper YAML array syntax with `-`
- **Cross-references**: Must point to valid entity IDs
- **Dates**: ISO-8601 format (YYYY-MM-DD)

### File Structure
```
A:\Brains\
├── PROJECT_RULES.md           # READ THIS FIRST!
├── _Templates\
│   └── Standard\              # These templates
├── Characters\
│   └── [character_id]\
│       ├── CH_[character_id].md
│       └── media\
├── Locations\
│   └── [location_id]\
│       ├── LOC_[location_id].md
│       └── media\
└── [Other entity folders...]
```

## 🔄 Application Integration

These templates are 100% aligned with:
- **Backend**: `CityBrainsStoryBuilder/backend/schemas.py`
- **Frontend**: `city-brains-studio/src/types/index.ts`
- **Database**: SQLAlchemy models in `models.py`

### Key Field Mappings

| Template Field | Database Field | Frontend Field | Notes |
|---------------|---------------|----------------|--------|
| character_id | character_id | character_id | Always lowercase |
| full_name | full_name | full_name | Human readable |
| location_id | location_id | location_id | Always lowercase |
| display_name | display_name | display_name | For locations |
| brand_id | brand_id | brand_id | Always lowercase |
| brand_name | brand_name | name* | *Frontend uses 'name' |

## 📝 YAML Frontmatter Rules

### Required for ALL Entities
```yaml
template_version: "1.0"
entity_id: "unique_lowercase_id"
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
status: "active"
```

### Optional Fields
- Can be `null` or omitted entirely
- Empty lists should be `[]`
- Empty strings should be `null`

### Structured Data
```yaml
# Good - Structured object
primary_skills:
  - skill: "combat"
    level: 5
    category: "physical"

# Bad - Simple strings (unless template specifies)
primary_skills:
  - "combat"
```

## 🎮 Entity Relationships

### Cross-References
All entity references use the target's `entity_id`:

```yaml
# Character referencing location
primary_location: "deal_mart"  # Points to Locations/deal_mart/

# Location referencing character
primary_npcs:
  - "gary_gasstation"  # Points to Characters/gary_gasstation/

# Brand referencing both
headquarters: "megamart_hq"  # Points to Locations/megamart_hq/
key_personnel:
  - character_id: "ceo_smith"  # Points to Characters/ceo_smith/
```

## 🛠️ Validation Checklist

Before creating/updating an entity:

- [ ] Entity ID is lowercase_with_underscores
- [ ] Folder name matches entity_id
- [ ] File has correct prefix (CH_, LOC_, etc.)
- [ ] All required fields are present
- [ ] Cross-references point to existing entities
- [ ] Media files are in media/ subfolder
- [ ] YAML syntax is valid
- [ ] Dates are in ISO-8601 format

## 🚫 Common Mistakes to Avoid

1. **Mixed Case IDs**: ❌ `GaryGasStation` → ✅ `gary_gasstation`
2. **Spaces in IDs**: ❌ `gary gas station` → ✅ `gary_gasstation`
3. **Wrong Prefix**: ❌ `gary_gasstation.md` → ✅ `CH_gary_gasstation.md`
4. **Missing Required Fields**: Always include all REQUIRED fields
5. **Invalid References**: Ensure referenced entities exist
6. **Wrong Field Names**: Use exact field names from templates

## 📚 Additional Resources

- **Main Rules**: See [PROJECT_RULES.md](../../PROJECT_RULES.md)
- **Backend Schema**: `CityBrainsStoryBuilder/backend/schemas.py`
- **Frontend Types**: `city-brains-studio/src/types/index.ts`
- **Database Models**: `CityBrainsStoryBuilder/backend/models.py`

## 🤖 For LLM Users

When generating content with AI:

1. **Provide the template**: Give the AI the exact template to follow
2. **Specify the entity_id**: Must be lowercase_with_underscores
3. **List existing entities**: For proper cross-references
4. **Request structured YAML**: Not simplified versions
5. **Validate output**: Check against this README

Example prompt:
```
Create a new character using the CHARACTER_TEMPLATE.md template.
Entity ID: john_survivor
Primary location: deal_mart (existing location)
Faction: survivors_alliance (existing faction)
Ensure all IDs are lowercase_with_underscores.
```

---

**Remember**: These templates are the single source of truth for entity structure!