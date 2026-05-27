# VPS Snapshot — Hermes Agent Azamoul · 2026-05-27

> Photographie complète du VPS Hermes à l'instant `2026-05-27 ~16h Paris`.
> Remplace [`VPS_SNAPSHOT_2026-05-16.md`](./VPS_SNAPSHOT_2026-05-16.md) (obsolète).
> Audit conduit par 4 agents en parallèle (skills, automation, workspace, intégrations).

---

## Synthèse exécutive

| Composant | État |
|---|---|
| **Hermes core** | v0.14.0 (565 commits behind, update différé) — Python 3.11.15, OpenAI SDK 2.24.0 |
| **Skills `azamoul-*`** | **25 actifs** (21 historiques + 3 Klaviyo 2026-05-21 + 1 theme-editor v1.1 2026-05-24) |
| **Crons** | **4 actifs** : lundi-perf, samedi-ideas, dimanche-meta, watchdog-conversion → 88 runs cumulés sans erreur |
| **Hooks v0.14** | 2 actifs : `inject-standing` (on_session_start), `log-learning` (post_tool_call) |
| **Gateway Telegram** | Up depuis 3 jours (PID 350702 + amlys PID 396520) |
| **Helpers `/root/.hermes/lib/`** | `klaviyo-fetch.sh` (cache 6h, 7 endpoints), `theme.sh` (14 fonctions) |
| **Memory** | OpenViking 0.3.16 (port 1933) + MEMORY.md 53 lignes + learnings.md append-only |
| **Phase courante** | `AZAMOUL_MODE=test` — apply+rollback même run pour mutations. Production techniquement validée (Grand Run W20 5/6 PASS) mais bascule = décision tuteur |
| **Coût 7j** | 1.08M tokens · 4 sessions · ~6h active time · pas de coût $ remonté par OpenRouter |
| **Modèles utilisés** | `gemini-3.1-flash-lite-preview` (3 sessions cron, 743k tokens) + `gemini-3.1-pro-preview` (1 session CLI, 340k tokens) |

---

## 1. Skills (25 total)

Voir [`../../docs/SKILLS-REFERENCE.md`](../../docs/SKILLS-REFERENCE.md) pour le détail.

**Répartition par catégorie** :
- Monitoring & rapport : 4 (`weekly-perf-report`, `baseline-kpi-fetch`, `low-conversion-diagnostic`, `kpi-drop-watchdog`)
- Klaviyo : 3 (`weekly-report`, `campaign-ideator`, `drop-watchdog`) — ajout 2026-05-21
- E-commerce mutation : 5 (`batch-executor`, `batch-rollback`, `catalog-gap-analyzer`, `shopify-schema-guard`, `theme-editor` v1.1)
- Content / SEO : 4 (`description-enricher`, `metatitle-generator`, `altext-generator`, `seo-mutation-batcher.PROPOSED`)
- Ideation : 3 (`instagram-ideator`, `product-ideator`, `cultural-calendar`)
- Campagne : 2 (`cultural-campaign-drafter`, `instagram-publisher`)
- Messaging : 1 (`email-sender`)
- Devops auto-proposed : 3 (`cron-output-watcher`, `snapshot-diff-validator`, `storefront-http-verifier.PROPOSED`)

**Évolutions clés mai 2026** :
- **2026-05-20/21** : vague Klaviyo (3 skills + helper unifié)
- **2026-05-24** : skill `theme-editor` v1.0 puis perfectionné v1.1 le même jour (helper lib `theme.sh`, workflow duplicate-preview, lint, multi-file atomic push)

---

## 2. Crons (4 actifs)

Voir [`../../docs/AUTOMATION.md`](../../docs/AUTOMATION.md) pour le détail.

| ID court | Nom | Schedule | Runs | Last status |
|---|---|---|---|---|
| `9b3edc60` | azamoul-lundi-perf | `0 9 * * 1` | 12 | ok 2026-05-25 |
| `7936943c` | azamoul-samedi-ideas | `0 10 * * 6` | 5 | ok 2026-05-23 |
| `8450eef5` | azamoul-dimanche-meta | `0 20 * * 0` | 5 | ok 2026-05-24 |
| `dd4a59c2` | azamoul-watchdog-conversion | `0 */6 * * *` | 66 | ok 2026-05-27 12:00 |

**Particularité watchdog** : `no_agent: true` → exécute un script bash directement, sans session LLM (économie tokens). Silencieux par défaut, alerte Telegram uniquement si chute KPI > 30% / 24h.

---

## 3. Helpers `/root/.hermes/lib/`

### `klaviyo-fetch.sh` (executable 755)
Façade unifiée API Klaviyo (revision `2024-10-15`).
- Cache disque 6h dans `/root/.hermes/cache/klaviyo/` (anti rate-limit 10/s, 150/min)
- Retry exponentiel `2^attempt` sur HTTP 429, max 3 tentatives
- 7 sous-commandes : `flows`, `campaigns`, `metrics`, `segments`, `lists`, `profiles-count`, `metric-aggregate <id> <interval> <since> <until>`

### `theme.sh` (sourçable 644)
Library bash pour ops thème Shopify headless.
- 14 fonctions : `theme_get`, `theme_backup`, `theme_lint`, `theme_diff`, `theme_push`, `theme_push_many` (atomic + rollback), `theme_verify`, `theme_duplicate`, `theme_preview_url`, `theme_delete`, `theme_publish`, `theme_list`, `theme_safety_level`, `theme_check_env`
- Niveaux sécurité par chemin : 🟢 green / 🟡 yellow / 🔴 red-block / 🚫 red-forbidden
- Contourne l'absence de scope OAuth `write_themes` via Theme Access token (`shptka_`)

---

