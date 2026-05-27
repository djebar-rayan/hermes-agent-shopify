# Skills Reference — Catalog of the 25 skills

> Catalog of the 25 reusable skills shipped with the Hermes framework.
> 21 prefixed `shopify-*` (Shopify domain) + 4 prefixed `hermes-*` (framework utilities).

---

## Overview

| # | Name | Version | Category | Invoked by cron | Helper dep |
|---|---|---|---|---|---|
| 1 | shopify-altext-generator | 1.0.0 | seo-content | — (batch-executor companion) | — |
| 2 | shopify-baseline-kpi-fetch | 1.0.0 | monitoring | weekly-perf-report | — |
| 3 | shopify-batch-executor | 1.0.0 | ecommerce-mutation | — (manual + /yes) | hermes-schema-guard |
| 4 | shopify-batch-rollback | 1.0.0 | ecommerce-mutation | — (safety net) | — |
| 5 | shopify-catalog-gap-analyzer | 1.0.0 | ecommerce-audit | — (pre-batch) | — |
| 6 | shopify-cron-output-watcher | 0.1.0 | devops (auto-proposed) | — | — |
| 7 | shopify-cultural-calendar | 1.0.0 | ideation | weekly-ideas + weekly-meta-review | — |
| 8 | shopify-cultural-campaign-drafter | 1.0.0 | campaign | — (D-21 to D-7) | shopify-cultural-calendar |
| 9 | shopify-description-enricher | 1.0.0 | content | — (batch-executor companion) | — |
| 10 | hermes-email-sender | 1.0.0 | messaging | — (SMTP factorization) | — |
| 11 | shopify-instagram-ideator | 1.0.0 | ideation | weekly-ideas | — |
| 12 | shopify-instagram-publisher | 2.0.0 | campaign (approval gate) | — | — |
| 13 | shopify-klaviyo-campaign-ideator | 1.0.0 | klaviyo-content | weekly-ideas | klaviyo-fetch.sh |
| 14 | shopify-klaviyo-drop-watchdog | 1.0.0 | klaviyo-monitoring | watchdog-conversion | klaviyo-fetch.sh |
| 15 | shopify-klaviyo-weekly-report | 1.0.0 | klaviyo-monitoring | weekly-perf-report | klaviyo-fetch.sh |
| 16 | shopify-kpi-drop-watchdog | 1.0.0 | monitoring | watchdog-conversion | — |
| 17 | shopify-low-conversion-diagnostic | 1.0.0 | ecommerce-audit | weekly-perf-report | — |
| 18 | shopify-metatitle-generator | 1.0.0 | seo-content | — (batch-executor companion) | — |
| 19 | shopify-product-ideator | 1.0.0 | ideation | weekly-ideas | — |
| 20 | shopify-seo-mutation-batcher | 0.1.0-PROPOSED | seo (auto-proposed) | — | hermes-schema-guard |
| 21 | hermes-schema-guard | 1.0.0 | ecommerce (reference) | — (mandatory dep) | — |
| 22 | hermes-snapshot-diff-validator | 0.1.0 | devops (auto-proposed) | — | — |
| 23 | hermes-storefront-http-verifier | 0.1.0-PROPOSED | monitoring | — | — |
| 24 | shopify-theme-editor | 1.1.0 | ecommerce-mutation | — (manual) | theme.sh |
| 25 | shopify-weekly-perf-report | 1.0.0 | monitoring | weekly-perf-report + weekly-meta-review | — |

Legend:
- **v1.0.0**: promoted stable skill
- **v0.1.0**: auto-proposed skill from a meta-review (documented pattern)
- **v0.1.0-PROPOSED**: proposed skill awaiting merchant validation

---

## Critical skills — Detailed cards

### Weekly monitoring & report

