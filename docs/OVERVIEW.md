# Hermes Framework — Overview

> Narrative document to understand in 15 min what Hermes is, what it does, and how it fits together.
> For technical details: [`ARCHITECTURE.md`](./ARCHITECTURE.md), [`SKILLS-REFERENCE.md`](./SKILLS-REFERENCE.md), [`AUTOMATION.md`](./AUTOMATION.md).

---

## 1. Mission

**Hermes** is an autonomous AI agent framework that drives the commercial growth of a Shopify store by continuously optimizing every aspect (SEO, content, images, UX, emailing, Instagram posts, theme code) and proposing creative ideas every week.

The merchant configures their brand once (vocabulary, event calendar, autonomy levels), then Hermes:
- Watches the store every day
- Identifies what can be improved
- Prepares the changes
- Requests validation via Telegram + email
- Applies after approval
- Learns from every action

It improves its own future decisions, including by **creating new skills automatically** when a pattern becomes recurrent.

---

## 2. Store configuration

You configure your store in `$HERMES_WORKSPACE/` with these files:

| File | Contents |
|---|---|
| `MISSION.md` | Charter specific to your store (based on the framework template) |
| `STORE-BRAND.md` | Mandatory vocabulary, autonomy levels 🟢/🟡/🔴, sensitivities |
| `brand-knowledge.md` | Competitors, positioning, USP |
| `cultural-events.json` | Events/seasons important to your brand (Christmas, Black Friday, cultural events, launches...) |
| `MEMORY.md` | Permanent facts (product categories, Shopify plan, currency, timezone, etc.) |

See [`examples/azamoul/`](../examples/azamoul/) for a complete configuration example on a real brand.

---

## 3. Conceptual architecture

```
        ┌─────────────────────────────────────────────────┐
        │      docs/ARCHITECTURE.md (framework charter)   │
        │   (read every cycle, parameterized by MISSION.md) │
        └─────────────────────────────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────────┐
            │   STANDING-CORE (11 rules)  │ ◄── injected every session
            │   STORE-BRAND  (3 rules)    │     via on_session_start hook
            │   MEMORY.md (facts)         │
            └─────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │           25 atomic SKILLS              │
        │  21 shopify-*  +  4 hermes-* (utilities) │
        └─────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       ┌──────────┐   ┌──────────┐  ┌──────────────┐
       │  4 CRONS │   │ Manual   │  │ Hook events  │
       │  weekly  │   │ triggers │  │ (auto-log)   │
       └──────────┘   └──────────┘  └──────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      OUTPUTS (report, email, Telegram,  │
        │      Shopify mutation, theme files,     │
        │      email/Insta campaign draft)        │
        └─────────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │   learnings.md (append-only) → memory   │
        │   OpenViking (cross-session RAG)        │
        └─────────────────────────────────────────┘
```

---

## 4. What does Hermes do each day of the week?

| When | Cron | Skills invoked | Output |
|---|---|---|---|
| **Monday 9am** | `<store>-weekly-perf-report` | `shopify-weekly-perf-report` + `shopify-baseline-kpi-fetch` + `shopify-low-conversion-diagnostic` + `shopify-klaviyo-weekly-report` | `reports/YYYY-Www-perf.md` + Telegram summary + email. Shopify KPIs + Klaviyo section, top wins/losses, diagnostic, executed actions, proposed actions 🟢/🟡, W+1 predictions |
| **Tuesday-Friday** | (nothing scheduled) | — | Hermes sleeps. Available for manual intervention via `hermes chat`. |
| **Saturday 10am** | `<store>-weekly-ideas` | `shopify-instagram-ideator` + `shopify-product-ideator` + `shopify-cultural-calendar` + `shopify-klaviyo-campaign-ideator` | `reports/YYYY-Www-ideas.md` + email. 3 proposals: 1 product + 1 Instagram post + 1 Klaviyo campaign draft |
| **Sunday 8pm** | `<store>-weekly-meta-review` | `shopify-weekly-perf-report` + `shopify-cultural-calendar` | `meta-reviews/YYYY-Www-meta.md` + Telegram. Meta-review: reads `learnings.md` 7d, identifies 3 patterns, **creates a new skill if pattern >3 occurrences** |
| **Every 6h** | `<store>-watchdog-conversion` | bash script + `shopify-klaviyo-drop-watchdog` | Silent by default. Telegram only if conversion drop or Klaviyo drop |

---

## 5. The 25 skills by category

Complete catalog: [`SKILLS-REFERENCE.md`](./SKILLS-REFERENCE.md).

