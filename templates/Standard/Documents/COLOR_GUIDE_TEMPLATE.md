---
# METADATA (REQUIRED)
	template_version: "1.0"
	template_category: "document"
	ui_icon: "PaintBrush"
	ui_color: "#EC4899"
	editable: true
	marketplace_eligible: true
	id: "[snake_case_name]"  # Must match universe_id
	entity_type: "color_guide"
	folder_name: "Color Guides"
	file_prefix: "COLOR_"
	asset_subfolders:
	  - images
	  - swatches
	  - examples
	universe_id: "universe_id"  # References universe configuration
	created_date: "YYYY-MM-DD"
	last_updated: "YYYY-MM-DD"
	associated_rules: []
	associated_skills: []

	# FIELD WIDGET CONFIGURATION
	field_config:
	  color_model:
	    widget: dropdown
	    options: ["RGB", "CMYK", "HSL", "PANTONE", "RAL"]
	  color_purpose:
	    widget: dropdown
	    options: ["UI Design", "Character Design", "Environment", "Branding", "Multi-purpose"]
	  accessibility_standard:
	    widget: dropdown
	    options: ["WCAG 2.1 AA", "WCAG 2.1 AAA", "Custom"]

	status: "active"  # active, development, archived

	# PRIMARY IMAGE
	primary_image: ""           # Path to primary image (set via EntityAssets component)

	# BASIC INFORMATION (REQUIRED)
	name: "Color Guide Display Name"
	version: "1.0"
	primary_medium: "video_game"  # video_game, film, animation, web, print

	# PRIMARY PALETTE
	primary_colors:
	  - name: "Primary Color 1"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null
	  - name: "Primary Color 2"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null
	  - name: "Accent Color"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null
	secondary_colors:
	  - name: "Secondary Color 1"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null
	  - name: "Secondary Color 2"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null

	# NEUTRAL PALETTE
	backgrounds:
	  - name: "Background Light"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null
	  - name: "Background Dark"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null
	text_colors:
	  - name: "Text Light"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null
	  - name: "Text Dark"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null
	border_and_divider_colors:
	  - name: "Border"
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null

	# SEMANTIC COLORS
	success_color:
	  hex: ""
	  rgb: [0, 0, 0]
	  usage: null
	warning_color:
	  hex: ""
	  rgb: [0, 0, 0]
	  usage: null
	error_color:
	  hex: ""
	  rgb: [0, 0, 0]
	  usage: null
	info_color:
	  hex: ""
	  rgb: [0, 0, 0]
	  usage: null

	# CHARACTER COLORS
	hero_colors:
	  - name: null
	    hex: ""
	    rgb: [0, 0, 0]
	villain_colors:
	  - name: null
	    hex: ""
	    rgb: [0, 0, 0]
	neutral_faction_colors:
	  - name: null
	    hex: ""
	    rgb: [0, 0, 0]
	skin_tone_palette:
	  - name: null
	    hex: ""
	    rgb: [0, 0, 0]
	    usage: null

	# ENVIRONMENT COLORS
	nature_colors:
	  - type: null  # Vegetation, Water, Sky, Terrain
	    hex: ""
	    rgb: [0, 0, 0]
	atmospheric_colors:
	  - name: null  # Day, Night, Sunset, Fog
	    hex: ""
	    rgb: [0, 0, 0]
	lighting_colors:
	  - type: null  # Ambient, Direct, Rim, Emissive
	    hex: ""
	    rgb: [0, 0, 0]

	# ACCESSIBILITY
	contrast_minimum_ratio: 4.5  # WCAG AA standard
	colorblind_tested: false
	colorblind_modes:
	  - Protanopia
	  - Deuteranopia
	  - Tritanopia
	dark_mode_palette: null  # Inverted or adjusted colors
	high_contrast_mode: null

	# USAGE GUIDELINES
	do:
	  - null
	dont:
	  - null
	usage_notes: null
	component_application:
	  - component: null
	    colors_used: []

	# FORBIDDEN COMBINATIONS
	inaccessible_pairs:
	  - foreground: null
	    background: null
	    reason: null
	brand_violations:
	  - null

	# GRADIENTS AND EFFECTS
	primary_gradient:
	  - type: null  # Linear, Radial, Conic
	    start_color: ""
	    end_color: ""
	    angle_or_position: null
	texture_overlays:
	  - name: null
	    description: null
	effects:
	  - type: null  # Bloom, Glow, Shadow, Gradient
	    settings: null

	# TESTING AND VALIDATION
	colorblind_simulation_notes: null
	accessibility_audit_date: null
	known_issues:
	  - issue: null
	    mitigation: null

	# CONTENT FIELDS
	color_philosophy: null  # Will be in markdown below
	usage_examples: null  # Will be in markdown below
	accessibility_notes: null  # Will be in markdown below
---
