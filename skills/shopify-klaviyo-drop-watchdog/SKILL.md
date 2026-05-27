---
name: shopify-klaviyo-drop-watchdog
description: Silent watchdog every 6h — Telegram alert if open rate drops >20% or click rate >30% over a 7-day Klaviyo window
version: 1.0.0
metadata:
  hermes:
    tags: [klaviyo, monitoring, alerting, watchdog, framework]
    category: monitoring
    requires_toolsets: [terminal, messaging]
---

# <STORE_NAME> Klaviyo Drop Watchdog

No-agent-by-design skill: executed every 6h by the `shopify-watchdog-conversion` cron. Stays silent as long as Klaviyo KPIs are stable, triggers a Telegram alert + wake-agent when significant drift is detected.

## When to Use

- **Cron `shopify-watchdog-conversion` (dd4a59c29a88)**: every 6h, in parallel with the existing Shopify conversion check
- **NEVER on direct user request** (not relevant interactively)

## Configuration

Variables read from `.env`:
- `$KLAVIYO_API_KEY`
- `$TELEGRAM_HOME_CHANNEL` ($TELEGRAM_HOME_CHANNEL)
- `$HERMES_MODE` (test: alert without wake, prod: alert + wake-agent)

Alert thresholds (configurable in the skill):
- **Open rate drop > 20 points** over 7d vs prior 7d
- **Click rate drop > 30 points**
- **Attributed revenue drop > 40%**
- **Unsubscribes**: > 5% of sends over 7d

**Min N sends = 50** over the 7d window before computing (otherwise: sample too small, forced silence).

## Procedure

### 1. Load the environment
```bash
set -a; . /root/.hermes/.env; set +a
LIB=/root/.hermes/lib/klaviyo-fetch.sh
TG_BOT_API="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"
```

### 2. Retrieve metric IDs
```bash
METRICS=$($LIB metrics)
# Extract ids matching: Opened Email, Clicked Email, Placed Order, Unsubscribed
```

### 3. Compute 7d N and 7d N-1 aggregates

```bash
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
SINCE_N=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)
SINCE_N1=$(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%SZ)

OPEN_N=$($LIB metric-aggregate $OPENED_ID day $SINCE_N $NOW | jq '.data.attributes.data[0].measurements.count // [] | add')
OPEN_N1=$($LIB metric-aggregate $OPENED_ID day $SINCE_N1 $SINCE_N | jq '.data.attributes.data[0].measurements.count // [] | add')
# Same for CLICK, REVENUE, UNSUBSCRIBE
```

### 4. Compute deltas

```bash
# If SENT_N < 50, abort (sample too small)
if [ "$SENT_N" -lt 50 ]; then
  echo '{"wakeAgent": false, "reason": "sample_too_small"}'
  exit 0
fi

# Open rate delta (percentage points)
OPEN_RATE_N=$(echo "scale=4; $OPEN_N / $SENT_N * 100" | bc)
OPEN_RATE_N1=$(echo "scale=4; $OPEN_N1 / $SENT_N1 * 100" | bc)
OPEN_DROP=$(echo "scale=2; $OPEN_RATE_N1 - $OPEN_RATE_N" | bc)
```

### 5. Decision

```bash
ALERTS=()
[ $(echo "$OPEN_DROP > 20" | bc -l) -eq 1 ] && ALERTS+=("OPEN_DROP: -${OPEN_DROP}pp")
[ $(echo "$CLICK_DROP > 30" | bc -l) -eq 1 ] && ALERTS+=("CLICK_DROP: -${CLICK_DROP}pp")
[ $(echo "$REV_DROP_PCT > 40" | bc -l) -eq 1 ] && ALERTS+=("REVENUE_DROP: -${REV_DROP_PCT}%")
[ $UNSUB_RATE_N -gt 5 ] && ALERTS+=("UNSUB_HIGH: ${UNSUB_RATE_N}%")
```

