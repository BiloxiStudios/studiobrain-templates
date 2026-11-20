---
id: "unique_lowercase_id"  # Derived from the name, e.g. smoky_chickpea_tacos
name: "Recipe Display Name"

# METADATA
template_version: "1.0"
template_category: "entity"
ui_icon: "Leaf"
ui_color: "#16a34a"
generation_instructions: |
  Write one vegan recipe a line cook can follow without asking questions.
  Every ingredient is plant-based: no meat, poultry, fish, shellfish, dairy, eggs, honey or gelatin.
  Put each ingredient on its own row with a quantity and a unit. Number the steps in the order they are cooked.
  State servings, prep time and cook time as whole numbers. List every allergen the dish contains.
  Leave a field empty rather than guessing a supplier, a price or a nutrition figure.
editable: true
marketplace_eligible: true
entity_type: "vegan_recipe"
folder_name: "VeganRecipes"
file_prefix: "VR_"
asset_subfolders:
  - images
  - video
created_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
associated_rules:
  - VEGAN_RECIPE_RULES.md
associated_skills: []

# FIELD CONFIGURATION
# `type` is the data type. `widget` is the editor control (canonical ids only).
field_config:
  status:
    type: enum
    widget: select
    options:
      - { value: "draft", label: "Draft" }
      - { value: "testing", label: "In testing" }
      - { value: "approved", label: "Approved for the menu" }
      - { value: "retired", label: "Retired" }
  course:
    type: enum
    widget: select
    options:
      - { value: "starter", label: "Starter" }
      - { value: "main", label: "Main" }
      - { value: "side", label: "Side" }
      - { value: "dessert", label: "Dessert" }
      - { value: "drink", label: "Drink" }
      - { value: "sauce", label: "Sauce or condiment" }
  cuisine:
    type: string
    widget: text
    help: "Free text, for example Oaxacan, Sichuan, Levantine."
  description:
    type: text
    widget: textarea
    help: "Two or three sentences a server could read to a guest."
  primary_image:
    type: image
    widget: image-ref
  servings:
    type: integer
    widget: number
    min: 1
    max: 500
    unit: "servings"
  prep_minutes:
    type: integer
    widget: number
    min: 0
    unit: "min"
  cook_minutes:
    type: integer
    widget: number
    min: 0
    unit: "min"
  difficulty:
    type: enum
    widget: select
    options:
      - { value: "easy", label: "Easy" }
      - { value: "medium", label: "Medium" }
      - { value: "hard", label: "Hard" }
  ingredients:
    type: array
    widget: object-array
    help: "One row per ingredient. Name the plant-based product exactly, for example oat milk, not milk."
    sub_fields:
      - { key: "item", label: "Ingredient", ui_component: "text" }
      - { key: "quantity", label: "Quantity", ui_component: "number" }
      - { key: "unit", label: "Unit", ui_component: "text" }
      - { key: "note", label: "Prep note", ui_component: "text" }
  steps:
    type: array
    widget: ordered-list
    help: "One action per step, in cooking order."
  allergens:
    type: tags
    widget: tag-input
    allow_custom: true
    suggestions:
      - "gluten"
      - "soy"
      - "peanuts"
      - "tree nuts"
      - "sesame"
      - "mustard"
      - "celery"
      - "sulphites"
      - "lupin"
  dietary_tags:
    type: tags
    widget: tag-input
    allow_custom: true
    suggestions:
      - "gluten-free"
      - "nut-free"
      - "soy-free"
      - "oil-free"
      - "raw"
      - "low-sodium"
  protein_source:
    type: string
    widget: text
    help: "Main plant protein, for example chickpeas, tofu, seitan, lentils."
  calories_per_serving:
    type: integer
    widget: number
    min: 0
    unit: "kcal"
  cost_per_serving:
    type: number
    widget: number
    min: 0
    step: 0.01
  related_recipes:
    type: references
    widget: entity-multiselect
    reference_type: vegan_recipe
    max_selections: 8
  last_tested:
    type: date
    widget: date
  chef_notes:
    type: text
    widget: textarea

# RECIPE FIELDS
status: "draft"
course: "main"
cuisine: ""
description: ""
primary_image: ""
servings: 4
prep_minutes: 0
cook_minutes: 0
difficulty: "easy"
ingredients: []
steps: []
allergens: []
dietary_tags: []
protein_source: ""
calories_per_serving: 0
cost_per_serving: 0
related_recipes: []
last_tested: ""
chef_notes: ""

# BROWSE VIEWS
views:
  default: cards
  enabled: [cards, gallery, table, board, calendar]
  roles:
    title: name
    subtitle: cuisine
    image: primary_image
    badges: [course, status, difficulty]
    card_fields: [servings, prep_minutes, cook_minutes, protein_source]
  table:
    columns:
      - { key: name }
      - { key: course, display: chips }
      - { key: status, display: chips }
      - { key: prep_minutes, display: unit }
      - { key: cook_minutes, display: unit }
      - { key: allergens, display: chips }
      - { key: updated, display: date }
  board:
    group_by: status
  calendar:
    date_field: last_tested
  gallery:
    aspect: landscape
  sort:
    default: name
    options: [name, course, prep_minutes, cook_minutes, last_tested, updated]
  facets: [course, status, difficulty, allergens, dietary_tags]
---

# {{name}}

## Why it is on the menu

Say what the dish is and who orders it.

## Method notes

Anything the numbered steps do not cover: resting times, what can be made ahead, how it is held on the line.

## Plating

Describe the plate, the garnish and the portion.

## Substitutions

List tested swaps for common allergens.
