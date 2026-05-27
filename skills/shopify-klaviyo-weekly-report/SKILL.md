---
name: shopify-klaviyo-weekly-report
description: Generates Klaviyo markdown section (flows, campaigns, email engagement) to inject into the Monday weekly report
version: 1.0.0
metadata:
  hermes:
    tags: [klaviyo, email, monitoring, framework, weekly-report]
    category: monitoring
    requires_toolsets: [terminal, file]
---

# <STORE_NAME> Klaviyo Weekly Report

Weekly Klaviyo analysis skill: produces a structured markdown section (email KPIs, top flows, top campaigns, delta vs N-1) to inject into the `shopify-lundi-perf` report.

## When to Use

- **Cron `shopify-lundi-perf` (9b3edc604e0d)**: every Monday at 9am, after the Shopify KPI section and before Top wins/losses
- On explicit user request: "Klaviyo weekly report", "email stats", "email marketing performance"

## Configuration

Reads `$KLAVIYO_API_KEY` from `/root/.hermes/.env`. If missing, returns `[KLAVIYO_FAIL: missing API key]`.

Uses the `/root/.hermes/lib/klaviyo-fetch.sh` helper (TTL 6h cache, exponential retry on 429).

## Procedure

### 1. Load the environment
```bash
set -a; . /root/.hermes/.env; set +a
LIB=/root/.hermes/lib/klaviyo-fetch.sh
```

### 2. Fetch base data
```bash
FLOWS_JSON=$($LIB flows)
METRICS_JSON=$($LIB metrics)
CAMPAIGNS_JSON=$($LIB campaigns)
```

### 3. Compute time windows

- `WEEK_N` = last 7 days (today-7 → today)
- `WEEK_N-1` = previous 7 days (today-14 → today-7)

### 4. For EACH live flow (status=live), retrieve engagement N and N-1

Metrics to aggregate via `metric-aggregate <metric_id> day <since> <until>`:
- `Opened Email` (metric_id found in METRICS_JSON via name="Opened Email")
- `Clicked Email`
- `Bounced Email`
- `Unsubscribed`
- `Placed Order` (revenue attribution)

For each flow, compute:
- Sent (estimated via flow_id filtering on Placed Order metric or via attribution)
- Open rate = Opened / Sent
- Click rate = Clicked / Sent
- Attributed revenue (via Placed Order with flow attribution)

### 5. Compute deltas

For each KPI: `delta_pct = (N - N1) / N1 * 100`. If N-1 = 0, display "n/a".

### 6. Produce markdown section

Format to inject into `reports/YYYY-Www-perf.md`:

```markdown
## 📧 Klaviyo Performance (Email Marketing)

### KPI snapshot N vs N-1

| Metric | Week N | Week N-1 | Δ |
|--------|--------|----------|---|
| Total sends | X | Y | +Z% |
| Avg open rate | X% | Y% | +Z pp |
| Avg click rate | X% | Y% | +Z pp |
| Attributed revenue | X€ | Y€ | +Z% |
| Unsubscribes | X | Y | +Z |

### Top active flows (7d)

| Flow | Sent | Open % | Click % | Revenue | Status |
|------|------|--------|---------|---------|--------|
| Welcome Club+ | … | … | … | …€ | 🟢/🟡/🔴 |
| Abandoned carts | … | … | … | …€ | … |
| Browse Abandonment | … | … | … | …€ | … |
| Ansuf Flow | … | … | … | …€ | … |
| Winback | … | … | … | …€ | … |
| Phone case purchase flow | … | … | … | …€ | … |
| Thanks first purchase | … | … | … | …€ | … |

Status: 🟢 if open>20% AND click>2%, 🟡 if between, 🔴 if below.

### Recent campaigns (30d)

| Date | Name | Open % | Click % | Revenue |
|------|------|--------|---------|---------|
| YYYY-MM-DD | … | …% | …% | …€ |

### Diagnosis

- **Top win**: <flow/campaign with best progression>
- **Top loss**: <flow/campaign with degradation>
- **🟢 level recommendation (Hermes can do alone)**: <concrete action if applicable>
- **🟡 level recommendation (operator validation)**: <proposed action>

```

### 7. Save in two places

- **Full section**: append to `$HERMES_WORKSPACE/reports/$(date +%Y-W%V)-perf.md` after marker `<!-- KLAVIYO_SECTION_START -->`
- **Section cache**: `/root/.hermes/cache/klaviyo/last-weekly-section-$(date +%Y-W%V).md` (for drop-watchdog to compare)

### 8. Log into learnings.md

Add entry in `$HERMES_WORKSPACE/learnings.md`:

```markdown
## $(date -u +%Y-%m-%dT%H:%M:%SZ) — Klaviyo weekly report
- Flows analyzed: X live + Y draft
- Average open rate: Z%
- Attributed revenue N vs N-1: delta_pct
- Top win: <flow_name>
- Top loss: <flow_name>
```

## Pitfalls

- **Rate-limit**: the helper handles backoff. NEVER bypass the TTL cache.
- **Sample size**: if Sent < 50 over the window, mark "(low sample)" in the cell instead of computing a %.
- **Missing data**: if metric-aggregate returns 0 everywhere (key without permission, empty period), display "n/a" (DO NOT hallucinate values).
- **Draft flow**: exclude flows with `status=draft` or `archived=true` from computation.
- **Anti-hallucination**: every number MUST come from `klaviyo-fetch.sh` (traceable JSON cache). No "typical values".
- **Currency**: always EUR (France store). If the API returns USD, convert or log.
- **Timezone**: windows in UTC for Shopify consistency, but display "(week W21: 2026-05-18 → 2026-05-24)" locally.

## Verification

At the end of the run:
- ✅ Generated markdown section starts with `## 📧 Klaviyo Performance`
- ✅ KPI snapshot table with 5 lines, each cell has a value (or "n/a")
- ✅ Flows table with 7 lines (the 7 live, draft Anniversary excluded)
- ✅ File `reports/YYYY-Www-perf.md` contains marker `<!-- KLAVIYO_SECTION_END -->`
- ✅ learnings.md entry created
- ✅ Section cache saved for drop-watchdog
- ✅ No "(fictitious data)" mention or similar — always real value or "n/a"

## Dependencies

- `/root/.hermes/lib/klaviyo-fetch.sh` — API helper
- `$HERMES_WORKSPACE/learnings.md` — auto-log
- `$HERMES_WORKSPACE/reports/` — output

## Read-only contract

This skill is **strictly read-only** on the Klaviyo side. No POST/PUT/DELETE mutation allowed. If the user wants to create a campaign, delegate to the `shopify-klaviyo-campaign-ideator` skill which produces a markdown draft (never a mutation API call).
