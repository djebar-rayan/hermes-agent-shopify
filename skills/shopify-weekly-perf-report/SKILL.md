---
name: shopify-weekly-perf-report
description: Generates the <STORE_NAME> weekly performance report (KPI, top wins/losses, diagnosis)
version: 1.0.0
author: Hermes (initial scaffold)
metadata:
  hermes:
    tags: [shopify, growth, report, framework]
    category: ecommerce
    requires_toolsets: [terminal]
---
# Weekly Performance Report <STORE_NAME>

## When to Use
Every Monday at 9am (cron `shopify-lundi-perf`), or on explicit request.

## Procedure
1. `cd $HERMES_WORKSPACE/shopify-automation-toolkit`
2. If `store-data/` is more than 7 days old, run `node fetch-store-data.js` (115s)
3. Extract KPIs for week N and N-1: sessions, conversions, orders, AOV, revenue, abandoned cart
4. Read `learnings.md` for the last 7 days
5. Compare vs week N-1: compute % deltas
6. Generate the report in `$HERMES_WORKSPACE/reports/$(date +%Y-W%V)-perf.md`
7. Telegram summary (max 20 lines): KPI snapshot, top 3 wins/losses, diagnosis, actions executed + impact, proposed actions

## Pitfalls
- If store-data/ is empty → fetch mandatory
- Comparing N vs N-1 requires >= 2 weeks of history, otherwise mention "baseline"
- Avoid very small absolute numbers in Telegram → prefer %

## Verification
- File `reports/YYYY-Www-perf.md` created
- Telegram message sent
- `learnings.md` updated
