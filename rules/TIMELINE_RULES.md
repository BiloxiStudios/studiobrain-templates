---
rule_category: "timeline"
rule_version: "1.0"
priority: "high"
applies_to: ["timeline_entry", "timeline_relationship"]
created_date: "2025-01-11"
last_updated: "2025-01-11"
---

# Timeline Management Rules

## Timeline Entry Rules

### Entry Structure
- **entry_id**: Must be unique and descriptive (e.g., "campaign_start_main_story_2024")
- **timestamp**: Must be valid ISO 8601 format with timezone
- **title**: Clear, concise description of what happens
- **entry_type**: Must be from approved list (see Entry Types section)
- **duration**: Specify time span using standard formats

### Entry Types (Controlled Vocabulary)
- **event**: World events, disasters, celebrations
- **quest_start**: When a quest becomes available
- **quest_complete**: When a quest is finished
- **quest_failed**: When a quest fails or expires
- **campaign_start**: Campaign launches
- **campaign_end**: Campaign concludes
- **dialogue**: Important conversations
- **world_change**: Permanent world state modifications
- **character_development**: Character growth moments
- **faction_event**: Faction-specific occurrences
- **location_event**: Location-specific changes
- **auto_discovered**: Entries found via AI/RAG analysis

### Temporal Constraints
- **Past Events**: Can be added for historical context
- **Future Events**: Must be marked as scheduled/planned
- **Concurrent Events**: Multiple events can occur simultaneously
- **Overlapping Events**: Must specify relationship type

### Cross-Reference Requirements
- **Entity Involvement**: At least one entity must be involved
- **Valid References**: All entity IDs must exist in database
- **Relationship Logic**: Character-location-faction relationships must be consistent
- **Campaign Coherence**: Timeline entries must align with campaign structure

## Timeline Organization Rules

### Timeline Categories
- **main**: Primary storyline events
- **character**: Character-specific developments
- **location**: Location-centered events
- **campaign**: Campaign-scoped timelines
- **faction**: Faction-oriented developments
- **global**: World-affecting changes

### Hierarchical Structure
- **Master Timeline**: Contains all major events
- **Campaign Timelines**: Subset of master focused on specific campaigns
- **Character Timelines**: Personal development arcs
- **Location Timelines**: Changes specific to places
- **Nested Timelines**: Sub-timelines within larger contexts

### Sequence Rules
- **Chronological Order**: Events must be temporally ordered
- **Causal Relationships**: Cause must precede effect
- **Prerequisites**: Dependencies must be satisfied before events
- **Enablements**: Events must unlock subsequent possibilities logically

## Auto-Population Rules

### RAG Integration Standards
- **Confidence Threshold**: Minimum 0.7 confidence for auto-discovered entries
- **Source Attribution**: Must reference vector database documents
- **Human Review**: Auto-entries marked for manual verification
- **Conflict Resolution**: Human entries override auto-discovered ones

### Discovery Triggers
- **New Entity Creation**: Automatically scan for temporal references
- **Content Updates**: Re-analyze when entities are modified
- **Periodic Scans**: Regular analysis of all content
- **Manual Requests**: On-demand timeline population

### Quality Control
- **Validation Rules**: Auto-entries must pass same validation as manual
- **Duplicate Prevention**: Check for existing similar entries
- **Relevance Filtering**: Only add entries relevant to main timeline
- **Accuracy Requirements**: Must be verifiable against source material

## Relationship Rules

### Relationship Types
- **causes**: Direct causal relationship
- **enables**: Makes subsequent events possible
- **prevents**: Blocks other events from occurring
- **conflicts_with**: Cannot happen simultaneously
- **follows**: Sequential relationship
- **precedes**: Temporal ordering
- **temporal_proximity**: Happens near same time
- **thematic_connection**: Related by theme/meaning

### Relationship Validation
- **Logical Consistency**: Relationships must make narrative sense
- **Temporal Logic**: Causal relationships must respect timeline
- **Strength Scoring**: Assign confidence/importance scores (0.0-1.0)
- **Bidirectional Check**: Consider inverse relationships

### Automatic Relationship Detection
- **Common Entities**: Entries sharing characters/locations
- **Time Windows**: Events within specified time ranges
- **Causal Analysis**: Events that logically connect
- **Thematic Grouping**: Related content clusters

