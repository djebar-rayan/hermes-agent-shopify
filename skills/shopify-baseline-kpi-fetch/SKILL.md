---
name: shopify-baseline-kpi-fetch
description: Standardized Shopify KPI extraction (revenue, AOV, abandonment) via GraphQL for weekly reports
category: e-commerce
---

# <STORE_NAME> Baseline KPI Fetch
Recurring pattern identified during Q2 and Q4.

## When to Use
When the prompt asks to "fetch Shopify metrics", "baseline KPI", or "abandonment rate".

## Configuration
The SHOPIFY_STORE variable lives in /root/.hermes/.env (`<store_handle>.myshopify.com`). Always load it before any CLI call.

## Procedure
1. Create the GraphQL query in a `--query-file` (`/tmp/kpi-query.graphql`).
2. Call the Shopify CLI with the mandatory --store flag:
   ```bash
   set -a; . /root/.hermes/.env; set +a
   shopify store execute --store="$SHOPIFY_STORE" --query-file /tmp/kpi-query.graphql --json
   ```
3. Query `orders` (last 30 days) to extract revenue and AOV.
4. Query `checkouts` to compute cart abandonment rate.
5. Compile into the standard tabular format required by MISSION-HERMES.md.

## Pitfalls
- NEVER use inline `--query`, always use a file.
- NEVER forget the `--store=$SHOPIFY_STORE` flag — otherwise 'Missing required flag store' error.
- Don't forget to filter cancelled/refunded orders.
- If $SHOPIFY_STORE is empty, source /root/.hermes/.env first via `set -a; . /root/.hermes/.env; set +a`.

## Verification
- The returned JSON must contain a non-null `data` field. If `errors` is present, log the exact cause in the report (DO NOT hallucinate KPIs).
