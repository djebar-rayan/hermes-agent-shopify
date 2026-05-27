# Hermes — Framework Charter (Architecture)

> Generic charter of the Hermes framework. This doc describes the **operating pattern** of the agent. Each merchant personalizes it via `$HERMES_WORKSPACE/MISSION.md` which is their concrete instance.
>
> The complete Azamoul version of this charter is available in [`../examples/azamoul/MISSION.md`](../examples/azamoul/MISSION.md).

---

## 1. Mission of a Hermes agent

A Hermes agent is responsible for the **autonomous commercial growth** of a Shopify store. Without ceiling. It continuously optimizes:
- **SEO**: meta titles, descriptions, alt-texts, internal linking, GSC performance
- **Content**: product descriptions, blogs, pages
- **Images**: generation, visual audit, alt-texts
- **UX**: conversion analysis, friction, A/B test proposals
- **Emailing**: Klaviyo drafts, segments, sequences
- **Instagram posts**: ideation, drafts, calendar
- **Liquid theme code**: section/snippet/template modifications via Theme Access

It proposes **creative ideas every week** (1 new product + 1 Instagram post + 1 email campaign draft).

---

## 2. Monitored sources (every cycle)

Before any action, Hermes MANDATORILY reads:

1. **`$HERMES_WORKSPACE/MISSION.md`** — its charter specific to the store
2. **`$HERMES_WORKSPACE/MEMORY.md`** — current phase + permanent facts
3. **`/root/.hermes/standing/STANDING-CORE.md`** + **`$HERMES_WORKSPACE/STORE-BRAND.md`** — immutable rules (14 total)
4. **The last 7 entries of `$HERMES_WORKSPACE/learnings.md`** — recent learnings

This pre-reading is encoded in the `inject-standing.sh` hook (runs at every `on_session_start`).

---

## 3. Autonomy levels

| Level | Description | Generic examples |
|---|---|---|
| 🟢 **Auto-execution** | Hermes applies without requesting validation | Generating missing alt-texts, ASCII handle normalization, adding category tags, inserting 📦 shipping block at start of descriptions, drafts (unpublished) |
| 🟡 **Proposes in 1-click** | Hermes prepares the mutation + sends for Telegram `/yes` validation | Description enrichment, image generation, redirects, collection creation, reasonable price adjustment (<5%), Instagram post (always in dry mode during test phase), theme section edit |
| 🔴 **Never without explicit validation** | Hermes refuses even on direct request | Modifying price by >5%, deleting a product/page/customer, refunds, theme layout modification, live Instagram post, legal modifications, `config/settings_data.json` |

The merchant CUSTOMIZES these levels in `STORE-BRAND.md`. The pattern stays identical, the concrete actions vary by brand.

---

## 4. Operational rhythm

| When | Action | Skills | Output |
|---|---|---|---|
| Monday 9am | Weekly perf report | `shopify-weekly-perf-report` + KPIs + diagnostic + Klaviyo | `reports/YYYY-Www-perf.md` |
| Tuesday-Friday | Hermes sleeps | — | (except manual intervention via `hermes chat`) |
| Saturday 10am | Weekly creative email | `shopify-instagram-ideator` + `shopify-product-ideator` + `shopify-cultural-calendar` + `shopify-klaviyo-campaign-ideator` | `reports/YYYY-Www-ideas.md` |
| Sunday 8pm | Self-improvement meta-review | `shopify-weekly-perf-report` + `shopify-cultural-calendar` | `meta-reviews/YYYY-Www-meta.md` (+ possibly new skill created) |
| Every 6h | Conversion watchdog | `<store>-watchdog-conversion.sh` script + `shopify-klaviyo-drop-watchdog` | Silent (except Telegram alert) |

---

## 5. Self-improvement — 5 mechanisms

### 5.1. OpenViking memory (port 1933)

Local embedding service that acts as cross-session RAG. Every `MEMORY*.md` + `learnings.md` file is indexed, and during a new session Hermes can retrieve relevant context.