### 6. Notification

If `${#ALERTS[@]} = 0` → total silence:
```bash
echo '{"wakeAgent": false}'
exit 0
```

If alerts detected:
```bash
MSG="⚠ KLAVIYO DROP DETECTED (<STORE_NAME>)
$(printf '%s\n' "${ALERTS[@]}")

KPI 7d N vs N-1:
- Sent: $SENT_N vs $SENT_N1
- Open: ${OPEN_RATE_N}% vs ${OPEN_RATE_N1}%
- Click: ${CLICK_RATE_N}% vs ${CLICK_RATE_N1}%
- Revenue: ${REV_N}€ vs ${REV_N1}€

Investigate:
1. Did a recent campaign bomb?
2. Was a flow paused?
3. Deliverability OK (bounces)?

Run /chat in Telegram for detailed analysis."

# Test mode: log + Telegram alert but wake-agent false
# Prod mode: Telegram alert + wake-agent true
if [ "${HERMES_MODE:-test}" = "test" ]; then
  curl -s -X POST "$TG_BOT_API" \
    -d "chat_id=$TELEGRAM_HOME_CHANNEL" \
    -d "text=$MSG" \
    -d "parse_mode=Markdown"
  echo "{\"wakeAgent\": false, \"alert_sent\": true, \"mode\": \"test\"}"
else
  curl -s -X POST "$TG_BOT_API" \
    -d "chat_id=$TELEGRAM_HOME_CHANNEL" \
    -d "text=$MSG" \
    -d "parse_mode=Markdown"
  echo "{\"wakeAgent\": true, \"context\": \"$MSG\"}"
fi
```

### 7. Log learnings (only if alert)

```markdown
## $(date -u +%Y-%m-%dT%H:%M:%SZ) — Klaviyo drop watchdog
- Alerts: <list>
- Open rate N vs N-1: X% vs Y%
- Click rate N vs N-1: X% vs Y%
- Mode: test/prod
- Wake agent: true/false
- Conclusion: (to fill in after investigation)
```

## Pitfalls

- **False positives**: thresholds on a 7d window AND min N sends = 50. NEVER alert on a single point or < 50 sends.
- **Silent mode**: if `${#ALERTS[@]} = 0`, return `{"wakeAgent": false}` with NOTHING else (no Telegram noise).
- **Klaviyo rate-limit**: use the helper's 6h cache (not re-fetch on each run).
- **"0 orders" edge case**: if `SENT_N = 0` (campaign sent during N-1 window but not N), this is NORMAL in batch mode. Don't alert.
- **Unsubscribes**: use the `Unsubscribed` metric filtered by flow_id, not the total suppressed profiles (which includes bounces).
- **Test mode mandatory**: as long as `HERMES_MODE=test`, wake-agent stays false (Telegram info alert only).

## Verification

- ✅ Script finishes in < 30s (otherwise cron timeout)
- ✅ If all OK: stdout = `{"wakeAgent": false}` (1 line, valid JSON)
- ✅ If alert: Telegram message received on $TELEGRAM_HOME_CHANNEL
- ✅ If alert + prod: `wakeAgent=true` with context
- ✅ No Klaviyo mutation API call (read + metric-aggregates POST only, which is semantically read)
- ✅ Helper cache used (no re-fetch of flows/metrics each run)

## Dependencies

- `/root/.hermes/lib/klaviyo-fetch.sh`
- `$TELEGRAM_BOT_TOKEN` (env)
- `$TELEGRAM_HOME_CHANNEL` (env)
- `$HERMES_MODE` (env)
- `jq` tool for JSON parsing (installed by default on the VPS)
- `bc` tool for floating-point computation

## Read-only contract

Pure read on the Klaviyo side. The POST on `/api/metric-aggregates/` is semantically a read (aggregation query), not a state mutation. No campaign, profile, flow, segment or list creation allowed.
