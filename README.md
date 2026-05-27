# Hermes — Reusable AI Growth Agent Framework for Shopify

> **Hermes** est un framework d'agent IA autonome conçu pour piloter la croissance commerciale d'une boutique Shopify de bout en bout — SEO, contenu, images, UX, emailing, posts Instagram, et même le code du thème Liquid.
>
> Ce dépôt contient **25 skills réutilisables**, **4 crons hebdomadaires**, **16 intégrations API** prêtes à l'emploi, et un **cas d'étude live** ([`examples/azamoul/`](./examples/azamoul/)) montrant Hermes en production sur une vraie boutique.

`v0.14.0` · **25 skills** · 4 crons · 16 intégrations · MIT License

---

## ⚡ TL;DR

Hermes regarde la boutique tous les jours, identifie ce qui peut être amélioré, prépare les changements, demande validation du marchand via Telegram + email, applique après accord. Il apprend de chaque action et améliore ses propres prochaines décisions — y compris en **créant de nouveaux skills automatiquement** quand un pattern devient récurrent.

**Cycle hebdo automatisé** :
- 🗓️ **Lundi 9h** — Rapport perf hebdo (KPI Shopify + Klaviyo, diagnostic, prédictions)
- 🎨 **Samedi 10h** — Email créatif (1 idée produit + 1 idée Insta + 1 draft campagne email)
- 🔄 **Dimanche 20h** — Méta-revue auto-amélioration (peut créer de nouveaux skills)
- 👁️ **Toutes les 6h** — Watchdog conversion (silencieux par défaut, alerte si chute)

---

## 🚀 Démarrer

Tu as une boutique Shopify et tu veux installer Hermes dessus ? Suis le guide :

👉 **[`GETTING-STARTED.md`](./GETTING-STARTED.md)** — Setup pas-à-pas pour une nouvelle boutique

Tu veux voir Hermes en production sur une vraie boutique ?

👉 **[`examples/azamoul/`](./examples/azamoul/)** — Cas d'étude complet (marque française, ~96 produits, 4 crons actifs depuis mai 2026)

---

## 🏗️ Architecture

```
        ┌─────────────────────────────────────────────────┐
        │           docs/ARCHITECTURE.md                  │
        │   (charter framework — lu à chaque cycle)       │
        └─────────────────────────────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────────┐
            │  STANDING-CORE (11 règles)  │ ◄── injecté chaque session
            │  STORE-BRAND.md (3 règles)  │     via hook on_session_start
            │  MEMORY.md (faits)          │
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
        │      draft campagne)                    │
        └─────────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │   learnings.md (append-only) → mémoire  │
        │   OpenViking (RAG cross-session)        │
        └─────────────────────────────────────────┘
```

---

## 🛠️ Stack technique

| Composant | Version |
|---|---|
| Hermes Agent | `v0.14.0` |
| Python | 3.11+ |
| Node.js | 20+ |
| Shopify CLI | 3.94+ |
| Memory provider | OpenViking 0.3.16 (port 1933, embedding local) |
| LLM principal | `google/gemini-3.1-flash-lite-preview` via OpenRouter |
| Context length | 262 144 tokens |
| Hôte | Tout VPS Ubuntu 24.04+ |

---

## 🧠 25 Skills opérationnels

| Catégorie | Skills |
|---|---|
| **Monitoring & rapport** | `shopify-weekly-perf-report`, `shopify-baseline-kpi-fetch`, `shopify-low-conversion-diagnostic`, `shopify-kpi-drop-watchdog` |
| **Klaviyo** | `shopify-klaviyo-weekly-report`, `shopify-klaviyo-campaign-ideator`, `shopify-klaviyo-drop-watchdog` |
| **E-commerce mutation** | `shopify-batch-executor`, `shopify-batch-rollback`, `shopify-catalog-gap-analyzer`, `shopify-theme-editor`, `hermes-schema-guard` |
| **Content / SEO** | `shopify-description-enricher`, `shopify-metatitle-generator`, `shopify-altext-generator`, `shopify-seo-mutation-batcher` |
| **Ideation** | `shopify-instagram-ideator`, `shopify-product-ideator`, `shopify-cultural-calendar` |
| **Campagne** | `shopify-cultural-campaign-drafter`, `shopify-instagram-publisher` |
| **Messaging** | `hermes-email-sender` |
| **DevOps** | `shopify-cron-output-watcher`, `hermes-snapshot-diff-validator`, `hermes-storefront-http-verifier` |

