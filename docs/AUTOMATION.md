# Automation — Crons, Hooks, STANDING, Memory

> Complete wiring of Hermes automation: 4 weekly crons, v0.14 hooks, 14 immutable STANDING rules, OpenViking memory system.

---

## 1. The 4 crons

Configuration in `/root/.hermes/cron/jobs.json` — timezone **Europe/Paris** (configurable via `config.yaml`).

| Name (template) | Cron expression | Decoding | Skills invoked |
|---|---|---|---|
| `<store>-weekly-perf-report` | `0 9 * * 1` | Monday 9:00am | `shopify-weekly-perf-report` + `shopify-baseline-kpi-fetch` + `shopify-low-conversion-diagnostic` + `shopify-klaviyo-weekly-report` |
| `<store>-weekly-ideas` | `0 10 * * 6` | Saturday 10:00am | `shopify-instagram-ideator` + `shopify-product-ideator` + `shopify-cultural-calendar` + `shopify-klaviyo-campaign-ideator` |
| `<store>-weekly-meta-review` | `0 20 * * 0` | Sunday 8:00pm | `shopify-weekly-perf-report` + `shopify-cultural-calendar` |
| `<store>-watchdog-conversion` | `0 */6 * * *` | Every 6h | Bash script + `shopify-klaviyo-drop-watchdog` |

Replace `<store>` with your handle in `cron-jobs.json`.

---

### Cron 1: Weekly performance report (Monday 9am)

**Mission**: weekly observation-actions report integrating Shopify KPIs + Klaviyo section.

**Skills invoked**:
- `shopify-weekly-perf-report` — orchestrates, generates the markdown
- `shopify-baseline-kpi-fetch` — fetches KPIs N and N-1 (sessions, conversions, AOV, revenue, abandoned carts)
- `shopify-low-conversion-diagnostic` — detects products with >50 views/7d without add-to-cart
- `shopify-klaviyo-weekly-report` — markdown section for email KPIs (open/click/bounce/unsub/order)

**Deliverables**:
- `$HERMES_WORKSPACE/reports/YYYY-Www-perf.md` — full report
- Telegram summary in `$TELEGRAM_HOME_CHANNEL` chat (max 20 lines)
- SMTP Gmail email via inline Python snippet with `EMAIL_SMTP_OK` sentinel

**Phase safeguard**: If `HERMES_MODE=test`, no Shopify mutation executed. Phase 2+ (= `HERMES_MODE=prod`): green 🟢 actions after Telegram /yes.

**Anti-hallucination**: hard rules embedded in the prompt — every KPI must have a cited source, otherwise `(data not available)`.

---

### Cron 2: Weekly creative email (Saturday 10am)

**Mission**: creative email with EXACTLY 3 proposals:

**Proposal 1 — New product**:
- Name (+ cultural variation if relevant for your brand)
- Category
- 50-word description (concept + brand universe)
- Why now (market signal, niche identified in `brand-knowledge.md`)
- Target price + estimated margin
- Similar competitors + differentiation
- Textual visual description for moodboard

**Proposal 2 — Instagram post**:
- Format (reel/carousel/single/story)
- Theme (brand storytelling / education / customer testimonial)
- FR + EN caption
- 15 hashtags (5 large >100k + 5 medium 10k-100k + 5 niche <10k)
- Textual visual description
- Recommended date + time (optimal slot for your brand, e.g., 6-10pm Paris)
- Explicit CTA

**Proposal 3 — Klaviyo campaign draft**:
- Aligned with `shopify-cultural-calendar` event D-21 to D-7 (read from `cultural-events.json`)
- Read-only markdown format (never direct POST to Klaviyo)
- Output: section in `reports/YYYY-Www-ideas.md` + archive in `campaigns/YYYY-Www-klaviyo-draft.md`

**Safeguard**: no automatic publishing, DRAFTS only, manual copy-paste by the merchant.

---

### Cron 3: Self-improvement meta-review (Sunday 8pm)

**Mission**: weekly meta-review with automatic skill creation.

