---
rules:
- id: inv_001
  category: naming
  priority: critical
  rule: Item IDs must use lowercase_with_underscores format
  validation_type: error
  applies_to:
  - inventory

- id: inv_002
  category: naming
  priority: critical
  rule: Item files must use ITEM_ prefix (e.g., ITEM_neural_sword.md)
  validation_type: error
  applies_to:
  - inventory

- id: inv_003
  category: verse_integration
  priority: high
  rule: Verse game_id must be within correct ranges - Currency (1-999), Weapons (1000-1999), Consumables (2000-2999), Cosmetics (3000-3999)
  validation_type: error
  applies_to:
  - inventory

- id: inv_004
  category: balance
  priority: high
  rule: Legendary items should have significant lore_significance and quest connections
  validation_type: warning
  applies_to:
  - inventory

- id: inv_005
  category: categorization
  priority: medium
  rule: Items with damage > 0 must have item_type as weapon
  validation_type: error
  applies_to:
  - inventory

- id: inv_006
  category: categorization
  priority: medium
  rule: Items with defense > 0 must have appropriate item_type (armor, clothing, etc.)
  validation_type: error
  applies_to:
  - inventory

- id: inv_007
  category: consumables
  priority: medium
  rule: Consumable items must have effects defined or usable set to true
  validation_type: warning
  applies_to:
  - inventory

- id: inv_008
  category: storage
  priority: medium
  rule: Items with stack_size > 1 should typically be materials or consumables
  validation_type: warning
  applies_to:
  - inventory

- id: inv_009
  category: economy
  priority: medium
  rule: Value should be proportional to rarity - common (1-100), uncommon (101-500), rare (501-2000), epic (2001-10000), legendary (10001+)
  validation_type: warning
  applies_to:
  - inventory

- id: inv_010
  category: lore
  priority: low
  rule: All weapons and key items should have flavor_text for immersion
  validation_type: warning
  applies_to:
  - inventory

- id: inv_011
  category: media
  priority: medium
  rule: All items should have icon_file defined for UI display
  validation_type: warning
  applies_to:
  - inventory

- id: inv_012
  category: world_consistency
  priority: high
  rule: No modern technology references beyond alternate 1990s tech level
  validation_type: error
  applies_to:
  - inventory

- id: inv_013
  category: brand_integration
  priority: low
  rule: Food items should typically have brand_id referencing a restaurant or food company
  validation_type: warning
  applies_to:
  - inventory

- id: inv_014
  category: quest_items
  priority: critical
  rule: Quest items should have quest_item set to true and reference required_quests
  validation_type: error
  applies_to:
  - inventory

- id: inv_015
  category: verse_storage
  priority: medium
  rule: Items with max_stack_size > 1000 may cause performance issues in Verse
  validation_type: warning
  applies_to:
  - inventory

- id: inv_016
  category: combat_balance
  priority: high
  rule: Weapons with damage > 100 should have cooldown or special restrictions
  validation_type: warning
  applies_to:
  - inventory

- id: inv_017
  category: rarity_consistency
  priority: medium
  rule: Unique rarity items should have exactly one spawn location or special acquisition method
  validation_type: warning
  applies_to:
  - inventory

- id: inv_018
  category: crafting
  priority: low
  rule: Craftable items should have realistic required_items and crafting_station
  validation_type: warning
  applies_to:
  - inventory

- id: inv_019
  category: sound_design
  priority: low
  rule: Weapons should have both pickup_sound and use_sound for audio feedback
  validation_type: warning
  applies_to:
  - inventory

- id: inv_020
  category: metadata
  priority: critical
  rule: All items must have template_version, created_date, and status defined
  validation_type: error
  applies_to:
  - inventory

- id: inv_021
  category: file_structure
  priority: medium
  rule: Item folders should contain appropriate asset subfolders (images/, audio/, data/, etc.)
  validation_type: warning
  applies_to:
  - inventory

- id: inv_022
  category: texture_references
  priority: medium
  rule: texture_path should reference actual texture files in the asset structure
  validation_type: warning
  applies_to:
  - inventory

- id: inv_023
  category: spawn_balance
  priority: medium
  rule: Rare and above items should not have spawn_rate > 0.1 to maintain scarcity
  validation_type: warning
  applies_to:
  - inventory

- id: inv_024
  category: vendor_pricing
  priority: medium
  rule: Vendor prices should be 110-150% of base item value for balanced economy
  validation_type: warning
  applies_to:
  - inventory

- id: inv_025
  category: ammo_consistency
  priority: high
  rule: Weapons with ammo_type must have damage > 0 and be ranged weapons
  validation_type: error
  applies_to:
  - inventory

---

# Inventory Rules Documentation

This file defines validation rules for inventory items in the City of Brains universe. These rules ensure consistency, balance, and proper integration across all systems.

## Rule Categories

### Critical Rules (Must Pass)
- **Naming**: Proper ID format and file naming conventions
- **Metadata**: Required template fields and version tracking
- **Verse Integration**: Game ID ranges and technical compatibility
- **Quest Items**: Proper flagging and quest relationships
- **Combat Balance**: Weapon damage and restriction validation

### High Priority Rules (Should Pass)
- **Balance**: Item rarity and value consistency  
- **World Consistency**: Lore and technology level adherence
- **Combat Balance**: Weapon restrictions and cooldowns

### Medium Priority Rules (Recommended)
- **Categorization**: Proper item type assignments
- **Economy**: Value and pricing guidelines
- **Storage**: Stack size and inventory behavior
- **Media**: Asset file requirements

### Low Priority Rules (Optional)
- **Immersion**: Flavor text and lore elements
- **Brand Integration**: Commercial relationships
- **Audio**: Sound effect assignments

## Validation Levels

- **Error**: Must be fixed before approval
- **Warning**: Should be addressed but won't block
- **Info**: Helpful suggestions for improvement

## Usage

These rules are automatically applied when:
- Creating new inventory items through the API
- Importing items from Verse or external sources  
- Running validation checks on existing items
- Generating item documentation

Items failing critical rules will be rejected. Items with warnings will be flagged for review but can still be processed.

## Rule Updates

When adding new rules:
1. Assign unique ID with `inv_` prefix
2. Choose appropriate category and priority
3. Specify clear validation criteria
4. Test against existing items
5. Update documentation

Rules should be backward compatible when possible to avoid breaking existing items.