---
name: shopify-altext-generator
description: Generate 3 SEO alt-text proposals FR+EN for a product image, based on title + brand vocabulary (STORE-BRAND.md)
category: e-commerce-seo
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, seo, alt-text, accessibility, llm-generation]
---

# <STORE_NAME> Alt-Text Generator

## When to Use
- Companion skill to `shopify-catalog-gap-analyzer` when a product has an empty alt-text
- Before `shopify-batch-executor` to prepare an alt-text batch
- On demand for a specific product

## Procedure
Expected input: `{handle, title, product_id, image_id, productType?}` (extracted via READ-ONLY GraphQL).

Generate 3 JSON proposals:
```json
{
  "alt_options": [
    {"id": 1, "fr": "...", "en": "..."},
    {"id": 2, "fr": "...", "en": "..."},
    {"id": 3, "fr": "...", "en": "..."}
  ],
  "selected_option": <1|2|3>,
  "rationale": "..."
}
```

Generation rules:
- Each alt-text: max 125 chars (Google SEO limit)
- FR AND EN mandatory
- AT LEAST 1 word from brand vocabulary (STORE-BRAND.md) per alt: see list in STORE-BRAND.md
- If the title contains "Made in France": mention it in at least 1 alt
- Describe what is VISIBLE in the image (color, symbol, format) + cultural context
- Selected option = the one that combines SEO + accessibility + cultural context

Output: valid JSON written to the path requested by the caller (typically `/tmp/altext-<handle>.json` or `tests/p3.X-...json` in test mode).

DO NOT apply the mutation. `shopify-batch-executor` will handle that after operator validation.

## Pitfalls
- Alt-text > 125 chars = degraded SEO, refuse.
- Without a brand vocabulary word = loss of identity.
- Avoid generic phrases ("nice creation", "unique product") — be specific about what the image shows.
- Do not reuse the product title verbatim (Google penalizes duplication).

## Verification
- 3 distinct proposals (no FR or EN duplicates)
- Each alt <= 125 chars
- Each alt contains >= 1 brand vocabulary word
- selected_option points to one of the 3 options
- rationale explains the choice in 1-2 sentences
