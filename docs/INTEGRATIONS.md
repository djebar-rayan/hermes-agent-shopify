# External integrations — Hermes Framework

> Catalog of external APIs, reusable helpers, and technical stack of the Hermes framework.

---

## 1. Integrated external APIs (16)

| # | Service | Env variable | Scope / usage | Helper / skill | Status |
|---|---|---|---|---|---|
| 1 | **Shopify Admin API** | `SHOPIFY_STORE` | OAuth catalog/orders/themes (read+write_products, read_themes, write_files, read_content, write_content, read_customers, read_orders) | `lib/shopify-graphql.js` | OK |
| 2 | **Shopify Theme Access** | `SHOPIFY_CLI_THEME_TOKEN` (`shptka_***`) | `write_themes` headless scope — works around its absence in the normal OAuth scope | `lib/theme.sh` + `shopify-theme-editor` | OK |
| 3 | **Klaviyo** | `KLAVIYO_API_KEY` | Read-only — flows, campaigns, metrics, segments, lists (revision `2024-10-15`) | `lib/klaviyo-fetch.sh` + 3 skills | OK |
| 4 | **Gemini (Google AI Studio)** | `GEMINI_API_KEY`, `GEMINI_MODEL` (flash-image), `GEMINI_TEXT_MODEL` (flash-lite text), `GEMINI_VISION_MODEL` (flash-lite vision) | Image generation + text/vision fallback | inline (MoA / image-tools) | OK |
| 5 | **OpenAI** | `OPENAI_API_KEY`, `OPENAI_TEXT_MODEL=gpt-4.1-nano`, `OPENAI_VISION_MODEL=gpt-4.1-nano` | Text + vision fallback | inline | OK |
| 6 | **OpenRouter** | `OPENROUTER_API_KEY` | Hermes primary LLM (typical quota $20/month) | core agent loop | OK |
| 7 | **Anthropic** | `ANTHROPIC_TOKEN`, `ANTHROPIC_API_KEY` | Backup LLM / direct Claude | core agent loop | OK |
| 8 | **Google Search Console** | `GSC_SERVICE_ACCOUNT_FILE`, `GSC_CLIENT_EMAIL`, `GSC_PROJECT_ID`, `GSC_TOKEN_PATH`, `GSC_SITE_URL` | Service account — domain SEO performance | `gsc_client.py` | OK |
| 9 | **Firecrawl** | `FIRECRAWL_API_KEY` | Competitive intelligence (structured scrape) | inline | OK |
| 10 | **SMTP Gmail** | `EMAIL_SMTP_HOST=smtp.gmail.com`, `EMAIL_SMTP_PORT=587`, `EMAIL_SMTP_USER`, `EMAIL_SMTP_PASSWORD` (16-char App Password), `EMAIL_FROM`, `EMAIL_TO` | Transactional sending — IMAP optional (can be disabled) | `hermes-email-sender` skill | OK |
| 11 | **Telegram Bot** | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `TELEGRAM_HOME_CHANNEL` | Wake-agent, watchdog alerts, `/yes` validation | inline (curl) | OK |
| 12 | **Browserbase** | `BROWSERBASE_ADVANCED_STEALTH`, `BROWSERBASE_PROXIES`, `BROWSER_INACTIVITY_TIMEOUT`, `BROWSER_SESSION_TIMEOUT` | Stealth browser sessions (web tools) | core web tools | OK |
| 13 | **OpenViking** | `OPENVIKING_ENDPOINT` | Memory endpoint + MoA vision (localhost:1933) | core | OK |
| 14 | **GitHub Copilot** | `COPILOT_GITHUB_TOKEN` | GH token (push docs, PRs) | inline | Optional |
| 15 | **Home Assistant** | `HASS_URL` | Personal home automation (out of Shopify scope) | core | Optional |
| 16 | **Modal terminal** | `TERMINAL_LIFETIME_SECONDS`, `TERMINAL_MODAL_IMAGE`, `TERMINAL_PERSISTENT_SHELL`, `TERMINAL_TIMEOUT` | Execution sandbox | core terminal tool | OK |

---

## 2. `lib/` helpers

### `lib/klaviyo-fetch.sh` (mode 755, executable)

Single facade for the Klaviyo API with disk cache and retry.

