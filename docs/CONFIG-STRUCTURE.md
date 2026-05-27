# Configuration Structure — `config.yaml`, `.env`, `cron/jobs.json`

> Optimal configuration architecture for Hermes. Explains how `config.yaml`, `.env`, hooks, and crons fit together.
>
> Concrete templates in [`../config/`](../config/).

---

## 1. Overview — Config hierarchy

```
/root/.hermes/                          ← FRAMEWORK (shared)
├── config.yaml                         ← Hermes Agent config (model, hooks, memory)
├── .env                                ← store secrets (chmod 600)
├── standing/STANDING-CORE.md           ← 11 universal rules
├── cron/jobs.json                      ← 4 crons (read parameterized prompts)
└── hooks/*.sh                          ← inject-standing + log-learning

$HERMES_WORKSPACE/                       ← USER-FACING (store instance)
├── MISSION.md                          ← specific charter
├── STORE-BRAND.md                      ← vocab + autonomy levels
├── brand-knowledge.md                  ← competitors + USP
├── cultural-events.json                ← event calendar
└── MEMORY.md                           ← permanent facts
```

**Principle**: framework files stay neutral and generic. User-facing files customize the behavior for YOUR store.

---

## 2. `/root/.hermes/config.yaml`

Main YAML file of the agent. Contains:

### LLM section
```yaml
language: fr
model:
  default: google/gemini-3.1-flash-lite-preview
  provider: openrouter
  base_url: https://openrouter.ai/api/v1
  api_mode: chat_completions
context_length: 262144
request_timeout: 1800
timezone: Europe/Paris
```

### Memory section
```yaml
memory:
  provider: openviking
  endpoint: http://localhost:1933
  char_limit: 3500
  user_char_limit: 1375
```

### Compression section
```yaml
compression:
  enabled: true
  target_ratio: 0.25
  threshold: 0.6
  protect_last_n: 30
```

### Approvals section
```yaml
approvals:
  mode: smart
  cron_mode: deny           # crons do not request interactive approval (use Telegram /yes instead)
  timeout: 60
```

### Security section
```yaml
security:
  redact_secrets: true       # auto-redact .env values in logs
  tirith_enabled: true       # outbound firewall
  tirith_fail_open: true
  tirith_timeout: 5
  allow_private_urls: false  # blocks private IPs
```

### v0.14 Hooks section
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

### Toolsets section
```yaml
toolsets:
  - hermes-cli

toolset_terminal:
  workdir: $HERMES_WORKSPACE
  env_passthrough:
    - SHOPIFY_STORE
    - SHOPIFY_CLI_THEME_TOKEN
    - KLAVIYO_API_KEY
    - OPENROUTER_API_KEY
    - GEMINI_API_KEY
    - OPENAI_API_KEY
    - FIRECRAWL_API_KEY
    - EMAIL_SMTP_HOST
    - EMAIL_SMTP_PORT
    - EMAIL_SMTP_USER
    - EMAIL_SMTP_PASSWORD
    - EMAIL_FROM
    - EMAIL_TO
    - HERMES_MODE
    - HERMES_WORKSPACE
    - LIVE_THEME_ID
    - TELEGRAM_BOT_TOKEN
    - TELEGRAM_HOME_CHANNEL
    - TELEGRAM_ALLOWED_USERS
```

---

## 3. `.env` — Secrets and store config

Template provided in [`../config/.env.template`](../config/.env.template).

