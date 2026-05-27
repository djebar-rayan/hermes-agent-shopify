# Skills Reference — Catalogue des 25 skills

> Catalogue des 25 skills réutilisables fournis avec le framework Hermes.
> 21 préfixés `shopify-*` (domaine Shopify) + 4 préfixés `hermes-*` (utilities framework).

---

## Vue d'ensemble

| # | Name | Version | Catégorie | Invoqué par cron | Helper dep |
|---|---|---|---|---|---|
| 1 | shopify-altext-generator | 1.0.0 | seo-content | — (compagnon batch-executor) | — |
| 2 | shopify-baseline-kpi-fetch | 1.0.0 | monitoring | weekly-perf-report | — |
| 3 | shopify-batch-executor | 1.0.0 | ecommerce-mutation | — (manuel + /yes) | hermes-schema-guard |
| 4 | shopify-batch-rollback | 1.0.0 | ecommerce-mutation | — (safety net) | — |
| 5 | shopify-catalog-gap-analyzer | 1.0.0 | ecommerce-audit | — (pré-batch) | — |
| 6 | shopify-cron-output-watcher | 0.1.0 | devops (auto-proposed) | — | — |
| 7 | shopify-cultural-calendar | 1.0.0 | ideation | weekly-ideas + weekly-meta-review | — |
| 8 | shopify-cultural-campaign-drafter | 1.0.0 | campagne | — (J-21 à J-7) | shopify-cultural-calendar |
| 9 | shopify-description-enricher | 1.0.0 | content | — (compagnon batch-executor) | — |
| 10 | hermes-email-sender | 1.0.0 | messaging | — (factorisation SMTP) | — |
| 11 | shopify-instagram-ideator | 1.0.0 | ideation | weekly-ideas | — |
| 12 | shopify-instagram-publisher | 2.0.0 | campagne (approval gate) | — | — |
| 13 | shopify-klaviyo-campaign-ideator | 1.0.0 | klaviyo-content | weekly-ideas | klaviyo-fetch.sh |
| 14 | shopify-klaviyo-drop-watchdog | 1.0.0 | klaviyo-monitoring | watchdog-conversion | klaviyo-fetch.sh |
| 15 | shopify-klaviyo-weekly-report | 1.0.0 | klaviyo-monitoring | weekly-perf-report | klaviyo-fetch.sh |
| 16 | shopify-kpi-drop-watchdog | 1.0.0 | monitoring | watchdog-conversion | — |
| 17 | shopify-low-conversion-diagnostic | 1.0.0 | ecommerce-audit | weekly-perf-report | — |
| 18 | shopify-metatitle-generator | 1.0.0 | seo-content | — (compagnon batch-executor) | — |
| 19 | shopify-product-ideator | 1.0.0 | ideation | weekly-ideas | — |
| 20 | shopify-seo-mutation-batcher | 0.1.0-PROPOSED | seo (auto-proposed) | — | hermes-schema-guard |
| 21 | hermes-schema-guard | 1.0.0 | ecommerce (reference) | — (dep obligatoire) | — |
| 22 | hermes-snapshot-diff-validator | 0.1.0 | devops (auto-proposed) | — | — |
| 23 | hermes-storefront-http-verifier | 0.1.0-PROPOSED | monitoring | — | — |
| 24 | shopify-theme-editor | 1.1.0 | ecommerce-mutation | — (manuel) | theme.sh |
| 25 | shopify-weekly-perf-report | 1.0.0 | monitoring | weekly-perf-report + weekly-meta-review | — |

Légende :
- **v1.0.0** : skill stable promu
- **v0.1.0** : skill auto-proposé issu d'une méta-revue (pattern documenté)
- **v0.1.0-PROPOSED** : skill proposé en attente validation marchand

---

## Skills critiques — Fiches détaillées

### Monitoring & rapport hebdo

