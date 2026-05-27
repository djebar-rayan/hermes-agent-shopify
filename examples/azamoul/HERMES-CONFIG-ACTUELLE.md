# Configuration Hermes — État effectif au 2026-05-17

> Document factuel : ce qui est **réellement déployé** sur le VPS, par opposition à `HERMES-CONFIG-OPTIMAL.md` qui est la cible théorique.
>
> Source : lecture SSH directe sur `azamoul-vps` (`<VPS_HOSTNAME>`, `<VPS_IP>`), Grand Run Test PASSED + corrections post-audit (2026-05-14) + vérifications du 2026-05-17.
>
> **Source canonique** : ce document doit refléter la réalité observable via SSH. Si une autre doc contredit ce fichier, c'est l'autre doc qui doit être mise à jour.

---

## 1. Stack opérationnelle

| Composant | Version | État | Auto-restart |
|---|---|---|---|
| Hermes Agent | **0.13.0 (build 2026.5.7)** ⚠️ 313 commits behind upstream | active | systemd `hermes-gateway.service` (**user**) |
| OpenViking | **0.3.16** | active + enabled | systemd `openviking.service` (**system**) |
| OpenAI SDK (côté Hermes) | 2.24.0 | — | — |
| Python (Hermes venv) | 3.11.15 (`/usr/local/lib/hermes-agent/venv/`) | — | — |
| Python (OpenViking) | 3.12.x (venv OpenViking séparé) | — | — |
| Node.js | 20.20.2 | — | — |
| Shopify CLI | 3.94.3 | — | — |
| Modèle d'embedding GGUF | `bge-small-zh-v1.5-f16` (36 Mo, dim 512) | téléchargé dans `~/.cache/openviking/models/` | n/a |

**Note maintenance** : la commande `hermes --version` signale « Update available: 313 commits behind — run `hermes update` ». Mise à jour reportée volontairement tant que la prod est stable.

---

## 2. Configuration Hermes (`/root/.hermes/config.yaml`)

### Bloc modèle & agent

| Clé | Valeur réelle | Notes |
|---|---|---|
| `model.default` | `google/gemini-3.1-flash-lite-preview` | **Modèle de prod actuel** (swap effectué post-Grand Run 2026-05-14) |
| `model.provider` | `openrouter` | OpenAI-compatible |
| `model.base_url` | `https://openrouter.ai/api/v1` | endpoint OpenRouter |
| `model.context_length` | `262144` | 256 k tokens |
| `model.request_timeout_seconds` | `1800` | 30 min (anti-timeout sur longs contextes) |
| `model.api_mode` | `chat_completions` | mode OpenAI standard |
| `agent.max_turns` | `120` | marge crons lourds |
| `agent.api_max_retries` | `5` | tolérance hoquets HTTP |
| `agent.reasoning_effort` | `medium` | équilibre vs drift sur sessions longues |
| `agent.gateway_timeout` | `1800` | s |
| `agent.gateway_timeout_warning` | `900` | s |
| `agent.clarify_timeout` | `600` | s |
| `agent.tool_use_enforcement` | `auto` | — |
| `agent.image_input_mode` | `auto` | — |
| `agent.max_concurrent_children` | `3` | concurrence sub-agents |
| `agent.max_spawn_depth` | `2` | profondeur récursion sub-agents |

### Historique des LLM testés

| Modèle | Provider | Période | Pourquoi changé |
|---|---|---|---|
| `kimi-k2-instruct-0905-fast` | groq / divers | Phase 0 préliminaire | swap pour stabilité |
| `gemini-3.1-pro-preview` | GitHub Copilot | Phase 0 → Grand Run 14 mai | rate-limit Copilot atteint en cours de Grand Run |
| `deepseek/deepseek-chat-v4-pro` | OpenRouter | Grand Run B4-B5 (14 mai 17h48 → 19h) | testé et validé, mais latence un peu plus haute |
| **`google/gemini-3.1-flash-lite-preview`** | **OpenRouter** | **2026-05-14 19h → actuel** | **modèle retenu pour la prod** (contexte 256 k, latence faible, coût très bas) |

### Fallback chain

**Aucune** — choix assumé :

```yaml
fallback_providers: []
providers: {}
credential_pool_strategies: {}
```

