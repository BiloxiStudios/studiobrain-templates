---
global: false
entity_type: product
template_reference: PRODUCT_TEMPLATE.md
rules:
- id: product_claims
  rule: Keep medical and guarantee claims out of product names, descriptions and care instructions.
  validation_type: error
  fields:
  - name
  - description
  - care_notes
  forbidden_terms:
  - cures
  - guaranteed results
  - risk-free
  applies_to:
  - product
- id: product_offer
  rule: Provide a SKU and price so customers can order this product.
  validation_type: warning
  required_fields:
  - sku
  - unit_price
  applies_to:
  - product
- id: product_image
  rule: Add a primary image to identify the product in the gallery.
  validation_type: suggestion
  required_fields:
  - primary_image
  applies_to:
  - product
- id: product_supplier
  rule: Link an existing supplier so stock can be reordered.
  validation_type: warning
  required_fields:
  - supplier_ref
  references:
    supplier_ref:
    - supplier
  applies_to:
  - product
---
# Product rules
