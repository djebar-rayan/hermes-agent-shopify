# Getting Started — Install Hermes on Your Shopify Store

> Step-by-step guide to configure Hermes Agent on a new Shopify store. Plan ~2-3 hours for a full first-time setup, or ~30 min if you follow the quick guide at the bottom of the page.

---

## 📋 Prerequisites

| Component | Min version | Why |
|---|---|---|
| **Ubuntu VPS** | 24.04+ | Hermes 24/7 host (~€5/month on OVH or similar) |
| **Python** | 3.11+ | Hermes runtime |
| **Node.js** | 20+ | Shopify automation toolkit + helpers |
| **Shopify CLI** | 3.94+ | GraphQL API + theme push |
| **Shopify store** | Any plan | Source of truth |
| **OpenRouter account** | — | LLM (~$20/month pay-as-you-go) |
| **Telegram bot** | — | `/yes` validation for actions |
| **Gmail App Password** | — | SMTP for deliverables |

Optional (recommended):
- Klaviyo API key (read-only) — emailing section
- Gemini API key — image generation + vision
- Firecrawl API key — competitive intelligence
- Google Search Console service account — SEO

---

## 🚀 Step-by-step Setup

### 1. Clone the repo

```bash
git clone https://github.com/djebar-rayan/hermes-agent-shopify.git ~/hermes-framework
cd ~/hermes-framework
```

### 2. Install Hermes Agent

Follow the official Hermes documentation (Anthropic Agent SDK). On Ubuntu:

```bash
# Python venv
python3.11 -m venv /usr/local/lib/hermes-agent
source /usr/local/lib/hermes-agent/bin/activate
pip install hermes-cli  # or install from source depending on your license
hermes --version  # must display 0.14.0+
```

### 3. Install the OpenViking memory provider

```bash
# Local service on port 1933 — cross-session RAG embedding
curl -L https://openviking.dev/install.sh | bash
# OR compile from source if using an alternative distribution
systemctl enable --now openviking
curl http://localhost:1933/health  # must return {"status":"healthy"}
```

### 4. Create your store workspace

```bash
# Choose a short name for your store
export STORE_HANDLE=mystore  # replace with your Shopify handle
export HERMES_WORKSPACE=/root/${STORE_HANDLE}-shopify
mkdir -p $HERMES_WORKSPACE
cd $HERMES_WORKSPACE

# Copy the templates from the framework
cp ~/hermes-framework/config/MISSION.md.template MISSION.md
cp ~/hermes-framework/config/STORE-BRAND.md.template STORE-BRAND.md
cp ~/hermes-framework/config/MEMORY.md.template MEMORY.md
cp ~/hermes-framework/config/cultural-events.json.template cultural-events.json
touch learnings.md brand-knowledge.md
mkdir -p reports meta-reviews batches campaigns theme-backups audits
```

### 5. Configure `.env` (at `/root/.hermes/.env`)

```bash
cp ~/hermes-framework/config/.env.template /root/.hermes/.env
chmod 600 /root/.hermes/.env
nano /root/.hermes/.env
```

Minimum variables to fill in:

