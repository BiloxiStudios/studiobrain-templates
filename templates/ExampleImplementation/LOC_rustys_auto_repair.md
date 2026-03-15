---
# LOCATION METADATA
template_version: "1.0"
location_type: "poi"
created_date: "2025-01-15"
last_updated: "2025-01-15"
status: "active"

# BASIC IDENTITY
location_id: "rustys_auto_repair"
display_name: "Rusty's Auto Repair"
business_name: "McDaniels Automotive Services & Gear Head Tools"
location_type: "auto_repair_shop"
category: "commercial"

# GEOGRAPHIC INFORMATION
parent_location: "westside"
coordinates:
  x: 2500
  y: 1800
  z: 0
biome: "westside"
district: "industrial_corridor"
address: "1247 Wrench Way, Westside"

# ACCESSIBILITY
enterable: true
exterior_access: true
entrance_points:
  - type: "main_door"
    location: "front_office"
    locked: false
    key_required: false
  - type: "service_bay_door"
    location: "garage_bay_1"
    locked: true
    key_required: "employee_access"
  - type: "loading_dock"
    location: "rear"
    locked: true
    key_required: "delivery_access"
interior_zones:
  - zone_id: "customer_waiting_area"
    accessible: true
    requirements: "none"
  - zone_id: "main_workshop"
    accessible: false
    requirements: "employee_permission"
  - zone_id: "tool_manufacturing_area"
    accessible: false
    requirements: "special_tour"

# PHYSICAL DESCRIPTION
building_type: "converted_warehouse"
architectural_style: "1960s_industrial"
size: "large"
condition: "well_maintained"
notable_features:
  - "hand_painted_gear_head_tools_sign"
  - "antique_hydraulic_lift_still_functional"
  - "tool_testing_station_visible_through_window"
  - "collection_of_vintage_car_parts_as_decoration"

# ATMOSPHERE & ENVIRONMENT
lighting: "bright_workshop_lighting"
color_palette:
  primary: "#FF4500" # gear head orange
  secondary: "#2F4F4F" # workshop gray
  accent: "#FFD700" # brass fixtures
ambient_sounds:
  - "air_compressor_cycling"
  - "metal_on_metal_tapping"
  - "radio_playing_classic_rock"
  - "occasional_power_tool_use"
weather_effects:
  - "dust_from_westside_storms"
  - "temperature_fluctuations_from_forge"
air_quality: "workshop_fumes" # oil, metal, rubber

# STORY INTEGRATION
narrative_importance: "minor"
story_chapters:
  - "prologue"
  - "chapter_4"
  - "chapter_5"
faction_control: null
faction_relationship: "neutral"

# INTERACTIVE ELEMENTS
searchable_objects:
  - object_type: "tool_cabinet"
    loot_table: "mechanical_tools"
    skill_required: "locksmith_3"
  - object_type: "cash_register"
    loot_table: "currency_moderate"
    skill_required: "none"
  - object_type: "parts_inventory"
    loot_table: "automotive_parts"
    skill_required: "mechanical_5"
vendors:
  - vendor_id: "rusty_tool_shop"
    character_id: "rusty_mcdaniels"
    vendor_type: "specialty_tools"
minigames:
  - game_type: "tool_crafting"
    difficulty: "medium"
    rewards: "custom_tools"
  - game_type: "engine_diagnosis"
    difficulty: "hard"
    rewards: "mechanical_skill_points"
interactive_features:
  - "hydraulic_lift"
  - "tool_forge"
  - "parts_washing_station"

# NPCS & POPULATION
primary_npcs:
  - character_id: "rusty_mcdaniels"
    role: "owner"
    always_present: true
  - character_id: "tommy_mcdaniels"
    role: "part_time_helper"
    schedule: "afternoons_weekends"
background_npcs:
  - type: "customer_with_car_trouble"
    count: "1-3"
    behavior: "waiting_discussing_repairs"
  - type: "delivery_driver"
    count: "1"
    behavior: "dropping_off_parts"
npc_density: "low"
crowd_behavior: "professional_business"

