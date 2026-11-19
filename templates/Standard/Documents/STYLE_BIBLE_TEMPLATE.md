---
# METADATA (REQUIRED)
template_version: "1.0"
template_category: "document"
ui_icon: "BookOpen"
ui_color: "#7c3aed"
editable: true
marketplace_eligible: true
id: "[snake_case_name]"  # Must match universe_id
entity_type: "style_bible"
folder_name: "Style Bibles"
file_prefix: "STYLE_"
asset_subfolders:
  - images
  - audio
  - video
universe_id: "universe_id"  # References universe configuration
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules: []
associated_skills: []

# FIELD WIDGET CONFIGURATION
field_config:
  key_light_color:
    widget: color-picker
  fill_light_color:
    widget: color-picker
  rim_light_color:
    widget: color-picker

status: "active"  # active, development, archived

# PRIMARY IMAGE
primary_image: ""           # Path to primary image (set via EntityAssets component)

# BASIC INFORMATION (REQUIRED)
name: "Style Bible Display Name"
version: "1.0"
primary_medium: "video_game"  # video_game, film, animation, mixed

# VISUAL IDENTITY
art_direction: ""  # realistic, stylized, abstract, mixed. Fill from this project.
visual_influences: []  # Fill from this project
rendering_style: "real_time_3d"  # 2d, 3d, mixed_media
target_platform: "cross_platform"  # mobile, console, pc, cross_platform

# COLOR PALETTE
primary_colors: []  # name, hex, usage from this project
secondary_colors: []
atmospheric_colors: []
forbidden_colors: []  # Colors this project refuses, if any

# LIGHTING DESIGN
lighting_philosophy: "Cinematic with dramatic contrasts"
key_light_color: ""  # Fill from this project
fill_light_color: ""
rim_light_color: ""
shadow_density: 0.7  # 0-1 scale
ambient_occlusion: true
global_illumination: "baked"  # realtime, baked, mixed

# ATMOSPHERE AND MOOD
fog_settings:
  density: "medium"
  color: "#2B2B2B"
  height_based: true
weather_effects:
  - "Light rain"
  - "Heavy fog"
  - "Haze"
time_of_day_presets:
  - preset: "Golden Hour"
    sun_angle: 15
    color_temp: "warm"
  - preset: "Night"
    sun_angle: -90
    color_temp: "cool"
post_processing:
  - "Film grain"
  - "Chromatic aberration"
  - "Vignette"
  - "Bloom"

# MATERIAL STANDARDS
material_types:
  - type: "Metal"
    roughness: 0.4
    metallic: 1.0
  - type: "Concrete"
    roughness: 0.8
    metallic: 0.0
  - type: "Neon"
    emissive: 2.0
    bloom: true
texture_resolution: "2048x2048"  # standard size
texture_style: "stylized_painterly"
normal_map_intensity: 0.5

# CHARACTER DESIGN
character_style: ""  # Fill from this project
polygon_budget: 5000  # tris per character
proportion_guide: "slightly_exaggerated"
face_detail_level: "simplified"  # realistic, simplified, abstract
clothing_era: ""  # Fill from this project
signature_elements:
  - "Bold silhouettes"
  - "Chunky shapes"
  - "Memorable colors"

# ENVIRONMENT DESIGN
architectural_style: ""  # Fill from this project
detail_density: "medium"  # low, medium, high
prop_distribution: "purposeful"  # sparse, balanced, dense, purposeful
landmark_visibility: "always_visible"
vista_design: "layered_depth"
environmental_storytelling: "heavy"

# UI/UX DESIGN
ui_style: ""  # Fill from this project
font_families:
  primary: ""
  secondary: ""
  body: ""
ui_colors: {}  # Fill from this project
button_style: ""  # Fill from this project
animation_style: "snappy"  # smooth, snappy, bouncy

# ICONOGRAPHY
icon_style: "line_art"
icon_weight: 2  # pixels
icon_color_scheme: "monochrome"  # monochrome, dual_tone, full_color
signature_icons: []  # Fill from this project

# TYPOGRAPHY
display_font:
  family: ""
  weight: ""
  size_range: ""
heading_font:
  family: ""
  weight: ""
  size_range: ""
body_font:
  family: ""
  weight: ""
  size_range: ""
special_font:
  family: ""
  usage: ""

# ANIMATION PRINCIPLES
animation_approach: "snappy_responsive"
frame_rate: 30  # fps
key_principles:
  - "Anticipation before action"
  - "Slight overshoot on stops"
  - "Weight affects timing"
character_idle: "subtle_breathing"
environmental_animation: "constant_subtle_motion"

# PARTICLE EFFECTS
particle_style: "stylized"
primary_particles:
  - type: "Steam"
    color: "#D6D6FF"
    behavior: "rises slowly"
  - type: "Sparks"
    color: "#FFD700"
    behavior: "falls with bounce"
  - type: "Chemical"
    color: "#00FF00"
    behavior: "bubbles and pops"

# AUDIO VISUAL STYLE
music_visualization: "reactive_neon"
sound_visualization: "ripple_effects"
ui_audio_feedback: "retro_beeps"

# CAMERA WORK
default_fov: 75
camera_movement: "smooth_cinematic"
camera_shake: "subtle_handheld"
depth_of_field: "selective_focus"
motion_blur: "per_object"

# SIGNATURE VISUAL ELEMENTS
recurring_motifs: []  # Fill from this project
iconic_props: []  # Fill from this project
environmental_details:
  - "Graffiti"
  - "Worn posters"
  - "Broken windows"
  - "Flickering lights"

# QUALITY SETTINGS
lod_levels: 3
shadow_quality: "medium"
texture_quality: "high"
effect_quality: "high"
performance_target: "60fps"

# PLATFORM ADAPTATIONS
mobile_adjustments:
  - "Reduced particle count"
  - "Simplified shadows"
  - "Lower texture resolution"
console_optimizations:
  - "Dynamic resolution"
  - "Adaptive quality"
pc_enhancements:
  - "Ray tracing option"
  - "Ultra textures"
  - "Unlimited fps"

# BRAND CONSISTENCY
logo_placement: "bottom_left"
watermark_opacity: 0.8
copyright_text: "© [Year] [Company]"
brand_colors_only: false  # Can use off-brand colors

# ACCESSIBILITY OPTIONS
colorblind_modes:
  - "Protanopia"
  - "Deuteranopia"
  - "Tritanopia"
contrast_options: "adjustable"
motion_reduction: "available"
subtitle_styling: "customizable"

# CONTENT FIELDS
style_overview: null  # Will be in markdown below
visual_examples: null  # Will be in markdown below
implementation_notes: null  # Will be in markdown below
---