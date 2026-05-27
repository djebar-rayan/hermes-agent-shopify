# Getting Started — Installer Hermes sur ta boutique Shopify

> Guide pas-à-pas pour configurer Hermes Agent sur une nouvelle boutique Shopify. Compte ~2-3 heures pour un premier setup complet, ou ~30 min si tu suis le guide rapide en bas de page.

---

## 📋 Pré-requis

| Composant | Version min | Pourquoi |
|---|---|---|
| **VPS Ubuntu** | 24.04+ | Hôte Hermes 24/7 (compte ~5€/mois OVH ou similaire) |
| **Python** | 3.11+ | Runtime Hermes |
| **Node.js** | 20+ | Toolkit Shopify automation + helpers |
| **Shopify CLI** | 3.94+ | API GraphQL + theme push |
| **Boutique Shopify** | Tous plans | Source de vérité |
| **OpenRouter account** | — | LLM (~20$/mois en pay-as-you-go) |
| **Telegram bot** | — | Validation `/yes` des actions |
| **Gmail App Password** | — | SMTP pour livrables |

Optionnels (recommandés) :
- Klaviyo API key (read-only) — section emailing
- Gemini API key — image generation + vision
- Firecrawl API key — veille concurrentielle
- Google Search Console service account — SEO

---

## 🚀 Setup étape par étape

### 1. Cloner le repo

```bash
git clone https://github.com/djebar-rayan/hermes-agent-shopify.git ~/hermes-framework
cd ~/hermes-framework
```

### 2. Installer Hermes Agent

Suivre la documentation officielle Hermes (Agent SDK Anthropic). Sur Ubuntu :

```bash
# Python venv
python3.11 -m venv /usr/local/lib/hermes-agent
source /usr/local/lib/hermes-agent/bin/activate
pip install hermes-cli  # ou install depuis source selon ta licence
hermes --version  # doit afficher 0.14.0+
```

### 3. Installer OpenViking memory provider

```bash
# Service local sur port 1933 — embedding RAG cross-session
curl -L https://openviking.dev/install.sh | bash
# OU compile depuis source si distribution alternative
systemctl enable --now openviking
curl http://localhost:1933/health  # doit retourner {"status":"healthy"}
```

### 4. Créer le workspace de ta boutique

```bash
# Choisis un nom court pour ta boutique
export STORE_HANDLE=mystore  # remplace par ton handle Shopify
export HERMES_WORKSPACE=/root/${STORE_HANDLE}-shopify
mkdir -p $HERMES_WORKSPACE
cd $HERMES_WORKSPACE

# Copier les templates depuis le framework
cp ~/hermes-framework/config/MISSION.md.template MISSION.md
cp ~/hermes-framework/config/STORE-BRAND.md.template STORE-BRAND.md
cp ~/hermes-framework/config/MEMORY.md.template MEMORY.md
cp ~/hermes-framework/config/cultural-events.json.template cultural-events.json
touch learnings.md brand-knowledge.md
mkdir -p reports meta-reviews batches campaigns theme-backups audits
```

### 5. Configurer `.env` (à `/root/.hermes/.env`)

```bash
cp ~/hermes-framework/config/.env.template /root/.hermes/.env
chmod 600 /root/.hermes/.env
nano /root/.hermes/.env
```

Variables minimales à remplir :

```bash
# === BOUTIQUE ===
SHOPIFY_STORE=mystore                              # handle .myshopify.com (sans le suffixe)
SHOP_BRAND_NAME=MyStore                            # nom affiché
SHOP_DOMAIN=mystore.com                            # domaine custom
HERMES_WORKSPACE=/root/mystore-shopify             # ton workspace
HERMES_MODE=test                                   # test (apply+rollback) | prod (persistant)
HERMES_TEST_EMAIL_TO=you@gmail.com                 # email destinataire en mode test
LIVE_THEME_ID=185550995780                         # ID du thème live (voir ci-dessous)

# === SHOPIFY ===
SHOPIFY_CLI_THEME_TOKEN=shptka_...                 # Theme Access token (voir ci-dessous)

# === LLM ===
OPENROUTER_API_KEY=sk-or-v1-...                    # principal
OPENAI_API_KEY=sk-proj-...                         # fallback (optionnel)
GEMINI_API_KEY=AIza...                             # image gen (optionnel)

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

# === OPTIONNELS ===
KLAVIYO_API_KEY=pk_...                             # read-only emailing
FIRECRAWL_API_KEY=fc-...                           # veille concurrentielle
GSC_SERVICE_ACCOUNT_FILE=/root/.hermes/gsc-service-account.json
GSC_SITE_URL=sc-domain:mystore.com
```