# ECONOMY & SERVICES
business_type: "auto_repair_tool_manufacturing"
operating_hours: "7am-6pm_weekdays"
currency_accepted:
  - "gold"
  - "brain_bucks"
services_offered:
  - "vehicle_repair"
  - "tool_sales"
  - "custom_tool_creation"
  - "mechanical_training"
price_range: "moderate_to_expensive"

# BRAND ASSOCIATIONS
primary_brand: "gear_head_tools"
associated_brands:
  - brand_id: "westside_steel_supply"
    relationship: "raw_material_supplier"
  - brand_id: "classic_car_parts_inc"
    relationship: "parts_supplier"
advertising_presence:
  - "gear_head_tools_signage"
  - "vintage_automotive_posters"
  - "quality_awards_displayed"

# SAFETY & HAZARDS
threat_level: "low"
hazards:
  - type: "industrial"
    description: "heavy_machinery_hot_forge"
    danger: "moderate"
  - type: "chemical"
    description: "automotive_fluids_solvents"
    danger: "mild"
zombie_risk: "low"
infection_status: "clean"

# TECHNICAL DETAILS
data_layer: "westside_commercial"
memory_optimization: "medium"
lod_distances:
  high: 400
  medium: 800
  low: 1600
spawn_rules:
  max_players: 8
  respawn_time: 180
audio_zones:
  - zone: "customer_area"
    audio_mix: "office_ambient"
  - zone: "workshop"
    audio_mix: "workshop_active"
  - zone: "forge_area"
    audio_mix: "industrial_heavy"

# ASSETS & MEDIA
concept_art: "locations/rustys_auto_repair/concept_sketch.png"
screenshots:
  - "locations/rustys_auto_repair/exterior_workshop.png"
  - "locations/rustys_auto_repair/interior_main_bay.png"
  - "locations/rustys_auto_repair/tool_display_area.png"
floor_plan: "locations/rustys_auto_repair/layout_blueprint.png"
3d_models:
  - "rustys_exterior_building.fbx"
  - "workshop_interior_complete.fbx"
  - "tool_manufacturing_equipment.fbx"
texture_sets:
  - "industrial_workshop_textures"
  - "vintage_automotive_materials"
audio_assets:
  - "workshop_ambient_loop.ogg"
  - "air_compressor_cycles.wav"
  - "metal_working_sounds.wav"
music_tracks:
  - "classic_rock_radio_playlist.m3u"

# EASTER EGGS & SECRETS
hidden_areas:
  - area_id: "prototype_vault"
    access_method: "rusty_personal_key"
    contents: "experimental_tools"
easter_eggs:
  - "photo_of_rusty_with_first_tool"
  - "hidden_message_in_tool_serial_numbers"
collectibles:
  - type: "vintage_tool_catalog"
    rarity: "common"
  - type: "gear_head_prototype_tool"
    rarity: "legendary"
---

# Rusty's Auto Repair Location Sheet

## Location Overview
Rusty's Auto Repair serves as both a functioning garage and the headquarters for Gear Head Tools manufacturing. This dual-purpose facility represents the intersection of service and craftsmanship in the City of Brains universe, where traditional automotive repair meets precision tool manufacturing.

## Physical Description

### Exterior
The building is a converted 1960s warehouse with distinctive hand-painted signage reading "McDaniels Automotive Services & Gear Head Tools" in bold orange and gray lettering. The Gear Head Tools logo - a stylized wrench crossed with a gear - dominates the front facade. Large bay doors reveal glimpses of the workshop interior, while a smaller customer entrance leads to the office area.

The exterior shows signs of honest wear: slightly faded paint from years of desert sun, oil stains in the parking area from countless repairs, and a collection of vintage automotive parts artfully arranged as outdoor decoration. A small monument made from old engine blocks serves as both art installation and testament to Rusty's philosophy of honoring quality engineering.

### Interior Layout
The facility is divided into distinct functional areas:

**Customer Waiting Area**: Clean, professional space with comfortable seating, coffee station, and walls lined with automotive magazines, quality awards, and vintage car posters. A large window provides customers with a view into the main workshop, demonstrating transparency and craftsmanship.