#### `shopify-weekly-perf-report` v1.0.0
- **When**: cron `<store>-weekly-perf-report` (Monday 9am), or explicit "perf report" request
- **Procedure**:
  1. Refresh `store-data/` if > 7d (`node fetch-store-data.js`, ~115s)
  2. Extract KPIs N and N-1 (sessions, conversions, AOV, revenue, abandoned carts)
  3. Compare % deltas
  4. Generate `reports/YYYY-Www-perf.md` (structure: KPI snapshot, top 3 wins/losses, diagnostic, executed actions + impact, proposed actions 🟢/🟡, W+1 predictions)
  5. 20-line Telegram summary + SMTP email via inline Python snippet (mandatory `EMAIL_SMTP_OK` sentinel)

#### `shopify-low-conversion-diagnostic` v1.0.0
- **When**: product > 50 views/7d without add-to-cart, or flagged in weekly report
- **Procedure**: 12-point checklist per product:
  1. Images ≥3 ≥800×800 + alt-text
  2. `descriptionHtml` ≥150 words structured HTML
  3. SEO title 30-70 chars, meta description 50-160
  4. 📦 shipping block at start (regex check)
  5. Price aligned with category (competitor reference)
  6. Variants with image
  7. Reviews ≥3
  8. Stock
  9. Tags ≥5
  10. Collections
  11. Mobile (mobile snapshot)
  12. Internal linking

#### `shopify-catalog-gap-analyzer` v1.0.0
- **When**: Phase 2+, before each `shopify-batch-executor`, or complementary weekly cron
- **Procedure**:
  1. Phase check via `MEMORY.md` (forbidden in Phase 1 / `HERMES_MODE=test` depending on config)
  2. Fetch GraphQL `products(first:250)` → tags, descriptionHtml, images
  3. Compute `tagsCount`, `hasShippingBlockFirst`, `imagesCount`
  4. Categorize (categories defined in `STORE-BRAND.md`)
  5. Diff vs target tags
  6. Write `audits/gap-analysis-YYYY-MM-DD.md` with batches of 10
  7. Telegram summary top 5

---

### E-commerce mutation

#### `shopify-batch-executor` v1.0.0 ⚠️ critical
- **When**: after gap-analyzer to apply green 🟢 actions, on explicit "execute batch N" request. **Forbidden in Phase 1**.
- **Reads `$HERMES_MODE`**:
  - `test`: apply+rollback in same run (safe by default)
  - `prod`: persistent + Telegram /yes required
  - Variable missing / other value → test behavior by default
- **Procedure**:
  1. Phase check via MEMORY.md
  2. Before snapshot in `batches/YYYY-Www-batchN-before.json` (max 10 products)
  3. Generate JSON diff preview + auto-generated bash rollback script
  4. Telegram + email validation with /yes /no /edit (10-min timeout)
  5. Sequential execution (2s spacing anti Shopify rate-limit 1.4 req/s)
  6. After snapshot + markdown diff + log in learnings.md
- **Mandatory dep**: `hermes-schema-guard`

#### `hermes-schema-guard` v1.0.0
- **When**: BEFORE any Shopify mutation (productCreate/Update/Delete, collectionCreate/Delete, productVariantsBulkUpdate, urlRedirect*). Auto trigger if `shopify store execute --allow-mutations`.
- **Procedure**:
  - Copy EXACTLY the validated GraphQL fragment listed in the SKILL.md
  - If mutation missing from catalog: `__type(name:...)` introspection first, then add to skill after success with timestamp
  - Validated fragments referenced: productCreate/Delete/Update, collectionCreate/Delete, productVariantsBulkUpdate
- **Known anti-pitfalls**:
  - No `createdAt` on Collection
  - No `createdAt`/`updatedAt` on productCreate payload