**Procedure**:
1. For each action executed this week (read in `learnings.md`), check KPI impact (before/after) if data available, otherwise flag for W+1 measurement
2. Run `hermes insights --days 7` → capture tokens / cost / models
3. Identify 3 patterns: what worked / what failed / what deserves a skill
4. **If recurrent pattern > 3 occurrences over 4 weeks** → automatically creates the corresponding SKILL.md in `/root/.hermes/skills/<store>-<name>/`
5. Updates `brand-knowledge.md` (max 5 lines added per week to avoid inflation)
6. Checks via `shopify-cultural-calendar` if event at D-21 → Telegram advance notice with cadence D-21/D-14/D-10/D-3
7. Updates `MEMORY.md` Current phase line if Phase transition

**Deliverables**:
- `$HERMES_WORKSPACE/meta-reviews/YYYY-Www-meta.md` (complete written summary)
- Telegram in `$TELEGRAM_HOME_CHANNEL` chat (max 15 lines)
- Possibly: 1 new `SKILL.md` created
- Possibly: 1 cultural advance-notice alert

**Safeguard**: no Shopify mutation. Only authorized writes: SKILL.md, brand-knowledge.md, MEMORY.md, meta-reviews/.

---

### Cron 4: Conversion watchdog (every 6h)

**Mode**: `no_agent: true` — runs a direct bash script, not an LLM agent session. **Token savings**: no open session if nothing to report.

**Mission**: monitors key KPIs:
- Shopify sessions (drop > 30% / 24h)
- Conversions (drop > 30% / 24h)
- Klaviyo drop alerts (open ↓>20pp, click ↓>30pp, revenue ↓>40%, unsub >5%)
- OpenRouter quota probe (alert if >80% consumed)

**Deliverable**: **Silent by default** — Telegram only if alert. If zero alert: `{"wakeAgent":false}` (the agent does not wake up).

---

## 2. v0.14 Hooks

The v0.13 → v0.14 migration changed the format (list → dict) and the event (`tool_call_completed` → `post_tool_call`).

Configuration in `/root/.hermes/config.yaml` `hooks:` section:

```yaml
hooks:
  on_session_start:
    - command: /root/.hermes/hooks/inject-standing.sh
      matcher: ".*"
      timeout: 10
  post_tool_call:
    - command: /root/.hermes/hooks/log-learning.sh
      matcher: ".*Update|.*Create|.*Delete|.*publish.*|.*email.*"
      timeout: 30
hooks_auto_accept: true
```

### `inject-standing.sh`

Reads `STANDING-CORE.md` + `$HERMES_WORKSPACE/STORE-BRAND.md`, concatenates, returns `{"continue": true, "context_injection": "<content>"}` via jq.

```bash
#!/bin/bash
STANDING_CORE=$(cat /root/.hermes/standing/STANDING-CORE.md)
STORE_BRAND=$([ -f "$HERMES_WORKSPACE/STORE-BRAND.md" ] && cat "$HERMES_WORKSPACE/STORE-BRAND.md" || echo "")
COMBINED="$STANDING_CORE

## Brand-Specific Rules
$STORE_BRAND"
jq -n --arg s "$COMBINED" '{"continue": true, "context_injection": $s}'
```

### `log-learning.sh`

Automatic append in `$HERMES_WORKSPACE/learnings.md` for every mutative action:
- Compatible with v0.13 (`args`) + v0.14 (`tool_input` + `hook_event_name`)
- Skip if event = `pre_tool_call` (log only post-exec)
- Regex filter on tool/input: `Update|Create|Delete|publish|email_send|productCreate|productUpdate|customerCreate|webhookCreate|fileUpdate|collectionCreate`
- Creates `learnings.md` with header if missing, then appends UTC timestamp + tool + input truncated to 400 chars + 4 placeholders (before/after/conclusion/future)

---

## 3. STANDING.md — 14 immutable rules

Injected at every session via the `inject-standing` hook. Decomposed into:
- **`STANDING-CORE.md`** (11 universal rules) — lives in `/root/.hermes/standing/`
- **`STORE-BRAND.md`** (3 brand-specific rules) — lives in `$HERMES_WORKSPACE/`

