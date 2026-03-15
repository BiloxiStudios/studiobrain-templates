# City of Brains Plugin Catalog

> 21 plugins for the City of Brains Studio plugin ecosystem.
> Each plugin includes backend API routes, event-driven automation, entity sidebar/tab panels, and a full dashboard page.

---

## Creative & AI Tools

### LoRA Trainer
**Train custom AI models from your characters.**
Manage training datasets from entity assets, configure LoRA parameters (rank, steps, learning rate), and monitor GPU training jobs in real time. Trained models are indexed with trigger words for instant use in image generation pipelines.

### Voice Forge
**Give every character a unique voice.**
Generate text-to-speech audio using ElevenLabs with per-character voice profiles and style presets (normal, angry, whisper, excited, sad). The sidebar mini-player lets you audition voices while editing, and the Voice Studio provides a full generation interface with waveform visualization.

### Music Gen
**AI-generated soundtracks for your world.**
Create entity-specific music from text prompts with automatic prompt generation that analyzes character personality, location biome, and narrative mood. Supports Suno and Udio providers with a built-in audio library and per-entity music player.

### ComfyUI Workflows
**Run AI image generation pipelines from the editor.**
Browse, import, and execute ComfyUI workflows directly from entity pages. Auto-maps entity descriptions to prompt inputs, randomizes seeds, and tracks execution history. The dashboard provides a full workflow library with queue monitoring.

### PDF Bible Exporter
**Print-ready character sheets and world bibles.**
Generate polished, print-ready HTML documents for any entity type -- character sheets, location guides, faction dossiers, and complete world bibles. Supports studio branding, custom templates, batch export, and browser-native PDF output via Ctrl+P.

---

## Game Engine Exporters

### Unity Exporter
**ScriptableObjects from your world data.**
Auto-generates C# ScriptableObject classes with proper Unity attributes, exports entities as `.asset` YAML files with stable GUIDs, and produces DataTable-ready enums. Batch export an entire entity type into a ready-to-import Unity package.

### Unreal Exporter
**USTRUCTs and DataTables for Unreal Engine.**
Generates compilable C++ USTRUCT headers with `UPROPERTY` macros, exports entities as DataAsset JSON and DataTable CSV in Unreal's native formats. Includes Blueprint-friendly type inference and batch export with organized output directories.

### UEFN Exporter
**Verse scripts for Fortnite Creative.**
Converts entities into Verse class definitions, data instances, and creative device configurations for Unreal Editor for Fortnite. Exports character dialogue as Verse structs, generates island metadata, and writes directly to your UEFN project's Content directory.

### Blender Bridge
**Live entity data in your 3D scenes.**
Exports entity data as structured JSON optimized for Blender -- characters include armature scale calculations from height/build, locations include HDRI and lighting suggestions from biome type. Supports auto-export on entity save and render queue management.

### Showrunner Exporter
**Character bibles for AI show production.**
Formats entities into Showrunner.xyz-compatible character bibles with personality traits, dialogue samples, voice style, and appearance data. Supports episode outline export, batch character sync, and auto-push when connected to a Showrunner project.

---

## Integrations & Sync

### Notion Sync
**Bidirectional sync with Notion databases.**
Map entity fields to Notion properties and sync characters, locations, items, and quests to Notion pages. Configurable field mappings, auto-sync on entity changes, and a dashboard with database selection and sync monitoring.

### Obsidian Vault
**Export your world as an Obsidian knowledge graph.**
Converts entities to Obsidian-flavored markdown with YAML frontmatter, wikilinks between related entities, and proper tag taxonomies. Includes image copying, folder-per-type organization, and a force-directed relationship graph visualization.

### Google Sheets Sync
**Spreadsheet view of all your entity data.**
Export entity data as CSV or sync to Google Sheets with configurable field-to-column mappings. Preview data as spreadsheet tables, track sync state per entity, and batch export across multiple entity types.

### Jira Sync
**Link entities to Jira issues.**
Bidirectional sync between Studio entities and Jira issues with configurable field and status mappings. Auto-create Jira issues on entity creation, auto-transition on status changes, and a webhook receiver for Jira-to-Studio updates.

### Discord Poster
**Share entities to Discord with rich embeds.**
Post entity cards to Discord channels via webhooks with auto-generated embeds including images, metadata fields, and descriptions. Supports multiple webhook channels, auto-post on entity create/update, and a post history dashboard.

### Social Publisher
**Cross-post to Twitter, Bluesky, Instagram, and Threads.**
Publish entity announcements across four platforms with customizable post templates, character limit enforcement, scheduled posting, and image attachments. Includes platform-specific preview and analytics.

### YouTube Manager
**Track and upload videos linked to entities.**
Link YouTube videos to entities, auto-generate titles and descriptions from entity data, scan asset directories for video files, and manage uploads. Works in mock mode for development without an API key.

---

## Workflow & Project Management

### Kanban Board
**Visual production pipeline for all entities.**
Drag-and-drop kanban board with configurable columns (Concept, In Progress, Review, Complete). Filter by entity type, search by name, and track completion percentages. The sidebar panel shows each entity's current pipeline stage with quick-move buttons.

### Time Tracker
**Track time spent on every entity.**
Start/stop timer widget in the entity sidebar with per-entity and per-type time logs. The dashboard provides daily, weekly, and monthly summaries with bar charts and billable/non-billable breakdowns.

### Version History
**Git-powered version control for entities.**
Browse the full git history of any entity with expandable inline diffs, contributor stats, and one-click rollback. The sidebar shows recent versions at a glance, and the dashboard provides commit-per-type breakdowns across the entire project.

### Webhook Automations
**Trigger external services on entity events.**
Define webhook rules that fire HTTP requests when entities are created, updated, or deleted. Supports payload templates with entity data substitution, retry logic, HMAC signing, and a delivery log with success/failure tracking.
