---
name: shopify-description-enricher
description: Enriches a short Shopify descriptionHtml (>=150 words, shipping block at start, brand vocabulary (STORE-BRAND.md))
category: e-commerce-content
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, content, description, llm-generation]
---

# <STORE_NAME> Description Enricher

## When to Use
- Companion skill to `shopify-catalog-gap-analyzer` when a descriptionHtml has fewer than 150 words OR lacks a shipping block at the start
- Before `shopify-batch-executor` for description batches
- On demand for a single product

## Procedure
Input: `{handle, title, descriptionHtml_actuel, productType?, tags?}`

JSON output:
```json
{
  "descriptionHtml_before": "...",
  "descriptionHtml_after": "...",
  "word_count_before": <n>,
  "word_count_after": <n>,
  "brand_vocab_used": ["...", "..."],
  "block_livraison_position": 0
}
```

Generation rules for `descriptionHtml_after`:
- MANDATORILY STARTS with the shipping block within chars 0-300:
  `<p>📦 <strong>Livraison estimee 5-6 jours France metropolitaine</strong>, 8-10 jours international. Expedition soignee depuis la France.</p>`
- Then paragraphs: cultural history + brand connection + product description + materials/usage + imaginative call (gift, wear, share)
- >= 150 words total (text without HTML tags)
- >= 3 brand vocabulary words (see STORE-BRAND.md)
- Valid HTML: closed tags (p, strong, h2, ul/li ok), no div/script/style
- <STORE_NAME> TONE: sober, proud, anchored in identity, no gratuitous superlatives

DO NOT apply the mutation. `shopify-batch-executor` will handle it via productUpdate.

## Pitfalls
- Shipping block anywhere other than the start (>300 chars) = REFUSED.
- Word count < 150 = REFUSED.
- Malformed HTML (unclosed tag) = REFUSED, regenerate.
- Excessive product name repetition = penalized by Google.
- Inventing non-confirmed materials (e.g. "silk") without evidence in title/tags = FORBIDDEN.

## Verification
- word_count_after >= 150
- block_livraison_position == 0 (or <= 300)
- brand_vocab_used.length >= 3
- HTML parseable (lxml/beautifulsoup raises no error)