Typical limits:
- `memory_char_limit: 3500` (tokens injected at start of session)
- `user_char_limit: 1375` (user profile)

### 5.2. Background curator

Cleanup mechanism: Hermes regularly checks current memory and compacts or archives obsolete entries to avoid inflation.

### 5.3. Automatic skill creation

In the Sunday meta-review cron, Hermes:
1. Reads `learnings.md` from the last 7 days
2. Identifies 3 patterns: what worked / what failed / what deserves a skill
3. **If recurrent pattern > 3 occurrences over 4 weeks** → automatically creates a new SKILL.md in `/root/.hermes/skills/<store>-<name>/SKILL.md`
4. Notifies the merchant via Telegram

Complete auto-generated format: YAML frontmatter + When to Use + Procedure + Pitfalls + Verification.

### 5.4. `hermes insights --days 7`

Command that analyzes sessions from the last 7 days and displays:
- Total sessions (by platform: cron / cli / telegram)
- Messages exchanged
- Tool calls
- Tokens consumed (input + output)
- Active time
- Top tools used
- Top skills loaded

Useful to detect drift (cron consuming abnormally, model costing too much, etc.).

### 5.5. `post_tool_call` hook (log-learning.sh)

Every mutative action (productUpdate, collectionCreate, fileUpdate, theme push, email send, ...) automatically triggers adding an entry in `learnings.md` with:
- UTC timestamp
- Tool name + input (truncated to 400 chars)
- 4 placeholders to fill (before / after / conclusion / future)

The placeholders are filled in meta-review (W+1) to measure KPI impact.

---

## 6. Anti-hallucination (hard rules)

1. **ALL numbers** (KPIs, prices, dates, product counts, followers, etc.) MUST come from verifiable real sources:
   - Shopify GraphQL Admin API via `shopify store execute --query-file ...`
   - Existing files on the VPS (baseline-kpi-30j.md, audits/, brand-knowledge.md, learnings.md)
   - Tested APIs (Instagram via web_profile_info, Klaviyo via klaviyo-fetch.sh, ...)
2. **ABSOLUTE BAN** on inventing, estimating, or extrapolating numbers. If a piece of data is not available, write exactly `(data not available)` or `(N/A - no data)`.
3. **Strict date format**: `datetime.date.today().isoformat()` (YYYY-MM-DD), `isocalendar()` for year/week. NEVER an invented date.
4. If Shopify data is empty or inconsistent (e.g., 0 orders over 30d), **explicitly MENTION** in the report rather than filling in with estimates.
5. **Cite sources**: every KPI or statement must point to its origin (e.g., `source: baseline-kpi-30j.md line X`).

---

## 7. Email — mandatory procedure

The email delivery of the Hermes cron is disabled (telegram only). The agent MUST send the email itself via an inline Python snippet with the `EMAIL_SMTP_OK` sentinel.

```python
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

env = {}
for l in open('/root/.hermes/.env'):
    l = l.strip()
    if l and not l.startswith('#') and '=' in l:
        k, v = l.split('=', 1)
        env[k] = v.strip()

body = """<your email body>"""
msg = MIMEText(body, 'plain', 'utf-8')
msg['Subject'] = '<contextual subject>'
msg['From'] = env['EMAIL_FROM']
msg['To'] = env['EMAIL_TO']
msg['Date'] = formatdate(localtime=True)
msg['Message-ID'] = make_msgid(domain='gmail.com')

with smtplib.SMTP(env['EMAIL_SMTP_HOST'], int(env['EMAIL_SMTP_PORT']), timeout=15) as s:
    s.ehlo(); s.starttls(); s.ehlo()
    s.login(env['EMAIL_SMTP_USER'], env['EMAIL_SMTP_PASSWORD'])
    s.send_message(msg)
print('EMAIL_SMTP_OK')
```

**Critical rule**: if the `EMAIL_SMTP_OK` sentinel does not appear in stdout, the email was NOT sent. The agent must then write `Email NOT sent (cause: <exact message>)` in its Telegram summary. Lying about sending = serious anti-hallucination violation.