**Main Workshop**: The heart of the operation, featuring four service bays with hydraulic lifts, comprehensive tool arrays, and organized parts storage. The space balances efficiency with craftsmanship - every tool has its place, and the workspace is kept meticulously clean.

**Tool Manufacturing Area**: A semi-separated section housing the forge, precision machining equipment, and quality testing station. This area represents the Gear Head Tools manufacturing operation, where Rusty personally creates and tests each tool.

**Office/Administrative Space**: Rusty's working office, filled with automotive repair manuals, tool catalogs, customer records, and business paperwork. Personal touches include family photos and letters from satisfied customers.

### Unique Features
The facility's most distinctive feature is the integration of automotive repair and tool manufacturing under one roof. The antique hydraulic lift, still fully functional after 40 years, serves as both practical equipment and symbol of enduring quality. The tool testing station, visible through the customer area window, demonstrates Rusty's commitment to quality assurance.

## Atmosphere & Mood

### Visual Design
The color scheme reflects the Gear Head Tools brand: rust orange accents against workshop gray, with brass fixtures providing warm highlights. Lighting is bright and functional in work areas, warmer and more comfortable in customer spaces. The overall aesthetic suggests competence, reliability, and honest craftsmanship.

### Audio Landscape
The soundscape varies by area and time of day. The customer area maintains quiet professionalism with soft classic rock radio and muffled workshop sounds. The main workshop pulses with activity: air compressor cycles, the rhythmic tapping of metalwork, occasional power tool use, and Rusty's radio playing classic rock at moderate volume. The forge area adds the more intense sounds of metal working and industrial processes.

### Environmental Storytelling
Every surface tells a story of dedicated craftsmanship: well-used tools showing decades of reliable service, before-and-after photos of restored vehicles, customer testimonials handwritten on company letterhead, and a progression of tool prototypes showing Rusty's evolution as a craftsman.

## Historical Context

### Pre-Outbreak History
Established in 1983 when Rusty McDaniels converted a failed warehouse into his combined auto repair and tool manufacturing facility. The business grew organically through word-of-mouth recommendations and Rusty's reputation for honest dealing and quality work.

The location became a gathering place for the local automotive community - mechanics would stop by to discuss difficult repairs, examine new tools, and share industry knowledge. The annual "Gear Head Challenge" held in the parking lot became a regional tradition.

### Current State
Pre-outbreak, the facility operated at steady capacity with a loyal customer base and growing tool manufacturing orders. The business was profitable but not aggressively expanding, reflecting Rusty's philosophy of controlled growth and maintained quality.

### Future Implications
The outbreak likely interrupted normal operations suddenly, leaving the facility as a time capsule of pre-disaster normalcy. The combination of automotive repair equipment and precision tools makes it potentially valuable to survivors seeking to maintain vehicles or create weapons.

## Gameplay Integration

### Player Activities
- **Vehicle Repair**: Complete automotive maintenance and upgrade quests
- **Tool Purchasing**: Buy professional-grade tools for improved mechanical abilities
- **Skill Training**: Learn advanced mechanical techniques from Rusty
- **Custom Tool Creation**: Commission specialized tools for specific purposes
- **Information Gathering**: Learn about other locations and characters through shop talk

### Skill Requirements
- **Basic Access**: No special skills required for customer area
- **Workshop Access**: Requires permission from Rusty or mechanical skill level 3+
- **Manufacturing Area**: Special tour requires relationship level 6+ with Rusty
- **Advanced Services**: Higher mechanical skills unlock better tools and training

### Risk vs. Reward
The location offers significant rewards for mechanically-inclined players but requires investment in relationship building and skill development. Higher-quality tools and training come at premium prices but provide substantial gameplay advantages.

### Quest Hub Functions
Serves as the starting point for vehicle-related quests, skill development missions, and community service opportunities. Rusty's connections throughout the automotive community make him a valuable source of information and referrals.

## Economic Role

### Business Operations
The facility operates on two revenue streams: automotive repair services providing steady daily income, and tool manufacturing generating higher-margin specialty sales. The business model emphasizes quality over volume, maintaining premium pricing through superior service and products.

