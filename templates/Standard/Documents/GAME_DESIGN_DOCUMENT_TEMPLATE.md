---
# METADATA (REQUIRED)
	template_version: "1.0"
	template_category: "document"
	ui_icon: "Gamepad2"
	ui_color: "#8B5CF6"
	editable: true
	marketplace_eligible: true
	id: "[snake_case_name]"  # Must match universe_id
	entity_type: "game_design_document"
	folder_name: "Game Design Documents"
	file_prefix: "GDD_"
	asset_subfolders:
	  - images
	  - diagrams
	  - references
	universe_id: "universe_id"  # References universe configuration
	created_date: "YYYY-MM-DD"
	last_updated: "YYYY-MM-DD"
	associated_rules: []
	associated_skills: []

	# FIELD WIDGET CONFIGURATION
	field_config:
	  target_platform:
	    widget: dropdown
	    options: ["PC", "Console", "Mobile", "Web", "Cross-platform"]
	  target_audience:
	    widget: text
	  genre:
	    widget: dropdown
	    options: ["Action", "Adventure", "RPG", "Strategy", "Simulation", "Puzzle", "Horror", "Sports", "Racing", "Other"]

	status: "active"  # active, development, archived

	# PRIMARY IMAGE
	primary_image: ""           # Path to primary image (set via EntityAssets component)

	# BASIC INFORMATION (REQUIRED)
	name: "Game Design Document Display Name"
	version: "1.0"
	primary_medium: "video_game"  # video_game, board_game, card_game, pen_and_paper

	# GAME OVERVIEW
	game_title: ""
	one_sentence_summary: null  # A compelling one-line pitch
	extended_summary: null  # 2-3 paragraph description

	# CORE GAMEPLAY LOOP
	core_loop_description: null
	player_goals: null
	victory_conditions: null
	failure_conditions: null

	# MECHANICS
	mechanics_overview: null
	core_systems:
	  - system_name: null
	    description: null
	interaction_model: null  # Click, Drag, Keyboard, Touch, Voice
	progression_system: null  # Linear, Open, Metroidvania, Roguelike
	difficulty_balancing: null

	# SYSTEMS
	ui_system: null
	save_system: null
	multiplayer: null  # None, Co-op, Competitive, MMO
	achievements_system: null
	microtransactions: null  # None, Cosmetic, Pay-to-win, Hybrid

	# CONTENT STRUCTURE
	level_design: null
	narrative_structure: null  # Linear, Branching, Environmental
	replayability_factors:
	  - null
	post_launch_content: null  # DLC, Seasons, Live Service, None

	# ART AND AUDIO DIRECTION
	art_style: null
	character_design_philosophy: null
	environment_design: null
	music_style: null
	sound_design_philosophy: null

	# TECHNICAL REQUIREMENTS
	target_platforms: []
	target_framerate: null
	engine_requirements: null
	estimated_development_time: null
	team_composition: null

	# MONETIZATION STRATEGY
	business_model: null  # Premium, F2P, Subscription, Premium + DLC
	price_point: null
	monetization_features:
	  - null

	# MARKETING POSITIONING
	target_demographic: null
	unique_selling_points:
	  - null
	competitors:
	  - name: null
	    differentiation: null

	# RISKS AND MITIGATION
	technical_risks:
	  - risk: null
	    mitigation: null
	schedule_risks:
	  - risk: null
	    mitigation: null
	market_risks:
	  - risk: null
	    mitigation: null

	# CONTENT FIELDS
	executive_summary: null  # Will be in markdown below
	detailed_mechanics: null  # Will be in markdown below
	prototyping_notes: null  # Will be in markdown below
	implementation_notes: null  # Will be in markdown below
---
