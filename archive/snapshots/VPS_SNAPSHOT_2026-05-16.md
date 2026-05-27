# Snapshot VPS Hermès Azamoul — 2026-05-16 20:14 CEST

> **Source canonique** : ces données sont issues d'une lecture SSH directe sur le VPS de production `azamoul-vps` le 16 mai 2026 à 20h14 CEST. Toute différence entre ce snapshot et un autre document doit être tranchée en faveur de ce snapshot.

## 1. Infrastructure

| Élément | Valeur réelle VPS |
|---|---|
| Hostname | `<VPS_HOSTNAME>` |
| Alias SSH (côté dev) | `azamoul-vps` |
| IP | `<VPS_IP>` |
| OS | Linux 6.8.0-111-generic x86_64 (Ubuntu 24.04 LTS) |
| Uptime au snapshot | 6 jours 6h36 |
| Load average | 0.00 / 0.00 / 0.00 (très calme) |

## 2. Services systemd actifs

```
hermes-gateway.service    user service, active running
                          ExecStart: /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
                          WorkingDirectory: /usr/local/lib/hermes-agent
                          Restart=always, RestartSec=60
                          WantedBy=default.target

openviking.service        system service (/etc/systemd/system/openviking.service)
                          ExecStart: /opt/openviking/bin/openviking-server
                          User=root, Restart=on-failure, RestartSec=10
                          (port 1933 par convention)
```

**Note critique** : `hermes-gateway` est un **user service** lancé via `systemctl --user`. OpenViking est un **system service** lancé via `systemctl` normal.

## 3. LLM réellement actif au 2026-05-16

**Source : `/root/.hermes/config.yaml`** :

```yaml
model:
  default: google/gemini-3.1-flash-lite-preview
  provider: openrouter
  context_length: 262144
  request_timeout_seconds: 1800
  base_url: https://openrouter.ai/api/v1
  api_mode: chat_completions
```

⚠️ **Incohérence détectée** : `MEMORY.md` affirme « DeepSeek v4 Pro via OpenRouter », mais `config.yaml` montre `google/gemini-3.1-flash-lite-preview`. Le swap post-Grand Run du 14 mai a bien pointé vers OpenRouter, mais le modèle final actif est **Gemini 3.1 Flash Lite Preview via OpenRouter**, pas DeepSeek. Le GUIDE doit refléter cette réalité.

## 4. Les 4 crons — IDs et état réels

| ID | Nom | Schedule | Runs effectués | Last run | Next run | Delivery |
|---|---|---|---:|---|---|---|
| `9b3edc604e0d` | `azamoul-lundi-perf` | `0 9 * * 1` | 10 | 2026-05-14 18:15 | 2026-05-18 09:00 | telegram |
| `7936943cee39` | `azamoul-samedi-ideas` | `0 10 * * 6` | 4 | 2026-05-16 10:00 | 2026-05-23 10:00 | telegram |
| `8450eef5fde8` | `azamoul-dimanche-meta` | `0 20 * * 0` | 3 | 2026-05-14 18:19 | 2026-05-17 20:00 | telegram |
| `dd4a59c29a88` | `azamoul-watchdog-conversion` | `0 */6 * * *` | 23 | 2026-05-16 18:00 | 2026-05-17 00:00 | telegram (no_agent script `azamoul-conversion-watchdog.sh`) |

**Workdir des crons LLM** : `/root/azamoul-shopify`
**Tous les crons** : `enabled: true`, `state: scheduled`, `last_status: ok`, `last_error: null`

**Particularité watchdog** : `no_agent: true` (script bash direct, pas de LLM appelé, économise quota).

## 5. Skills réellement présents sur VPS

Total répertoires `/root/.hermes/skills/` : **45**

### Skills Azamoul actifs (21, tous en `.md`, AUCUN `.PROPOSED` restant)

```
azamoul-altext-generator
azamoul-baseline-kpi-fetch
azamoul-batch-executor
azamoul-batch-rollback
azamoul-catalog-gap-analyzer
azamoul-cron-output-watcher
azamoul-cultural-calendar
azamoul-cultural-campaign-drafter
azamoul-description-enricher
azamoul-email-sender
azamoul-instagram-ideator
azamoul-instagram-publisher
azamoul-kpi-drop-watchdog
azamoul-low-conversion-diagnostic
azamoul-metatitle-generator
azamoul-product-ideator
azamoul-seo-mutation-batcher
azamoul-shopify-schema-guard
azamoul-snapshot-diff-validator
azamoul-storefront-http-verifier
azamoul-weekly-perf-report
```

⚠️ **Levée d'ambiguïté** : les 4 skills `.PROPOSED` (`seo-mutation-batcher`, `storefront-http-verifier`, `snapshot-diff-validator`, `cron-output-watcher`) ont **tous été validés et renommés en `.md`**. Il n'y a plus aucun `.PROPOSED` en attente sur le VPS au 16 mai 2026.

### Skills système Hermes (24, fournis avec Hermes Agent v0.13.0)

