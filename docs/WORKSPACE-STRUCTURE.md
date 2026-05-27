# Workspace Structure — `$HERMES_WORKSPACE/`

> Le workspace est l'espace de travail propre à TA boutique. Tous les artefacts produits par Hermes (rapports, batches, campagnes, theme backups) y sont stockés. Le framework dans `/root/.hermes/` reste neutre et générique.
>
> Voir [`../examples/azamoul/`](../examples/azamoul/) pour des exemples concrets de rapports, méta-revues, et brand-knowledge.

---

## 1. Arborescence type

```
$HERMES_WORKSPACE/              (ex: /root/mystore-shopify/)
├── MISSION.md                  ← Charte permanente de l'agent pour TA boutique
├── STORE-BRAND.md              ← Vocabulaire + niveaux autonomie + sensibilités
├── brand-knowledge.md          ← Concurrents + USP + positionnement
├── cultural-events.json        ← Événements/saisons importants
├── MEMORY.md                   ← Faits permanents boutique
├── learnings.md                ← Journal append-only (auto-logué par hook)
├── baseline-kpi-30j.md         ← Snapshot KPI initial (généré à l'install)
├── gsc-30j.md                  ← Google Search Console 30j (si GSC configuré)
│
├── reports/                    ← Rapports hebdo (lundi-perf + samedi-ideas)
├── meta-reviews/               ← Méta-revues dominicales
├── audits/                     ← Audits qualité catalogue ponctuels
├── batches/                    ← Batches productUpdate (preview + rollback)
├── campaigns/                  ← Drafts Klaviyo par événement
│   ├── <event-1>/
│   ├── <event-2>/
│   └── ...
├── theme-backups/              ← Sauvegardes templates Liquid avant mutation
└── shopify-automation-toolkit/ ← Toolkit Node.js réutilisable (cœur du système)
```

Variable d'environnement : `HERMES_WORKSPACE=/root/<store_handle>-shopify` (configurable dans `.env`).

---

## 2. Toolkit `shopify-automation-toolkit/`

Module Node.js réutilisable v1.0.0 (Node ≥18), zéro dépendance npm, pilotage par task files Markdown + Gemini.

### 2.1 `lib/` — Modules cœur

| Fichier | Rôle |
|---|---|
| `shopify-graphql.js` | Client GraphQL Admin via `shopify store execute` — règles critiques : `--query-file` (jamais inline), `stdio: 'inherit'`, pas d'enveloppe `.data` |
| `config.js` | Chargement `.env`, constantes, chemins |
| `image-upload.js` | Upload Shopify Files (`stagedUploadsCreate` → `resource: PRODUCT_IMAGE`) |
| `gemini-image.js` | Génération images via Gemini Image (flash-image-preview) |
| `filter-dsl.js` | Mini-langage de filtrage produits |
| `store-data.js` | Lecture des dumps `store-data/` |
| `gemini-vision.js` | Audit visuel produit via Gemini Vision |
| `task-file.js` | Parseur task files Markdown |
| `gemini-text.js` | Génération texte Gemini (descriptions, SEO) |
| `cli.js` | Utilitaires CLI (sleep, args) |
| `image-validate.js` | Validation images (dimensions, format, taille) |
| `image-download.js` | Download d'images depuis URLs |
| `text.js` | `stripHtml`, `wordCount`, `escapeMd`, `trunc` |
| `builders/` | Sous-modules : `content-prompts.js`, `handle.js`, `seo-meta.js`, `shipping.js`, `translit-presets/` |

### 2.2 Modules d'action

```
audit/        audit.js, full-audit.js, examples/(content-thin, images-low, seo-missing)
content/      handle-normalize.js, update-collections.js, update-pages.js, update-products.js
              examples/(collections-descriptions, enrich-descriptions, normalize-handles, shipping-block)
seo/          seo-update.js, examples/(meta-titles, meta-descriptions, alt-texts)
images/       image-alt.js, image-audit.js, image-generate.js, image-upload.js, visual-audit.js
              examples/(audit-images, audit-visual, generate-multi-variant, update-alt-texts)
integrations/ klaviyo/(klaviyo-export.js), shopify-email/(adapt-templates.js)
queries/      *.graphql files (queries stockées)
tasks/        _template.md, README.md (task files Markdown)
docs/         COMMAND_REFERENCE, GEMINI_SETUP, QUICK_START, SHOPIFY_AUTH, SKILLS, TASK_FORMAT, TROUBLESHOOTING
store-data/   Dumps Markdown : products.md, collections.md, customers.md, orders.md,
              pages.md, metafields.md, navigation.md, redirects.md, store-meta.md
```

### 2.3 `fetch-store-data.js` — Extracteur initial

Read-only, alimente `store-data/` avec un fichier Markdown par catégorie. Source of truth locale, rejouable à volonté. Durée typique : 60-180s selon la taille du catalogue.

### 2.4 Scripts npm

```bash
npm run fetch              # node fetch-store-data.js
npm run audit              # audit ciblé via task file
npm run audit:full         # audit complet catalogue
npm run image:audit        # audit images (dimensions, alt-text)
npm run image:visual-audit # audit visuel Gemini Vision
npm run klaviyo:export     # export Klaviyo legacy
npm run klaviyo:adapt      # adaptation templates Shopify Email → Klaviyo
npm run syntax-check       # vérifie tous les .js parsent
npm run test:shopify       # test-shopify-connection.js
```

---

## 3. Workflow standard

```
1. fetch-store-data.js          → dump Markdown du catalogue (read-only)
2. audit/full-audit.js          → identifie produits faibles (description, SEO, images)
3. tasks/*.md (task file)       → décrit la mutation à appliquer
4. content|seo|images/*.js      → exécute via shopify-graphql.js
5. re-fetch                     → snapshot N+1
6. hermes-snapshot-diff-validator → diff avant/après archivé dans batches/
7. learnings.md                 → log auto par hook post_tool_call
```