### 6. Authentifier Shopify CLI

```bash
shopify store auth --store mystore.myshopify.com \
  --scopes read_products,write_products,read_content,write_content,read_themes,write_files,read_customers,read_orders
```

Cette commande ouvre le browser pour validation. Une fois auth OK, tester :

```bash
shopify store info  # doit afficher ta boutique
shopify theme list  # liste les thèmes
```

Note le `LIVE_THEME_ID` (rôle `main`) et reporte-le dans `.env`.

### 7. Créer un Theme Access token

Pour les modifications de thème en headless, le scope OAuth `write_themes` peut être indisponible. Solution : Theme Access token (`shptka_...`).

1. Va sur `https://admin.shopify.com/store/mystore/apps/theme-access`
2. Installe l'app Theme Access si pas déjà fait
3. Génère un password avec ton email
4. Reçois `shptka_xxxxx` par email
5. Reporte dans `.env` sous `SHOPIFY_CLI_THEME_TOKEN=shptka_...`

### 8. Configurer ta marque dans `STORE-BRAND.md`

Édite `$HERMES_WORKSPACE/STORE-BRAND.md` pour décrire :
- **Vocabulaire obligatoire** : les mots-clés qui DOIVENT apparaître dans tout contenu généré (ton univers culturel, le nom de la marque, ton USP)
- **Calendrier événementiel** : événements importants pour ta marque (cf. `cultural-events.json` pour le format structuré)
- **Niveaux d'autonomie** : ce que Hermes peut faire seul (🟢), ce qu'il doit te proposer (🟡), ce qu'il ne fait jamais (🔴)
- **Concurrents** : liste de 5-10 concurrents avec leur niche

Voir [`examples/azamoul/STORE-BRAND.md`](./examples/azamoul/STORE-BRAND.md) pour un exemple complet.

### 9. Remplir `MISSION.md`

Adapte le template `MISSION.md.template` avec ta mission spécifique. Garde le pattern (niveaux autonomie, rythme, anti-hallucination) mais personnalise les détails.

### 10. Configurer les 4 crons

Édite `cron-jobs.json.template` :

```bash
cp ~/hermes-framework/config/cron-jobs.json.template /root/.hermes/cron/jobs.json
nano /root/.hermes/cron/jobs.json
```

Remplace les placeholders :
- `<STORE_NAME>` → ton handle (ex: `mystore`)
- `<TELEGRAM_HOME_CHANNEL>` → ton user ID Telegram
- `<EMAIL_TO>` → ton email
- `<HERMES_WORKSPACE>` → `/root/mystore-shopify`

Les 4 crons :
- `mystore-weekly-perf-report` (lundi 9h)
- `mystore-weekly-ideas` (samedi 10h)
- `mystore-weekly-meta-review` (dimanche 20h)
- `mystore-watchdog-conversion` (toutes 6h)

### 11. Activer les hooks v0.14

```bash
# Dans /root/.hermes/config.yaml, ajouter :
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

Les scripts hook sont fournis dans `hooks/` du framework.

### 12. Configurer STANDING (les 14 règles)

```bash
# Combine STANDING-CORE (11 règles universelles) avec ton STORE-BRAND (3 brand-specific)
cp ~/hermes-framework/config/STANDING-CORE.md.template /root/.hermes/standing/STANDING-CORE.md
# Le hook inject-standing.sh va concaténer STANDING-CORE + $HERMES_WORKSPACE/STORE-BRAND.md
```

### 13. Smoke test du framework

```bash
# Test theme.sh
source /root/.hermes/.env
source ~/hermes-framework/lib/theme.sh
theme_check_env  # doit retourner 0
theme_list       # doit lister tes thèmes Shopify
theme_safety_level "assets/theme.css"  # doit retourner "green"