#### `shopify-weekly-perf-report` v1.0.0
- **When** : cron `<store>-weekly-perf-report` (lundi 9h), ou demande explicite "rapport perf"
- **Procedure** :
  1. Refresh `store-data/` si > 7j (`node fetch-store-data.js`, ~115s)
  2. Extrait KPI N et N-1 (sessions, conversions, AOV, CA, paniers abandonnés)
  3. Compare deltas %
  4. Génère `reports/YYYY-Www-perf.md` (structure : KPI snapshot, top 3 wins/pertes, diagnostic, actions exécutées + impact, actions proposées 🟢/🟡, prédictions S+1)
  5. Résumé Telegram 20 lignes + email SMTP via snippet Python inline (sentinelle `EMAIL_SMTP_OK` obligatoire)

#### `shopify-low-conversion-diagnostic` v1.0.0
- **When** : produit > 50 vues/7j sans add-to-cart, ou flag rapport hebdo
- **Procedure** : checklist 12 points par produit :
  1. Images ≥3 ≥800×800 + alt-text
  2. `descriptionHtml` ≥150 mots structuré HTML
  3. SEO title 30-70 chars, meta description 50-160
  4. Bloc 📦 livraison en début (regex check)
  5. Prix aligné catégorie (référence concurrents)
  6. Variantes avec image
  7. Reviews ≥3
  8. Stock
  9. Tags ≥5
  10. Collections
  11. Mobile (snapshot mobile)
  12. Internal linking

#### `shopify-catalog-gap-analyzer` v1.0.0
- **When** : phase 2+, avant chaque `shopify-batch-executor`, ou cron hebdo complémentaire
- **Procedure** :
  1. Phase check via `MEMORY.md` (interdit Phase 1 / `HERMES_MODE=test` selon config)
  2. Fetch GraphQL `products(first:250)` → tags, descriptionHtml, images
  3. Calcule `tagsCount`, `hasShippingBlockFirst`, `imagesCount`
  4. Catégorise (catégories définies dans `STORE-BRAND.md`)
  5. Diff vs tags cibles
  6. Écrit `audits/gap-analysis-YYYY-MM-DD.md` avec batches de 10
  7. Résumé Telegram top 5

---

### E-commerce mutation

#### `shopify-batch-executor` v1.0.0 ⚠️ critique
- **When** : après gap-analyzer pour appliquer actions vertes 🟢, sur demande explicite "execute batch N". **Interdit en Phase 1**.
- **Lit `$HERMES_MODE`** :
  - `test` : apply+rollback même run (safe par défaut)
  - `prod` : persistant + /yes Telegram requis
  - Variable absente / autre valeur → comportement test par défaut
- **Procedure** :
  1. Phase check via MEMORY.md
  2. Snapshot avant dans `batches/YYYY-Www-batchN-before.json` (max 10 produits)
  3. Génère preview JSON diff + script rollback bash auto-généré
  4. Validation Telegram + email avec /yes /no /edit (timeout 10 min)
  5. Exécution séquentielle (espacement 2s anti rate-limit Shopify 1.4 req/s)
  6. Snapshot after + diff markdown + log learnings.md
- **Dep obligatoire** : `hermes-schema-guard`

#### `hermes-schema-guard` v1.0.0
- **When** : AVANT toute mutation Shopify (productCreate/Update/Delete, collectionCreate/Delete, productVariantsBulkUpdate, urlRedirect*). Trigger auto si `shopify store execute --allow-mutations`.
- **Procedure** :
  - Copier EXACTEMENT le fragment GraphQL validé listé dans le SKILL.md
  - Si mutation absente du catalogue : introspection `__type(name:...)` d'abord, puis ajout au skill après succès avec timestamp
  - Fragments validés référencés : productCreate/Delete/Update, collectionCreate/Delete, productVariantsBulkUpdate
- **Anti-pièges connus** :
  - Pas de `createdAt` sur Collection
  - Pas de `createdAt`/`updatedAt` sur productCreate payload