**Règle dure en phase test** : toute mutation est **éphémère** (apply + rollback même run) jusqu'à `HERMES_MODE=prod`.

---

## 4. Reports/

Les rapports hebdo générés par les crons sont stockés ici.

Convention de nommage :
- `YYYY-Www-perf.md` — rapport perf hebdo (lundi)
- `YYYY-Www-ideas.md` — email créatif samedi
- (Voir `meta-reviews/` pour la méta-revue dominicale)

Voir [`../examples/azamoul/reports-samples/`](../examples/azamoul/reports-samples/) pour des exemples concrets.

---

## 5. Meta-reviews/

Méta-revues dominicales auto-générées. Convention : `YYYY-Www-meta.md`.

Sections types d'une méta-revue :
1. Revue des actions exécutées cette semaine (impact KPI mesuré ou flagué pour W+1)
2. Patterns identifiés (success / fail / à skillifier)
3. Nouveaux skills proposés ou créés automatiquement
4. Veille calendrier culturel (J-21, J-14, J-10, J-3)
5. Prévisions S+1

---

## 6. Batches/

Tous les artefacts liés aux mutations Shopify de `shopify-batch-executor` :

```
batches/
├── YYYY-Www-batchN-before.json    # Snapshot avant mutation
├── YYYY-Www-batchN-preview.md     # Preview lisible des changements
├── YYYY-Www-batchN-rollback.sh    # Script rollback shell auto-généré
├── YYYY-Www-batchN-after.json     # Snapshot après /yes appliqué
└── YYYY-Www-batchN-diff.md        # Diff lisible avant/après
```

**Rule** : max 10 produits par batch (anti rate-limit Shopify).

---

## 7. Audits/

Audits qualité catalogue ponctuels :
- `initial-catalog-audit.md` — généré à l'install Phase 0
- `phase2-gap-analysis-YYYY-MM-DD.md` — gap-analyzer pré-batch

---

## 8. Campaigns/

Drafts de campagnes email Klaviyo, organisés par événement :

```
campaigns/
├── YYYY-Www-klaviyo-draft.md    # Draft hebdo (samedi-ideas)
├── <event-1>-<year>/             # Campagne dédiée à un événement
│   ├── brief-visuel.md
│   ├── caption-instagram.md
│   ├── email-campagne.md
│   ├── handles-produits.json
│   └── planning.md
└── <event-2>-<year>/             # idem
```

Le marchand customise les événements dans `cultural-events.json`.

---

## 9. Theme-backups/

Sauvegardes des fichiers du thème AVANT toute modification par `shopify-theme-editor`.

Pattern de nommage : `<filename>.theme<theme_id>.<UTC-timestamp>Z.bak`

Ex : `templates__product.test-returns.json.theme<LIVE_THEME_ID>.2026-05-24T214907Z.bak`

Le pattern inclut l'ID du thème source pour permettre rollback ciblé même si le thème live a changé entretemps.

---

## 10. `MISSION.md` — Charter spécifique à la boutique

Template fourni dans `config/MISSION.md.template`. Sections recommandées :
- **Mission** : la croissance autonome de la boutique X
- **Phase courante** : `HERMES_MODE=test` ou `prod`
- **Sources surveillées** : Shopify, GSC, Klaviyo, Instagram, etc.
- **Rythme** : 4 crons + intervention manuelle
- **Niveaux d'autonomie** : pointe vers STORE-BRAND.md pour le détail
- **Mécaniques d'auto-amélioration** (5 mécaniques framework)
- **Verification** : checklist standard

La version Azamoul est dans [`../examples/azamoul/MISSION.md`](../examples/azamoul/MISSION.md).

---

## 11. `STORE-BRAND.md` — Vocabulaire et sensibilités

Template fourni dans `config/STORE-BRAND.md.template`. Sections :

- **Identité boutique** : nom, URL, plan Shopify, devise, fuseau
- **Vocabulaire obligatoire** : 10-20 mots-clés qui DOIVENT apparaître dans tout contenu généré
- **Bloc HTML livraison standard** : template du bloc à insérer en début de description produit
- **Niveaux d'autonomie 🟢/🟡/🔴** : ce que Hermes peut faire seul, proposer, ou refuser
- **Sensibilités** : ce sur quoi il faut être prudent (légal, prix, social)

Voir [`../examples/azamoul/STORE-BRAND.md`](../examples/azamoul/STORE-BRAND.md) pour un exemple complet.

---

## 12. `brand-knowledge.md` — Concurrents et positionnement

Sections recommandées :
- **Concurrents directs** (5-10 marques avec URL, niche, USP, opportunité différenciation)
- **Concurrents indirects** (3-5)
- **Positionnement** : où ta marque se situe vs eux
- **USP unique** : ce qui te différencie

---

## 13. `cultural-events.json` — Événements à surveiller

Format JSON pour que `shopify-cultural-calendar` puisse le lire programmatiquement :

```json
{
  "events": [
    {
      "name": "Nom de l'événement",
      "date": "YYYY-MM-DD",
      "lead_days": 21,
      "category": "religieux | commercial | culturel | saisonnier",
      "campaign_type": "email | instagram | both",
      "vocabulary_boost": ["mot1", "mot2"]
    }
  ]
}
```

`lead_days` = combien de jours avant l'événement Hermes doit commencer à proposer des campagnes.

Voir [`../examples/azamoul/cultural-events.json`](../examples/azamoul/cultural-events.json) pour un exemple complet (Yennayer, Aïd, Tafsut, etc.).