#### `shopify-theme-editor` v1.1.0
- **When**: incremental theme file edit (CSS, section, snippet, JSON template); custom template creation; visual redesign (→ mandatory duplicate-preview workflow)
- **NEVER use for**: product/page/blog/collection content
- **Procedure**:
  1. `set -a; . /root/.hermes/.env; set +a`
  2. `. lib/theme.sh && theme_check_env`
  3. `theme_safety_level $PATH` → safety level
  4. **green** level (assets/, snippets/): backup + lint + direct push
  5. **yellow** level (sections/, templates/, locales/): backup + lint + diff + Telegram /yes + push + verify
  6. **red-block** level (layout/, settings_schema.json): refuses unless exact text override "I confirm \<action\> on \<file\>"
  7. **red-forbidden** level (settings_data.json): refuses even with /yes
- **Workflows**: A (single file low-risk), B (multi-file atomic via `theme_push_many`), C (duplicate-preview for redesign)
- **Live theme ID**: `$LIVE_THEME_ID` (configurable)
- **Backups**: `$HERMES_WORKSPACE/theme-backups/` with pattern `<filename>.theme<id>.<UTC-ts>Z.bak`

---

### Klaviyo (3 skills, depend on `lib/klaviyo-fetch.sh`)

#### `shopify-klaviyo-weekly-report` v1.0.0
- **When**: cron `<store>-weekly-perf-report` (injected after Shopify KPI section), or "Klaviyo report" request
- **Procedure**:
  1. Source `.env` + `klaviyo-fetch.sh` helper (6h cache)
  2. Fetch `flows`, `metrics`, `campaigns`
  3. Windows N (today-7) vs N-1 (today-14 → today-7)
  4. For each live flow: aggregate `Opened Email`, `Clicked Email`, `Bounced`, `Unsubscribed`, `Placed Order` via `metric-aggregate <id> day <since> <until>`
  5. Compute open rate, click rate, attributed revenue, % delta (n/a if N-1 = 0)
  6. Markdown section injected between `<!-- KLAVIYO_SECTION_START -->` and `<!-- KLAVIYO_SECTION_END -->` markers in `reports/YYYY-Www-perf.md`
- **🟢 status**: open rate > 20% AND click rate > 2%

#### `shopify-klaviyo-campaign-ideator` v1.0.0
- **When**: cron `<store>-weekly-ideas`, in addition to `shopify-product-ideator` and `shopify-instagram-ideator`
- **Procedure**:
  1. klaviyo-fetch.sh helper → `segments`, `lists`, historical `campaigns`
  2. Invoke `shopify-cultural-calendar` to identify event D-21 to D-7 (read from `$HERMES_WORKSPACE/cultural-events.json`)
  3. Analyze history of similar campaigns (best subject, best CTA, best time)
  4. Markdown draft: target segment + volume, 3 A/B/C subject variants, preview text 50-90 chars, body structure (hook, contextual intro, CTA — mandatory vocab per STORE-BRAND.md)
  5. Archive in `campaigns/YYYY-Www-klaviyo-draft.md`
- **Read-only**: no Klaviyo mutation, manual UI copy-paste required

#### `shopify-klaviyo-drop-watchdog` v1.0.0
- **When**: cron `<store>-watchdog-conversion` every 6h. Never interactive.
- **Procedure**:
  1. 7d N and 7d N-1 aggregates on metric IDs (Opened, Clicked, Placed Order, Unsubscribed)
  2. Safeguard: n_min 50 sends otherwise silent abort
  3. Thresholds: open drop > 20pp, click drop > 30pp, revenue drop > 40%, unsub > 5%
  4. If zero alert: total silence (`{"wakeAgent":false}`)
  5. Otherwise: Telegram + wake-agent in prod mode

---

### Weekly ideation

#### `shopify-instagram-ideator` v1.0.0
- **When**: cron `<store>-weekly-ideas` 10am, or "Insta idea" request
- **Procedure**:
  1. Reads `brand-knowledge.md` + `learnings.md`
  2. Chooses format (carousel/reel/single/story) + theme (storytelling/edu/testimonial)
  3. FR+EN caption with hook/body/CTA (mandatory vocab per STORE-BRAND.md)
  4. 15 hashtags (5 large >100k + 5 medium 10k-100k + 5 niche <10k)
  5. Textual visual description (image generation unavailable in Test phase)
  6. Recommended date/time (optimal slot for your brand)