```bash
# === Store ===
SHOPIFY_STORE=<store_handle>            # without .myshopify.com
SHOP_BRAND_NAME=<Display Name>
SHOP_DOMAIN=<store>.com
HERMES_WORKSPACE=/root/<store>-shopify
HERMES_MODE=test                        # test | prod
HERMES_TEST_EMAIL_TO=<your_email>
LIVE_THEME_ID=<numeric_id>

# === Shopify Auth ===
SHOPIFY_CLI_THEME_TOKEN=shptka_***

# === LLM Providers ===
OPENROUTER_API_KEY=sk-or-v1-***
GEMINI_API_KEY=AIza***
GEMINI_MODEL=gemini-3.1-flash-image-preview
GEMINI_TEXT_MODEL=gemini-3.1-flash-lite-preview
GEMINI_VISION_MODEL=gemini-3.1-flash-lite-preview
OPENAI_API_KEY=sk-proj-***
OPENAI_TEXT_MODEL=gpt-4.1-nano
OPENAI_VISION_MODEL=gpt-4.1-nano
ANTHROPIC_API_KEY=sk-ant-***
ANTHROPIC_TOKEN=***

# === Email SMTP ===
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=<your_email>
EMAIL_SMTP_PASSWORD=<App Password 16 chars>
EMAIL_FROM=<your_email>
EMAIL_TO=<your_email>

# === Telegram ===
TELEGRAM_BOT_TOKEN=***
TELEGRAM_ALLOWED_USERS=<user_id>
TELEGRAM_HOME_CHANNEL=<user_id>

# === Optional ===
KLAVIYO_API_KEY=pk_***
FIRECRAWL_API_KEY=fc-***
GSC_SERVICE_ACCOUNT_FILE=/root/.hermes/gsc-service-account.json
GSC_CLIENT_EMAIL=<service-account>@<project>.iam.gserviceaccount.com
GSC_PROJECT_ID=<gcp-project>
GSC_SITE_URL=sc-domain:<store>.com

# === Browser tools (optional) ===
BROWSERBASE_ADVANCED_STEALTH=true
BROWSERBASE_PROXIES=true
BROWSER_INACTIVITY_TIMEOUT=300
BROWSER_SESSION_TIMEOUT=3600

# === Memory ===
OPENVIKING_ENDPOINT=http://localhost:1933
```

**Security**: `chmod 600 /root/.hermes/.env` mandatory. Never commit.

---

## 4. `/root/.hermes/cron/jobs.json`

Template provided in [`../config/cron-jobs.json.template`](../config/cron-jobs.json.template).

JSON structure:

```json
{
  "jobs": [
    {
      "id": "<auto-generated-uuid>",
      "name": "<store>-weekly-perf-report",
      "prompt": "<prompt template with placeholders>",
      "skills": [
        "shopify-weekly-perf-report",
        "shopify-baseline-kpi-fetch",
        "shopify-low-conversion-diagnostic",
        "shopify-klaviyo-weekly-report"
      ],
      "skill": "shopify-weekly-perf-report",
      "model": null,
      "provider": null,
      "base_url": null,
      "script": null,
      "no_agent": false,
      "context_from": null,
      "schedule": {
        "kind": "cron",
        "expr": "0 9 * * 1"
      },
      "enabled": true,
      "state": "scheduled",
      "deliver": "telegram",
      "workdir": "$HERMES_WORKSPACE"
    },
    {
      "id": "<auto>",
      "name": "<store>-weekly-ideas",
      ...
    },
    {
      "id": "<auto>",
      "name": "<store>-weekly-meta-review",
      ...
    },
    {
      "id": "<auto>",
      "name": "<store>-watchdog-conversion",
      "no_agent": true,
      "script": "<store>-watchdog-conversion.sh",
      ...
    }
  ]
}
```

### Key fields per cron

| Field | Description |
|---|---|
| `id` | Auto-generated UUID (at cron creation) |
| `name` | Human-readable name (prefixed by your store handle) |
| `prompt` | Template of the prompt sent to the agent (with placeholders to fill) |
| `skills` | List of skills to load at session start |
| `skill` | Main skill (the first in the list) |
| `no_agent` | If `true`: runs a bash script directly (no LLM session) |
| `schedule.expr` | Standard cron expression (5 fields: min hour day month dow) |
| `enabled` | Enable/disable without deleting |
| `deliver` | `telegram` or `email` (prefer telegram, email handled by inline snippet) |
| `workdir` | Working directory for the terminal tool (= $HERMES_WORKSPACE) |

---

## 5. `STANDING-CORE.md` + `STORE-BRAND.md`

### 2-file architecture

| File | Location | Contents |
|---|---|---|
| `STANDING-CORE.md` | `/root/.hermes/standing/` | 11 universal rules (framework) |
| `STORE-BRAND.md` | `$HERMES_WORKSPACE/` | 3 brand-specific rules (user customizes) |

The `inject-standing.sh` hook concatenates the two and injects them into the context of every session.

### Concatenation pattern