### 11 universal rules (STANDING-CORE)

| # | Rule | Explanation |
|---|---|---|
| 1 | **Mandatory pre-reading** | Before any mutation: MISSION + MEMORY + STANDING + last 7 learnings entries |
| 2 | **Never `shopify store auth`** | Auth already OK, re-running = headless crash (port 13387 + TTY required) |
| 3 | **Never publish Instagram without validation** | Always propose in forced `dry` mode during test phase |
| 4 | **+5% price forbidden without /yes** | Modifying `price` directly = 🔴, prefer `compareAtPrice` |
| 5 | **No deletion** | Product / page / customer: totally forbidden |
| 7 | **Measurable impact in N+1** | Every action documented in learnings.md the following week |
| 8 | **Expired Shopify token = notify** | Don't try to re-auth alone |
| 11 | **Anti-hallucination KPI** | Every number must have a verifiable cited source |
| 12 | **No repeated padding** | Forbidden to repeat a word N times to reach a threshold |
| 13 | **No invention of GraphQL field** | Always read `hermes-schema-guard` BEFORE any mutation, otherwise introspect |
| 14 | **No PASS on Exception** | Try/except returning PASS = forbidden, always `EMAIL_FAIL: <exact cause>` |

### 3 brand-specific rules (STORE-BRAND.md to customize)