## World State Integration

### State Change Tracking
- **Persistent Changes**: World modifications that remain
- **Temporary Changes**: Time-limited alterations
- **Reversible Changes**: Can be undone by future events
- **Cumulative Changes**: Effects that build over time

### Change Documentation
- **Before State**: Document conditions prior to change
- **Change Description**: Clear explanation of what changed
- **After State**: Document new conditions
- **Impact Analysis**: Assess effects on other entities

### Consistency Maintenance
- **State Validation**: Ensure world state remains coherent
- **Conflict Detection**: Identify contradictory changes
- **Rollback Capability**: Ability to reverse problematic changes
- **Version Control**: Track state change history

## Export and Formatting Rules

### Markdown Export Standards
- **Hierarchical Structure**: Year > Month > Day organization
- **Entry Format**: Standardized template for all entries
- **Cross-References**: Hyperlinks to related entities
- **Metadata Inclusion**: Technical details in YAML frontmatter

### Master Timeline Format
```markdown
# Master Timeline

## Year YYYY
### Month YYYY
#### YYYY-MM-DD HH:MM - Event Title
- **Type**: entry_type
- **Duration**: duration
- **Entities**: involved entities
- **Description**: event description
```

### File Organization
- **Master Timeline**: Single comprehensive file
- **Entity Timelines**: Separate files for major entities
- **Campaign Timelines**: Campaign-specific timeline files
- **Archive Structure**: Organized by date ranges

## Performance and Scale Rules

### Entry Limits
- **Maximum Entries**: 10,000 entries per timeline
- **Query Limits**: Paginate results for large timelines
- **Export Limits**: Chunk large exports into manageable sizes
- **Memory Limits**: Lazy load timeline data

### Optimization Guidelines
- **Index Requirements**: Timestamp and entity reference indexes
- **Cache Strategy**: Cache frequently accessed timelines
- **Background Processing**: Auto-population runs async
- **Cleanup Rules**: Archive old or irrelevant entries

### Maintenance Procedures
- **Regular Cleanup**: Remove outdated auto-discovered entries
- **Relationship Pruning**: Clean up low-confidence relationships
- **Duplicate Removal**: Merge similar timeline entries
- **Performance Monitoring**: Track query performance metrics

## Integration Rules

### Story System Integration
- **Campaign Sync**: Auto-create entries for campaign milestones
- **Quest Tracking**: Timeline entries for quest state changes
- **Event Integration**: World events automatically added
- **Character Development**: Personal growth moments tracked

### Entity System Integration
- **Character Actions**: Track important character decisions
- **Location Changes**: Monitor location state modifications
- **Brand Activities**: Corporate events and announcements
- **Faction Dynamics**: Political and military developments

### AI System Integration
- **Generation Context**: Use timeline for story context
- **Consistency Checking**: Validate generated content against timeline
- **Relationship Discovery**: Leverage timeline for entity connections
- **Narrative Planning**: Use timeline to plan future content

## Quality Assurance Rules

### Entry Quality Standards
- **Clarity**: Entries must be clearly written and understandable
- **Accuracy**: Information must be factually correct within world
- **Relevance**: Must contribute meaningfully to overall narrative
- **Completeness**: All required fields must be populated

### Review Process
- **Auto-Entry Review**: Human verification of auto-discovered content
- **Consistency Check**: Regular validation against world rules
- **Narrative Review**: Story coherence assessment
- **Technical Review**: Database and performance validation

### Error Handling
- **Validation Errors**: Clear error messages for rule violations
- **Data Recovery**: Backup and recovery procedures
- **Conflict Resolution**: Process for handling timeline conflicts
- **User Feedback**: System for reporting timeline issues

## Timeline Visualization Rules

### Display Standards
- **Chronological Order**: Always display in time order
- **Visual Hierarchy**: Clear distinction between entry types
- **Interactive Elements**: Clickable entries for detailed view
- **Filtering Options**: By entity type, time range, category

### User Experience
- **Loading Performance**: Fast timeline loading and navigation
- **Search Functionality**: Full-text search within timeline
- **Export Options**: Multiple export formats available
- **Collaboration Features**: Multi-user timeline editing

### Accessibility
- **Screen Reader Support**: Proper semantic markup
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: Accessible color schemes
- **Text Scaling**: Support for various text sizes