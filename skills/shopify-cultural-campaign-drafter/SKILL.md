---
name: shopify-cultural-campaign-drafter
description: Generates campaign drafts for a cultural event (product capsule + email + 2 Instagram posts + distribution calendar)
version: 1.0.0
author: Hermes (Phase 2 scaffold)
metadata:
  hermes:
    tags: [campaign, marketing, instagram, email, framework]
    category: ecommerce
    requires_toolsets: [terminal, file]
---
# Cultural Campaign Drafter <STORE_NAME>

## When to Use
- 2 to 4 weeks before a cultural event (see shopify-cultural-calendar)
- On explicit request: "draft the Aid al-Adha campaign" or "prepare Yennayer"
- Pre-notice alert auto-triggered by cultural-calendar: this skill takes over
- Always in draft mode, NEVER automatic publishing

## Procedure
1. Receives parameter eventName (e.g. "Aid al-Adha 2026", "<cultural new year from cultural-events.json>", "November 1st 2026")
   + dateJ0 (e.g. "2026-06-26") OR computed from cultural-calendar.

2. Verify current phase in MEMORY.md: Phase 2+ required. If Phase 1, drafts only (without product creation).

3. Read sources:
   - brand-knowledge.md (competitors, brand tone, underused niches)
   - audits/initial-catalog-audit.md (products available for capsule)
   - reports/baseline-kpi-30j.md (estimated volume)
   - cron list shopify-samedi-ideas prompt for the ideas format

4. Select 3-5 existing catalog products for the capsule (NO new product creation). Criteria:
   - Thematic alignment with the event (e.g. Aid al-Adha = family celebration = gift products + identity)
   - Stock available (totalInventory > 0)
   - Brand vocabulary respected

5. Create $HERMES_WORKSPACE/campaigns/<event-slug-YYYY>/ with these 5 files:

   a. README.md: campaign brief, distribution calendar (D-21 / D-14 / D-10 / D-3 / D0), suggested promo code (e.g. AID2026 -15 percent), target KPIs
   b. email-draft.txt: subject + email body (clear text, max 30 lines, brand vocabulary (STORE-BRAND.md), product link, promo code, signature)
   c. insta-post-1-reel.md: 1st post draft (D-21 teaser) reel format: storytelling, caption FR + EN, 15 hashtags (5 big + 5 medium + 5 niche), textual visual description, recommended time 6-10pm Paris, CTA
   d. insta-post-2-carrousel.md: 2nd post draft (D-10 capsule products) carousel format 3-5 slides: product focus, price, hashtags, visual
   e. produit-capsule.md: 3-5 selected products with rationale per product + proposed highlight + bundle suggestion

6. Notify Telegram + email:
   "Campaign <eventName> drafts ready in campaigns/<slug>/.
   Calendar: D-21 on YYYY-MM-DD (first post), D-14 (email), D-10 (carousel + promo code), D-3 (reminder).
   /yes to validate the set, /edit <file> <adjustment>, /no to restart."

7. NEVER automatic publishing. This skill produces drafts only for operator validation.

## Pitfalls
- FORBIDDEN to create new product via productCreate: 🟡 level out of scope.
- Promo code must be valid - to be set AFTERWARDS by the operator via Shopify Admin (Hermes does not create the promo code automatically).
- Calendar D-21/14/10/3 per MISSION-HERMES.md 2-week minimum advance notice rule.
- Brand vocabulary mandatory (see STANDING.md list).
- TEXTUAL visual description only (image generation unavailable in Phase 2).

## Verification
- 5 files created in campaigns/<event-slug-YYYY>/
- README.md contains explicit D-21/14/10/3/0 calendar
- Post hashtags respect 5+5+5 split (big/medium/niche)
- Telegram + email received with the brief