#### `shopify-product-ideator` v1.0.0
- **When**: cron `<store>-weekly-ideas` paired with `shopify-instagram-ideator`
- **Procedure**:
  1. Reads `store-data/products.md`, `collections.md`, `brand-knowledge.md` (catalog gap), historical `learnings.md`
  2. Identifies 1 opportunity with explicit market signal
  3. Card: name (+ cultural variation if relevant), category, 50-word description, why now, target price + estimated margin, competitors + differentiation, textual moodboard

#### `shopify-cultural-calendar` v1.0.0 (data-driven)
- **When**: before each commercial season, mention in perf report if event <14d, propose campaign in Saturday email
- **Procedure**:
  1. Reads `$HERMES_WORKSPACE/cultural-events.json` (template provided in `config/`, example in `examples/azamoul/`)
  2. Computes days remaining until each event
  3. If <14d: alert + propose email campaign + Insta + product
  4. Maintains a 6-month rolling index

**Note**: this skill is **data-driven**. You define your events in `cultural-events.json` (Christmas, Black Friday, cultural events, product launches, brand anniversaries, etc.). The skill contains NO hardcoded events.

---

### Auto-proposed skills (Sunday meta-review)

Skills emerging from patterns automatically detected by the meta-review cron:

| Skill | Version | Status |
|---|---|---|
| `shopify-cron-output-watcher` | 0.1.0 | documentary pattern from W20 meta-review of the Azamoul case |
| `hermes-snapshot-diff-validator` | 0.1.0 | documentary pattern |
| `shopify-seo-mutation-batcher` | 0.1.0-PROPOSED | awaiting merchant validation |
| `hermes-storefront-http-verifier` | 0.1.0-PROPOSED | awaiting merchant validation |

**Mechanism**: if recurrent pattern > 3 occurrences over 4 weeks detected in `learnings.md`, the cron `<store>-weekly-meta-review` automatically creates the corresponding SKILL.md. The merchant then validates the 0.1.0 → 1.0.0 promotion.

---

## `lib/` helpers

### `lib/klaviyo-fetch.sh` — Klaviyo API wrapper
- API revision: `2024-10-15`
- 6h UTC slot cache in `/root/.hermes/cache/klaviyo/`
- Exponential retry `2^attempt` on HTTP 429, max 3 attempts
- Exit codes: 0 (OK), 1 (key missing), 2 (API error), 3 (usage error)
- Consumed by the 3 Klaviyo skills

### `lib/theme.sh` — bash library for theme ops
- 14 exported functions (see [`INTEGRATIONS.md`](./INTEGRATIONS.md))
- Configurable constants: `LIVE_THEME_ID`, `SHOPIFY_STORE`, `HERMES_WORKSPACE`
- Consumed by `shopify-theme-editor` (and exposed for direct use in any future skill)

---

## Notable evolutions (Azamoul case study)

| Date | Evolution | Impact |
|---|---|---|
| 2026-05-13 | Phase 1+2 auto-validation | 9/10 PASS Phase 4 |
| 2026-05-14 | Grand Run W20 | GO Production verdict |
| 2026-05-14 | Meta-review detects patterns | 2 auto-PROPOSED skills |
| 2026-05-20/21 | Klaviyo wave | 3 new skills + unified helper |
| 2026-05-21 | Hook migration v0.13 → v0.14 | Dict format + `tool_input` payload |
| 2026-05-24 | `shopify-theme-editor` v1.0 then v1.1 | Theme Access workflow + `theme.sh` helper |
| 2026-05-24 | First live usage | 62 textile products bulk-update |

See [`../examples/azamoul/`](../examples/azamoul/) for the detailed case study.