#### `shopify-theme-editor` v1.1.0
- **When** : modif incrémentale fichier thème (CSS, section, snippet, template JSON) ; création template custom ; refonte visuelle (→ workflow duplicate-preview obligatoire)
- **NE JAMAIS utiliser pour** : contenus produits/pages/blogs/collections
- **Procedure** :
  1. `set -a; . /root/.hermes/.env; set +a`
  2. `. lib/theme.sh && theme_check_env`
  3. `theme_safety_level $PATH` → niveau de sécurité
  4. Niveau **green** (assets/, snippets/) : backup + lint + push direct
  5. Niveau **yellow** (sections/, templates/, locales/) : backup + lint + diff + /yes Telegram + push + verify
  6. Niveau **red-block** (layout/, settings_schema.json) : refuse sauf override texte exact "I confirm \<action\> on \<file\>"
  7. Niveau **red-forbidden** (settings_data.json) : refuse même avec /yes
- **Workflows** : A (single file low-risk), B (multi-file atomique via `theme_push_many`), C (duplicate-preview pour refonte)
- **Live theme ID** : `$LIVE_THEME_ID` (paramétrable)
- **Backups** : `$HERMES_WORKSPACE/theme-backups/` avec pattern `<filename>.theme<id>.<UTC-ts>Z.bak`

---

### Klaviyo (3 skills, dépendent de `lib/klaviyo-fetch.sh`)

#### `shopify-klaviyo-weekly-report` v1.0.0
- **When** : cron `<store>-weekly-perf-report` (injecté après section KPI Shopify), ou demande "rapport Klaviyo"
- **Procedure** :
  1. Source `.env` + helper `klaviyo-fetch.sh` (cache 6h)
  2. Fetch `flows`, `metrics`, `campaigns`
  3. Fenêtres N (today-7) vs N-1 (today-14 → today-7)
  4. Pour chaque flow live : agrège `Opened Email`, `Clicked Email`, `Bounced`, `Unsubscribed`, `Placed Order` via `metric-aggregate <id> day <since> <until>`
  5. Calcule open rate, click rate, revenue attribué, delta % (n/a si N-1 = 0)
  6. Section markdown injectée entre marqueurs `<!-- KLAVIYO_SECTION_START -->` et `<!-- KLAVIYO_SECTION_END -->` dans `reports/YYYY-Www-perf.md`
- **Statut 🟢** : open rate > 20% ET click rate > 2%

#### `shopify-klaviyo-campaign-ideator` v1.0.0
- **When** : cron `<store>-weekly-ideas`, en complément de `shopify-product-ideator` et `shopify-instagram-ideator`
- **Procedure** :
  1. Helper klaviyo-fetch.sh → `segments`, `lists`, `campaigns` historique
  2. Invoque `shopify-cultural-calendar` pour identifier événement J-21 à J-7 (lu depuis `$HERMES_WORKSPACE/cultural-events.json`)
  3. Analyse historique campagnes similaires (best subject, best CTA, meilleure heure)
  4. Draft markdown : segment cible + volume, 3 variantes subject A/B/C, preview text 50-90 chars, corps structure (hook, intro contextuelle, CTA — vocab obligatoire selon STORE-BRAND.md)
  5. Archive dans `campaigns/YYYY-Www-klaviyo-draft.md`
- **Read-only** : aucune mutation Klaviyo, copier-coller manuel UI requis

#### `shopify-klaviyo-drop-watchdog` v1.0.0
- **When** : cron `<store>-watchdog-conversion` toutes les 6h. Jamais interactif.
- **Procedure** :
  1. Agrégats 7j N et 7j N-1 sur metrics IDs (Opened, Clicked, Placed Order, Unsubscribed)
  2. Garde-fou : n_min 50 envois sinon abort silencieux
  3. Seuils : open drop > 20pp, click drop > 30pp, revenue drop > 40%, unsub > 5%
  4. Si zéro alerte : silence total (`{"wakeAgent":false}`)
  5. Sinon : Telegram + wake-agent en mode prod

---

### Ideation hebdo

#### `shopify-instagram-ideator` v1.0.0
- **When** : cron `<store>-weekly-ideas` 10h, ou demande "idée Insta"
- **Procedure** :
  1. Lit `brand-knowledge.md` + `learnings.md`
  2. Choisit format (carrousel/reel/single/story) + thème (storytelling/édu/témoignage)
  3. Caption FR+EN avec hook/corps/CTA (vocab obligatoire selon STORE-BRAND.md)
  4. 15 hashtags (5 gros >100k + 5 moyens 10k-100k + 5 niches <10k)
  5. Description visuelle textuelle (génération image indispo en Phase test)
  6. Date/heure recommandée (créneau optimal selon ta marque)

