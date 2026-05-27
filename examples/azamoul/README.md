# Case Study — Azamoul

> Live instance of Hermes Framework on the [Azamoul](https://azamoul.com) store, a French brand that promotes Amazigh (Berber) culture through fashion and accessories.
>
> This doc shows **a complete example** of Hermes configuration for a real store running in production since May 2026.

---

## Identity

| Field | Value |
|---|---|
| Brand | **Azamoul** |
| Domain | [azamoul.com](https://azamoul.com) |
| Shopify | `azamoul-symboles-berberes.myshopify.com` (Basic, EUR) |
| Plan | Shopify Basic — Europe/Paris |
| Catalog | ~96 active products, 19 collections, 11 pages |
| Universe | Fashion, jewelry, decor, Amazigh culture accessories (tifinagh, yaz ⵣ, kabyle) |
| Instagram | [@azamoul](https://instagram.com/azamoul) — 5,769 followers, 116 posts (83% reels) |
| Made in | France |

---

## Hermes operational metrics (as of 2026-05-27)

| Metric | Value |
|---|---|
| Operational skills | **25** (21 shopify-* + 4 hermes-*) |
| Active crons | 4 (88 cumulative runs without errors) |
| API integrations | 16 (Shopify, Klaviyo, Gemini, OpenRouter, GSC, Firecrawl, SMTP, Telegram, ...) |
| Tokens (7d) | 1,083,362 |
| Active time (7d) | ~6h 9m |
| Sessions (7d) | 4 (3 cron + 1 CLI) |
| Skills auto-created by meta-review | 1 (azamoul-cron-output-watcher) |
| Cumulative Shopify mutations | 62 textile products bulk-updated (on 2026-05-24) |

---

## Configuration files (Azamoul instance)

| File | Content |
|---|---|
| [`MISSION.md`](./MISSION.md) | Full charter of the agent for Azamoul (~19KB) |
| [`STORE-BRAND.md`](./STORE-BRAND.md) | Mandatory Amazigh vocabulary + brand-specific autonomy levels |
| [`brand-knowledge.md`](./brand-knowledge.md) | 4 identified competitors + 10 Amazigh events |
| [`cultural-events.json`](./cultural-events.json) | Calendar in JSON: Yennayer, Aïd, Tafsut, Tafaska, Imilchil, etc. |
| [`MEMORY.md`](./MEMORY.md) | Store persistent facts (53 condensed lines) |
| [`cron-jobs.json`](./cron-jobs.json) | The 4 real Azamoul crons (secret-sanitized) |
| [`HERMES-CONFIG-ACTUELLE.md`](./HERMES-CONFIG-ACTUELLE.md) | Full snapshot of Azamoul config (~24KB) |
| [`GUIDE-OPERATIONNEL.md`](./GUIDE-OPERATIONNEL.md) | Practical operational guide for Azamoul (~67KB) |

---

## Notable milestones

| Date | Milestone |
|---|---|
| 2026-05-11 | Phase 0 start (VPS provisioning, Hermes install) |
| 2026-05-13 | Phase 1+2 self-validation 9/10 PASS |
| 2026-05-14 | Grand Run W20 (5/6 authentic PASS) → Verdict GO Production |
| 2026-05-14 | Meta-review detects 2 patterns → PROPOSED skills (`cron-output-watcher`, `snapshot-diff-validator`) |
| **2026-05-20/21** | **Klaviyo wave**: 3 new skills + `klaviyo-fetch.sh` helper |
| 2026-05-21 | Hooks migration v0.13 → v0.14 (dict format + tool_input) |
| 2026-05-21 | MEMORY.md refactor 8166 → 3014 chars |
| 2026-05-24 | SMTP switch `djebar.rayan75` → `contact.azamoul@gmail.com` |
| **2026-05-24** | **`theme-editor` skill v1.0 then v1.1** (helper `theme.sh`, lint, duplicate-preview, multi-file atomic) |
| 2026-05-24 | First live use: 62 textile products bulk-updated with "Refund Policy" block |

---

## Brand vocabulary (excerpt)

```
amazigh, berbère, tifinagh, imazighen, yaz (ⵣ), azamoul, kabyle, djurdjura,
thilelli, dihya, aza, afzim, tiseghnest, tafaska, tamghra, asseggas, amegaz,
tafsut, tamejja, lawan, tameddurt
```

See [`STORE-BRAND.md`](./STORE-BRAND.md) for the meaning of each term.

---

## Identified competitors

| # | Brand | URL | Niche | Azamoul differentiation |
|---|---|---|---|---|
| 1 | Bahya Brand | [bahyabrand.com](https://bahyabrand.com) | Streetwear, statement t-shirts | Tifinagh motifs on modern cuts |
| 2 | Maison Amazira | [kabylefashion.com](https://kabylefashion.com) | Sacred heritage couture | Ready-to-wear vs haute couture |
| 3 | Princesse Berbère | [princesseberbere.com](https://princesseberbere.com) | Tradition + modernity fashion | Review reassurance + IG engagement |
| 4 | Artisanat Shop | [artisanat-shop.com](https://artisanat-shop.com) | Berber artisan jewelry | Modernized industrializable Aza/Afzim |

---

## How to use this case study

1. **If you're new to Hermes**: read [`../../GETTING-STARTED.md`](../../GETTING-STARTED.md) first, then come back here to see a concrete example of each filled config file.

2. **If you're adapting Hermes to your brand**: copy the templates from `../../config/` and adapt them to your brand, taking inspiration from the structure and level of detail shown here.

3. **If you're looking for a specific item**:
   - Brand vocabulary → [`STORE-BRAND.md`](./STORE-BRAND.md)
   - Event calendar → [`cultural-events.json`](./cultural-events.json)
   - Competitors + positioning → [`brand-knowledge.md`](./brand-knowledge.md)
   - Parameterized crons → [`cron-jobs.json`](./cron-jobs.json)
   - Full mission charter → [`MISSION.md`](./MISSION.md)
   - Practical operational guide → [`GUIDE-OPERATIONNEL.md`](./GUIDE-OPERATIONNEL.md)

---

## What's sanitized vs what remains

**Sanitized in these files**:
- VPS IP, OVH hostname, Telegram chat ID → placeholders `<VPS_IP>`, `<VPS_HOSTNAME>`, `<TELEGRAM_USER_ID>`
- No token, password, or API key in clear
- `.env` not versioned (see `.gitignore`)

**Remains visible** (public metadata):
- Brand name, domain, Shopify handle (all already publicly available on azamoul.com)
- Email `contact.azamoul@gmail.com` (publicly listed on the store)
- Amazigh vocabulary (public culture)
- Skill and helper structure

---

## Note on language

This case study contains both English (framework-facing documentation) and French (the original operational content for the French brand). The full operational guide (`GUIDE-OPERATIONNEL.md`), mission charter (`MISSION.md`), and config snapshot (`HERMES-CONFIG-ACTUELLE.md`) remain in French as they represent the actual artifacts running in production for this French-speaking store.

---

## Credits

Hermes Framework was created by **Rayan Djebar** during an internship at Azamoul (BUT2, May 2026). The generic framework was extracted by generalizing this live instance.

See [`../../README.md`](../../README.md) for the framework vitrine and [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) to contribute.
