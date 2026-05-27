# Configuration Structure — `config.yaml`, `.env`, `cron/jobs.json`

> Architecture de configuration optimale pour Hermes. Explique comment les fichiers `config.yaml`, `.env`, hooks, et crons s'articulent.
>
> Templates concrets dans [`../config/`](../config/).

---

## 1. Vue d'ensemble — Hiérarchie de config

```
/root/.hermes/                          ← FRAMEWORK (partagé)
├── config.yaml                         ← config Hermes Agent (model, hooks, memory)
├── .env                                ← secrets boutique (chmod 600)
├── standing/STANDING-CORE.md           ← 11 règles universelles
├── cron/jobs.json                      ← 4 crons (lit prompts paramétrés)
└── hooks/*.sh                          ← inject-standing + log-learning

$HERMES_WORKSPACE/                       ← USER-FACING (instance boutique)
├── MISSION.md                          ← charter spécifique
├── STORE-BRAND.md                      ← vocab + niveaux autonomie
├── brand-knowledge.md                  ← concurrents + USP
├── cultural-events.json                ← calendrier événementiel
└── MEMORY.md                           ← faits permanents
```

**Principe** : les fichiers framework restent neutres et génériques. Les fichiers user-facing customisent le comportement pour TA boutique.

---

## 2. `/root/.hermes/config.yaml`

Fichier YAML principal de l'agent. Contient :

### Section LLM
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

### Section Memory
```yaml
memory:
  provider: openviking
  endpoint: http://localhost:1933
  char_limit: 3500
  user_char_limit: 1375
```

### Section Compression
```yaml
compression:
  enabled: true
  target_ratio: 0.25
  threshold: 0.6
  protect_last_n: 30
```

### Section Approvals
```yaml
approvals:
  mode: smart
  cron_mode: deny           # crons ne demandent pas d'approval interactif (utilisent /yes Telegram à la place)
  timeout: 60
```

### Section Security
```yaml
security:
  redact_secrets: true       # redact auto des values .env dans les logs
  tirith_enabled: true       # firewall sortie
  tirith_fail_open: true
  tirith_timeout: 5
  allow_private_urls: false  # bloque IPs privées
```

### Section Hooks v0.14
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

### Section Toolsets
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

## 3. `.env` — Secrets et config boutique

Template fourni dans [`../config/.env.template`](../config/.env.template).

```bash
# === Boutique ===
SHOPIFY_STORE=<store_handle>            # sans .myshopify.com
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

# === Optionnels ===
KLAVIYO_API_KEY=pk_***
FIRECRAWL_API_KEY=fc-***
GSC_SERVICE_ACCOUNT_FILE=/root/.hermes/gsc-service-account.json
GSC_CLIENT_EMAIL=<service-account>@<project>.iam.gserviceaccount.com
GSC_PROJECT_ID=<gcp-project>
GSC_SITE_URL=sc-domain:<store>.com

# === Browser tools (optionnels) ===
BROWSERBASE_ADVANCED_STEALTH=true
BROWSERBASE_PROXIES=true
BROWSER_INACTIVITY_TIMEOUT=300
BROWSER_SESSION_TIMEOUT=3600

# === Memory ===
OPENVIKING_ENDPOINT=http://localhost:1933
```

**Sécurité** : `chmod 600 /root/.hermes/.env` obligatoire. Jamais commit.

---

## 4. `/root/.hermes/cron/jobs.json`

Template fourni dans [`../config/cron-jobs.json.template`](../config/cron-jobs.json.template).

Structure JSON :

```json
{
  "jobs": [
    {
      "id": "<auto-generated-uuid>",
      "name": "<store>-weekly-perf-report",
      "prompt": "<prompt template avec placeholders>",
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

### Champs clés par cron

| Champ | Description |
|---|---|
| `id` | UUID auto-généré (à la création du cron) |
| `name` | Nom human-readable (préfixé par ton store handle) |
| `prompt` | Template du prompt envoyé à l'agent (avec placeholders à remplir) |
| `skills` | Liste des skills à charger en début de session |
| `skill` | Skill principal (le premier de la liste) |
| `no_agent` | Si `true` : exécute un script bash directement (pas de session LLM) |
| `schedule.expr` | Cron expression standard (5 champs : min hour day month dow) |
| `enabled` | Active/désactive sans supprimer |
| `deliver` | `telegram` ou `email` (préfère telegram, email géré par snippet inline) |
| `workdir` | Répertoire de travail pour le tool terminal (= $HERMES_WORKSPACE) |

---

## 5. `STANDING-CORE.md` + `STORE-BRAND.md`

### Architecture en 2 fichiers

| Fichier | Localisation | Contenu |
|---|---|---|
| `STANDING-CORE.md` | `/root/.hermes/standing/` | 11 règles universelles (framework) |
| `STORE-BRAND.md` | `$HERMES_WORKSPACE/` | 3 règles brand-specific (user customise) |

Le hook `inject-standing.sh` concatène les deux et les injecte dans le contexte de chaque session.

### Pattern de concaténation

```bash
#!/bin/bash
STANDING_CORE=$(cat /root/.hermes/standing/STANDING-CORE.md)
STORE_BRAND=$([ -f "$HERMES_WORKSPACE/STORE-BRAND.md" ] && cat "$HERMES_WORKSPACE/STORE-BRAND.md" || echo "")
COMBINED="$STANDING_CORE

