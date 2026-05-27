# Intégrations externes — Hermes Framework

> Catalogue des APIs externes, helpers réutilisables, et stack technique du framework Hermes.

---

## 1. APIs externes intégrées (16)

| # | Service | Variable env | Scope / usage | Helper / skill | Status |
|---|---|---|---|---|---|
| 1 | **Shopify Admin API** | `SHOPIFY_STORE` | OAuth catalog/orders/themes (read+write_products, read_themes, write_files, read_content, write_content, read_customers, read_orders) | `lib/shopify-graphql.js` | OK |
| 2 | **Shopify Theme Access** | `SHOPIFY_CLI_THEME_TOKEN` (`shptka_***`) | Scope `write_themes` headless — contourne l'absence dans le scope OAuth normal | `lib/theme.sh` + `shopify-theme-editor` | OK |
| 3 | **Klaviyo** | `KLAVIYO_API_KEY` | Read-only — flows, campaigns, metrics, segments, lists (revision `2024-10-15`) | `lib/klaviyo-fetch.sh` + 3 skills | OK |
| 4 | **Gemini (Google AI Studio)** | `GEMINI_API_KEY`, `GEMINI_MODEL` (flash-image), `GEMINI_TEXT_MODEL` (flash-lite text), `GEMINI_VISION_MODEL` (flash-lite vision) | Génération image + fallback text/vision | inline (MoA / image-tools) | OK |
| 5 | **OpenAI** | `OPENAI_API_KEY`, `OPENAI_TEXT_MODEL=gpt-4.1-nano`, `OPENAI_VISION_MODEL=gpt-4.1-nano` | Fallback text + vision | inline | OK |
| 6 | **OpenRouter** | `OPENROUTER_API_KEY` | LLM principal Hermes (quota typique 20$/mois) | core agent loop | OK |
| 7 | **Anthropic** | `ANTHROPIC_TOKEN`, `ANTHROPIC_API_KEY` | Backup LLM / Claude direct | core agent loop | OK |
| 8 | **Google Search Console** | `GSC_SERVICE_ACCOUNT_FILE`, `GSC_CLIENT_EMAIL`, `GSC_PROJECT_ID`, `GSC_TOKEN_PATH`, `GSC_SITE_URL` | Service account — performance SEO du domaine | `gsc_client.py` | OK |
| 9 | **Firecrawl** | `FIRECRAWL_API_KEY` | Veille concurrentielle (scrape structuré) | inline | OK |
| 10 | **SMTP Gmail** | `EMAIL_SMTP_HOST=smtp.gmail.com`, `EMAIL_SMTP_PORT=587`, `EMAIL_SMTP_USER`, `EMAIL_SMTP_PASSWORD` (App Password 16 chars), `EMAIL_FROM`, `EMAIL_TO` | Envoi transactionnel — IMAP optionnel (peut être désactivé) | `hermes-email-sender` skill | OK |
| 11 | **Telegram Bot** | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `TELEGRAM_HOME_CHANNEL` | Wake-agent, alertes watchdogs, validation `/yes` | inline (curl) | OK |
| 12 | **Browserbase** | `BROWSERBASE_ADVANCED_STEALTH`, `BROWSERBASE_PROXIES`, `BROWSER_INACTIVITY_TIMEOUT`, `BROWSER_SESSION_TIMEOUT` | Sessions browser stealth (web tools) | core web tools | OK |
| 13 | **OpenViking** | `OPENVIKING_ENDPOINT` | Endpoint memory + MoA vision (localhost:1933) | core | OK |
| 14 | **GitHub Copilot** | `COPILOT_GITHUB_TOKEN` | Token GH (push doc, PRs) | inline | Optional |
| 15 | **Home Assistant** | `HASS_URL` | Domotique perso (hors scope Shopify) | core | Optional |
| 16 | **Modal terminal** | `TERMINAL_LIFETIME_SECONDS`, `TERMINAL_MODAL_IMAGE`, `TERMINAL_PERSISTENT_SHELL`, `TERMINAL_TIMEOUT` | Sandbox d'exécution | core terminal tool | OK |

---

## 2. Helpers `lib/`

### `lib/klaviyo-fetch.sh` (mode 755, executable)

Façade unique pour l'API Klaviyo avec cache disque et retry.

**Spécifications** :
- **Cache** : `/root/.hermes/cache/klaviyo/<endpoint>-YYYY-MM-DD-HH.json` — TTL 6h (slot horaire UTC)
- **Headers** : `Authorization: Klaviyo-API-Key ***`, `revision: 2024-10-15`, `Accept: application/vnd.api+json`
- **Retry** : exponentiel `2^attempt` secondes sur HTTP 429, max 3 tentatives → `{"error":"rate-limit max retries"}` au-delà
- **Anti rate-limit** : 10 req/s burst + 150 req/min sustained Klaviyo

