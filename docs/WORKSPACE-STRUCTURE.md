# Workspace Structure — `$HERMES_WORKSPACE/`

> The workspace is the working space specific to YOUR store. All artifacts produced by Hermes (reports, batches, campaigns, theme backups) are stored there. The framework in `/root/.hermes/` stays neutral and generic.
>
> See [`../examples/azamoul/`](../examples/azamoul/) for concrete examples of reports, meta-reviews, and brand-knowledge.

---

## 1. Typical tree

```
$HERMES_WORKSPACE/              (ex: /root/mystore-shopify/)
├── MISSION.md                  ← Permanent charter of the agent for YOUR store
├── STORE-BRAND.md              ← Vocabulary + autonomy levels + sensitivities
├── brand-knowledge.md          ← Competitors + USP + positioning
├── cultural-events.json        ← Important events/seasons
├── MEMORY.md                   ← Permanent store facts
├── learnings.md                ← Append-only journal (auto-logged by hook)
├── baseline-kpi-30j.md         ← Initial KPI snapshot (generated at install)
├── gsc-30j.md                  ← Google Search Console 30d (if GSC configured)
│
├── reports/                    ← Weekly reports (Monday-perf + Saturday-ideas)
├── meta-reviews/               ← Sunday meta-reviews
├── audits/                     ← Ad-hoc catalog quality audits
├── batches/                    ← productUpdate batches (preview + rollback)
├── campaigns/                  ← Klaviyo drafts per event
│   ├── <event-1>/
│   ├── <event-2>/
│   └── ...
├── theme-backups/              ← Liquid template backups before mutation
└── shopify-automation-toolkit/ ← Reusable Node.js toolkit (system core)
```

Environment variable: `HERMES_WORKSPACE=/root/<store_handle>-shopify` (configurable in `.env`).

---

## 2. Toolkit `shopify-automation-toolkit/`

Reusable Node.js module v1.0.0 (Node ≥18), zero npm dependency, driven by Markdown task files + Gemini.

### 2.1 `lib/` — Core modules

| File | Role |
|---|---|
| `shopify-graphql.js` | GraphQL Admin client via `shopify store execute` — critical rules: `--query-file` (never inline), `stdio: 'inherit'`, no `.data` wrapper |
| `config.js` | `.env` loading, constants, paths |
| `image-upload.js` | Shopify Files upload (`stagedUploadsCreate` → `resource: PRODUCT_IMAGE`) |
| `gemini-image.js` | Image generation via Gemini Image (flash-image-preview) |
| `filter-dsl.js` | Mini product filtering language |
| `store-data.js` | Reading `store-data/` dumps |
| `gemini-vision.js` | Visual product audit via Gemini Vision |
| `task-file.js` | Markdown task file parser |
| `gemini-text.js` | Gemini text generation (descriptions, SEO) |
| `cli.js` | CLI utilities (sleep, args) |
| `image-validate.js` | Image validation (dimensions, format, size) |
| `image-download.js` | Image download from URLs |
| `text.js` | `stripHtml`, `wordCount`, `escapeMd`, `trunc` |
| `builders/` | Sub-modules: `content-prompts.js`, `handle.js`, `seo-meta.js`, `shipping.js`, `translit-presets/` |

### 2.2 Action modules

```
audit/        audit.js, full-audit.js, examples/(content-thin, images-low, seo-missing)
content/      handle-normalize.js, update-collections.js, update-pages.js, update-products.js
              examples/(collections-descriptions, enrich-descriptions, normalize-handles, shipping-block)
seo/          seo-update.js, examples/(meta-titles, meta-descriptions, alt-texts)
images/       image-alt.js, image-audit.js, image-generate.js, image-upload.js, visual-audit.js
              examples/(audit-images, audit-visual, generate-multi-variant, update-alt-texts)
integrations/ klaviyo/(klaviyo-export.js), shopify-email/(adapt-templates.js)
queries/      *.graphql files (stored queries)
tasks/        _template.md, README.md (Markdown task files)
docs/         COMMAND_REFERENCE, GEMINI_SETUP, QUICK_START, SHOPIFY_AUTH, SKILLS, TASK_FORMAT, TROUBLESHOOTING
store-data/   Markdown dumps: products.md, collections.md, customers.md, orders.md,
              pages.md, metafields.md, navigation.md, redirects.md, store-meta.md
```

### 2.3 `fetch-store-data.js` — Initial extractor

Read-only, feeds `store-data/` with one Markdown file per category. Local source of truth, replayable at will. Typical duration: 60-180s depending on catalog size.

### 2.4 npm scripts

```bash
npm run fetch              # node fetch-store-data.js
npm run audit              # targeted audit via task file
npm run audit:full         # full catalog audit
npm run image:audit        # image audit (dimensions, alt-text)
npm run image:visual-audit # visual audit Gemini Vision
npm run klaviyo:export     # legacy Klaviyo export
npm run klaviyo:adapt      # Shopify Email → Klaviyo template adaptation
npm run syntax-check       # checks all .js parse
npm run test:shopify       # test-shopify-connection.js
```

---

## 3. Standard workflow