```bash
# === STORE ===
SHOPIFY_STORE=mystore                              # .myshopify.com handle (without the suffix)
SHOP_BRAND_NAME=MyStore                            # displayed name
SHOP_DOMAIN=mystore.com                            # custom domain
HERMES_WORKSPACE=/root/mystore-shopify             # your workspace
HERMES_MODE=test                                   # test (apply+rollback) | prod (persistent)
HERMES_TEST_EMAIL_TO=you@gmail.com                 # recipient email in test mode
LIVE_THEME_ID=185550995780                         # live theme ID (see below)

# === SHOPIFY ===
SHOPIFY_CLI_THEME_TOKEN=shptka_...                 # Theme Access token (see below)

# === LLM ===
OPENROUTER_API_KEY=sk-or-v1-...                    # primary
OPENAI_API_KEY=sk-proj-...                         # fallback (optional)
GEMINI_API_KEY=AIza...                             # image gen (optional)

# === EMAIL ===
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=you@gmail.com
EMAIL_SMTP_PASSWORD=<16-char Gmail App Password>   # myaccount.google.com/apppasswords
EMAIL_FROM=you@gmail.com
EMAIL_TO=you@gmail.com

# === TELEGRAM ===
TELEGRAM_BOT_TOKEN=<bot_token>                     # via @BotFather
TELEGRAM_ALLOWED_USERS=<your_user_id>              # via @userinfobot
TELEGRAM_HOME_CHANNEL=<your_user_id>

# === OPTIONAL ===
KLAVIYO_API_KEY=pk_...                             # read-only emailing
FIRECRAWL_API_KEY=fc-...                           # competitive intelligence
GSC_SERVICE_ACCOUNT_FILE=/root/.hermes/gsc-service-account.json
GSC_SITE_URL=sc-domain:mystore.com
```

### 6. Authenticate the Shopify CLI

```bash
shopify store auth --store mystore.myshopify.com \
  --scopes read_products,write_products,read_content,write_content,read_themes,write_files,read_customers,read_orders
```

This command opens the browser for validation. Once auth is OK, test:

```bash
shopify store info  # must display your store
shopify theme list  # lists themes
```

Note the `LIVE_THEME_ID` (role `main`) and copy it into `.env`.

### 7. Create a Theme Access token

For headless theme modifications, the `write_themes` OAuth scope may be unavailable. The workaround: a Theme Access token (`shptka_...`).

1. Go to `https://admin.shopify.com/store/mystore/apps/theme-access`
2. Install the Theme Access app if not already done
3. Generate a password with your email
4. Receive `shptka_xxxxx` by email
5. Add to `.env` under `SHOPIFY_CLI_THEME_TOKEN=shptka_...`

### 8. Configure your brand in `STORE-BRAND.md`

Edit `$HERMES_WORKSPACE/STORE-BRAND.md` to describe:
- **Required vocabulary**: the keywords that MUST appear in any generated content (your cultural universe, brand name, USP)
- **Event calendar**: events important to your brand (see `cultural-events.json` for the structured format)
- **Autonomy levels**: what Hermes can do on its own (🟢), what it must propose to you (🟡), what it never does (🔴)
- **Competitors**: list 5-10 competitors with their niche

See [`examples/azamoul/STORE-BRAND.md`](./examples/azamoul/STORE-BRAND.md) for a complete example.

### 9. Fill in `MISSION.md`

Adapt the `MISSION.md.template` to your specific mission. Keep the pattern (autonomy levels, cadence, anti-hallucination) but personalize the details.

### 10. Configure the 4 crons

Edit `cron-jobs.json.template`:

```bash
cp ~/hermes-framework/config/cron-jobs.json.template /root/.hermes/cron/jobs.json
nano /root/.hermes/cron/jobs.json
```

Replace the placeholders:
- `<STORE_NAME>` → your handle (e.g. `mystore`)
- `<TELEGRAM_HOME_CHANNEL>` → your Telegram user ID
- `<EMAIL_TO>` → your email
- `<HERMES_WORKSPACE>` → `/root/mystore-shopify`

The 4 crons:
- `mystore-weekly-perf-report` (Monday 9am)
- `mystore-weekly-ideas` (Saturday 10am)
- `mystore-weekly-meta-review` (Sunday 8pm)
- `mystore-watchdog-conversion` (every 6h)

### 11. Enable v0.14 hooks