## 4. Memory system

| Fichier | Taille | Lignes | Rôle |
|---|---|---|---|
| `MEMORY.md` | 3065 o | 53 | Mémoire courante (boutique, stack, phase, decisions ouvertes) |
| `MEMORY-HISTORY.md` | 8166 o | 118 | Historique détaillé Phases 0-4, Grand Run, bugs corrigés |
| `USER.md` | 641 o | 20 | Profil utilisateur (tuteur) |
| `learnings.md` (hooks) | — | 6 | Auto-log post_tool_call (entrées récentes en attente de complétion W+1) |

**Provider** : OpenViking 0.3.16 sur port 1933, char_limit 3500 (memory) / 1375 (user).

---

## 5. Stack Hermes

| Élément | Valeur |
|---|---|
| Hermes | v0.14.0 (2026.5.16) |
| Python | 3.11.15 (venv `/usr/local/lib/hermes-agent`) |
| OpenAI SDK | 2.24.0 |
| Node | v20.20.2 |
| Shopify CLI | 3.94.3 |
| Model défaut | `google/gemini-3.1-flash-lite-preview` via OpenRouter |
| Context length | 262 144 tokens |
| Request timeout | 1800s |
| Timezone | Europe/Paris |
| Toolset actif | `hermes-cli` |
| Workdir terminal | `/root/azamoul-shopify` |
| Compression | enabled (target ratio 0.25, threshold 0.6, protect_last_n 30) |
| Approvals | `smart`, cron_mode `deny`, timeout 60s |
| Security | `redact_secrets: true`, `tirith_enabled: true`, `allow_private_urls: false` |

**MCP servers** : `composio` (https://connect.composio.dev/mcp, Bearer **REDACTED**, timeout 120s).

---

## 6. Profile `amlys` (secondaire)

| Élément | Valeur |
|---|---|
| Gateway PID | 396520 (depuis 2026-05-27 11:16) |
| Model défaut | `google/gemini-3-flash-preview` |
| max_turns | 90 |
| state.db | ~43 MB |
| Skills | 29 directories |
| Sandbox runtime | docker / singularity / modal / daytona |
| Identité | `SOUL.md` 513 o, `gerard_martin_facts.md` 579 o |

---

## 7. Activité 7 derniers jours (hermes insights)

Période 2026-05-20 → 2026-05-25.

- **Sessions** : 4 (3 cron + 1 CLI)
- **Messages** : 81 (10 user)
- **Tool calls** : 31
- **Tokens** : 422 141 input + 7 670 output = **1 083 362 total**
- **Active time** : ~6h 9m (1h 32m / session)

**Pics d'activité** : Lun, Mer, Sam, Dim · Heures 7h, 8h, 18h, 20h.

**Top tools** : `terminal` 18 · `execute_code` 4 · `skill_view` 3 · `read_file` 3.

**Top skills loaded** : `klaviyo-campaign-ideator`, `product-ideator`, `instagram-ideator` (1 load chacun = samedi-ideas).

---

## 8. Learnings récents

5 dernières entrées dans `/root/azamoul-shopify/learnings.md` :

| Date | Résumé |
|---|---|
| 2026-05-24 | Skill créé `azamoul-theme-editor v1.0.0` — modif thème Sense headless via Theme Access. Premier usage : template `product.test-returns.json` + bloc retours sweat tifinagh |
| 2026-05-24 | Bulk update 61 productUpdate templateSuffix='test-returns' sur produits textiles (62 au total avec sweat déjà fait). 0 fail |
| 2026-05-24 | Skill perfectionné v1.0 → v1.1 — helper `theme.sh` (12 fonctions), lint, workflow duplicate-preview, multi-file atomic push. 9/9 tests PASS |
| 2026-05-14 | Meta-review DeepSeek : patterns Snapshot-diff-validation (3 occ) + Cron-log-polling (4 occ) → 2 skills PROPOSED |
| 2026-05-14 | Grand Run FINAL : 5/6 PASS authentique + 1/6 PARTIAL. 9/9 critères PASS. **Verdict GO Phase Production** (bascule en attente tuteur) |

---

## 9. Points d'attention

- **Update Hermes** : 565 commits behind v0.14.0 (différé pour éviter rupture)
- **Email IMAP** désactivé depuis 2026-05-21 (timeouts) — fallback SMTP inline via snippet Python avec sentinelle `EMAIL_SMTP_OK` obligatoire
- **Skills PROPOSED non promus** : `seo-mutation-batcher.PROPOSED`, `storefront-http-verifier.PROPOSED` — en attente décision tuteur
- **Hook learnings.md** : 4 entrées 2026-05-21 restées avec placeholders vides — mécanisme complétion N+1 n'a pas tourné
- **Phase test exclusive** : aucune mutation Shopify persistante depuis 2026-05-13 (sauf cas explicites validés user — ex. theme editor 2026-05-24)
- **brand-knowledge.md** : 4 concurrents listés (cible MISSION-HERMES = 5-10) — gap à combler

---

## 10. Sécurité / GitHub publication

- **Secrets uniquement dans** : `/root/.hermes/.env` (chmod 600, 3889 bytes)
- **Aucun repo git** sur VPS (`/root/.hermes/` et `/root/azamoul-shopify/` non versionnés)
- **À ne JAMAIS publier** : `.env`, `cache/klaviyo/`, `theme-backups/`, `ACCES-AZAMOUL.md`
- **Safe à publier** (déjà sanitized dans ce repo) : `lib/*.sh`, `SKILL.md` (que des noms de variables), docs architecture

---

*Audit conduit le 2026-05-27 par 4 agents en parallèle. Read-only, aucune mutation, tous les tokens et secrets redacted (`***REDACTED***`).*