Catalogue complet et fiches détaillées dans [`docs/SKILLS-REFERENCE.md`](./docs/SKILLS-REFERENCE.md).

---

## ⚙️ Helpers réutilisables `lib/`

### `lib/klaviyo-fetch.sh`
Façade unifiée API Klaviyo (revision `2024-10-15`). Cache 6h, retry exponentiel sur 429, 7 endpoints (`flows`, `campaigns`, `metrics`, `segments`, `lists`, `profiles-count`, `metric-aggregate`).

### `lib/theme.sh`
Library bash pour ops thème Shopify headless. 14 fonctions : `theme_get/backup/lint/diff/push/push_many/verify/duplicate/preview_url/delete/publish/list/safety_level/check_env`. Contourne l'absence du scope OAuth `write_themes` via **Theme Access token** (`shptka_`).

---

## 📚 Documentation

| Doc | Contenu |
|---|---|
| [`docs/OVERVIEW.md`](./docs/OVERVIEW.md) | Vue d'ensemble narrative du framework |
| [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) | Charter framework + niveaux d'autonomie + auto-amélioration |
| [`docs/AUTOMATION.md`](./docs/AUTOMATION.md) | 4 crons + hooks v0.14 + 14 règles STANDING + memory system |
| [`docs/SKILLS-REFERENCE.md`](./docs/SKILLS-REFERENCE.md) | Catalogue détaillé des 25 skills |
| [`docs/WORKSPACE-STRUCTURE.md`](./docs/WORKSPACE-STRUCTURE.md) | Structure du workspace + toolkit Node.js + workflow standard |
| [`docs/INTEGRATIONS.md`](./docs/INTEGRATIONS.md) | 16 APIs externes intégrées |
| [`docs/VPS-SETUP.md`](./docs/VPS-SETUP.md) | Spécifications techniques VPS + setup |
| [`docs/CONFIG-STRUCTURE.md`](./docs/CONFIG-STRUCTURE.md) | Architecture de configuration optimale |
| [`docs/PRODUCTION-CHECKLIST.md`](./docs/PRODUCTION-CHECKLIST.md) | Checklist de bascule test → prod |

---

## 🗂️ Structure du repo

```
.
├── README.md                 ← Tu es ici
├── GETTING-STARTED.md        ← Setup pour une nouvelle boutique
├── CONTRIBUTING.md           ← Comment contribuer
├── LICENSE                   ← MIT
├── docs/                     ← Documentation framework générique
├── skills/                   ← 25 SKILL.md atomiques
├── lib/                      ← Helpers bash réutilisables (theme.sh, klaviyo-fetch.sh)
├── config/                   ← Templates de configuration
│   ├── .env.template
│   ├── cron-jobs.json.template
│   ├── STORE-BRAND.md.template
│   ├── MISSION.md.template
│   ├── MEMORY.md.template
│   ├── STANDING-CORE.md.template
│   └── cultural-events.json.template
├── examples/azamoul/         ← Cas d'étude live (marque française)
└── archive/                  ← Historique du projet pilote
```

---

## 🎯 Cas d'étude live — Azamoul

Hermes tourne en production depuis mai 2026 sur [azamoul.com](https://azamoul.com), une marque française qui valorise la culture amazighe (berbère) via la mode et les accessoires.

Quelques métriques opérationnelles :
- ~96 produits actifs, 19 collections, 11 pages
- 4 crons actifs (88 runs cumulés sans erreur au 2026-05-27)
- 25 skills opérationnels (dont 1 créé automatiquement par l'agent en méta-revue dominicale)
- 1.08M tokens consommés sur 7 jours, ~6h de temps actif
- Bulk update de 62 produits textiles en un run (theme editor v1.1)

Tout le détail dans [`examples/azamoul/`](./examples/azamoul/).

---

## 🤝 Contribuer

Tu veux ajouter un skill, une intégration, un helper ? Voir [`CONTRIBUTING.md`](./CONTRIBUTING.md).

Convention de nommage :
- `shopify-*` pour les skills domaine Shopify (catalogue, theme, KPI, Klaviyo, Instagram, etc.)
- `hermes-*` pour les utilities framework (email, schema-guard, validators)

---

## 📄 License

[MIT](./LICENSE) — Copyright (c) 2026 Rayan Djebar

---

## 🙏 Crédits

Hermes Agent est développé sur l'Agent SDK Anthropic + Hermes runtime (v0.14.0). Ce framework est né du besoin opérationnel de la boutique Azamoul, puis a été généralisé pour servir n'importe quel marchand Shopify.
