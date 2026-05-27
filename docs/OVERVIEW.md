# Hermes Framework — Vue d'ensemble

> Document narratif pour comprendre en 15 min ce qu'est Hermes, ce qu'il fait, et comment il s'articule.
> Pour les détails techniques : [`ARCHITECTURE.md`](./ARCHITECTURE.md), [`SKILLS-REFERENCE.md`](./SKILLS-REFERENCE.md), [`AUTOMATION.md`](./AUTOMATION.md).

---

## 1. Mission

**Hermes** est un framework d'agent IA autonome qui pilote la croissance commerciale d'une boutique Shopify en optimisant en continu chaque aspect (SEO, contenu, images, UX, emailing, posts Instagram, code du thème) et en proposant des idées créatives chaque semaine.

Le marchand configure une fois sa marque (vocabulaire, calendrier événementiel, niveaux d'autonomie), puis Hermes :
- Regarde la boutique tous les jours
- Identifie ce qui peut être amélioré
- Prépare les changements
- Demande validation via Telegram + email
- Applique après accord
- Apprend de chaque action

Il améliore ses propres prochaines décisions, y compris en **créant de nouveaux skills automatiquement** quand un pattern devient récurrent.

---

## 2. Configuration de la boutique

Tu configures ta boutique dans `$HERMES_WORKSPACE/` avec ces fichiers :

| Fichier | Contenu |
|---|---|
| `MISSION.md` | Charter spécifique à ta boutique (basé sur le template du framework) |
| `STORE-BRAND.md` | Vocabulaire obligatoire, niveaux d'autonomie 🟢/🟡/🔴, sensibilités |
| `brand-knowledge.md` | Concurrents, positionnement, USP |
| `cultural-events.json` | Événements/saisons importants pour ta marque (Noël, Black Friday, événements culturels, lancements...) |
| `MEMORY.md` | Faits permanents (catégories produits, plan Shopify, devise, fuseau, etc.) |

Voir [`examples/azamoul/`](../examples/azamoul/) pour un exemple complet de configuration sur une vraie marque.

---

## 3. Architecture conceptuelle

```
        ┌─────────────────────────────────────────────────┐
        │      docs/ARCHITECTURE.md (charter framework)   │
        │   (lu à chaque cycle, paramétré par MISSION.md) │
        └─────────────────────────────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────────┐
            │   STANDING-CORE (11 règles) │ ◄── injecté chaque session
            │   STORE-BRAND  (3 règles)   │     via hook on_session_start
            │   MEMORY.md (faits)         │
            └─────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │           25 SKILLS atomiques            │
        │  21 shopify-*  +  4 hermes-* (utilities) │
        └─────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       ┌──────────┐   ┌──────────┐  ┌──────────────┐
       │  4 CRONS │   │ Triggers │  │ Hook events  │
       │  hebdo   │   │ manuels  │  │ (auto-log)   │
       └──────────┘   └──────────┘  └──────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      OUTPUTS (rapport, mail, Telegram,  │
        │      mutation Shopify, theme files,     │
        │      draft campagne email/Insta)        │
        └─────────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │   learnings.md (append-only) → mémoire  │
        │   OpenViking (RAG cross-session)        │
        └─────────────────────────────────────────┘
```

---

## 4. Que fait Hermes chaque jour de la semaine ?

| Quand | Cron | Skills appelés | Output |
|---|---|---|---|
| **Lundi 9h** | `<store>-weekly-perf-report` | `shopify-weekly-perf-report` + `shopify-baseline-kpi-fetch` + `shopify-low-conversion-diagnostic` + `shopify-klaviyo-weekly-report` | `reports/YYYY-Www-perf.md` + résumé Telegram + email. KPI Shopify + section Klaviyo, top wins/pertes, diagnostic, actions exécutées, actions proposées 🟢/🟡, prédictions S+1 |
| **Mardi-Vendredi** | (rien planifié) | — | Hermes dort. Disponible pour intervention manuelle via `hermes chat`. |
| **Samedi 10h** | `<store>-weekly-ideas` | `shopify-instagram-ideator` + `shopify-product-ideator` + `shopify-cultural-calendar` + `shopify-klaviyo-campaign-ideator` | `reports/YYYY-Www-ideas.md` + email. 3 propositions : 1 produit + 1 post Instagram + 1 draft campagne Klaviyo |
| **Dimanche 20h** | `<store>-weekly-meta-review` | `shopify-weekly-perf-report` + `shopify-cultural-calendar` | `meta-reviews/YYYY-Www-meta.md` + Telegram. Méta-revue : lit `learnings.md` 7j, identifie 3 patterns, **crée un nouveau skill si pattern >3 occurrences** |
| **Toutes les 6h** | `<store>-watchdog-conversion` | script bash + `shopify-klaviyo-drop-watchdog` | Silencieux par défaut. Telegram uniquement si chute conversion ou drop Klaviyo |

---

## 5. Les 25 skills par catégorie

Catalogue complet : [`SKILLS-REFERENCE.md`](./SKILLS-REFERENCE.md).

| Catégorie | Skills |
|---|---|
| Monitoring & rapport | `shopify-weekly-perf-report`, `shopify-baseline-kpi-fetch`, `shopify-low-conversion-diagnostic`, `shopify-kpi-drop-watchdog` |
| Klaviyo | `shopify-klaviyo-weekly-report`, `shopify-klaviyo-campaign-ideator`, `shopify-klaviyo-drop-watchdog` |
| E-commerce mutation | `shopify-batch-executor`, `shopify-batch-rollback`, `shopify-catalog-gap-analyzer`, `shopify-theme-editor`, `hermes-schema-guard` |
| Content / SEO | `shopify-description-enricher`, `shopify-metatitle-generator`, `shopify-altext-generator`, `shopify-seo-mutation-batcher` |
| Ideation hebdo | `shopify-instagram-ideator`, `shopify-product-ideator`, `shopify-cultural-calendar` |
| Campagne | `shopify-cultural-campaign-drafter`, `shopify-instagram-publisher` |
| Messaging | `hermes-email-sender` |
| DevOps auto-proposés | `shopify-cron-output-watcher`, `hermes-snapshot-diff-validator`, `hermes-storefront-http-verifier` |

---

## 6. Modèle LLM et stack

| Élément | Valeur défaut |
|---|---|
| Provider principal | OpenRouter (https://openrouter.ai/api/v1) |
| Modèle défaut | `google/gemini-3.1-flash-lite-preview` |
| Modèle alternatif | `google/gemini-3.1-pro-preview` (sessions CLI) |
| Modèle fallback | DeepSeek v4 Pro, Claude direct |
| Context length | 262 144 tokens |
| Request timeout | 1800s |
| Quota OpenRouter typique | 20$/mois pay-as-you-go |
| Timezone | Configurable (défaut Europe/Paris) |

**Stack VPS** : Ubuntu 24.04+ · Python 3.11+ · Node 20+ · Shopify CLI 3.94+ · OpenViking 0.3.16 (port 1933) · Hermes Agent v0.14.0.

---

## 7. Niveaux d'autonomie

| Niveau | Description | Exemples typiques (à customiser dans `STORE-BRAND.md`) |
|---|---|---|
| 🟢 **Auto-exécution** | Hermes applique sans demander | alt-text, handles ASCII, tags simples, bloc 📦 livraison en début de description, meta SEO vides à compléter, drafts |
| 🟡 **Propose en 1-clic** | Hermes prépare + valide via Telegram /yes | enrichissement descriptions, images, redirects, collections, prix raisonnable, post Instagram (mode dry forcé), modif sections thème |
| 🔴 **Jamais sans validation** | Hermes refuse même avec demande | prix > 5%, suppressions, refunds, layout thème, post Instagram direct, modifications légales, `config/settings_data.json` |

Le marchand DOIT customiser ces niveaux dans `$HERMES_WORKSPACE/STORE-BRAND.md` selon ses propres sensibilités.

---

## 8. Phase : TEST EXCLUSIVE par défaut

À l'installation, Hermes démarre en `HERMES_MODE=test` :
- **Test mode** : toute mutation est apply + rollback dans le même run (éphémère)
- **Prod mode** : mutation persistante + /yes Telegram obligatoire

Cette phase test sert de période d'apprentissage. Le marchand confirme les bons comportements avant de basculer en prod (modifier `HERMES_MODE=prod` dans `.env`).

Avant la bascule, voir [`PRODUCTION-CHECKLIST.md`](./PRODUCTION-CHECKLIST.md).

---

## 9. Auto-amélioration — 5 mécaniques

1. **Memory OpenViking** (`localhost:1933`) : embedding local, RAG cross-session sur tous les fichiers `MEMORY*.md` + `learnings.md`
2. **Curator background** : nettoyage et compaction automatique de la mémoire courante
3. **Création automatique de skills** dans le cron méta-revue dominicale : si pattern récurrent > 3 occurrences sur 4 semaines détecté dans `learnings.md`, le cron crée un nouveau `SKILL.md`
4. **`hermes insights --days 7`** : analyse coût/tokens/modèles par cron pour détecter dérive
5. **Hook `post_tool_call`** : chaque action mutative est auto-loguée dans `learnings.md` avec 4 placeholders (avant/après/conclusion/futur) à compléter en W+1

---

## 10. Intégrations externes (16 APIs)

Voir [`INTEGRATIONS.md`](./INTEGRATIONS.md) pour le détail.

**Surfaces principales** :
- **Shopify** (Admin API + Theme Access pour write_themes headless)
- **Klaviyo** (read-only, helper `klaviyo-fetch.sh` cache 6h)
- **Gemini** (3 modèles : image, text, vision)
- **OpenAI** (fallback gpt-4.1-nano)
- **OpenRouter** (LLM principal)
- **Google Search Console** (service account, performance SEO)
- **Firecrawl** (veille concurrentielle)
- **SMTP Gmail** (envoi via snippet Python inline)
- **Telegram Bot** (validation /yes, alertes watchdog)

---

## 11. Helpers réutilisables (`lib/`)

### `klaviyo-fetch.sh`
Façade unifiée API Klaviyo avec cache 6h et retry exponentiel sur 429. 7 endpoints exposés. Consommé par les 3 skills Klaviyo.

### `theme.sh`
Library bash pour ops thème Shopify headless. 14 fonctions (get/backup/lint/diff/push/push_many atomic/verify/duplicate/preview_url/delete/publish/list/safety_level/check_env). Contourne l'absence du scope OAuth `write_themes` via Theme Access token. Consommé par `shopify-theme-editor`.

---

## 12. Démarrer

Pour installer Hermes sur ta boutique : [`../GETTING-STARTED.md`](../GETTING-STARTED.md).

Cet agent est entièrement configurable via `$HERMES_WORKSPACE/STORE-BRAND.md`. Voir [`../examples/azamoul/`](../examples/azamoul/) pour un cas d'étude complet d'une marque française en production depuis mai 2026.
