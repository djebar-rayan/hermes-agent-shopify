# VPS Setup — Specifications & installation

> Technical specifications of the recommended VPS host to run Hermes 24/7.
>
> For application setup (skills, crons, workspace): see [`../GETTING-STARTED.md`](../GETTING-STARTED.md).

---

## 1. Minimum specifications

| Component | Min | Recommended | Why |
|---|---|---|---|
| OS | Ubuntu 22.04 | Ubuntu 24.04 LTS | Hermes compat + recent packages |
| RAM | 2 GB | 4 GB | OpenViking + Hermes + concurrent LLM sessions |
| CPU | 1 vCPU | 2 vCPU | Parallel crons + image processing |
| Storage | 20 GB | 40 GB | Workspace + cache + theme-backups + logs |
| Bandwidth | 1 TB/month | Unlimited | API calls + monitoring scrape |
| Typical cost | €5/month | €10/month | OVH, Hetzner, DigitalOcean |

---

## 2. Software stack

| Component | Version | How to install |
|---|---|---|
| Ubuntu LTS | 24.04 | `apt update && apt upgrade` |
| Python | 3.11 (venv) + 3.12 (system) | `apt install python3.11 python3.11-venv` |
| Node.js | 20+ | `curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt install -y nodejs` |
| Shopify CLI | 3.94+ | `npm install -g @shopify/cli @shopify/theme` |
| OpenViking | 0.3.16 | See [OpenViking](https://openviking.dev) instructions |
| Hermes Agent | v0.14.0 | `pip install hermes-cli` (in venv `/usr/local/lib/hermes-agent`) |
| jq | latest | `apt install -y jq` |
| git | latest | `apt install -y git` |

---

## 3. Hermes Agent — configuration

### Directory structure

```
/root/.hermes/                          [framework — shared between all instances]
├── config.yaml                         (Hermes config: hooks, model, etc.)
├── .env                                (secrets — chmod 600)
├── standing/
│   └── STANDING-CORE.md                (11 universal rules)
├── hooks/
│   ├── inject-standing.sh
│   └── log-learning.sh
├── lib/
│   ├── theme.sh
│   └── klaviyo-fetch.sh
├── skills/                             (25 SKILL.md)
├── cron/
│   └── jobs.json                       (4 crons)
├── memories/
│   ├── MEMORY.md
│   └── USER.md
└── cache/
    └── klaviyo/                        (6h cache)
```

```
$HERMES_WORKSPACE/                       [user-facing — store instance]
├── MISSION.md
├── STORE-BRAND.md
├── brand-knowledge.md
├── cultural-events.json
├── MEMORY.md
├── learnings.md
├── reports/
├── meta-reviews/
├── batches/
├── campaigns/
├── theme-backups/
├── audits/
└── shopify-automation-toolkit/
```

### Key env variables (cf. `config/.env.template`)

```bash
# === Store ===
SHOPIFY_STORE=<store_handle>            # without .myshopify.com
SHOP_BRAND_NAME=<Display Name>
SHOP_DOMAIN=<store>.com
HERMES_WORKSPACE=/root/<store>-shopify
HERMES_MODE=test                        # test | prod
LIVE_THEME_ID=<theme_id>

# === Shopify Auth ===
SHOPIFY_CLI_THEME_TOKEN=shptka_***      # via Theme Access app

# === LLM ===
OPENROUTER_API_KEY=sk-or-v1-***
GEMINI_API_KEY=AIza***
OPENAI_API_KEY=sk-proj-***              # optional

# === Email ===
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=<your_email>
EMAIL_SMTP_PASSWORD=***                 # Gmail App Password 16 chars
EMAIL_FROM=<your_email>
EMAIL_TO=<your_email>
HERMES_TEST_EMAIL_TO=<your_email>

# === Telegram ===
TELEGRAM_BOT_TOKEN=***
TELEGRAM_ALLOWED_USERS=<user_id>
TELEGRAM_HOME_CHANNEL=<user_id>

# === Optional ===
KLAVIYO_API_KEY=pk_***
FIRECRAWL_API_KEY=fc-***
GSC_SERVICE_ACCOUNT_FILE=/root/.hermes/gsc-service-account.json
GSC_SITE_URL=sc-domain:<store>.com
```

---

## 4. Step-by-step setup (recap)

For detailed setup, see [`../GETTING-STARTED.md`](../GETTING-STARTED.md).

Express summary:

1. **Provision VPS** Ubuntu 24.04 (at OVH, Hetzner, etc.)
2. **SSH config** on client side:
   ```
   Host mystore-vps
     HostName <VPS_IP>
     User root
     IdentityFile ~/.ssh/id_ed25519
   ```
3. **Install stack** (Python, Node, Shopify CLI, jq, git)
4. **Install Hermes Agent** in venv `/usr/local/lib/hermes-agent`
5. **Install OpenViking** on port 1933 (systemd service)
6. **Clone framework**: `git clone https://github.com/djebar-rayan/hermes-agent-shopify.git ~/hermes-framework`
7. **Create `$HERMES_WORKSPACE`** and copy templates from `config/`
8. **Fill `.env`** + `STORE-BRAND.md` + `MISSION.md` + `cultural-events.json`
9. **Auth Shopify CLI** + create Theme Access token
10. **Configure crons** in `/root/.hermes/cron/jobs.json`
11. **Enable v0.14 hooks**
12. **Smoke test**: `source lib/theme.sh ; theme_list`
13. **Launch Telegram gateway**: `hermes gateway run --replace`

---

## 5. Hermes config.yaml

Recommended config example:

```yaml
# /root/.hermes/config.yaml
language: fr
model:
  default: google/gemini-3.1-flash-lite-preview
  provider: openrouter
  base_url: https://openrouter.ai/api/v1
  api_mode: chat_completions
context_length: 262144
request_timeout: 1800
timezone: Europe/Paris

memory:
  provider: openviking
  endpoint: http://localhost:1933
  char_limit: 3500
  user_char_limit: 1375

compression:
  enabled: true
  target_ratio: 0.25
  threshold: 0.6
  protect_last_n: 30

approvals:
  mode: smart
  cron_mode: deny
  timeout: 60

security:
  redact_secrets: true
  tirith_enabled: true
  tirith_fail_open: true
  tirith_timeout: 5
  allow_private_urls: false

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

# Active toolsets
toolsets:
  - hermes-cli

# For the terminal tool: env vars to pass to the subshell
toolset_terminal:
  workdir: $HERMES_WORKSPACE
  env_passthrough:
    - OPENROUTER_API_KEY
    - KLAVIYO_API_KEY
    - SHOPIFY_STORE
    - SHOPIFY_CLI_THEME_TOKEN
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
```

---

## 6. Routine maintenance

### Hermes update

```bash
source /usr/local/lib/hermes-agent/bin/activate
pip install --upgrade hermes-cli
hermes --version
```

⚠️ Test the new version on a manual cron before letting it run as an auto cron.

### Log rotation

The `log-learning` hook continuously appends to `$HERMES_WORKSPACE/learnings.md`. To avoid inflation, plan a manual rotation:

```bash
# Every 6 months, archive old entries
mv $HERMES_WORKSPACE/learnings.md $HERMES_WORKSPACE/learnings-YYYY-S1.md
touch $HERMES_WORKSPACE/learnings.md
```

### Config backup

```bash
# Back up regularly (cf. "Setup" rule)
tar -czf /tmp/hermes-backup-$(date +%Y%m%d).tar.gz \
  /root/.hermes/.env \
  /root/.hermes/config.yaml \
  /root/.hermes/cron/jobs.json \
  /root/.hermes/standing/ \
  /root/.hermes/skills/ \
  $HERMES_WORKSPACE/MISSION.md \
  $HERMES_WORKSPACE/STORE-BRAND.md \
  $HERMES_WORKSPACE/brand-knowledge.md \
  $HERMES_WORKSPACE/cultural-events.json \
  $HERMES_WORKSPACE/MEMORY.md
```

### Klaviyo cache

To force a refresh of a Klaviyo endpoint (bypass 6h cache):

```bash
rm /root/.hermes/cache/klaviyo/<endpoint>-YYYY-MM-DD-HH.json
# The next call will re-fetch from the API
```

---

## 7. VPS monitoring

### Service status

```bash
# Hermes Telegram gateway
systemctl status hermes-gateway || ps aux | grep hermes
ls -la /root/.hermes/gateway.lock /root/.hermes/gateway.pid

# OpenViking memory
systemctl status openviking
curl http://localhost:1933/health

# Crons (Hermes-managed, not crontab)
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | {name, last_status, last_run_at, next_run_at}'
```

### Cost/token insights

```bash
hermes insights --days 7
hermes insights --days 30
```

---

## 8. Troubleshooting

| Error | Probable cause | Solution |
|---|---|---|
| `SHOPIFY_STORE missing in .env` | `.env` not loaded | `set -a; . /root/.hermes/.env; set +a` |
| `Gemini Text 429` | Rate limit 10req/min | Auto retry 60s, max 3 times |
| `blockReason: OTHER` Gemini | `GEMINI_MODEL` (Flash Image) used for text | Switch to `GEMINI_TEXT_MODEL` |
| `EMAIL_FAIL` SMTP | Gmail App Password expired | Regenerate at myaccount.google.com/apppasswords |
| Expired Shopify token | OAuth lapsed | DO NOT re-auth headless — notify user to run from Windows |
| Klaviyo 401 | `KLAVIYO_API_KEY` invalid | Check that it starts with `pk_` |
| `urlRedirectCreate denied` | `write_online_store_navigation` scope missing | Defer or request re-auth with added scope |
| `themeFilesUpsert ACCESS_DENIED` | `write_themes` scope absent + no exemption | Use Theme Access token `shptka_` + `shopify theme push` |
| Telegram bot not responding | `TELEGRAM_BOT_TOKEN` invalid or gateway not running | `curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe` + restart `hermes gateway run --replace` |
| Cron `last_status: fail` | See details in Hermes logs | `tail -50 /root/.hermes/logs/*.log` |
