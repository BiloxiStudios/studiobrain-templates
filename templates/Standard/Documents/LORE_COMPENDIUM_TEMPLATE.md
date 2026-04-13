---
# METADATA (REQUIRED)
	template_version: "1.0"
	template_category: "document"
	ui_icon: "Scroll"
	ui_color: "#6366F1"
	editable: true
	marketplace_eligible: true
	id: "[snake_case_name]"  # Must match universe_id
	entity_type: "lore_compendium"
	folder_name: "Lore Compendia"
	file_prefix: "LORE_"
	asset_subfolders:
	  - images
	  - maps
	  - timelines
	universe_id: "universe_id"  # References universe configuration
	created_date: "YYYY-MM-DD"
	last_updated: "YYYY-MM-DD"
	associated_rules: []
	associated_skills: []

	# FIELD WIDGET CONFIGURATION
	field_config:
	  lore_type:
	    widget: dropdown
	    options: ["Historical", "Mythological", "Scientific", "Fantasy", "Sci-Fi", "Mixed"]
	  organization_method:
	    widget: dropdown
	    options: ["Chronological", "Thematic", "Geographical", "Entity-based", "Mixed"]
	  discovery_method:
	    widget: dropdown
	    options: ["Direct", "Environmental", "Collectible", "Unlockable", "Progressive"]

	status: "active"  # active, development, archived

	# PRIMARY IMAGE
	primary_image: ""           # Path to primary image (set via EntityAssets component)

	# BASIC INFORMATION (REQUIRED)
	name: "Lore Compendium Display Name"
	version: "1.0"
	primary_medium: "video_game"  # video_game, film, animation, literature, transmedia

	# HISTORY
	world_origin: null
	timeline:
	  - era: null
	    events: []
	historical_events:
	  - event: null
	    date: null
	    significance: null

	# FACTIONS AND ORGANIZATIONS
	factions:
	  - name: null
	    philosophy: null
	    structure: null
	    key_figures: []
	    relationships:
	      - target: null
	        nature: null  # Alliance, Rivalry, Neutral, Subordinate

	# LOCATIONS
	geographical_regions:
	  - name: null
	    description: null
	    significance: null
	    connected_locations: []
	key_structures:
	  - name: null
	    purpose: null
	    history: null
	    current_status: null

	# ARTIFACTS AND OBJECTS
	magical_items:
	  - name: null
	    origin: null
	    properties: null
	    owners: []
	technological_artifacts:
	  - name: null
	    inventor: null
	    purpose: null
	    limitations: null
	signature_objects:
	  - name: null
	    cultural_significance: null
	    visual_designation: null

	# EVENTS
	world_shaping_events:
	  - name: null
	    description: null
	    consequences: []
	political_events:
	  - name: null
	    description: null
	    affected_parties: []
	mysterious_incidents:
	  - name: null
	    description: null
	    open_questions: []

	# BESTIARY AND CREATURES
	intelligent_species:
	  - name: null
	    characteristics: null
	    society: null
	    relationship_with_others: null
	animals_and_monsters:
	  - name: null
	    habitat: null
	    behavior: null
	    threats: null
	mythological_entities:
	  - name: null
	    legends: null
	    manifestations: null

	# GLOSSARY
	terminology:
	  - term: null
	    definition: null
	    context: null
	slang_and_idioms:
	  - phrase: null
	    origin: null
	    usage: null

	# CONNECTIONS TO OTHER WORKS
	related_documents:
	  - name: null
	    connection: null
	related_entities:
	  - name: null
	    connection: null
	canonical_sources: []  # Books, films, etc. that inspired this lore

	# CONTENT FIELDS
	historical_overview: null  # Will be in markdown below
	detailed_factions: null  # Will be in markdown below
	world_geography: null  # Will be in markdown below
	cultural_notes: null  # Will be in markdown below
---
