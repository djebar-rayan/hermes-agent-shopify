# Hermes — Reusable AI Growth Agent Framework for Shopify

> **Hermes** is an autonomous AI agent framework designed to drive end-to-end commercial growth for a Shopify store — SEO, content, images, UX, emailing, Instagram posts, and even Liquid theme code.
>
> This repo contains **25 reusable skills**, **4 weekly crons**, **16 ready-to-use API integrations**, and a **live case study** ([`examples/azamoul/`](./examples/azamoul/)) showing Hermes in production on a real store.

`v0.14.0` · **25 skills** · 4 crons · 16 integrations · MIT License

---

## ⚡ TL;DR

Hermes monitors the store every day, identifies what can be improved, prepares the changes, requests merchant validation via Telegram + email, and applies them after approval. It learns from every action and improves its own future decisions — including by **automatically creating new skills** when a pattern becomes recurrent.

**Automated weekly cycle**:
- 🗓️ **Monday 9am** — Weekly performance report (Shopify + Klaviyo KPIs, diagnostics, predictions)
- 🎨 **Saturday 10am** — Creative email (1 product idea + 1 Instagram idea + 1 email campaign draft)
- 🔄 **Sunday 8pm** — Self-improvement meta-review (can create new skills)
- 👁️ **Every 6 hours** — Conversion watchdog (silent by default, alerts on drops)

---

## 🚀 Get Started

You have a Shopify store and want to install Hermes on it? Follow the guide:

👉 **[`GETTING-STARTED.md`](./GETTING-STARTED.md)** — Step-by-step setup for a new store

Want to see Hermes in production on a real store?

👉 **[`examples/azamoul/`](./examples/azamoul/)** — Complete case study (French brand, ~96 products, 4 active crons since May 2026)

---

## 🏗️ Architecture