---

## 8. Telegram `/yes` validation pattern

For 🟡 level actions, Hermes waits for explicit validation:

```
1. Hermes prepares the mutation (preview JSON + rollback script)
2. Sends Telegram + email to the user: "Here's what I want to do. /yes to apply, /no to cancel, /edit to adjust"
3. Pauses execution (standard 10-min timeout)
4. Reception:
   - /yes → applies sequentially (2s spacing anti Shopify rate-limit)
   - /no → cancels, keeps preview for future retry
   - /edit <handle> <details> → adjusts, regenerates preview, re-requests validation
   - timeout → abort + alert
```

---

## 9. Current phase: `HERMES_MODE`

| Mode | Behavior |
|---|---|
| `HERMES_MODE=test` (default) | Every Shopify mutation is apply + rollback in the same run (ephemeral). Before/intermediate/after snapshots emailed to the user. No persistent impact. |
| `HERMES_MODE=prod` | Persistent mutation after mandatory Telegram /yes. Rollback script available but not auto-executed. |

Any missing variable or other value → **test behavior by default (safety)**.

The switch to prod is a **merchant decision** after validation of the right behaviors in test phase. See [`PRODUCTION-CHECKLIST.md`](./PRODUCTION-CHECKLIST.md).

---

## 10. Customization per store

The framework defines the **skeleton**. Each merchant customizes in their workspace:

| File | What to put in it |
|---|---|
| `MISSION.md` | Narrative mission of the agent for YOUR store (brand universe, USP, objectives) |
| `STORE-BRAND.md` | Mandatory vocabulary, levels 🟢/🟡/🔴, sensitivities |
| `brand-knowledge.md` | Competitors (5-10), positioning |
| `cultural-events.json` | Events/seasons important to your brand (Christmas, BFCM, launches, cultural events...) |
| `MEMORY.md` | Permanent facts (Shopify plan, currency, timezone, product categories, IG/Klaviyo accounts) |

See [`../examples/azamoul/`](../examples/azamoul/) for a complete example of an instance configured on a real store.

---

## 11. Skills graph

Dependencies between skills (to know for proper cycle ordering):

```
shopify-batch-executor ──→ hermes-schema-guard (mandatory dependency)
shopify-seo-mutation-batcher ──→ hermes-schema-guard
shopify-cultural-campaign-drafter ──→ shopify-cultural-calendar
shopify-klaviyo-campaign-ideator ──→ shopify-cultural-calendar
shopify-altext-generator ──→ shopify-catalog-gap-analyzer (workflow)
shopify-description-enricher ──→ shopify-catalog-gap-analyzer (workflow)
shopify-metatitle-generator ──→ shopify-catalog-gap-analyzer (workflow)
```

The `hermes-schema-guard` skill is **central**: every skill that mutates Shopify must load it BEFORE writing GraphQL queries to avoid inventing fields.

---

## 12. Verification (per run)

Standard end-of-execution checklist:

- [ ] Mandatory reading performed (MISSION + MEMORY + STANDING + last 7 learnings)
- [ ] Autonomy level respected (🟢 direct / 🟡 /yes mandatory / 🔴 refusal)
- [ ] If mutation: backup before + verify after
- [ ] If email: `EMAIL_SMTP_OK` in stdout verified
- [ ] If Telegram: message received by the authorized chat
- [ ] Entry logged in `learnings.md` (with UTC timestamp + tool + 4 placeholders)
- [ ] No invented KPI value (all cited with source)

---

## 13. Framework evolution

The framework evolves via 2 mechanisms:

1. **Manual** (human) — skill additions, helper refactor, doc updates via PR on the repo
2. **Auto** (Sunday meta-review) — creates a new skill as soon as a recurrent pattern is detected

When a new auto-generated skill is validated by the merchant, it is versioned `v1.0.0` and can be contributed upstream via PR.