**Specifications**:
- **Cache**: `/root/.hermes/cache/klaviyo/<endpoint>-YYYY-MM-DD-HH.json` — TTL 6h (UTC hourly slot)
- **Headers**: `Authorization: Klaviyo-API-Key ***`, `revision: 2024-10-15`, `Accept: application/vnd.api+json`
- **Retry**: exponential `2^attempt` seconds on HTTP 429, max 3 attempts → `{"error":"rate-limit max retries"}` beyond
- **Anti rate-limit**: 10 req/s burst + 150 req/min sustained Klaviyo

**Subcommands**:
```bash
$ klaviyo-fetch.sh flows                                              # live flows
$ klaviyo-fetch.sh campaigns                                          # campaigns 30d
$ klaviyo-fetch.sh metrics                                            # metrics
$ klaviyo-fetch.sh segments                                           # segments
$ klaviyo-fetch.sh lists                                              # lists
$ klaviyo-fetch.sh profiles-count                                     # total profile count
$ klaviyo-fetch.sh metric-aggregate <id> <interval> <since> <until>   # custom metric aggregate
$ klaviyo-fetch.sh flow-message-stats <flow-id> <since> <until>       # stats per flow
```

**Exit codes**:
- `0`: success
- `1`: `KLAVIYO_API_KEY` missing
- `2`: API error
- `3`: invalid usage

**Consumed by**: `shopify-klaviyo-weekly-report`, `shopify-klaviyo-campaign-ideator`, `shopify-klaviyo-drop-watchdog`.

---

### `lib/theme.sh` (mode 644, sourceable)

Bash library for headless Shopify theme operations via Theme Access token.

**Why this helper exists**: the `write_themes` OAuth scope is not always granted. The `themeFilesUpsert` GraphQL mutation often returns ACCESS_DENIED. And `shopify store auth --scopes write_themes` can be refused by the installed Shopify CLI app ("Shopify granted fewer scopes than were requested").

**Solution**: **Theme Access password** (`shptka_...`) created via the official Shopify app, single `write_themes` scope, functional with `shopify theme push` in headless.

**Constants** (configurable via env vars):
- `LIVE_THEME_ID` (live theme ID, to discover via `shopify theme list`)
- `SHOPIFY_STORE` (store handle)
- `THEME_BACKUP_DIR=$HERMES_WORKSPACE/theme-backups` (default)
- `THEME_WORK_BASE=/tmp/theme-work`
- `TOOLKIT_LIB=$HERMES_WORKSPACE/shopify-automation-toolkit/lib/shopify-graphql.js`

**Exported functions (14)**:

| Function | Role |
|---|---|
| `theme_check_env` | Verifies `SHOPIFY_CLI_THEME_TOKEN` + presence of GraphQL toolkit |
| `theme_safety_level <path>` | Returns `green` / `yellow` / `red-block` / `red-forbidden` based on pattern |
| `theme_get <filename> [output] [theme_id]` | Fetches file content via GraphQL `theme(id).files` |
| `theme_backup <filename> [theme_id]` | UTC-timestamped backup in `theme-backups/`, chmod 600, echoes path |
| `theme_lint <local>` | JSON valid, balanced Liquid tags (`if/endif`, `for/endfor`...), CSS braces |
| `theme_diff <local> <remote> [theme_id]` | Unified diff (rc=0 identical, 1 diff, 2 err) |
| `theme_push <local> <remote> [theme_id]` | Push 1 file via `shopify theme push --only` |
| `theme_push_many <work_dir> [theme_id]` | Multi-file atomic with transactional rollback |
| `theme_verify <local> <remote> [theme_id]` | Re-fetches and compares (rc=0 if match, otherwise diff on stderr) |
| `theme_duplicate [name]` | Duplicates live → preview theme, echoes new theme ID |
| `theme_preview_url <theme_id>` | Echoes preview URL |
| `theme_delete <theme_id>` | Deletes a theme (refuses if == LIVE) |
| `theme_publish <theme_id>` | Set as live |
| `theme_list` | Lists id\|name\|role |

**Consumed by**: `shopify-theme-editor` (and exposed for direct use in any future skill).

---

## 3. Integration skills

### Klaviyo (3 skills)

