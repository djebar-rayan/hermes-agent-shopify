---
name: shopify-kpi-drop-watchdog
description: Monitors Shopify KPIs over 24h and Telegram-alerts if conversion, sessions, or orders drop > 30%
category: monitoring
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, monitoring, alert, telegram]
    requires_toolsets: [terminal]
---

# <STORE_NAME> KPI Drop Watchdog

## When to Use
- Cron `shopify-watchdog-conversion` (every 6h)
- On demand for an ad-hoc store health check

## Procedure
1. Load env: `set -a; . /root/.hermes/.env; set +a`
2. Fetch rolling 24h KPIs via GraphQL `orders(query: "created_at:>...")`:
   - current 24h order count
   - previous 24h order count (D-1 same window)
   - corresponding revenue
3. Compute deltas in %: `(current - previous) / previous * 100`
4. If delta < -30% on AT LEAST ONE critical KPI:
   - Compose a short Telegram message (< 500 chars):
     "ALERT KPI <STORE_NAME>: <KPI> dropped <X>% over 24h. Current: <val>, D-1: <val>. Recommended action: check checkout flow + service status."
   - Send to chat $TELEGRAM_HOME_CHANNEL via Hermes messaging tool
5. If all OK: return `[SILENT]` (suppress cron delivery).
6. Log in `$HERMES_WORKSPACE/learnings.md` with timestamp + verdict.

## Pitfalls
- Don't alert if previous orders < 3 (weak signal). Use `[SILENT]`.
- Don't alert if delta < 30% (normal noise). Hard threshold.
- NEVER send email for a 24h alert (reserved for weekly report). Telegram only.
- If GraphQL fails, return `[SILENT]` rather than alerting on bad data.

## Verification
- Telegram message received only when actual drop > 30%
- 0 alerts on low traffic (< 3 baseline orders)
- learnings.md log mentions each check (alert or silent)