**Sous-commandes** :
```bash
$ klaviyo-fetch.sh flows                                              # flows live
$ klaviyo-fetch.sh campaigns                                          # campagnes 30j
$ klaviyo-fetch.sh metrics                                            # metrics
$ klaviyo-fetch.sh segments                                           # segments
$ klaviyo-fetch.sh lists                                              # lists
$ klaviyo-fetch.sh profiles-count                                     # nb profils total
$ klaviyo-fetch.sh metric-aggregate <id> <interval> <since> <until>   # agrégat metric custom
$ klaviyo-fetch.sh flow-message-stats <flow-id> <since> <until>       # stats par flow
```

**Exit codes** :
- `0` : succès
- `1` : `KLAVIYO_API_KEY` manquante
- `2` : erreur API
- `3` : usage invalide

**Consommé par** : `shopify-klaviyo-weekly-report`, `shopify-klaviyo-campaign-ideator`, `shopify-klaviyo-drop-watchdog`.

---

### `lib/theme.sh` (mode 644, sourçable)

Library bash pour opérations thème Shopify headless via Theme Access token.

**Pourquoi ce helper existe** : le scope OAuth `write_themes` n'est pas toujours accordé. La mutation GraphQL `themeFilesUpsert` retourne souvent ACCESS_DENIED. Et `shopify store auth --scopes write_themes` peut être refusé par l'app Shopify CLI installée ("Shopify granted fewer scopes than were requested").

**Solution** : **Theme Access password** (`shptka_...`) créé via l'app officielle Shopify, scope unique `write_themes`, fonctionnel avec `shopify theme push` en headless.

**Constantes** (paramétrables via env vars) :
- `LIVE_THEME_ID` (ID du thème live, à découvrir via `shopify theme list`)
- `SHOPIFY_STORE` (handle de la boutique)
- `THEME_BACKUP_DIR=$HERMES_WORKSPACE/theme-backups` (défaut)
- `THEME_WORK_BASE=/tmp/theme-work`
- `TOOLKIT_LIB=$HERMES_WORKSPACE/shopify-automation-toolkit/lib/shopify-graphql.js`

**Fonctions exportées (14)** :

| Fonction | Rôle |
|---|---|
| `theme_check_env` | Vérifie `SHOPIFY_CLI_THEME_TOKEN` + présence du toolkit GraphQL |
| `theme_safety_level <path>` | Retourne `green` / `yellow` / `red-block` / `red-forbidden` selon pattern |
| `theme_get <filename> [output] [theme_id]` | Fetch contenu fichier via GraphQL `theme(id).files` |
| `theme_backup <filename> [theme_id]` | Backup horodaté UTC dans `theme-backups/`, chmod 600, echoes path |
| `theme_lint <local>` | JSON valide, balises Liquid balancées (`if/endif`, `for/endfor`...), accolades CSS |
| `theme_diff <local> <remote> [theme_id]` | Unified diff (rc=0 identique, 1 diff, 2 err) |
| `theme_push <local> <remote> [theme_id]` | Push 1 fichier via `shopify theme push --only` |
| `theme_push_many <work_dir> [theme_id]` | Multi-file atomique avec rollback transactionnel |
| `theme_verify <local> <remote> [theme_id]` | Re-fetch et compare (rc=0 si match, sinon diff sur stderr) |
| `theme_duplicate [name]` | Duplique le live → preview theme, echoes new theme ID |
| `theme_preview_url <theme_id>` | Echoes URL preview |
| `theme_delete <theme_id>` | Supprime un thème (refuse si == LIVE) |
| `theme_publish <theme_id>` | Set as live |
| `theme_list` | Liste id\|name\|role |

**Consommé par** : `shopify-theme-editor` (et exposé pour usage direct dans tout skill futur).

---

## 3. Skills d'intégration

### Klaviyo (3 skills)

| Skill | When to use | Description condensée |
|---|---|---|
| `shopify-klaviyo-weekly-report` v1.0.0 | Cron weekly-perf-report, demande "rapport Klaviyo" | Section markdown KPI emails injectée dans rapport hebdo. Agrège open/click/bounce/unsub/order sur 7j vs 7j précédents |
| `shopify-klaviyo-campaign-ideator` v1.0.0 | Cron weekly-ideas | Draft campagne email aligné `cultural-events.json` + perf passée. Read-only, copier-coller manuel UI |
| `shopify-klaviyo-drop-watchdog` v1.0.0 | Cron watchdog-conversion (6h) — jamais interactif | Silencieux par défaut. Alerte Telegram + wake-agent si open ↓>20pp, click ↓>30pp, revenue ↓>40%, unsub >5% |

