---
global: false
entity_type: article
template_reference: ARTICLE_TEMPLATE.md
rules:
- id: article_placeholders
  rule: Replace drafting placeholders in the headline, summary and article body.
  validation_type: error
  fields:
  - name
  - summary
  - article_copy
  forbidden_terms:
  - lorem ipsum
  - TBD
  - '[insert'
  applies_to:
  - article
- id: article_schedule
  rule: Set a publish date and provide a summary before scheduling this article.
  validation_type: warning
  required_fields:
  - publish_date
  - summary
  applies_to:
  - article
- id: article_headline
  rule: Review the headline length against the selected channel’s guideline.
  validation_type: suggestion
  fields:
  - name
  - channel_ref
  applies_to:
  - article
---
# Article rules