Si OpenRouter est saturé ou indisponible, Hermès retry jusqu'à 5 fois puis échoue. Aucune bascule automatique. La bascule vers Copilot Gemini Pro ou DeepSeek v4 Pro reste **manuelle** en éditant `config.yaml` (~5 min, zéro redémarrage). Procédure documentée en §10.5.4 du `GUIDE-HERMES-POUR-AZAMOUL.md`.

### Memory

| Clé | Valeur |
|---|---|
| `memory.memory_enabled` | `true` |
| `memory.user_profile_enabled` | `true` |
| `memory.memory_char_limit` | `2200` |
| `memory.user_char_limit` | `1375` |
| `memory.provider` | `openviking` |

**Note** : `MEMORY.md` fait actuellement **8095 caractères** (vs limite 2200 dans le prompt). L'écart est normal : la limite affichée concerne le **résumé injecté dans le prompt**, pas le stockage. OpenViking et la memory built-in chargent le fichier entier mais ne renvoient que les extraits pertinents à chaque session.

### Display, web, approvals, security, timezone, terminal

| Clé | Valeur |
|---|---|
| `display.personality` | `helpful` |
| `display.language` | `fr` |
| `display.streaming` | `true` |
| `compression.threshold` | `0.60` |
| `compression.protect_last_n` | `30` |
| `web.backend` | `firecrawl` |
| `web.search_backend` | `firecrawl` |
| `web.extract_backend` | `firecrawl` |
| `approvals.mode` | `smart` |
| `security.redact_secrets` | `true` |
| `security.tirith_enabled` | `true` |
| `timezone` | `Europe/Paris` |
| `group_sessions_per_user` | `true` |
| `terminal.backend` | `local` |
| `terminal.cwd` | `/root/azamoul-shopify` |
| `terminal.timeout` | `900` |
| `terminal.lifetime_seconds` | `300` |
| `terminal.persistent_shell` | `false` |
| `terminal.docker_image` | `nikolaik/python-nodejs:python3.11-nodejs20` |
| `toolsets` | `[hermes-cli]` |
| `browser.engine` | `auto` |
| `browser.inactivity_timeout` | `120` s |
| `browser.allow_private_urls` | `false` |
| `checkpoints.enabled` | `false` |

### Hooks dans `config.yaml`

```yaml
hooks:
- event: tool_call_completed
  matcher: .*Update|.*Create|.*Delete|.*publish.*|.*email.*
  command: /root/.hermes/hooks/log-learning.sh
  timeout: 30
  hooks_auto_accept: true
```

⚠️ **Note importante** : seul `log-learning.sh` est déclaré dans `config.yaml`. Le hook `inject-standing.sh` existe dans `/root/.hermes/hooks/` mais n'apparaît pas dans la config YAML — son déclenchement (`session_started`) est probablement configuré ailleurs (via `hermes config set hook ...` qui le persiste dans l'état SQLite, ou via un mécanisme intégré au gateway). À vérifier si on a un doute sur l'injection automatique de STANDING.md au démarrage de session.

---

## 3. OpenViking (`/root/.openviking/ov.conf`)