```bash
#!/bin/bash
STANDING_CORE=$(cat /root/.hermes/standing/STANDING-CORE.md)
STORE_BRAND=$([ -f "$HERMES_WORKSPACE/STORE-BRAND.md" ] && cat "$HERMES_WORKSPACE/STORE-BRAND.md" || echo "")
COMBINED="$STANDING_CORE

## Brand-Specific Rules
$STORE_BRAND"
jq -n --arg s "$COMBINED" '{"continue": true, "context_injection": $s}'
```

See [`AUTOMATION.md`](./AUTOMATION.md) section 3 for details of the 14 rules.

---

## 6. `MISSION.md` (workspace)

Template provided in [`../config/MISSION.md.template`](../config/MISSION.md.template).

Typical sections:
- Narrative mission specific to YOUR store
- Store identity (catalog, plan, currency, timezone)
- Monitored sources
- Operational rhythm (4 crons)
- Autonomy levels (points to STORE-BRAND.md)
- Self-improvement mechanisms
- Verification

See [`../examples/azamoul/MISSION.md`](../examples/azamoul/MISSION.md) for a complete example (~19KB).

---

## 7. `MEMORY.md` (workspace)

Template provided in [`../config/MEMORY.md.template`](../config/MEMORY.md.template).

Typical sections:
- Store (handle, domain, plan, currency, timezone, categories)
- VPS stack
- LLM model used
- Credentials summary (names only, never values)
- Current phase (`HERMES_MODE=test|prod`)
- Autonomy levels (summary)
- Open decisions

Keep compact (< 60 lines recommended). For detailed history, use a separate `MEMORY-HISTORY.md`.

---

## 8. `cultural-events.json` (workspace)

Template provided in [`../config/cultural-events.json.template`](../config/cultural-events.json.template).

Format:

```json
{
  "events": [
    {
      "name": "Black Friday",
      "date": "2026-11-27",
      "lead_days": 30,
      "category": "commercial",
      "campaign_type": "both",
      "vocabulary_boost": ["promo", "réduction", "exclusif"]
    },
    {
      "name": "Fête des mères",
      "date": "2026-05-31",
      "lead_days": 21,
      "category": "saisonnier",
      "campaign_type": "email",
      "vocabulary_boost": ["maman", "cadeau", "amour"]
    }
  ]
}
```

The `shopify-cultural-calendar` skill reads this file programmatically and triggers the corresponding workflows (D-21 advance-notice alert, campaign proposals, etc.).

See [`../examples/azamoul/cultural-events.json`](../examples/azamoul/cultural-events.json) for a complete example (Amazigh calendar).

---

## 9. Session initialization order

When Hermes starts a session (cron or interactive):

1. **`on_session_start` hook** runs → injects `STANDING-CORE.md` + `STORE-BRAND.md` into context
2. **Loading skills**: skills declared in the cron are loaded (their SKILL.md becomes accessible to the agent)
3. **Mandatory pre-reading**: the agent reads MISSION.md + MEMORY.md + last 7 entries of learnings.md
4. **Cron prompt execution**: the agent executes the mission following the autonomy levels
5. **`post_tool_call` hook**: every mutative action is auto-logged in learnings.md
6. **Deliverables**: generation of reports/ files + Telegram send + email send (via Python snippet with `EMAIL_SMTP_OK` sentinel)
7. **Cron status update** in `jobs.json` (`last_run_at`, `last_status`)

---

## 10. Customization for your store

At install (follow [`../GETTING-STARTED.md`](../GETTING-STARTED.md)), you copy the templates from `config/` and fill them with your values:

| Template | Destination |
|---|---|
| `config/.env.template` | `/root/.hermes/.env` (chmod 600) |
| `config/STANDING-CORE.md.template` | `/root/.hermes/standing/STANDING-CORE.md` |
| `config/cron-jobs.json.template` | `/root/.hermes/cron/jobs.json` |
| `config/MISSION.md.template` | `$HERMES_WORKSPACE/MISSION.md` |
| `config/STORE-BRAND.md.template` | `$HERMES_WORKSPACE/STORE-BRAND.md` |
| `config/MEMORY.md.template` | `$HERMES_WORKSPACE/MEMORY.md` |
| `config/cultural-events.json.template` | `$HERMES_WORKSPACE/cultural-events.json` |

The framework stays generic. Only user-facing files evolve with your store.