```
apple, autonomous-ai-agents, creative, data-science, devops, diagramming,
dogfood, domain, email, gaming, gifs, github, inference-sh, mcp, media,
mlops, note-taking, productivity, red-teaming, research, smart-home,
social-media, software-development, yuanbao
```

Plus quelques fichiers de test :
- `SKILLS-FUNCTIONAL-TEST-2026-05-13.txt`
- `SKILLS-RETEST-2026-05-13.txt`
- `SKILLS-SMOKE-TEST-2026-05-13.md`

## 6. STANDING.md — 14 règles réelles (extrait, source canonique)

Voir `/root/.hermes/standing/STANDING.md`. Confirme :

- **Phase courante** : TEST EXCLUSIVE depuis 2026-05-13
- **14 règles immuables** (voir extrait complet ci-dessous)
- **Provider LLM mentionné dans STANDING** : « GitHub Copilot (gemini-3.1-pro-preview default) » — ⚠️ **également périmé** par rapport à `config.yaml` actuel (Gemini 3.1 Flash Lite via OpenRouter). STANDING n'a pas été mis à jour après le swap.
- Email à `contact.azamoul@gmail.com` via skill `azamoul-email-sender` (smtplib inline avec `print('EMAIL_SMTP_OK')` en fin) — **PAS via tool messaging Hermes (gateway IMAP/SMTP en panne)**.
- Telegram à `<TELEGRAM_USER_ID>` UNIQUEMENT.

### Les 14 règles (numérotées)

1. AVANT toute action mutative, relis MISSION-HERMES.md, MEMORY.md (Phase courante), STANDING.md et learnings.md (7 dernières entrées).
2. JAMAIS lancer `shopify store auth` — auth est OK, relancer = plantage headless.
3. JAMAIS publier un post Instagram sans validation explicite — TOUJOURS proposer (en mode test : mode `dry` forcé).
4. JAMAIS modifier un prix > 5% sans validation. Modifier `price` directement = action 🔴 (sauf si /yes prod). Préférer `compareAtPrice`.
5. JAMAIS supprimer produit / page / client.
6. TOUJOURS intégrer le vocabulaire culturel amazigh/berbère (19 mots listés).
7. TOUJOURS documenter l'impact mesurable dans learnings.md à la semaine N+1.
8. Si token Shopify expire, NOTIFIE — ne pas réauthentifier seul.
9. Email à `contact.azamoul@gmail.com` via skill `azamoul-email-sender` (smtplib inline).
10. Telegram à `<TELEGRAM_USER_ID>` UNIQUEMENT.
11. INTERDICTION ABSOLUE d'inventer des chiffres KPI.
12. INTERDICTION ABSOLUE de padding répété.
13. INTERDICTION ABSOLUE d'inventer un champ GraphQL — TOUJOURS lire `azamoul-shopify-schema-guard` AVANT.
14. INTERDICTION ABSOLUE de marquer PASS sur Exception.

## 7. Variables d'environnement (45 clés exactement, noms uniquement)

```
ANTHROPIC_API_KEY, ANTHROPIC_TOKEN
AZAMOUL_MODE, AZAMOUL_TEST_EMAIL_TO
BROWSERBASE_ADVANCED_STEALTH, BROWSERBASE_PROXIES
BROWSER_INACTIVITY_TIMEOUT, BROWSER_SESSION_TIMEOUT
COPILOT_GITHUB_TOKEN
EMAIL_ADDRESS, EMAIL_ALLOWED_USERS, EMAIL_FROM, EMAIL_HOME_ADDRESS
EMAIL_IMAP_HOST, EMAIL_PASSWORD
EMAIL_SMTP_HOST, EMAIL_SMTP_PASSWORD, EMAIL_SMTP_PORT, EMAIL_SMTP_USER
EMAIL_TO
FIRECRAWL_API_KEY
GSC_CLIENT_EMAIL, GSC_PROJECT_ID, GSC_SERVICE_ACCOUNT_FILE
GSC_SITE_URL, GSC_TOKEN_PATH
HASS_URL
IMAGE_TOOLS_DEBUG, MOA_TOOLS_DEBUG
OPENAI_API_KEY, OPENAI_TEXT_MODEL, OPENAI_VISION_MODEL
OPENROUTER_API_KEY
OPENVIKING_ENDPOINT
SHOPIFY_STORE
TELEGRAM_ALLOWED_USERS, TELEGRAM_BOT_TOKEN, TELEGRAM_HOME_CHANNEL
TERMINAL_LIFETIME_SECONDS, TERMINAL_MODAL_IMAGE
TERMINAL_PERSISTENT_SHELL, TERMINAL_TIMEOUT
VISION_TOOLS_DEBUG, WEB_TOOLS_DEBUG
```

## 8. MEMORY.md — synthèse des décisions Phase Production (snapshot)