Permissions : `chmod 600` (contient la clé OpenRouter du VLM).

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 1933
  },
  "storage": {
    "workspace": "/root/.openviking/data"
  },
  "embedding": {
    "dense": {
      "provider": "local",
      "model": "bge-small-zh-v1.5-f16",
      "dimension": 512
    }
  },
  "vlm": {
    "provider": "openai",
    "api_base": "https://openrouter.ai/api/v1",
    "api_key": "<REDACTED — OpenRouter API key>",
    "model": "deepseek/deepseek-v4-pro",
    "temperature": 0.0,
    "max_retries": 2
  }
}
```

**Décisions clés au 2026-05-17** :

- Embedding 100 % local (llama.cpp + GGUF) → zéro dépendance cloud pour la vectorisation
- **VLM = DeepSeek v4 Pro via OpenRouter** (différent du LLM principal Hermes qui est Gemini 3.1 Flash Lite via OpenRouter — les deux passent par OpenRouter avec la même clé `OPENROUTER_API_KEY`)
- Bind `127.0.0.1` uniquement → accessible seulement par Hermes local sur la même machine

**Pourquoi un VLM différent du LLM principal** : OpenViking utilise un modèle plus puissant (DeepSeek v4 Pro) pour les opérations sémantiques rares (extraction de souvenirs structurés), tandis que Hermès utilise un modèle plus rapide et économique (Gemini 3.1 Flash Lite) pour ses appels conversationnels fréquents.

**Health check** :
```
$ curl -s http://127.0.0.1:1933/health
{"status":"ok","healthy":true,"version":"0.3.16","auth_mode":"dev"}
```

---

## 4. Variables d'environnement (`/root/.hermes/.env`)

Permissions : `chmod 600`. **45 clés** au total, regroupées par catégorie (valeurs masquées) :

### LLM (8 clés)

| Clé | Rôle |
|---|---|
| `OPENROUTER_API_KEY` | LLM principal Hermes (Gemini 3.1 Flash Lite) + VLM OpenViking (DeepSeek v4 Pro) |
| `COPILOT_GITHUB_TOKEN` | LLM fallback documenté (Gemini 3.1 Pro Preview via GitHub Copilot) |
| `OPENAI_API_KEY` | Fallback rare (gpt-4.1-nano text + vision) |
| `OPENAI_TEXT_MODEL` | `gpt-4.1-nano` |
| `OPENAI_VISION_MODEL` | `gpt-4.1-nano` |
| `ANTHROPIC_API_KEY` | Configuré, non utilisé en prod |
| `ANTHROPIC_TOKEN` | Configuré, non utilisé en prod |

### Shopify (1 clé)

| Clé | Valeur (visible) |
|---|---|
| `SHOPIFY_STORE` | `azamoul-symboles-berberes.myshopify.com` |

Note : pas de token Shopify Admin en variable d'env — l'authentification passe par la **Shopify CLI** (déjà authentifiée). Ne **jamais** relancer `shopify store auth` (plantage headless garanti — STANDING règle 2).

### Email (10 clés)

| Clé | Valeur observable |
|---|---|
| `EMAIL_FROM` | `djebar.rayan75@gmail.com` (expéditeur dev — à changer en prod) |
| `EMAIL_TO` / `EMAIL_HOME_ADDRESS` | `contact.azamoul@gmail.com` (gérant) |
| `EMAIL_SMTP_HOST` | `smtp.gmail.com` |
| `EMAIL_SMTP_PORT` | `587` |
| `EMAIL_SMTP_USER` | `djebar.rayan75@gmail.com` |
| `EMAIL_SMTP_PASSWORD` | Gmail App Password 16 chars |
| `EMAIL_ADDRESS` | `djebar.rayan75@gmail.com` |
| `EMAIL_PASSWORD` | App Password (alias) |
| `EMAIL_IMAP_HOST` | `imap.gmail.com` (non utilisé actuellement) |
| `EMAIL_ALLOWED_USERS` | Liste blanche destinataires |

⚠️ **Bug connu** : le gateway IMAP/SMTP intégré de Hermes Agent est en panne depuis Phase 1. Les crons LLM contiennent en réalité un snippet Python `smtplib` inline qui se connecte directement au SMTP Gmail et émet `EMAIL_SMTP_OK` en stdout. Ne pas tenter de réparer le gateway intégré (procédure officielle).

### Telegram (3 clés)

| Clé | Valeur |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot Telegram |
| `TELEGRAM_ALLOWED_USERS` | `<TELEGRAM_USER_ID>` (gérant unique autorisé) |
| `TELEGRAM_HOME_CHANNEL` | `<TELEGRAM_USER_ID>` |

### Google Search Console (5 clés)

| Clé | Rôle |
|---|---|
| `GSC_CLIENT_EMAIL` | Email du service account |
| `GSC_PROJECT_ID` | Projet Google Cloud |
| `GSC_SERVICE_ACCOUNT_FILE` | Path JSON du service account |
| `GSC_SITE_URL` | URL de la propriété GSC vérifiée |
| `GSC_TOKEN_PATH` | `/root/.hermes/.gsc_token.json` |

### Mode application (2 clés)

| Clé | Valeur actuelle | Rôle |
|---|---|---|
| `AZAMOUL_MODE` | `test` | Flag central — `test` = mutations éphémères, emails forcés vers contact.azamoul, Instagram dry. Bascule prod = `prod` (décision tuteur, pas encore prise) |
| `AZAMOUL_TEST_EMAIL_TO` | `contact.azamoul@gmail.com` | Destinataire forcé en mode test |

### Outils externes (5 clés)

| Clé | Rôle |
|---|---|
| `OPENVIKING_ENDPOINT` | `http://localhost:1933` |
| `FIRECRAWL_API_KEY` | Veille concurrentielle |
| `BROWSERBASE_ADVANCED_STEALTH` | Vars browser Hermes (non utilisées Phase 1) |
| `BROWSERBASE_PROXIES` | idem |
| `HASS_URL` | Home Assistant (non utilisé) |