### Economic Impact
As one of the few remaining independent automotive facilities in Westside, Rusty's plays a crucial role in maintaining the transportation infrastructure for working-class residents who can't afford dealership service prices.

### Currency and Trade
Accepts both Gold (standard currency) and BrainBucks (premium currency) for different service levels. Offers payment plans for major repairs and bulk tool purchases, reflecting Rusty's understanding of his customers' financial situations.

## Technical Implementation

### Performance Considerations
The facility requires medium optimization due to detailed workshop equipment and manufacturing machinery. LOD systems should prioritize the customer and main workshop areas while allowing distant views of the manufacturing section.

### Interactive Systems
Complex interaction systems support multiple gameplay mechanics: vehicle repair minigames, tool crafting sequences, skill training challenges, and relationship-building dialogue trees. Each area requires specific scripting for appropriate player activities.

### Audio Implementation
Dynamic audio mixing adjusts based on player location and time of day. Workshop sounds intensify during business hours, forge area audio triggers during manufacturing sequences, and customer area maintains consistent ambient professional atmosphere.

### Visual Effects
Special effects support the industrial atmosphere: welding sparks, forge heat shimmer, hydraulic lift steam, and tool testing demonstrations. Particle systems should emphasize the working environment without overwhelming performance.

## Dynamic Events

### Random Events
- **Rush Repair**: Emergency vehicle repair with time pressure
- **Tool Demonstration**: Rusty showcases new tool prototypes
- **Customer Testimonial**: Satisfied customers share success stories
- **Supply Delivery**: Raw materials arrive for tool manufacturing

### Time-Based Changes
**Morning (7-9 AM)**: Setup and preparation, coffee brewing, radio news
**Peak Hours (9 AM-4 PM)**: Active repair work, customer interactions, manufacturing
**Wind-Down (4-6 PM)**: Cleanup, administrative work, planning tomorrow
**Evening**: Personal projects, prototype development, maintenance

### Weather Interactions
- **Hot Days**: Increased use of cooling fans, earlier morning start times
- **Dust Storms**: Protective coverings deployed, air filtration activated
- **Rain**: Ideal conditions for indoor manufacturing work

### Faction Events
While Rusty maintains neutrality, faction members may bring vehicles for repair, creating opportunities for player observation and information gathering about factional activities and resources.

## Security & Dangers

### Threat Assessment
Generally safe location with low risk of violence or theft due to Rusty's reputation and community standing. Primary dangers involve industrial accidents from unfamiliarity with heavy machinery or automotive repair equipment.

### Security Measures
Basic security includes sturdy locks on valuable tool storage and after-hours lighting. However, security relies more on community respect and Rusty's personal relationships than physical barriers.

### Zombie Presence
Pre-outbreak: No zombie risk
Post-outbreak: Low zombie presence due to industrial location away from main population centers, but potential for isolated encounters

### Environmental Hazards
- **Industrial Equipment**: Heavy machinery poses crush/cut dangers
- **Chemical Exposure**: Automotive fluids and solvents require careful handling
- **Fire Risk**: Forge operations and fuel storage create potential fire hazards
- **Structural**: Heavy equipment and elevated storage require attention to weight limits

## Progression Gates

### Access Requirements
- **Customer Area**: Open to all during business hours
- **Workshop**: Requires permission or mechanical skill demonstration
- **Manufacturing**: Invitation only, requires established relationship
- **After Hours**: Emergency access for established customers only

### Unlock Conditions
- **Advanced Tools**: Requires demonstrated mechanical competency
- **Custom Orders**: Requires relationship level 5+ and detailed specifications
- **Training Programs**: Requires commitment to learning and practice time
- **Business Insights**: Requires trusted friend status (relationship level 8+)

---

*This location example demonstrates how to create a rich, functional space that supports multiple gameplay mechanics while serving as the intersection point for character relationships, brand presence, and narrative development. The detailed implementation guidelines ensure that AI systems have sufficient context to generate consistent descriptions, dialogue, and interactive elements.*