```
1. fetch-store-data.js          → Markdown dump of catalog (read-only)
2. audit/full-audit.js          → identifies weak products (description, SEO, images)
3. tasks/*.md (task file)       → describes the mutation to apply
4. content|seo|images/*.js      → executes via shopify-graphql.js
5. re-fetch                     → N+1 snapshot
6. hermes-snapshot-diff-validator → before/after diff archived in batches/
7. learnings.md                 → auto log by post_tool_call hook
```

**Hard rule in test phase**: any mutation is **ephemeral** (apply + rollback same run) until `HERMES_MODE=prod`.

---

## 4. Reports/

Weekly reports generated by crons are stored here.

Naming convention:
- `YYYY-Www-perf.md` — weekly perf report (Monday)
- `YYYY-Www-ideas.md` — Saturday creative email
- (See `meta-reviews/` for the Sunday meta-review)

See [`../examples/azamoul/reports-samples/`](../examples/azamoul/reports-samples/) for concrete examples.

---

## 5. Meta-reviews/

Auto-generated Sunday meta-reviews. Convention: `YYYY-Www-meta.md`.

Typical sections of a meta-review:
1. Review of actions executed this week (KPI impact measured or flagged for W+1)
2. Patterns identified (success / fail / to be skillified)
3. New skills proposed or automatically created
4. Cultural calendar watch (D-21, D-14, D-10, D-3)
5. W+1 forecasts

---

## 6. Batches/

All artifacts related to `shopify-batch-executor` Shopify mutations:

```
batches/
├── YYYY-Www-batchN-before.json    # Snapshot before mutation
├── YYYY-Www-batchN-preview.md     # Readable preview of changes
├── YYYY-Www-batchN-rollback.sh    # Auto-generated shell rollback script
├── YYYY-Www-batchN-after.json     # Snapshot after /yes applied
└── YYYY-Www-batchN-diff.md        # Readable before/after diff
```

**Rule**: max 10 products per batch (anti Shopify rate-limit).

---

## 7. Audits/

Ad-hoc catalog quality audits:
- `initial-catalog-audit.md` — generated at install Phase 0
- `phase2-gap-analysis-YYYY-MM-DD.md` — pre-batch gap-analyzer

---

## 8. Campaigns/

Klaviyo email campaign drafts, organized by event:

```
campaigns/
├── YYYY-Www-klaviyo-draft.md    # Weekly draft (Saturday-ideas)
├── <event-1>-<year>/             # Campaign dedicated to an event
│   ├── brief-visuel.md
│   ├── caption-instagram.md
│   ├── email-campagne.md
│   ├── handles-produits.json
│   └── planning.md
└── <event-2>-<year>/             # ditto
```

The merchant customizes events in `cultural-events.json`.

---

## 9. Theme-backups/

Backups of theme files BEFORE any modification by `shopify-theme-editor`.

Naming pattern: `<filename>.theme<theme_id>.<UTC-timestamp>Z.bak`

Ex: `templates__product.test-returns.json.theme<LIVE_THEME_ID>.2026-05-24T214907Z.bak`

The pattern includes the source theme ID to allow targeted rollback even if the live theme has changed in the meantime.

---

## 10. `MISSION.md` — Charter specific to the store

Template provided in `config/MISSION.md.template`. Recommended sections:
- **Mission**: autonomous growth of the X store
- **Current phase**: `HERMES_MODE=test` or `prod`
- **Monitored sources**: Shopify, GSC, Klaviyo, Instagram, etc.
- **Rhythm**: 4 crons + manual intervention
- **Autonomy levels**: points to STORE-BRAND.md for details
- **Self-improvement mechanisms** (5 framework mechanisms)
- **Verification**: standard checklist

The Azamoul version is in [`../examples/azamoul/MISSION.md`](../examples/azamoul/MISSION.md).

---

## 11. `STORE-BRAND.md` — Vocabulary and sensitivities

Template provided in `config/STORE-BRAND.md.template`. Sections:

- **Store identity**: name, URL, Shopify plan, currency, timezone
- **Mandatory vocabulary**: 10-20 keywords that MUST appear in any generated content
- **Standard HTML shipping block**: template of the block to insert at start of product description
- **Autonomy levels 🟢/🟡/🔴**: what Hermes can do alone, propose, or refuse
- **Sensitivities**: what to be careful about (legal, price, social)

See [`../examples/azamoul/STORE-BRAND.md`](../examples/azamoul/STORE-BRAND.md) for a complete example.

---

## 12. `brand-knowledge.md` — Competitors and positioning

Recommended sections:
- **Direct competitors** (5-10 brands with URL, niche, USP, differentiation opportunity)
- **Indirect competitors** (3-5)
- **Positioning**: where your brand sits vs them
- **Unique USP**: what differentiates you

---

## 13. `cultural-events.json` — Events to monitor

JSON format so `shopify-cultural-calendar` can read it programmatically:

```json
{
  "events": [
    {
      "name": "Event name",
      "date": "YYYY-MM-DD",
      "lead_days": 21,
      "category": "religious | commercial | cultural | seasonal",
      "campaign_type": "email | instagram | both",
      "vocabulary_boost": ["word1", "word2"]
    }
  ]
}
```

`lead_days` = how many days before the event Hermes should start proposing campaigns.

See [`../examples/azamoul/cultural-events.json`](../examples/azamoul/cultural-events.json) for a complete example (Yennayer, Aïd, Tafsut, etc.).
