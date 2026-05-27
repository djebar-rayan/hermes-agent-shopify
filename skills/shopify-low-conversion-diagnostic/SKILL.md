---
name: shopify-low-conversion-diagnostic
description: Diagnoses why a Shopify product is not converting (12-point checklist)
version: 1.0.0
author: Hermes (initial scaffold)
metadata:
  hermes:
    tags: [diagnostic, conversion, shopify, framework]
    category: ecommerce
---
# Product Low Conversion Diagnostic

## When to Use
Product > 50 views/7d but 0 add-to-cart, or flagged in weekly report.

## Procedure
For the targeted product, verify the 12 points:
1. Primary image: quality >= 800×800, >= 3 images, alt text filled
2. Description: >= 150 words, structured HTML (h2+ul), cultural vocabulary
3. SEO: meta title (30-70 chars), meta description (50-160 chars)
4. Price: aligned with category
5. Variants: all have their dedicated image
6. Shipping: 📦 block at the START of description
7. Reviews: >= 3 if app installed
8. Stock: shown as available
9. Tags: >= 5 relevant
10. Position in collections
11. Readable mobile preview
12. Internal linking in description

## Output
Table: {check, status ✓/⚠/✗, recommendation, level 🟢/🟡/🔴}

## Pitfalls
- Don't modify without validation (except 🟢 actions)

## Verification
- 12 points checked
- >= 1 🟢 action executed if present
- >= 1 🟡 proposal documented