| Category | Skills |
|---|---|
| Monitoring & reporting | `shopify-weekly-perf-report`, `shopify-baseline-kpi-fetch`, `shopify-low-conversion-diagnostic`, `shopify-kpi-drop-watchdog` |
| Klaviyo | `shopify-klaviyo-weekly-report`, `shopify-klaviyo-campaign-ideator`, `shopify-klaviyo-drop-watchdog` |
| E-commerce mutation | `shopify-batch-executor`, `shopify-batch-rollback`, `shopify-catalog-gap-analyzer`, `shopify-theme-editor`, `hermes-schema-guard` |
| Content / SEO | `shopify-description-enricher`, `shopify-metatitle-generator`, `shopify-altext-generator`, `shopify-seo-mutation-batcher` |
| Weekly ideation | `shopify-instagram-ideator`, `shopify-product-ideator`, `shopify-cultural-calendar` |
| Campaign | `shopify-cultural-campaign-drafter`, `shopify-instagram-publisher` |
| Messaging | `hermes-email-sender` |
| Auto-proposed DevOps | `shopify-cron-output-watcher`, `hermes-snapshot-diff-validator`, `hermes-storefront-http-verifier` |

---

## 6. LLM model and stack

| Item | Default value |
|---|---|
| Primary provider | OpenRouter (https://openrouter.ai/api/v1) |
| Default model | `google/gemini-3.1-flash-lite-preview` |
| Alternative model | `google/gemini-3.1-pro-preview` (CLI sessions) |
| Fallback model | DeepSeek v4 Pro, Claude direct |
| Context length | 262,144 tokens |
| Request timeout | 1800s |
| Typical OpenRouter quota | $20/month pay-as-you-go |
| Timezone | Configurable (default Europe/Paris) |

**VPS stack**: Ubuntu 24.04+ · Python 3.11+ · Node 20+ · Shopify CLI 3.94+ · OpenViking 0.3.16 (port 1933) · Hermes Agent v0.14.0.

---

## 7. Autonomy levels

| Level | Description | Typical examples (to customize in `STORE-BRAND.md`) |
|---|---|---|
| 🟢 **Auto-execution** | Hermes applies without asking | alt-text, ASCII handles, simple tags, 📦 shipping block at start of description, empty SEO meta to fill, drafts |
| 🟡 **Proposes in 1-click** | Hermes prepares + validates via Telegram /yes | description enrichment, images, redirects, collections, reasonable price, Instagram post (forced dry mode), theme section edit |
| 🔴 **Never without validation** | Hermes refuses even on request | price > 5%, deletions, refunds, theme layout, direct Instagram post, legal modifications, `config/settings_data.json` |

The merchant MUST customize these levels in `$HERMES_WORKSPACE/STORE-BRAND.md` based on their own sensitivities.

---

## 8. Phase: TEST EXCLUSIVE by default

On install, Hermes starts in `HERMES_MODE=test`:
- **Test mode**: every mutation is apply + rollback in the same run (ephemeral)
- **Prod mode**: persistent mutation + mandatory Telegram /yes

This test phase serves as a learning period. The merchant confirms the right behaviors before switching to prod (modify `HERMES_MODE=prod` in `.env`).

Before the switch, see [`PRODUCTION-CHECKLIST.md`](./PRODUCTION-CHECKLIST.md).

---

## 9. Self-improvement — 5 mechanisms

1. **OpenViking memory** (`localhost:1933`): local embedding, cross-session RAG over all `MEMORY*.md` + `learnings.md` files
2. **Background curator**: automatic cleanup and compaction of current memory
3. **Automatic skill creation** in the Sunday meta-review cron: if a recurrent pattern > 3 occurrences over 4 weeks is detected in `learnings.md`, the cron creates a new `SKILL.md`
4. **`hermes insights --days 7`**: cost/tokens/models analysis per cron to detect drift
5. **`post_tool_call` hook**: every mutative action is auto-logged in `learnings.md` with 4 placeholders (before/after/conclusion/future) to fill in W+1

---

## 10. External integrations (16 APIs)

See [`INTEGRATIONS.md`](./INTEGRATIONS.md) for details.

**Main surfaces**:
- **Shopify** (Admin API + Theme Access for headless write_themes)
- **Klaviyo** (read-only, `klaviyo-fetch.sh` helper with 6h cache)
- **Gemini** (3 models: image, text, vision)
- **OpenAI** (gpt-4.1-nano fallback)
- **OpenRouter** (primary LLM)
- **Google Search Console** (service account, SEO performance)
- **Firecrawl** (competitive intelligence)
- **SMTP Gmail** (sending via inline Python snippet)
- **Telegram Bot** (/yes validation, watchdog alerts)

---

## 11. Reusable helpers (`lib/`)

### `klaviyo-fetch.sh`
Unified Klaviyo API facade with 6h cache and exponential retry on 429. 7 exposed endpoints. Consumed by the 3 Klaviyo skills.

### `theme.sh`
Bash library for headless Shopify theme ops. 14 functions (get/backup/lint/diff/push/push_many atomic/verify/duplicate/preview_url/delete/publish/list/safety_level/check_env). Works around the absence of the `write_themes` OAuth scope via Theme Access token. Consumed by `shopify-theme-editor`.

---

## 12. Get started

To install Hermes on your store: [`../GETTING-STARTED.md`](../GETTING-STARTED.md).

This agent is fully configurable via `$HERMES_WORKSPACE/STORE-BRAND.md`. See [`../examples/azamoul/`](../examples/azamoul/) for a complete case study of a French brand in production since May 2026.