### Vars Hermes par défaut (11 clés)

`BROWSER_INACTIVITY_TIMEOUT`, `BROWSER_SESSION_TIMEOUT`, `TERMINAL_LIFETIME_SECONDS`, `TERMINAL_MODAL_IMAGE`, `TERMINAL_PERSISTENT_SHELL`, `TERMINAL_TIMEOUT`, `IMAGE_TOOLS_DEBUG`, `MOA_TOOLS_DEBUG`, `VISION_TOOLS_DEBUG`, `WEB_TOOLS_DEBUG`.

---

## 5. Hooks (`/root/.hermes/hooks/`)

Permissions : dossier `chmod 700`, fichiers `chmod 700`.

| Fichier | Taille | Rôle | Déclencheur |
|---|---:|---|---|
| `log-learning.sh` | 1001 B | Log auto chaque action mutative dans `/root/azamoul-shopify/learnings.md` | `tool_call_completed` matching `Update\|Create\|Delete\|publish\|email` (déclaré dans `config.yaml`) |
| `inject-standing.sh` | 226 B | Injecte `STANDING.md` dans le system prompt | `session_started` (config probablement persistée dans l'état SQLite — pas dans `config.yaml`) |

Tous deux datés du **2026-05-12** (création initiale, jamais modifiés depuis).

---

## 6. Mémoire locale fichier

| Fichier | Taille actuelle | Rôle |
|---|---:|---|
| `/root/.hermes/memories/MEMORY.md` | **8095 B** | Faits Azamoul (boutique, vocabulaire, décisions Grand Run, état Phase Production) — augmenté depuis Phase 0 par enrichissement progressif |
| `/root/.hermes/memories/USER.md` | 641 B | Profil gérant (langue fr, sensibilité coût, tuteur stage) — inchangé |
| `/root/.hermes/standing/STANDING.md` | **7719 B** | **14 règles immuables** (au lieu de 10 en Phase 0) — version augmentée post-Phase 4 et Grand Run avec règles 11-14 anti-hallucination et padding |

Ces fichiers sont chargés par la memory **built-in** ET indexés par OpenViking pour la recherche sémantique cross-session.

---

## 7. Skills Azamoul (`/root/.hermes/skills/`)

**21 skills Azamoul actifs au 2026-05-17** (vs 5 en Phase 0 — multiplication par 4 grâce aux phases 2-4 et au Grand Run). **Aucun `.PROPOSED` en attente.**

### Référence / contexte (3)

| Skill | Rôle |
|---|---|
| `azamoul-shopify-schema-guard` | Fragments GraphQL validés par introspection (productCreate/Update/Delete, collectionCreate/Delete, productVariantsBulkUpdate, urlRedirectCreate, fileUpdate) — **anti-hallucination** |
| `azamoul-cultural-calendar` | Calendrier culturel amazigh (Yennayer, Tafsut, Aïd al-Adha, Imilchil, Révolution algérienne 1ᵉʳ nov) |
| `azamoul-shopify-schema-guard` | (référence GraphQL) |

### Lecture / audit (4)

`azamoul-baseline-kpi-fetch`, `azamoul-catalog-gap-analyzer`, `azamoul-low-conversion-diagnostic`, `azamoul-cultural-calendar`

### Monitoring (3)

| Skill | Rôle |
|---|---|
| `azamoul-kpi-drop-watchdog` | Alerte Telegram si chute KPI > 30 % sur 24 h |
| `azamoul-cron-output-watcher` ⭐ | Trigger cron + poll output dir + parse `## Response` (auto-créé Grand Run B4) |
| `azamoul-storefront-http-verifier` ⭐ | curl HTTP 200/404 post-mutation (auto-créé Phase 4) |

### Génération LLM (4)

`azamoul-instagram-ideator`, `azamoul-product-ideator`, `azamoul-cultural-campaign-drafter`, `azamoul-description-enricher`

### Génération SEO (3)

| Skill | Rôle |
|---|---|
| `azamoul-altext-generator` | 3 propositions alt-text SEO FR+EN |
| `azamoul-metatitle-generator` | meta_title + meta_description SEO |
| `azamoul-seo-mutation-batcher` ⭐ | Orchestre productUpdate.seo en batch avec snapshot+apply+rollback (auto-créé Phase 4) |

### Mutation Shopify (3)

| Skill | Rôle |
|---|---|
| `azamoul-batch-executor` | Batch ≤ 10 productUpdate, lit schema-guard, snapshot before/after, lit AZAMOUL_MODE |
| `azamoul-batch-rollback` | Restaure batch depuis snapshot before.json |
| `azamoul-snapshot-diff-validator` ⭐ | Compare snapshot BEFORE vs AFTER-ROLLBACK, FAIL si diff non vide — garde-fou mode test (auto-créé Grand Run B4) |

### Messaging (2)

| Skill | Rôle |
|---|---|
| `azamoul-email-sender` | SMTP Gmail, lit AZAMOUL_MODE (test=contact.azamoul / prod=liste), **exige `EMAIL_SMTP_OK` en stdout** |
| `azamoul-instagram-publisher` v2.0.0 | Payload Graph API, modes dry/container/publish, lit AZAMOUL_MODE (test=dry forcé), **approval gate `/yes_insta` obligatoire même en prod** |

### Reporting (1)

`azamoul-weekly-perf-report`

⭐ = skills **auto-créés par la méta-revue dominicale** suite à détection de patterns récurrents (≥ 3 occurrences), validés manuellement par renommage `SKILL.md.PROPOSED` → `SKILL.md`.

### Skills système Hermes (24 supplémentaires)

`apple`, `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `diagramming`, `dogfood`, `domain`, `email`, `gaming`, `gifs`, `github`, `inference-sh`, `mcp`, `media`, `mlops`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`, `yuanbao` — fournis avec Hermes Agent v0.13.0, non spécifiques à Azamoul mais disponibles si Hermès en a besoin.

---

## 8. Crons (`/root/.hermes/cron/jobs.json`) — état au 2026-05-17

| ID | Nom | Schedule (Europe/Paris) | Mode | Runs effectués | Last run | Next run | Delivery |
|---|---|---|---|---:|---|---|---|
| `9b3edc604e0d` | `azamoul-lundi-perf` | `0 9 * * 1` | agent | 10 | 2026-05-14 18:15 | **2026-05-18 09:00** | telegram |
| `7936943cee39` | `azamoul-samedi-ideas` | `0 10 * * 6` | agent | 4 | 2026-05-16 10:00 | 2026-05-23 10:00 | telegram |
| `8450eef5fde8` | `azamoul-dimanche-meta` | `0 20 * * 0` | agent | 3 | 2026-05-14 18:19 | **2026-05-17 20:00** (dans quelques heures) | telegram |
| `dd4a59c29a88` | `azamoul-watchdog-conversion` | `0 */6 * * *` | **no-agent** (script bash) | 23 | 2026-05-16 18:00 | 2026-05-17 00:00 | telegram |

Tous les crons : `enabled: true`, `state: scheduled`, `last_status: ok`, `last_error: null`. Workdir des crons LLM : `/root/azamoul-shopify`.

**Particularité watchdog** : `no_agent: true`, exécute directement le script `azamoul-conversion-watchdog.sh` sans appel LLM — économise le quota OpenRouter.

**Particularité prompts crons** : chaque prompt LLM contient un **snippet Python `smtplib` inline obligatoire** qui envoie l'email avec confirmation `EMAIL_SMTP_OK`. Voir `/root/.hermes/cron/jobs.json` pour le détail.

---

## 9. Sécurité

| Vérification | État | Source |
|---|---|---|
| `/root/.hermes/.env` | `chmod 600` ✅ | `stat` |
| `/root/.hermes/config.yaml` | `chmod 600` ✅ | `stat` |
| `/root/.openviking/ov.conf` | `chmod 600` ✅ | `stat` |
| `/root/.hermes/` (dir) | `chmod 700` ✅ | `stat` |
| `/root/.hermes/hooks/` (dir) | `chmod 700` ✅ | `stat` |
| `hooks/*.sh` | `chmod 700` ✅ | `ls -la` |
| `TELEGRAM_ALLOWED_USERS` | restreint à `<TELEGRAM_USER_ID>` ✅ | `.env` |
| `unauthorized_dm_behavior` | `ignore` ✅ | par défaut |
| `security.redact_secrets` | `true` ✅ | `config.yaml` |
| `security.tirith_enabled` | `true` (scan pre-exec) ✅ | `config.yaml` |
| OpenViking bind | `127.0.0.1` only ✅ | `ov.conf` |
| SSH connexion | clé Ed25519, mot de passe désactivé | `sshd_config` |

**Statut secrets sensibles** :

- **Clés sensibles non régénérées** (décision tuteur du 14 mai, risque accepté tant qu'on reste en `AZAMOUL_MODE=test`) :
  - App Password Gmail SMTP (partagé en clair pendant les phases de dev)
  - `OPENAI_API_KEY`
  - `FIRECRAWL_API_KEY`
- À régénérer **avant bascule prod** : voir `PHASE-PRODUCTION-CHECKLIST.md`.

---

## 10. Phase courante : Grand Run Test PASSED → GO Phase Production

**`AZAMOUL_MODE=test`** dans `/root/.hermes/.env` — confirmé.

### Conséquences mode test
- `batch-executor` : apply + rollback dans le même run (zéro mutation persistante Shopify)
- `email-sender` : destinataire forcé = `contact.azamoul@gmail.com`, sujet préfixé `[TEST]`
- `instagram-publisher` : mode `dry` forcé, zéro appel Graph API
- Aucune publication publique, aucun envoi à liste cliente

### Décisions tuteur du 14 mai (toutes optionnelles)
- Régénération des 3 clés sensibles : **différée**
- Activation scope Shopify `write_online_store_navigation` : **différée**
- Setup Meta Graph API : **différée**
- Bascule `AZAMOUL_MODE=test` → `prod` : **décision business** non prise

---

## 11. Investigations résolues (cumul Phases 0-4 + Grand Run)

| Investigation | Résolution |
|---|---|
| Instagram officiel | **@azamoul** confirmé (5 769 followers, 116 posts, 83 % reels) |
| Auth Shopify | OK (ne jamais relancer `shopify store auth` en headless) |
| SMTP Gmail | testé end-to-end, email reçu — règle `EMAIL_SMTP_OK` ajoutée |
| Hallucination `productUpdate.media[].alt` | Corrigée → bonne mutation `fileUpdate(files: [{id, alt}])` (fragment ajouté à `schema-guard`) |
| Padding lexical répété (« berbère » × 30) | Règle STANDING #12 ajoutée + retest strict |
| Rate-limit Copilot hebdo | Mitigé : swap vers OpenRouter (Gemini Flash Lite principal + DeepSeek fallback) validé pendant Grand Run |
| Gateway IMAP/SMTP Hermes en panne | Procédure officielle : snippet Python `smtplib` inline obligatoire dans chaque prompt cron |
| Mega-prompt unique | Rejeté définitivement (triche systématique observée) → modèle d'autonomie = sous-prompts orchestrés |

---

## 12. Bloqueurs reportés (post-bascule prod, hors scope Hermès)

| Bloqueur | Impact | Mitigation actuelle |
|---|---|---|
| Scope Shopify `write_online_store_navigation` non activé | Pas de `urlRedirectCreate` automatique | Hermès évite les renommages de handle |
| Instagram Graph API non configurée | Mode `dry` permanent | Skill v2.0.0 avec approval gate prêt dès configuration des tokens Meta |
| Pas de génération d'images IA satisfaisante | 33 produits < 3 images | Décision business : photos studio à externaliser |
| 44 produits en rupture stock | Manque à gagner | Décision business côté tuteur |
| Rate-limit OpenRouter free tier | Quota à surveiller en prod | Dashboard openrouter.ai/credits |

---

## 13. Tests fonctionnels validés au 2026-05-17

| Test | Résultat |
|---|---|
| `systemctl is-active openviking` | `active` ✅ |
| `systemctl --user is-active hermes-gateway` | `active running` ✅ |
| `curl http://127.0.0.1:1933/health` | `{"status":"ok","healthy":true,"version":"0.3.16","auth_mode":"dev"}` ✅ |
| `hermes --version` | `Hermes Agent v0.13.0 (2026.5.7)` ✅ (313 commits derrière upstream — non bloquant) |
| `hermes cron list` | 4/4 enabled, last_status ok partout ✅ |
| Cron `lundi-perf` | 10 runs effectués, dernier 2026-05-14 ✅ |
| Cron `samedi-ideas` | 4 runs, dernier 2026-05-16 (ce matin) ✅ |
| Cron `dimanche-meta` | 3 runs, prochain 2026-05-17 20h ⏳ |
| Cron `watchdog-conversion` | 23 runs (toutes les 6 h depuis 2026-05-12), dernier 2026-05-16 18:00 ✅ |
| Permissions `.env`, `config.yaml`, `ov.conf` | 600 ✅ |
| Permissions `/root/.hermes/`, `/root/.hermes/hooks/` | 700 ✅ |

---

## 14. Backups

| Backup | Taille | Date | État |
|---|---:|---|---|
| `/root/backups/hermes-backup-2026-05-12-004811.zip` | 156 Mo | 2026-05-12 00:48 | **Seul backup existant** ⚠️ |

⚠️ **Manque critique** : pas de backup depuis le 2026-05-12. Les phases 1-4 et le Grand Run Test ne sont pas inclus dans le backup actuel. **Recommandation** : lancer `hermes backup -o /root/backups --label "post-grand-run-$(date +%Y%m%d)"` rapidement, et **mettre en place un cron de backup hebdomadaire**.

---

## 15. Commandes de référence

### Vérifier que tout tourne (audit rapide)

```bash
systemctl is-active openviking
systemctl --user is-active hermes-gateway
curl -s http://127.0.0.1:1933/health
hermes cron list
hermes config check
hermes doctor
```

### Redémarrer après reboot VPS

Le watchdog systemd se charge de tout — rien à faire manuellement. Pour forcer :

```bash
systemctl restart openviking
systemctl --user restart hermes-gateway
```

### Modifier la config en cours

```bash
hermes config set <clé> <valeur>           # une clé scalaire
nano /root/.hermes/config.yaml             # blocs complexes (hooks, model)
nano /root/.hermes/.env                    # secrets
chmod 600 /root/.hermes/.env               # toujours après édition
```

### Swap LLM (rate-limit, panne fournisseur)

Éditer `/root/.hermes/config.yaml`, section `model:`. Modèles déjà validés :

- **Actuel** (prod) : `google/gemini-3.1-flash-lite-preview` via OpenRouter
- Fallback A : `deepseek/deepseek-chat-v4-pro` via OpenRouter
- Fallback B : `gemini-3.1-pro-preview` via GitHub Copilot

Effectif au prochain run, pas de redémarrage. Tester : `hermes chat -q 'echo ok'`.

### Backups

```bash
hermes backup -o /root/backups --label "manual-$(date +%Y%m%d)"
ls -lh /root/backups/
```

### Restaurer

```bash
hermes import /root/backups/<archive>.zip
```

---

## 16. Différences notables vs `HERMES-CONFIG-OPTIMAL.md` (cible théorique)

| Point | Cible OPTIMAL | Réalité ACTUELLE | Décision |
|---|---|---|---|
| Modèle LLM principal | DeepSeek v4 Pro via OpenRouter | Gemini 3.1 Flash Lite Preview via OpenRouter | Acté : meilleur ratio coût/latence pour le volume hebdo |
| Fallback chain | Documentée (Copilot, DeepSeek) | `[]` vide | Acté : swap manuel suffisant |
| Skills Azamoul | 17 cible | 21 actifs | Dépassé : 4 skills auto-créés en bonus |
| Backups | Cron hebdo | 1 seul backup au 2026-05-12 | **À mettre en place** |
| Régénération clés sensibles | Avant prod | Différée | Acté : risque accepté en test |
| Instagram Graph API | Configurée | Non configurée | Différée, mode `dry` permanent |
| Mise à jour Hermes Agent | dernière version | 313 commits behind | Reportée tant que prod stable |

---

*Document mis à jour le 2026-05-17 par Rayan Djebar, après lecture SSH directe du VPS `azamoul-vps` (<VPS_HOSTNAME>, <VPS_IP>). Source canonique : sortie de `cat /root/.hermes/config.yaml`, `cat /root/.openviking/ov.conf`, `cat /root/.hermes/cron/jobs.json`, `systemctl status`, `stat`, `wc -c` du jour. À mettre à jour à chaque changement majeur de config.*