```
        ┌─────────────────────────────────────────────────┐
        │           docs/ARCHITECTURE.md                  │
        │   (framework charter — read each cycle)         │
        └─────────────────────────────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────────┐
            │  STANDING-CORE (11 rules)   │ ◄── injected each session
            │  STORE-BRAND.md (3 rules)   │     via on_session_start hook
            │  MEMORY.md (facts)          │
            └─────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │           25 atomic SKILLS               │
        │  21 shopify-*  +  4 hermes-* (utilities) │
        └─────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       ┌──────────┐   ┌──────────┐  ┌──────────────┐
       │  4 CRONS │   │  Manual  │  │ Hook events  │
       │  weekly  │   │ triggers │  │  (auto-log)  │
       └──────────┘   └──────────┘  └──────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      OUTPUTS (report, email, Telegram,  │
        │      Shopify mutation, theme files,     │
        │      campaign draft)                    │
        └─────────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │   learnings.md (append-only) → memory   │
        │   OpenViking (cross-session RAG)        │
        └─────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Version |
|---|---|
| Hermes Agent | `v0.14.0` |
| Python | 3.11+ |
| Node.js | 20+ |
| Shopify CLI | 3.94+ |
| Memory provider | OpenViking 0.3.16 (port 1933, local embedding) |
| Primary LLM | `google/gemini-3.1-flash-lite-preview` via OpenRouter |
| Context length | 262,144 tokens |
| Host | Any Ubuntu 24.04+ VPS |

---

## 🧠 25 Operational Skills

| Category | Skills |
|---|---|
| **Monitoring & reporting** | `shopify-weekly-perf-report`, `shopify-baseline-kpi-fetch`, `shopify-low-conversion-diagnostic`, `shopify-kpi-drop-watchdog` |
| **Klaviyo** | `shopify-klaviyo-weekly-report`, `shopify-klaviyo-campaign-ideator`, `shopify-klaviyo-drop-watchdog` |
| **E-commerce mutation** | `shopify-batch-executor`, `shopify-batch-rollback`, `shopify-catalog-gap-analyzer`, `shopify-theme-editor`, `hermes-schema-guard` |
| **Content / SEO** | `shopify-description-enricher`, `shopify-metatitle-generator`, `shopify-altext-generator`, `shopify-seo-mutation-batcher` |
| **Ideation** | `shopify-instagram-ideator`, `shopify-product-ideator`, `shopify-cultural-calendar` |
| **Campaign** | `shopify-cultural-campaign-drafter`, `shopify-instagram-publisher` |
| **Messaging** | `hermes-email-sender` |
| **DevOps** | `shopify-cron-output-watcher`, `hermes-snapshot-diff-validator`, `hermes-storefront-http-verifier` |

Full catalog and detailed sheets in [`docs/SKILLS-REFERENCE.md`](./docs/SKILLS-REFERENCE.md).

---

## ⚙️ Reusable Helpers `lib/`

### `lib/klaviyo-fetch.sh`
Unified Klaviyo API facade (revision `2024-10-15`). 6h cache, exponential retry on 429, 7 endpoints (`flows`, `campaigns`, `metrics`, `segments`, `lists`, `profiles-count`, `metric-aggregate`).

### `lib/theme.sh`
Bash library for headless Shopify theme operations. 14 functions: `theme_get/backup/lint/diff/push/push_many/verify/duplicate/preview_url/delete/publish/list/safety_level/check_env`. Works around the missing `write_themes` OAuth scope via **Theme Access token** (`shptka_`).

---

## 📚 Documentation

| Doc | Content |
|---|---|
| [`docs/OVERVIEW.md`](./docs/OVERVIEW.md) | Narrative overview of the framework |
| [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) | Framework charter + autonomy levels + self-improvement |
| [`docs/AUTOMATION.md`](./docs/AUTOMATION.md) | 4 crons + v0.14 hooks + 14 STANDING rules + memory system |
| [`docs/SKILLS-REFERENCE.md`](./docs/SKILLS-REFERENCE.md) | Detailed catalog of the 25 skills |
| [`docs/WORKSPACE-STRUCTURE.md`](./docs/WORKSPACE-STRUCTURE.md) | Workspace structure + Node.js toolkit + standard workflow |
| [`docs/INTEGRATIONS.md`](./docs/INTEGRATIONS.md) | 16 integrated external APIs |
| [`docs/VPS-SETUP.md`](./docs/VPS-SETUP.md) | VPS technical specifications + setup |
| [`docs/CONFIG-STRUCTURE.md`](./docs/CONFIG-STRUCTURE.md) | Optimal configuration architecture |
| [`docs/PRODUCTION-CHECKLIST.md`](./docs/PRODUCTION-CHECKLIST.md) | Test → prod switchover checklist |

---

## 🗂️ Repo Structure

```
.
├── README.md                 ← You are here
├── GETTING-STARTED.md        ← Setup for a new store
├── CONTRIBUTING.md           ← How to contribute
├── LICENSE                   ← MIT
├── docs/                     ← Generic framework documentation
├── skills/                   ← 25 atomic SKILL.md
├── lib/                      ← Reusable bash helpers (theme.sh, klaviyo-fetch.sh)
├── config/                   ← Configuration templates
│   ├── .env.template
│   ├── cron-jobs.json.template
│   ├── STORE-BRAND.md.template
│   ├── MISSION.md.template
│   ├── MEMORY.md.template
│   ├── STANDING-CORE.md.template
│   └── cultural-events.json.template
├── examples/azamoul/         ← Live case study (French brand)
└── archive/                  ← History of the pilot project
```

---

## 🎯 Live Case Study — Azamoul

Hermes has been running in production since May 2026 on [azamoul.com](https://azamoul.com), a French brand that celebrates Amazigh (Berber) culture through fashion and accessories.

A few operational metrics:
- ~96 active products, 19 collections, 11 pages
- 4 active crons (88 cumulative runs with no errors as of 2026-05-27)
- 25 operational skills (including 1 automatically created by the agent during a Sunday meta-review)
- 1.08M tokens consumed over 7 days, ~6h of active time
- Bulk update of 62 textile products in a single run (theme editor v1.1)

Full details in [`examples/azamoul/`](./examples/azamoul/).

---

## 🤝 Contributing

Want to add a skill, integration, or helper? See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

Naming convention:
- `shopify-*` for Shopify domain skills (catalog, theme, KPI, Klaviyo, Instagram, etc.)
- `hermes-*` for framework utilities (email, schema-guard, validators)

---

## 📄 License

[MIT](./LICENSE) — Copyright (c) 2026 Rayan Djebar

---

## 🙏 Credits

Hermes Agent is built on the Anthropic Agent SDK + Hermes runtime (v0.14.0). This framework was born from the operational needs of the Azamoul store, then generalized to serve any Shopify merchant.
