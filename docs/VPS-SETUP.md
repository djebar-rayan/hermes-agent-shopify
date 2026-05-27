# VPS Setup — Spécifications & installation

> Spécifications techniques de l'hôte VPS recommandé pour faire tourner Hermes 24/7.
>
> Pour le setup applicatif (skills, crons, workspace) : voir [`../GETTING-STARTED.md`](../GETTING-STARTED.md).

---

## 1. Spécifications minimales

| Composant | Min | Recommandé | Pourquoi |
|---|---|---|---|
| OS | Ubuntu 22.04 | Ubuntu 24.04 LTS | Compat Hermes + paquets récents |
| RAM | 2 GB | 4 GB | OpenViking + Hermes + sessions LLM concurrentes |
| CPU | 1 vCPU | 2 vCPU | Crons en parallèle + traitement images |
| Stockage | 20 GB | 40 GB | Workspace + cache + theme-backups + logs |
| Bande passante | 1 TB/mois | Illimitée | Calls API + scrape veille |
| Coût typique | 5€/mois | 10€/mois | OVH, Hetzner, DigitalOcean |

---

## 2. Stack logicielle

| Composant | Version | Comment installer |
|---|---|---|
| Ubuntu LTS | 24.04 | `apt update && apt upgrade` |
| Python | 3.11 (venv) + 3.12 (system) | `apt install python3.11 python3.11-venv` |
| Node.js | 20+ | `curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt install -y nodejs` |
| Shopify CLI | 3.94+ | `npm install -g @shopify/cli @shopify/theme` |
| OpenViking | 0.3.16 | Cf. instructions [OpenViking](https://openviking.dev) |
| Hermes Agent | v0.14.0 | `pip install hermes-cli` (dans venv `/usr/local/lib/hermes-agent`) |
| jq | latest | `apt install -y jq` |
| git | latest | `apt install -y git` |

---

## 3. Hermes Agent — configuration

### Structure de répertoires

```
/root/.hermes/                          [framework — partagé entre toutes les instances]
├── config.yaml                         (config Hermes : hooks, model, etc.)
├── .env                                (secrets — chmod 600)
├── standing/
│   └── STANDING-CORE.md                (11 règles universelles)
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
    └── klaviyo/                        (cache 6h)
```

```
$HERMES_WORKSPACE/                       [user-facing — instance boutique]
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

### Variables d'env clés (cf. `config/.env.template`)

```bash
# === Boutique ===
SHOPIFY_STORE=<store_handle>            # sans .myshopify.com
SHOP_BRAND_NAME=<Display Name>
SHOP_DOMAIN=<store>.com
HERMES_WORKSPACE=/root/<store>-shopify
HERMES_MODE=test                        # test | prod
LIVE_THEME_ID=<theme_id>

# === Shopify Auth ===
SHOPIFY_CLI_THEME_TOKEN=shptka_***      # via app Theme Access

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

# === Optionnels ===
KLAVIYO_API_KEY=pk_***
FIRECRAWL_API_KEY=fc-***
GSC_SERVICE_ACCOUNT_FILE=/root/.hermes/gsc-service-account.json
GSC_SITE_URL=sc-domain:<store>.com
```

---

## 4. Setup étape par étape (récap)

Pour le setup détaillé, voir [`../GETTING-STARTED.md`](../GETTING-STARTED.md).

Résumé express :

1. **Provision VPS** Ubuntu 24.04 (chez OVH, Hetzner, etc.)
2. **SSH config** côté client :
   ```
   Host mystore-vps
     HostName <VPS_IP>
     User root
     IdentityFile ~/.ssh/id_ed25519
   ```
3. **Install stack** (Python, Node, Shopify CLI, jq, git)
4. **Install Hermes Agent** dans venv `/usr/local/lib/hermes-agent`
5. **Install OpenViking** sur port 1933 (systemd service)
6. **Clone framework** : `git clone https://github.com/djebar-rayan/hermes-agent-shopify.git ~/hermes-framework`
7. **Créer `$HERMES_WORKSPACE`** et copier les templates depuis `config/`
8. **Remplir `.env`** + `STORE-BRAND.md` + `MISSION.md` + `cultural-events.json`
9. **Auth Shopify CLI** + créer Theme Access token
10. **Configurer crons** dans `/root/.hermes/cron/jobs.json`
11. **Activer hooks v0.14**
12. **Smoke test** : `source lib/theme.sh ; theme_list`
13. **Lancer gateway Telegram** : `hermes gateway run --replace`

---

## 5. Hermes config.yaml

Exemple de config recommandée :

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

# Toolsets actifs
toolsets:
  - hermes-cli

# Pour le tool terminal : env vars à passer au sous-shell
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

## 6. Maintenance courante

### Mise à jour Hermes

```bash
source /usr/local/lib/hermes-agent/bin/activate
pip install --upgrade hermes-cli
hermes --version
```

⚠️ Tester la nouvelle version sur un cron manuel avant de la laisser tourner en cron auto.

### Rotation des logs

Le hook `log-learning` append en continu à `$HERMES_WORKSPACE/learnings.md`. Pour éviter l'inflation, prévoir une rotation manuelle :

```bash
# Tous les 6 mois, archiver les anciennes entrées
mv $HERMES_WORKSPACE/learnings.md $HERMES_WORKSPACE/learnings-YYYY-S1.md
touch $HERMES_WORKSPACE/learnings.md
```

### Backup config

```bash
# Sauvegarder régulièrement (cf. règle "Mise en place")
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

### Cache Klaviyo

Pour forcer un refresh d'un endpoint Klaviyo (bypass cache 6h) :

```bash
rm /root/.hermes/cache/klaviyo/<endpoint>-YYYY-MM-DD-HH.json
# Le prochain appel re-fetchera depuis l'API
```

---

## 7. Monitoring du VPS

### Status services

```bash
# Hermes gateway Telegram
systemctl status hermes-gateway || ps aux | grep hermes
ls -la /root/.hermes/gateway.lock /root/.hermes/gateway.pid

# OpenViking memory
systemctl status openviking
curl http://localhost:1933/health

# Crons (Hermes-managed, pas crontab)
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | {name, last_status, last_run_at, next_run_at}'
```

### Insights coût/tokens

```bash
hermes insights --days 7
hermes insights --days 30
```

---

## 8. Troubleshooting

| Erreur | Cause probable | Solution |
|---|---|---|
| `SHOPIFY_STORE missing in .env` | `.env` non chargé | `set -a; . /root/.hermes/.env; set +a` |
| `Gemini Text 429` | Rate limit 10req/min | Retry auto 60s, max 3 fois |
| `blockReason: OTHER` Gemini | `GEMINI_MODEL` (Flash Image) utilisé pour texte | Switch sur `GEMINI_TEXT_MODEL` |
| `EMAIL_FAIL` SMTP | App Password Gmail expiré | Regénérer sur myaccount.google.com/apppasswords |
| Token Shopify expiré | OAuth caduc | NE PAS réauth headless — notifier user pour run depuis Windows |
| Klaviyo 401 | `KLAVIYO_API_KEY` invalide | Vérifier qu'elle commence par `pk_` |
| `urlRedirectCreate denied` | Scope `write_online_store_navigation` manquant | Différer ou demander réauth avec scope ajouté |
| `themeFilesUpsert ACCESS_DENIED` | Scope `write_themes` absent + pas d'exemption | Utiliser Theme Access token `shptka_` + `shopify theme push` |
| Telegram bot ne répond pas | `TELEGRAM_BOT_TOKEN` invalide ou gateway pas lancé | `curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe` + relancer `hermes gateway run --replace` |
| Cron `last_status: fail` | Voir détail dans logs Hermes | `tail -50 /root/.hermes/logs/*.log` |
