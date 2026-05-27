---
name: shopify-klaviyo-campaign-ideator
description: Proposes a Klaviyo email campaign draft aligned with the cultural calendar (cultural-events.json) and existing segments
version: 1.0.0
metadata:
  hermes:
    tags: [klaviyo, email, content, marketing, framework, ideator]
    category: content
    requires_toolsets: [terminal, file]
---

# <STORE_NAME> Klaviyo Campaign Ideator

Read-only creative skill: proposes ONE Klaviyo email campaign for the week, ready to copy-paste into the Klaviyo UI. **No API mutation.**

## When to Use

- **Cron `shopify-samedi-ideas` (7936943cee39)**: every Saturday at 10am, alongside `shopify-product-ideator` and `shopify-instagram-ideator`
- On user request: "email campaign idea", "Klaviyo draft", "campaign for Yennayer/Aid/etc."

## Configuration

Reads:
- `$KLAVIYO_API_KEY` from `.env`
- `$HERMES_WORKSPACE/brand-knowledge.md` (editorial style)
- `/root/.hermes/cache/klaviyo/` (segments + past performance)
- Skill `shopify-cultural-calendar` (upcoming events D-N)

## Mandatory dependency

Also load the `shopify-cultural-calendar` skill to identify the cultural event to anticipate.

## Procedure

### 1. Load the environment
```bash
set -a; . /root/.hermes/.env; set +a
LIB=/root/.hermes/lib/klaviyo-fetch.sh
```

### 2. Fetch Klaviyo context
```bash
SEGMENTS=$($LIB segments)        # 1 segment: <premium segment>
LISTS=$($LIB lists)              # 2 lists: welcome_ansuf, SMSBump
CAMPAIGNS_HISTORY=$($LIB campaigns)  # 30 past campaigns (for tone/timing consistency)
```

### 3. Read cultural calendar
Call `shopify-cultural-calendar` → identify the event to anticipate (D-21 to D-7 ideal).

Key events to consider (priority by proximity):
- <event from cultural-events.json> (~June 26 2026, D-X)
- <cultural new year from cultural-events.json> (January 12 2027)
- <spring event from cultural-events.json>
- <event from cultural-events.json> (summer)
- <new year event from cultural-events.json>
- Back-to-school / Black Friday / Christmas (mainstream commerce)

### 4. Analyze past similar campaign performance

Look in `CAMPAIGNS_HISTORY` for campaigns of the same type (lifecycle, cultural event, promo):
- Which subject had the best open rate?
- Which CTA converted?
- Which send time worked?

### 5. Build the draft

Format to produce:

```markdown
## 📧 Klaviyo Campaign Proposal — Week 2026-Www

### Strategic context
- **Event**: <cultural event name> (D-X)
- **Why now**: <1-line justification>
- **Recommended target segment**: <premium segment> (X profiles) OR welcome_ansuf (X profiles) OR "Engaged 30d" (to create in Klaviyo)
- **Estimated send volume**: X profiles

### Subject line (3 variants for A/B test)
1. **Variant A** (emotional): "..." (X chars, preview: "...")
2. **Variant B** (urgency): "..."
3. **Variant C** (curiosity): "..."

### Preview text (50-90 chars)
"<invisible text but visible in preview>"

### Email body — structure

**Hook (1 line)**
"..."

**Intro (2-3 lines)**
- Cultural reference (mandatory vocab (from STORE-BRAND.md))
- Event context
- What the <STORE_NAME> community celebrates

**Featured product**
- 1 to 3 Shopify catalog products aligned with the event
- Link: https://${SHOP_DOMAIN}/products/<handle>
- Shipping block 📦 if relevant

**Promo code (optional)**
- Suggested code: `<EVENT><YEAR>` (e.g. AID2026, YENNAYER2977)
- Suggested discount: 10-15% (operator to validate)
- Validity: <start date> → <end date> (typically 5-7d)

**Primary CTA**
- Button text: "Discover the collection" / "Use the code" / "See new arrivals"
- Target URL: `https://${SHOP_DOMAIN}/<collection-handle>`

**Signature**
- <STORE_NAME> editorial style (see brand-knowledge.md)
- Made in France mention if relevant

### Recommended send time
- **Send date**: <date near event, D-X>
- **Time**: <based on campaign history: e.g. 6pm Paris if best past open rate>
- **Justification**: <reference campaign: "Winter & holidays 2024 24% open at 7pm Thursday">

### Hashtags / SEO keywords
- For reuse on Instagram/blog: #<your-niche> #<your-brand> #<event>

### Checklist before copying into Klaviyo
- [ ] Subject under 50 chars (mobile-friendly)
- [ ] Preview text 50-90 chars
- [ ] Mandatory vocab present (min 2 words from dictionary)
- [ ] Single, clear CTA
- [ ] Product link tested (200 OK)
- [ ] Promo code created in Shopify (manual action required)
- [ ] Segment verified in Klaviyo > Audience > Segments

### ⚠️ Test / prod mode
Reads `$HERMES_MODE`:
- `test` (default): markdown draft only, no campaign creation in Klaviyo, test recipient = $EMAIL_TO
- `prod`: validated draft ready for manual entry in Klaviyo (Hermes never POSTs)
```

### 6. Save

- **Ideas section**: append to `$HERMES_WORKSPACE/reports/$(date +%Y-W%V)-ideas.md` after the product/Insta sections
- **Separate cache**: `$HERMES_WORKSPACE/campaigns/$(date +%Y-W%V)-klaviyo-draft.md` (for archival)

### 7. Log learnings

```markdown
## $(date -u +%Y-%m-%dT%H:%M:%SZ) — Klaviyo campaign drafted
- Target event: <event>
- Recommended segment: <segment>
- Suggested promo code: <code>
- Status: DRAFT (test mode, no send)
```

## Pitfalls

- **NEVER POST to Klaviyo** (strict read-only). If user asks "send", reply: "I propose the draft. You validate in Klaviyo UI then click Send."
- **Mandatory vocab**: Minimum 2 words from brand dictionary (see MEMORY.md → "Mandatory brand vocabulary")
- **No stereotypes**: see STANDING.md rule #6
- **Promo code**: only SUGGEST, NEVER create in Shopify (🔴 level mutation forbidden)
- **Product links**: verify the handle exists in store-data/products.md BEFORE including it
- **Sample size**: if campaigns_history < 5 similar campaigns, indicate "(limited baseline)" in timing justification
- **EUR currency** only (France store)

## Verification

- ✅ Markdown draft contains the 7 sections (Context / Subject / Preview / Body / Promo / Send time / Checklist)
- ✅ Min 2 brand vocabulary words (STORE-BRAND.md) in the body
- ✅ No mutation API call (verifiable via curl POST log)
- ✅ File `campaigns/YYYY-Www-klaviyo-draft.md` created
- ✅ Section added to `reports/YYYY-Www-ideas.md`
- ✅ learnings.md entry created
- ✅ Draft explicitly mentions the mode (test/prod)

## Dependencies

- `/root/.hermes/lib/klaviyo-fetch.sh`
- Skill `shopify-cultural-calendar`
- `$HERMES_WORKSPACE/brand-knowledge.md`
- `$HERMES_WORKSPACE/store-data/products.md`
- `$HERMES_WORKSPACE/learnings.md`