| Skill | When to use | Condensed description |
|---|---|---|
| `shopify-klaviyo-weekly-report` v1.0.0 | Cron weekly-perf-report, "Klaviyo report" request | Markdown section of email KPIs injected in weekly report. Aggregates open/click/bounce/unsub/order over 7d vs previous 7d |
| `shopify-klaviyo-campaign-ideator` v1.0.0 | Cron weekly-ideas | Email campaign draft aligned with `cultural-events.json` + past performance. Read-only, manual UI copy-paste |
| `shopify-klaviyo-drop-watchdog` v1.0.0 | Cron watchdog-conversion (6h) — never interactive | Silent by default. Telegram alert + wake-agent if open ↓>20pp, click ↓>30pp, revenue ↓>40%, unsub >5% |

### Theme (1 skill)

| Skill | When to use | Description |
|---|---|---|
| `shopify-theme-editor` v1.1.0 | Incremental theme file edit, custom template creation, redesign (→ duplicate-preview) | Edits the live theme via Theme Access token. Auto backup, lint, diff, verify, rollback. Levels green/yellow/red-block/red-forbidden. Workflows A (single file), B (multi atomic), C (duplicate-preview) |

### Email (1 skill)

| Skill | When to use | Description |
|---|---|---|
| `hermes-email-sender` v1.0.0 | Any email send (factorizes smtplib snippets) | SMTP Gmail STARTTLS. Reads `HERMES_MODE`: `test` → forces `to = $HERMES_TEST_EMAIL_TO` + subject prefix `[TEST]`. `prod` → real list (mandatory "mode=prod" mention) |

---

## 4. Technical stack

| Component | Version |
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

## 5. Shopify themes

A Shopify store can have N themes but only one `main` (live) role. Recommended typical pattern:

| Theme | Role |
|---|---|
| `<current theme>` | **[live]** — the one displayed to visitors |
| `<pre-migration theme>` | unpublished — quick rollback possible |
| `Backup <date>` | unpublished — point-in-time backup |
| `Hermes-Preview-<timestamp>` | unpublished — created by `theme_duplicate`, deleted after /yes |

**Local theme backups**: `$HERMES_WORKSPACE/theme-backups/` with pattern `<filename>.theme<id>.<UTC-ts>.bak`.

---

## 6. Security

### Secret storage

- **Single file**: `/root/.hermes/.env` (chmod 600 root:root)
- **No public** `.env.example` copy
- **No global shell export**; no secrets in CLI args
- Loading by skills/helpers via:
  ```bash
  set -a; . /root/.hermes/.env; set +a
  ```
  Variables are NOT exported to the external shell environment.

### Permissions

| File | Permissions |
|---|---|
| `/root/.hermes/.env` | 600 root:root |
| `lib/klaviyo-fetch.sh` | 755 (direct executable) |
| `lib/theme.sh` | 644 (sourceable only) |
| `$HERMES_WORKSPACE/theme-backups/*.bak` | 600 (auto chmod after write by `theme_backup`) |
| `~/.hermes/` | 700 |

### Klaviyo cache

- `/root/.hermes/cache/klaviyo/`: 755, contents in 644
- No secrets (only public API responses for the token)
- TTL 6h, rotation per hourly slot
- No automatic purge (slow growth)

### Git / GitHub

- **`/root/.hermes/`**: not versioned on the VPS side (by convention)
- **`$HERMES_WORKSPACE/`**: not versioned on the VPS side
- **Consequence**: code/config/secrets live only on the VPS side. To publish docs on GitHub: create the repo on workstation side + strict `.gitignore`

### "test-exclusive mode" variables

- `HERMES_MODE=test` (global lock)
- `HERMES_TEST_EMAIL_TO=<your_email>`
- All mutations are ephemeral as long as `HERMES_MODE` ≠ `prod`
- Global kill-switch before Production switch

### Attention points for GitHub publication

| Category | NEVER commit |
|---|---|
| Secrets | `.env`, `*_token.json`, `*_secret.json`, `*_service_account.json`, `client_secret.json` |
| Caches | `cache/klaviyo/`, `__pycache__/`, `node_modules/` |
| Backups | `theme-backups/`, `*.bak` |
| Internal documents | `ACCES-*.md` |

| Category | Safe to publish (already sanitized) |
|---|---|
| Helpers | `lib/klaviyo-fetch.sh`, `lib/theme.sh` (variable names only) |
| Skills | All `SKILL.md` (never values, only names) |
| Docs | Architecture, workflows, redacted audits |
