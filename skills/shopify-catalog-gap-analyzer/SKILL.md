---
name: shopify-catalog-gap-analyzer
description: Read-only audit of the <STORE_NAME> catalog - identifies products without sufficient tags and without a shipping block at the start of the description, prioritized by business impact
version: 1.0.0
author: Hermes (Phase 2 scaffold)
metadata:
  hermes:
    tags: [shopify, audit, phase2, framework]
    category: ecommerce
    requires_toolsets: [terminal, file]
---
# Catalog Gap Analyzer <STORE_NAME>

## When to Use
- At Phase 2 startup (basic mutative action 🟢)
- Before each execution batch to target priority products
- On explicit request: "do a catalog gap analysis"
- Weekly cron complementing the performance report

## Procedure
1. Read MEMORY.md "Current Phase" line to confirm Phase 2+ (otherwise this skill is informational only).

2. Load existing sources:
   - $HERMES_WORKSPACE/audits/initial-catalog-audit.md (initial baseline)
   - $HERMES_WORKSPACE/brand-knowledge.md (brand context)

3. Via Shopify toolkit (shopify store execute --query-file, NEVER inline --query), fetch:
   - products(first: 250) with id, handle, title, status, tags, descriptionHtml(first 600 chars), images.edges.node.id, productType
   - For each product, compute:
     - tagsCount = len(tags)
     - hasShippingBlockFirst = bool(regex /📦|livraison|expedition/i match in first 300 chars of descriptionHtml)
     - imagesCount = len(images.edges)

4. Categorize products by business category (textile, accessory, jewelry, decor, book, phone case) via productType + heuristic on title if needed.

5. For each category, define the set of mandatory target tags (e.g. textile = (vocab from STORE-BRAND.md), phone case = (category vocab)). Compute missing tags per product.

6. Generate $HERMES_WORKSPACE/audits/phase2-gap-analysis-YYYY-MM-DD.md with:
   - Global stats: X/96 products without shipping block at start, Y/96 with fewer than 5 tags
   - Detailed list per product (handle, proposed action, severity)
   - Suggested batches: splits into groups of 10 products with estimated impact

7. Short Telegram summary (max 12 lines): number of detected gaps, top 5 green actions by impact, propose batch 1.

## Pitfalls
- FORBIDDEN to invent numbers: if no sessions/conversion data, mark "(N/A)"
- No Shopify mutation in this skill: 100 percent read-only
- The shipping-block regex may false-positive on descriptions that mention "livraison" mid-text without a dedicated block. Check the context (first 300 chars).
- If more than 250 products, paginate via GraphQL cursors (currently <STORE_NAME> = 96 products, OK)

## Verification
- audits/phase2-gap-analysis-YYYY-MM-DD.md file created, size >= 2 KB
- Global stats consistent with the 96 catalog products
- Top 10 prioritized by real customer signal (native Shopify sessions/conversion)
- Telegram summary sent, max 12 lines
