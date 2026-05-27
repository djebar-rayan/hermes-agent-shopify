---
name: shopify-metatitle-generator
description: Generates SEO meta title + meta description for a Shopify product (60/160 chars target)
category: e-commerce-seo
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, seo, meta-title, meta-description, llm-generation]
---

# <STORE_NAME> Meta Title/Description Generator

## When to Use
- Companion skill to `shopify-catalog-gap-analyzer` when `seo.title` or `seo.description` is empty or < 30 chars
- Before `shopify-batch-executor` for meta-title batches
- On demand for a single product

## Procedure
Input: `{handle, title, productType, descriptionHtml_excerpt, current_seo: {title, description}}`

Generates:
```json
{
  "meta_title": "...",        // <= 60 chars target (max 70)
  "meta_description": "...",  // <= 160 chars target (max 170)
  "rationale": "..."
}
```

meta_title rules:
- 50-60 chars optimal (Google truncates beyond ~580px)
- Includes product name + main keyword + brand "<STORE_NAME>" if possible
- At least 1 brand vocabulary word (STORE-BRAND.md)
- Standard format: "<Product name> - <Symbol/Character> | <STORE_NAME>"

meta_description rules:
- 140-160 chars optimal
- Includes an implicit CTA (discover, offer, wear)
- Mentions "Made in France" if applicable
- At least 1 brand vocabulary word (STORE-BRAND.md)
- Does NOT repeat meta_title verbatim (Google penalizes)

DO NOT apply the mutation. `shopify-batch-executor` (via productUpdate with seo: {title, description}) will handle it.

## Pitfalls
- Title > 70 chars = truncated in SERP, refused.
- Description > 170 chars = truncated, refused.
- Without a brand vocabulary word = lost identity.
- Avoid stop words ("the best", "amazing") — Google ignores them.

## Verification
- meta_title <= 70 chars
- meta_description <= 170 chars
- Both contain >= 1 brand vocabulary word
- No duplication between title and description
- rationale specifies the main target keyword