# Test klaviyo-fetch (si Klaviyo configuré)
~/hermes-framework/lib/klaviyo-fetch.sh flows  # doit retourner JSON
```

### 14. Lancer le gateway Telegram

```bash
hermes gateway run --replace
```

Vérifier dans Telegram que le bot répond (envoie `/start` au bot).

### 15. Premier dry-run

Avant le premier vrai cron, fais un dry-run manuel :

```bash
hermes chat --skill shopify-baseline-kpi-fetch
# Doit fetcher les KPI sans rien modifier
```

---

## ✅ Vérification finale

Quand le setup est complet, tu devrais avoir :

- [ ] `/root/.hermes/.env` rempli (chmod 600)
- [ ] `/root/.hermes/cron/jobs.json` avec 4 crons paramétrés
- [ ] `/root/.hermes/standing/STANDING-CORE.md` en place
- [ ] `$HERMES_WORKSPACE/MISSION.md`, `STORE-BRAND.md`, `cultural-events.json` remplis
- [ ] `shopify store info` fonctionne
- [ ] `theme_list` retourne tes thèmes
- [ ] OpenViking healthy sur port 1933
- [ ] Gateway Telegram up + bot répond
- [ ] Hooks v0.14 activés
- [ ] `learnings.md` initialisé (vide ou avec header)

---

## 🆘 Troubleshooting

### `EMAIL_SMTP_OK` n'apparaît pas après send

App Password Gmail expiré ou révoqué. Regénère sur [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

### `shopify theme push` retourne ACCESS_DENIED

Le scope OAuth `write_themes` est probablement absent. Crée un Theme Access token (étape 7) et utilise `SHOPIFY_CLI_THEME_TOKEN=shptka_...`.

### `theme_check_env` échoue

Vérifier que `SHOPIFY_CLI_THEME_TOKEN`, `SHOPIFY_STORE`, et `LIVE_THEME_ID` sont bien dans `.env` et que `source /root/.hermes/.env` a bien chargé les vars.

### Telegram bot ne répond pas

Vérifier `TELEGRAM_BOT_TOKEN` valide via `curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe`. Vérifier `TELEGRAM_ALLOWED_USERS` matche ton user ID.

---

## ⚡ Guide rapide (30 min)

Pour les utilisateurs expérimentés :

```bash
# 1. Clone + workspace
git clone https://github.com/djebar-rayan/hermes-agent-shopify.git ~/hermes-framework
export STORE_HANDLE=mystore
export HERMES_WORKSPACE=/root/${STORE_HANDLE}-shopify
mkdir -p $HERMES_WORKSPACE
cd $HERMES_WORKSPACE

# 2. Copier templates
cp ~/hermes-framework/config/*.template .
cp ~/hermes-framework/config/.env.template /root/.hermes/.env

# 3. Éditer .env + remplir STORE-BRAND.md + MISSION.md + cultural-events.json
# 4. shopify store auth ... + Theme Access token
# 5. cron-jobs.json + STANDING-CORE.md
# 6. hooks v0.14
# 7. Smoke test : source lib/theme.sh ; theme_list
# 8. hermes gateway run --replace
```

Pour les détails de chaque étape, voir la section complète au-dessus.

---

## 📖 Lectures suivantes

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — comprendre l'architecture conceptuelle
- [`docs/SKILLS-REFERENCE.md`](./docs/SKILLS-REFERENCE.md) — catalogue des 25 skills
- [`docs/AUTOMATION.md`](./docs/AUTOMATION.md) — comprendre les 4 crons + hooks
- [`examples/azamoul/`](./examples/azamoul/) — voir Hermes en production sur une vraie boutique