### Theme (1 skill)

| Skill | When to use | Description |
|---|---|---|
| `shopify-theme-editor` v1.1.0 | Modif fichier thème incrémentale, création template custom, refonte (→ duplicate-preview) | Édite le thème live via Theme Access token. Backup auto, lint, diff, verify, rollback. Niveaux green/yellow/red-block/red-forbidden. Workflows A (single file), B (multi atomic), C (duplicate-preview) |

### Email (1 skill)

| Skill | When to use | Description |
|---|---|---|
| `hermes-email-sender` v1.0.0 | Tout envoi email (factorise les snippets smtplib) | SMTP Gmail STARTTLS. Lit `HERMES_MODE` : `test` → force `to = $HERMES_TEST_EMAIL_TO` + prefix sujet `[TEST]`. `prod` → liste réelle (mention "mode=prod" obligatoire) |

---

## 4. Stack technique

| Composant | Version |
|---|---|
| Node.js | v20+ |
| Python | 3.11+ |
| Shopify CLI | 3.94+ |
| Hermes Agent | v0.14.0 |
| OpenAI SDK | 2.24.0+ |
| OpenViking | 0.3.16 (port 1933) |
| Klaviyo API revision | `2024-10-15` |
| Shopify Admin API | 2025-10 |

---

## 5. Thèmes Shopify

Une boutique Shopify peut avoir N thèmes mais un seul rôle `main` (live). Pattern typique recommandé :

| Thème | Rôle |
|---|---|
| `<theme courant>` | **[live]** — celui qui s'affiche aux visiteurs |
| `<theme avant migration>` | unpublished — rollback rapide possible |
| `Backup <date>` | unpublished — sauvegarde ponctuelle |
| `Hermes-Preview-<timestamp>` | unpublished — créé par `theme_duplicate`, supprimé après /yes |

**Theme backups locaux** : `$HERMES_WORKSPACE/theme-backups/` avec pattern `<filename>.theme<id>.<UTC-ts>.bak`.

---

## 6. Sécurité

### Stockage des secrets

- **Fichier unique** : `/root/.hermes/.env` (chmod 600 root:root)
- **Aucune copie** `.env.example` publique
- **Aucun export shell global** ; aucun secret en CLI args
- Chargement par les skills/helpers via :
  ```bash
  set -a; . /root/.hermes/.env; set +a
  ```
  Les variables ne sont PAS exportées à l'environnement extérieur du shell.

### Permissions

| Fichier | Permissions |
|---|---|
| `/root/.hermes/.env` | 600 root:root |
| `lib/klaviyo-fetch.sh` | 755 (executable direct) |
| `lib/theme.sh` | 644 (sourçable uniquement) |
| `$HERMES_WORKSPACE/theme-backups/*.bak` | 600 (chmod auto après écriture par `theme_backup`) |
| `~/.hermes/` | 700 |

### Cache Klaviyo

- `/root/.hermes/cache/klaviyo/` : 755, contenu en 644
- Pas de secrets (uniquement réponses API publiques au token)
- TTL 6h, rotation par slot horaire
- Pas de purge automatique (croissance lente)

### Git / GitHub

- **`/root/.hermes/`** : pas versionné côté VPS (par convention)
- **`$HERMES_WORKSPACE/`** : pas versionné côté VPS
- **Conséquence** : code/config/secrets vivent côté VPS uniquement. Pour publier de la doc sur GitHub : créer le repo côté workstation + `.gitignore` strict

### Variables "test-exclusive mode"

- `HERMES_MODE=test` (verrou global)
- `HERMES_TEST_EMAIL_TO=<your_email>`
- Toutes les mutations sont éphémères tant que `HERMES_MODE` ≠ `prod`
- Kill-switch global avant bascule Production

### Points d'attention pour publication GitHub

| Catégorie | À ne JAMAIS commiter |
|---|---|
| Secrets | `.env`, `*_token.json`, `*_secret.json`, `*_service_account.json`, `client_secret.json` |
| Caches | `cache/klaviyo/`, `__pycache__/`, `node_modules/` |
| Backups | `theme-backups/`, `*.bak` |
| Documents internes | `ACCES-*.md` |

| Catégorie | Safe à publier (déjà sanitized) |
|---|---|
| Helpers | `lib/klaviyo-fetch.sh`, `lib/theme.sh` (que des noms de variables) |
| Skills | Tous les `SKILL.md` (jamais de valeurs, juste des noms) |
| Docs | Architecture, workflows, audits redacted |