```bash
# In /root/.hermes/config.yaml, add:
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

The hook scripts are provided in the framework's `hooks/` directory.

### 12. Configure STANDING (the 14 rules)

```bash
# Combine STANDING-CORE (11 universal rules) with your STORE-BRAND (3 brand-specific)
cp ~/hermes-framework/config/STANDING-CORE.md.template /root/.hermes/standing/STANDING-CORE.md
# The inject-standing.sh hook will concatenate STANDING-CORE + $HERMES_WORKSPACE/STORE-BRAND.md
```

### 13. Framework smoke test

```bash
# Test theme.sh
source /root/.hermes/.env
source ~/hermes-framework/lib/theme.sh
theme_check_env  # must return 0
theme_list       # must list your Shopify themes
theme_safety_level "assets/theme.css"  # must return "green"

# Test klaviyo-fetch (if Klaviyo is configured)
~/hermes-framework/lib/klaviyo-fetch.sh flows  # must return JSON
```

### 14. Start the Telegram gateway

```bash
hermes gateway run --replace
```

Check in Telegram that the bot responds (send `/start` to the bot).

### 15. First dry-run

Before the first real cron, do a manual dry-run:

```bash
hermes chat --skill shopify-baseline-kpi-fetch
# Must fetch KPIs without modifying anything
```

---

## ✅ Final Verification

When setup is complete, you should have:

- [ ] `/root/.hermes/.env` filled in (chmod 600)
- [ ] `/root/.hermes/cron/jobs.json` with 4 configured crons
- [ ] `/root/.hermes/standing/STANDING-CORE.md` in place
- [ ] `$HERMES_WORKSPACE/MISSION.md`, `STORE-BRAND.md`, `cultural-events.json` filled in
- [ ] `shopify store info` works
- [ ] `theme_list` returns your themes
- [ ] OpenViking healthy on port 1933
- [ ] Telegram gateway up + bot responds
- [ ] v0.14 hooks enabled
- [ ] `learnings.md` initialized (empty or with header)

---

## 🆘 Troubleshooting

### `EMAIL_SMTP_OK` doesn't appear after send

Gmail App Password expired or revoked. Regenerate it at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

### `shopify theme push` returns ACCESS_DENIED

The `write_themes` OAuth scope is likely missing. Create a Theme Access token (step 7) and use `SHOPIFY_CLI_THEME_TOKEN=shptka_...`.

### `theme_check_env` fails

Make sure `SHOPIFY_CLI_THEME_TOKEN`, `SHOPIFY_STORE`, and `LIVE_THEME_ID` are in `.env` and that `source /root/.hermes/.env` actually loaded the vars.

### Telegram bot doesn't respond

Verify `TELEGRAM_BOT_TOKEN` is valid via `curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe`. Check that `TELEGRAM_ALLOWED_USERS` matches your user ID.

---

## ⚡ Quick Guide (30 min)

For experienced users:

```bash
# 1. Clone + workspace
git clone https://github.com/djebar-rayan/hermes-agent-shopify.git ~/hermes-framework
export STORE_HANDLE=mystore
export HERMES_WORKSPACE=/root/${STORE_HANDLE}-shopify
mkdir -p $HERMES_WORKSPACE
cd $HERMES_WORKSPACE

# 2. Copy templates
cp ~/hermes-framework/config/*.template .
cp ~/hermes-framework/config/.env.template /root/.hermes/.env

# 3. Edit .env + fill in STORE-BRAND.md + MISSION.md + cultural-events.json
# 4. shopify store auth ... + Theme Access token
# 5. cron-jobs.json + STANDING-CORE.md
# 6. v0.14 hooks
# 7. Smoke test: source lib/theme.sh ; theme_list
# 8. hermes gateway run --replace
```

For details on each step, see the full section above.

---

## 📖 Further Reading

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — understand the conceptual architecture
- [`docs/SKILLS-REFERENCE.md`](./docs/SKILLS-REFERENCE.md) — catalog of the 25 skills
- [`docs/AUTOMATION.md`](./docs/AUTOMATION.md) — understand the 4 crons + hooks
- [`examples/azamoul/`](./examples/azamoul/) — see Hermes in production on a real store
