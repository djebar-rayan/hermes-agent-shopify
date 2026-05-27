# Cas d'étude — Azamoul

> Instance live de Hermes Framework sur la boutique [Azamoul](https://azamoul.com), marque française qui valorise la culture amazighe (berbère) via la mode et les accessoires.
>
> Cette doc montre **un exemple complet** de configuration Hermes pour une vraie boutique en production depuis mai 2026.

---

## Identité

| Champ | Valeur |
|---|---|
| Marque | **Azamoul** |
| Domaine | [azamoul.com](https://azamoul.com) |
| Shopify | `azamoul-symboles-berberes.myshopify.com` (Basic, EUR) |
| Plan | Shopify Basic — Europe/Paris |
| Catalogue | ~96 produits actifs, 19 collections, 11 pages |
| Univers | Mode, bijoux, déco, accessoires culture amazighe (tifinagh, yaz ⵣ, kabyle) |
| Instagram | [@azamoul](https://instagram.com/azamoul) — 5769 followers, 116 posts (83% reels) |
| Made in | France |

---

## Métriques opérationnelles Hermes (au 2026-05-27)

| Métrique | Valeur |
|---|---|
| Skills opérationnels | **25** (21 shopify-* + 4 hermes-*) |
| Crons actifs | 4 (88 runs cumulés sans erreur) |
| Intégrations API | 16 (Shopify, Klaviyo, Gemini, OpenRouter, GSC, Firecrawl, SMTP, Telegram, ...) |
| Tokens 7j | 1 083 362 |
| Active time 7j | ~6h 9m |
| Sessions 7j | 4 (3 cron + 1 CLI) |
| Skills auto-créés par méta-revue | 1 (azamoul-cron-output-watcher) |
| Mutations Shopify cumulées | 62 produits textiles bulk-update (le 2026-05-24) |

---

## Fichiers de configuration (instance Azamoul)

| Fichier | Contenu |
|---|---|
| [`MISSION.md`](./MISSION.md) | Charter complet de l'agent pour Azamoul (~19KB) |
| [`STORE-BRAND.md`](./STORE-BRAND.md) | Vocabulaire amazigh obligatoire + niveaux autonomie spécifiques |
| [`brand-knowledge.md`](./brand-knowledge.md) | 4 concurrents identifiés + 10 événements amazighs |
| [`cultural-events.json`](./cultural-events.json) | Calendrier en JSON : Yennayer, Aïd, Tafsut, Tafaska, Imilchil, etc. |
| [`MEMORY.md`](./MEMORY.md) | Faits permanents boutique (53 lignes condensées) |
| [`cron-jobs.json`](./cron-jobs.json) | Les 4 crons réels Azamoul (sanitized des secrets) |
| [`HERMES-CONFIG-ACTUELLE.md`](./HERMES-CONFIG-ACTUELLE.md) | Snapshot complet de la config Azamoul (~24KB) |
| [`GUIDE-OPERATIONNEL.md`](./GUIDE-OPERATIONNEL.md) | Guide pratique opérationnel pour Azamoul (~67KB) |

---

## Évolutions notables

| Date | Évolution |
|---|---|
| 2026-05-11 | Démarrage Phase 0 (provisionnement VPS, install Hermes) |
| 2026-05-13 | Phase 1+2 auto-validation 9/10 PASS |
| 2026-05-14 | Grand Run W20 (5/6 PASS authentique) → Verdict GO Production |
| 2026-05-14 | Méta-review détecte 2 patterns → skills PROPOSED (`cron-output-watcher`, `snapshot-diff-validator`) |
| **2026-05-20/21** | **Vague Klaviyo** : 3 nouveaux skills + helper `klaviyo-fetch.sh` |
| 2026-05-21 | Migration hooks v0.13 → v0.14 (format dict + tool_input) |
| 2026-05-21 | Refactor MEMORY.md 8166 → 3014 chars |
| 2026-05-24 | Switch SMTP `djebar.rayan75` → `contact.azamoul@gmail.com` |
| **2026-05-24** | **Skill `theme-editor` v1.0 puis v1.1** (helper `theme.sh`, lint, duplicate-preview, multi-file atomic) |
| 2026-05-24 | Premier usage live : 62 produits textiles bulk-update avec bloc "Politique de retours" |

---

## Vocabulaire de marque (extrait)

```
amazigh, berbère, tifinagh, imazighen, yaz (ⵣ), azamoul, kabyle, djurdjura,
thilelli, dihya, aza, afzim, tiseghnest, tafaska, tamghra, asseggas, amegaz,
tafsut, tamejja, lawan, tameddurt
```

Voir [`STORE-BRAND.md`](./STORE-BRAND.md) pour l'interprétation de chaque terme.

---

## Concurrents identifiés

| # | Marque | URL | Niche | Différenciation Azamoul |
|---|---|---|---|---|
| 1 | Bahya Brand | [bahyabrand.com](https://bahyabrand.com) | Streetwear, t-shirts engagés | Motifs tifinagh sur coupes modernes |
| 2 | Maison Amazira | [kabylefashion.com](https://kabylefashion.com) | Mode couture héritage sacré | Prêt-à-porter vs haute couture |
| 3 | Princesse Berbère | [princesseberbere.com](https://princesseberbere.com) | Mode tradition + modernité | Réassurance avis + engagement IG |
| 4 | Artisanat Shop | [artisanat-shop.com](https://artisanat-shop.com) | Bijoux berbères artisanaux | Aza/Afzim modernisés industrialisables |

---

## Comment utiliser ce cas d'étude

1. **Si tu débutes avec Hermes** : lis d'abord [`../../GETTING-STARTED.md`](../../GETTING-STARTED.md), puis reviens ici pour voir un exemple concret de chaque fichier de config rempli.

2. **Si tu adaptes Hermes à ta marque** : copie les templates depuis `../../config/` et adapte-les à ta marque, en t'inspirant de la structure et du niveau de détail vu ici.

3. **Si tu cherches un point précis** :
   - Vocabulaire de marque → [`STORE-BRAND.md`](./STORE-BRAND.md)
   - Calendrier événementiel → [`cultural-events.json`](./cultural-events.json)
   - Concurrents + positionnement → [`brand-knowledge.md`](./brand-knowledge.md)
   - Crons paramétrés → [`cron-jobs.json`](./cron-jobs.json)
   - Charter mission complet → [`MISSION.md`](./MISSION.md)
   - Guide opérationnel pratique → [`GUIDE-OPERATIONNEL.md`](./GUIDE-OPERATIONNEL.md)

---

## Ce qui est sanitized vs ce qui reste

**Sanitized dans ces fichiers** :
- IP VPS, hostname OVH, chat ID Telegram → placeholders `<VPS_IP>`, `<VPS_HOSTNAME>`, `<TELEGRAM_USER_ID>`
- Aucun token, password, ou clé API en clair
- `.env` non versionné (cf. `.gitignore`)

**Reste visible** (métadonnées publiques) :
- Nom de la marque, domaine, handle Shopify (toutes ces infos sont déjà publiques sur azamoul.com)
- Email `contact.azamoul@gmail.com` (publiquement listé sur la boutique)
- Vocabulaire amazigh (culture publique)
- Structure des skills et helpers

---

## Crédits

Hermes Framework a été créé par **Rayan Djebar** lors d'un stage chez Azamoul (BUT2, mai 2026). Le framework générique est issu de la généralisation de cette instance live.

Voir [`../../README.md`](../../README.md) pour la vitrine framework et [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) pour contribuer.