## Brand-Specific Rules
$STORE_BRAND"
jq -n --arg s "$COMBINED" '{"continue": true, "context_injection": $s}'
```

Voir [`AUTOMATION.md`](./AUTOMATION.md) section 3 pour le détail des 14 règles.

---

## 6. `MISSION.md` (workspace)

Template fourni dans [`../config/MISSION.md.template`](../config/MISSION.md.template).

Sections type :
- Mission narrative spécifique à TA boutique
- Identité boutique (catalogue, plan, devise, fuseau)
- Sources surveillées
- Rythme opérationnel (4 crons)
- Niveaux d'autonomie (pointe vers STORE-BRAND.md)
- Mécaniques d'auto-amélioration
- Verification

Voir [`../examples/azamoul/MISSION.md`](../examples/azamoul/MISSION.md) pour un exemple complet (~19KB).

---

## 7. `MEMORY.md` (workspace)

Template fourni dans [`../config/MEMORY.md.template`](../config/MEMORY.md.template).

Sections type :
- Boutique (handle, domaine, plan, devise, fuseau, catégories)
- Stack VPS
- Modèle LLM utilisé
- Credentials résumés (noms uniquement, jamais de valeurs)
- Phase courante (`HERMES_MODE=test|prod`)
- Niveaux d'autonomie (résumé)
- Decisions ouvertes

Reste compact (< 60 lignes recommandées). Pour l'historique détaillé, utiliser `MEMORY-HISTORY.md` séparé.

---

## 8. `cultural-events.json` (workspace)

Template fourni dans [`../config/cultural-events.json.template`](../config/cultural-events.json.template).

Format :

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

Le skill `shopify-cultural-calendar` lit ce fichier programmatiquement et déclenche les workflows correspondants (alerte préavis J-21, propositions campagnes, etc.).

Voir [`../examples/azamoul/cultural-events.json`](../examples/azamoul/cultural-events.json) pour un exemple complet (calendrier amazigh).

---

## 9. Ordre d'initialisation lors d'une session

Quand Hermes démarre une session (cron ou interactif) :

1. **Hook `on_session_start`** s'exécute → injecte `STANDING-CORE.md` + `STORE-BRAND.md` dans le contexte
2. **Loading skills** : les skills déclarés dans le cron sont chargés (leur SKILL.md devient accessible à l'agent)
3. **Pré-lecture obligatoire** : l'agent lit MISSION.md + MEMORY.md + 7 dernières entrées learnings.md
4. **Exécution du prompt cron** : l'agent exécute la mission en suivant les niveaux d'autonomie
5. **Hook `post_tool_call`** : chaque action mutative est auto-loguée dans learnings.md
6. **Livrables** : génération des fichiers reports/ + envoi Telegram + envoi email (via snippet Python avec sentinelle `EMAIL_SMTP_OK`)
7. **Mise à jour status cron** dans `jobs.json` (`last_run_at`, `last_status`)

---

## 10. Customisation pour ta boutique

À l'install (suivre [`../GETTING-STARTED.md`](../GETTING-STARTED.md)), tu copies les templates depuis `config/` et tu les remplis avec tes valeurs :

| Template | Destination |
|---|---|
| `config/.env.template` | `/root/.hermes/.env` (chmod 600) |
| `config/STANDING-CORE.md.template` | `/root/.hermes/standing/STANDING-CORE.md` |
| `config/cron-jobs.json.template` | `/root/.hermes/cron/jobs.json` |
| `config/MISSION.md.template` | `$HERMES_WORKSPACE/MISSION.md` |
| `config/STORE-BRAND.md.template` | `$HERMES_WORKSPACE/STORE-BRAND.md` |
| `config/MEMORY.md.template` | `$HERMES_WORKSPACE/MEMORY.md` |
| `config/cultural-events.json.template` | `$HERMES_WORKSPACE/cultural-events.json` |

Le framework reste générique. Seuls les fichiers user-facing évoluent avec ta boutique.
