---
name: shopify-cultural-calendar
description: Planning and alerts for cultural events (read from cultural-events.json)
version: 1.0.0
author: Hermes (Phase 0 scaffold)
metadata:
  hermes:
    tags: [culture, calendar, marketing, framework]
    category: ecommerce
    requires_toolsets: [web]
---
# Amazigh Cultural Calendar <STORE_NAME>

## When to Use
- Before each commercial season (Yennayer = January, Ramadan, holidays)
- In the Monday performance report: mention upcoming event (< 14 days)
- In the Saturday email: propose a themed campaign

## Procedure
1. Check cultural events calendar (read from cultural-events.json)
2. Compute days remaining before next event
3. If < 14 days: alert and propose a campaign (email + Insta + product)
4. Record events for the next 6 months in brand-knowledge.md

## Key events (recurring)
- <new year event from cultural-events.json>
- Imilchil Festival: September
- <local cultural event from cultural-events.json>
- Ramadan: variable (hijri)
- Local cultural events (festivals, etc.)

## Pitfalls
- Islamic dates are variable (computed with hijri)
- No stereotypes / cultural appropriation
- Align with catalog products (product matching by event category)

## Verification
- brand-knowledge.md table updated with dates for the next 6 months
- Telegram alerts sent (> 2 weeks)