| # | Rule (template) | To customize |
|---|---|---|
| 6 | **Mandatory brand vocabulary** | List of keywords that MUST appear in any generated content (cultural universe, brand name, USP). Ex: "amazigh, berbère, tifinagh, yaz" for Azamoul; "artisanal, terroir, biodynamie" for a wine estate; etc. |
| 9 | **Email via `hermes-email-sender` skill** | Defines the canonical skill for email sending (uses inline smtplib + `EMAIL_SMTP_OK` sentinel) |
| 10 | **Single Telegram chat** | The `$TELEGRAM_HOME_CHANNEL` (= merchant's user_id) is the ONLY authorized recipient for notifications |

---

## 4. Memory system

### Architecture

```
/root/.hermes/memories/        [framework — shared]
├── MEMORY.md                  ← can stay empty or point to the workspace
└── USER.md                    ← user profile (configured at setup)

$HERMES_WORKSPACE/             [user-facing — store instance]
├── MISSION.md                 ← charter specific to the store
├── MEMORY.md                  ← current memory (permanent facts)
├── STORE-BRAND.md             ← vocab + autonomy levels + sensitivities
├── brand-knowledge.md         ← competitors + USP
├── cultural-events.json       ← important events/seasons
└── learnings.md               ← append-only journal auto-logged by hook
```

**Provider**: OpenViking 0.3.16 on port 1933 (local embedding for cross-session RAG).

**Typical limits**:
- `memory_char_limit: 3500` (tokens injected at start of session)
- `user_char_limit: 1375` (user profile)

### Typical `MEMORY.md` content

Template provided in `config/MEMORY.md.template`. Recommended sections:

- **Store**: Shopify handle, domain, plan, currency, timezone, categories
- **Stack**: Hermes version, Python/Node, LLM provider
- **Current phase**: `HERMES_MODE=test|prod`, date of last transition
- **Autonomy levels**: 🟢/🟡/🔴 recap (may reference STORE-BRAND.md)
- **Open decisions**: what awaits a merchant decision

### `learnings.md`

Append-only journal. The `log-learning.sh` hook automatically adds every mutative action. The merchant can also manually add notes.

Typical entry format:
```
- [YYYY-MM-DD HH:MM UTC] toolName: <inputTruncated400chars>
  Before: <to fill in W+1 via meta-review>
  After: <to fill in W+1>
  Conclusion: <to fill in W+1>
  Future: <to fill in W+1>
```

---

## 5. Telegram gateway

| Item | Value (to configure in `.env`) |
|---|---|
| Bot token | `TELEGRAM_BOT_TOKEN` (via @BotFather) |
| Allowed users | `TELEGRAM_ALLOWED_USERS=<user_id>` (via @userinfobot) |
| Home channel | `TELEGRAM_HOME_CHANNEL=<user_id>` |
| Launch command | `hermes gateway run --replace` |
| Lock file | `/root/.hermes/gateway.lock` |
| Restart drain timeout | 180s |
| Auto-continue freshness | 3600s |

The gateway responds only to messages from `TELEGRAM_HOME_CHANNEL`. `/yes`, `/no`, `/edit` commands received while a cron is waiting for validation trigger the corresponding action.

---

## 6. Insights & monitoring

Source: `hermes insights --days N` — analyzes sessions from the last N days.

Exposed metrics:
- Sessions per platform (cron / cli / telegram)
- Messages exchanged (total + user)
- Tool calls
- Tokens (input + output + total)
- Active time (total + average per session)
- Top tools used
- Top skills loaded
- Activity pattern (peak days + hours)

**Usefulness**: detect drift (cron consuming abnormally, model costing too much, skill loading unnecessarily).

---

## 7. `/yes` validation pattern

For 🟡 level actions:

```
1. Hermes prepares the mutation
   - Before snapshot → batches/YYYY-Www-batchN-before.json
   - JSON diff preview → batches/YYYY-Www-batchN-preview.json
   - Auto-generated bash rollback script → batches/YYYY-Www-batchN-rollback.sh
2. Sends USER VALIDATION (mandatory before mutation):
   - Telegram chat $TELEGRAM_HOME_CHANNEL: message with short preview + file links
   - Email to $EMAIL_TO via inline Python smtplib with detailed preview
   - Message includes: "Reply /yes to apply, /no to cancel, /edit to adjust"
3. WAITS for user response (skill pauses, user replies via Telegram)
   - Standard 10-min timeout (configurable)
4. If response = /yes:
   - Executes mutations sequentially (2s spacing anti Shopify rate-limit 1.4 req/s)
   - After snapshot → batches/YYYY-Www-batchN-after.json
   - Actual diff → batches/YYYY-Www-batchN-diff.md
   - Hook auto-logs in learnings.md
   - Telegram + email confirmation
5. If response = /no: clean cancel, keeps preview + rollback files for future retry
6. If response = /edit <handle> <details>: adjusts, regenerates preview, re-requests validation
7. If timeout: abort + Telegram alert
```

---

## 8. Known pitfalls

- **`/yes` arrived while the agent is not waiting** → ignored (safety). The merchant must wait for the message that requests /yes.
- **Shopify rate-limit** (1.4 req/s by default) → space mutations by 2s minimum. If batch > 100 items, plan 30s cooldown every 50 items.
- **Klaviyo 6h cache** → don't expect real-time on email KPIs. To force a refresh, delete the corresponding cache file in `/root/.hermes/cache/klaviyo/`.
- **Shopify CDN cache after theme push** → wait 30-60s before `theme_verify` for propagation, or use cache-bust `?v=$(date +%s)`.
- **Expired Gmail App Password** → email send fails silently. Always check the `EMAIL_SMTP_OK` sentinel in stdout.
- **Expired Shopify token** → Hermes does NOT attempt to re-auth alone (rule 8). It notifies the merchant who must re-auth manually from their Windows workstation (port 13387 + TTY required).

---

## 9. Verification (per cron run checklist)

- [ ] `inject-standing` hook executed at session start (STANDING + STORE-BRAND injected)
- [ ] Mandatory pre-reading performed (MISSION + MEMORY + last 7 learnings)
- [ ] Autonomy level respected (🟢 direct, 🟡 /yes, 🔴 refusal)
- [ ] Anti-hallucination: all numbers have a cited source
- [ ] If email: `EMAIL_SMTP_OK` sentinel verified in stdout
- [ ] If Telegram: message received by the authorized chat
- [ ] `log-learning` hook added an entry in learnings.md for every mutative action
- [ ] `last_status: ok` in `jobs.json` after the run