#### `shopify-product-ideator` v1.0.0
- **When** : cron `<store>-weekly-ideas` pair avec `shopify-instagram-ideator`
- **Procedure** :
  1. Lit `store-data/products.md`, `collections.md`, `brand-knowledge.md` (gap catalogue), `learnings.md` historique
  2. Identifie 1 opportunité avec signal marché explicite
  3. Fiche : nom (+ déclinaison culturelle si pertinent), catégorie, description 50 mots, pourquoi maintenant, prix cible + marge estimée, concurrents + différenciation, moodboard textuel

#### `shopify-cultural-calendar` v1.0.0 (data-driven)
- **When** : avant chaque saison commerciale, mention dans rapport perf si event <14j, propose campagne dans email samedi
- **Procedure** :
  1. Lit `$HERMES_WORKSPACE/cultural-events.json` (template fourni dans `config/`, exemple dans `examples/azamoul/`)
  2. Calcule jours restants jusqu'à chaque événement
  3. Si <14j : alerte + propose campagne email + Insta + produit
  4. Maintient un index 6 mois glissants

**Note** : ce skill est **data-driven**. Tu définis tes événements dans `cultural-events.json` (Noël, Black Friday, événements culturels, lancements produits, anniversaires de la marque, etc.). Le skill ne contient AUCUN événement hardcodé.

---

### Skills auto-proposés (méta-revue dominicale)

Skills issus de patterns détectés automatiquement par le cron méta-revue :

| Skill | Version | Statut |
|---|---|---|
| `shopify-cron-output-watcher` | 0.1.0 | pattern documentaire issu de la méta-revue W20 du cas Azamoul |
| `hermes-snapshot-diff-validator` | 0.1.0 | pattern documentaire |
| `shopify-seo-mutation-batcher` | 0.1.0-PROPOSED | en attente validation marchand |
| `hermes-storefront-http-verifier` | 0.1.0-PROPOSED | en attente validation marchand |

**Mécanique** : si pattern récurrent > 3 occurrences sur 4 semaines détecté dans `learnings.md`, le cron `<store>-weekly-meta-review` crée automatiquement le SKILL.md correspondant. Le marchand valide ensuite la promotion 0.1.0 → 1.0.0.

---

## Helpers `lib/`

### `lib/klaviyo-fetch.sh` — wrapper API Klaviyo
- Revision API : `2024-10-15`
- Cache 6h slot UTC dans `/root/.hermes/cache/klaviyo/`
- Retry exponentiel `2^attempt` sur HTTP 429, max 3 tentatives
- Exit codes : 0 (OK), 1 (key missing), 2 (API error), 3 (usage error)
- Consommé par les 3 skills Klaviyo

### `lib/theme.sh` — library bash ops thème
- 14 fonctions exportées (voir [`INTEGRATIONS.md`](./INTEGRATIONS.md))
- Constantes paramétrables : `LIVE_THEME_ID`, `SHOPIFY_STORE`, `HERMES_WORKSPACE`
- Consommé par `shopify-theme-editor` (et exposé pour usage direct dans tout skill futur)

---

## Évolutions notables (cas d'étude Azamoul)

| Date | Évolution | Impact |
|---|---|---|
| 2026-05-13 | Phase 1+2 auto-validation | 9/10 PASS Phase 4 |
| 2026-05-14 | Grand Run W20 | Verdict GO Production |
| 2026-05-14 | Meta-review détecte patterns | 2 skills auto-PROPOSED |
| 2026-05-20/21 | Vague Klaviyo | 3 nouveaux skills + helper unifié |
| 2026-05-21 | Migration hooks v0.13 → v0.14 | Format dict + `tool_input` payload |
| 2026-05-24 | `shopify-theme-editor` v1.0 puis v1.1 | Theme Access workflow + helper `theme.sh` |
| 2026-05-24 | Premier usage live | 62 produits textiles bulk-update |

Voir [`../examples/azamoul/`](../examples/azamoul/) pour le cas d'étude détaillé.