- **Phase courante** : Grand Run Test passé ✅ GO → Phase Production prête (décision tuteur)
- `AZAMOUL_MODE=test` dans `.env` — bascule prod = changer en `prod`
- `AZAMOUL_TEST_EMAIL_TO=contact.azamoul@gmail.com`
- En mode test : batch-executor applique + rollback même run ; email-sender destinataire forcé ; instagram-publisher mode `dry` forcé
- 21 skills Azamoul actifs (cohérent avec listing VPS)
- Décisions user du 14 mai (toutes différées) :
  - Clés sensibles non régénérées
  - Scope Shopify `write_online_store_navigation` différé
  - Setup Meta Graph API différé
  - Bascule prod = décision business

## 9. Particularités d'envoi email — source canonique

**Le gateway IMAP/SMTP intégré de Hermes Agent est en panne.** Tous les crons LLM contiennent dans leur prompt un **snippet Python smtplib inline obligatoire** qui :

1. Lit `/root/.hermes/.env` ligne par ligne
2. Crée un MIMEText avec `body` contextualisé
3. Connecte au SMTP via `EMAIL_SMTP_HOST` + `EMAIL_SMTP_PORT` + `EMAIL_SMTP_USER` + `EMAIL_SMTP_PASSWORD`
4. Termine par `print('EMAIL_SMTP_OK')` en stdout

La règle est dure : si la chaîne `EMAIL_SMTP_OK` n'apparaît pas dans le stdout du tool terminal, l'email **n'a pas été envoyé**. Hermès doit alors écrire `Email NON envoyé (cause: ...)` dans son résumé Telegram. Mentir = violation grave de la règle anti-hallucination.

## 10. Bugs connus / hardcodes périmés (source : MEMORY.md)

- **Prompt cron lundi-perf hardcode** « Phase 1 lecture seule jusqu'au 2026-05-25 » → à remplacer par lecture directe `AZAMOUL_MODE`
- **Hermes pense Telegram CLI échoue** → faux positif sans impact, le cron gateway gère via `delivery: telegram`
- **Scope Shopify `write_online_store_navigation`** non activé → Hermes évite renommages handle
- **Instagram Graph API** non configuré → mode `dry` permanent
- **GitHub Copilot rate-limit hebdo** (~30-35 prompts/semaine) → bloqueur principal du Grand Run, mitigé par swap OpenRouter

## 11. Chemins critiques (source canonique)

```
/root/.hermes/                         # core Hermes
├── .env                               # 45 clés env
├── config.yaml                        # config principale (LLM, agent, terminal)
├── cron/jobs.json                     # 4 crons + leurs prompts
├── cron/output/<job-id>/              # sorties horodatées par run
├── hooks/log-learning.sh
├── hooks/inject-standing.sh
├── logs/agent.log, errors.log, gateway.log
├── memories/MEMORY.md                 # mémoire persistante Hermes
├── sessions/                          # 14 sessions JSON
├── skills/                            # 45 skills (21 azamoul + 24 système)
├── standing/STANDING.md               # 14 règles immuables
└── state.db (SQLite + WAL + SHM)

/root/azamoul-shopify/                 # workspace projet
├── MISSION-HERMES.md
├── learnings.md                       # append-only via hook
├── brand-knowledge.md
├── baseline-kpi-30j.md
├── reports/YYYY-Www-perf.md           # cron lundi
├── reports/YYYY-Www-ideas.md          # cron samedi
├── meta-reviews/YYYY-Www-meta.md      # cron dimanche
├── audits/, batches/, campaigns/, tests/
└── shopify-automation-toolkit/        # toolkit Node.js réutilisable

/opt/openviking/                       # serveur mémoire
└── bin/openviking-server

/usr/local/lib/hermes-agent/           # binaire Hermes v0.13.0
├── venv/                              # Python 3.11
└── node_modules/

/etc/systemd/system/openviking.service
~/.config/systemd/user/hermes-gateway.service  (user service)
```

## 12. Incohérences détectées entre la doc et la réalité VPS

| Doc | Affirmation doc | Réalité VPS | Action |
|---|---|---|---|
| GUIDE §2 | « DeepSeek v4 Pro principal, Copilot Gemini fallback » | `google/gemini-3.1-flash-lite-preview` via OpenRouter | **Corriger GUIDE** |
| MEMORY.md | « DeepSeek v4 Pro via OpenRouter » | Idem | **Corriger MEMORY** |
| STANDING.md (interne) | « GitHub Copilot (gemini-3.1-pro-preview default) » | Idem | **Corriger STANDING** |
| GUIDE §11 | « 21 skills atomiques, 4 ⭐ en attente validation » | 21 actifs, 0 `.PROPOSED` restant | **Clarifier GUIDE** (les ⭐ ont été validés) |
| STANDING.md ligne 328 | « 17 skills Azamoul + 2 .PROPOSED » | 21 actifs, 0 .PROPOSED | **Corriger STANDING** |
| GUIDE §10 | (aucune mention) | Gateway IMAP/SMTP Hermes en panne → snippet Python obligatoire | **Ajouter au GUIDE** |
| GUIDE §3 | crons mentionnés mais pas leurs IDs | IDs : 9b3edc604e0d, 7936943cee39, 8450eef5fde8, dd4a59c29a88 | **Ajouter IDs au GUIDE** |
