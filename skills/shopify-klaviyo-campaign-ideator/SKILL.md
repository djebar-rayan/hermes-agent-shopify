---
name: shopify-klaviyo-campaign-ideator
description: Propose un draft de campagne email Klaviyo aligné avec le calendrier culturel (cultural-events.json) et les segments existants
version: 1.0.0
metadata:
  hermes:
    tags: [klaviyo, email, content, marketing, framework, ideator]
    category: content
    requires_toolsets: [terminal, file]
---

# <STORE_NAME> Klaviyo Campaign Ideator

Skill créatif read-only : propose UNE campagne email Klaviyo pour la semaine, prête à être copiée-collée dans l'UI Klaviyo. **Aucune mutation API.**

## When to Use

- **Cron `shopify-samedi-ideas` (7936943cee39)** : chaque samedi 10h, en complément de `shopify-product-ideator` et `shopify-instagram-ideator`
- Sur demande user : "idée campagne email", "draft Klaviyo", "campagne pour Yennayer/Aïd/etc."

## Configuration

Lit :
- `$KLAVIYO_API_KEY` depuis `.env`
- `$HERMES_WORKSPACE/brand-knowledge.md` (style éditorial)
- `/root/.hermes/cache/klaviyo/` (segments + performances passées)
- Skill `shopify-cultural-calendar` (événements à venir J-N)

## Dependency obligatoire

Charge AUSSI le skill `shopify-cultural-calendar` pour identifier l'événement culturel à anticiper.

## Procedure

### 1. Charger l'environnement
```bash
set -a; . /root/.hermes/.env; set +a
LIB=/root/.hermes/lib/klaviyo-fetch.sh
```

### 2. Fetcher contexte Klaviyo
```bash
SEGMENTS=$($LIB segments)        # 1 segment : <premium segment>
LISTS=$($LIB lists)              # 2 listes : welcome_ansuf, SMSBump
CAMPAIGNS_HISTORY=$($LIB campaigns)  # 30 campagnes passées (pour cohérence ton/timing)
```

### 3. Lire calendrier culturel
Appeler `shopify-cultural-calendar` → identifier l'événement à anticiper (J-21 à J-7 idéal).

Événements clés à considérer (priorité par proximité) :
- <événement depuis cultural-events.json> (~26 juin 2026, J-X)
- <nouvel an culturel depuis cultural-events.json> (12 janvier 2027)
- <événement printemps depuis cultural-events.json>
- <événement depuis cultural-events.json> (été)
- <événement nouvel-an depuis cultural-events.json>
- Saison de rentrée / Black Friday / Noël (commerce généraliste)

### 4. Analyser performance des campagnes similaires passées

Regarder dans `CAMPAIGNS_HISTORY` les campagnes du même type (lifecycle, événement culturel, promo) :
- Quel sujet a eu le meilleur open rate ?
- Quel CTA a converti ?
- Quelle heure d'envoi a marché ?

### 5. Construire le draft

Format à produire :

```markdown
## 📧 Proposition Campagne Klaviyo — Semaine 2026-Www

### Contexte stratégique
- **Événement** : <nom événement culturel> (J-X)
- **Pourquoi maintenant** : <justification 1 ligne>
- **Segment cible recommandé** : <premium segment> (X profils) OU welcome_ansuf (X profils) OU "Engaged 30j" (à créer dans Klaviyo)
- **Volume estimé envoi** : X profils

### Sujet (3 variantes pour A/B test)
1. **Variante A** (émotionnel) : "..." (X chars, prévisualisation : "...")
2. **Variante B** (urgence) : "..."
3. **Variante C** (curiosité) : "..."

### Aperçu (preview text — 50-90 chars)
"<texte invisible mais visible en preview>"

### Corps email — structure

**Hook (1 ligne)**
"..."

**Intro (2-3 lignes)**
- Référence culturelle (vocab obligatoire (depuis STORE-BRAND.md))
- Contexte événement
- Ce que la communauté <STORE_NAME> célèbre

**Produit mis en avant**
- 1 à 3 produits du catalogue Shopify alignés avec l'événement
- Lien : https://${SHOP_DOMAIN}/products/<handle>
- Bloc livraison 📦 si pertinent

**Code promo (optionnel)**
- Code suggéré : `<EVENEMENT><ANNEE>` (ex: AID2026, YENNAYER2977)
- Remise suggérée : 10-15% (à valider tuteur)
- Validité : <date début> → <date fin> (typiquement 5-7j)

**CTA principal**
- Texte bouton : "Découvrir la collection" / "Profiter du code" / "Voir les nouveautés"
- URL cible : `https://${SHOP_DOMAIN}/<collection-handle>`

**Signature**
- Style éditorial <STORE_NAME> (voir brand-knowledge.md)
- Mention Made in France si pertinent

### Send time recommandé
- **Date d'envoi** : <date proche événement, J-X>
- **Heure** : <basé sur historique campagnes : ex 18h Paris si meilleur open rate passé>
- **Justification** : <campagne référence : "Hiver & fêtes 2024 ouverture 24% à 19h jeudi">

### Hashtags / Mots-clés SEO
- Pour réutilisation sur Instagram/blog : #<your-niche> #<your-brand> #<événement>

### Checklist avant copie dans Klaviyo
- [ ] Sujet sous 50 chars (mobile-friendly)
- [ ] Preview text 50-90 chars
- [ ] Vocab obligatoire présent (min 2 mots du dictionnaire)
- [ ] CTA unique et clair
- [ ] Lien produit testé (200 OK)
- [ ] Code promo créé dans Shopify (action manuelle requise)
- [ ] Segment vérifié dans Klaviyo > Audience > Segments

### ⚠️ Mode test / prod
Lit `$HERMES_MODE` :
- `test` (défaut) : draft markdown seulement, aucune création campagne dans Klaviyo, destinataire test = $EMAIL_TO
- `prod` : draft validé prêt pour saisie manuelle dans Klaviyo (Hermes ne POST jamais)
```

### 6. Sauvegarder

- **Section ideas** : append à `$HERMES_WORKSPACE/reports/$(date +%Y-W%V)-ideas.md` après les sections produit/Insta
- **Cache séparé** : `$HERMES_WORKSPACE/campaigns/$(date +%Y-W%V)-klaviyo-draft.md` (pour archivage)

### 7. Log learnings

```markdown
## $(date -u +%Y-%m-%dT%H:%M:%SZ) — Klaviyo campaign drafted
- Événement cible : <event>
- Segment recommandé : <segment>
- Code promo suggéré : <code>
- Statut : DRAFT (mode test, aucun envoi)
```

## Pitfalls

- **JAMAIS d'appel POST Klaviyo** (read-only strict). Si user demande "envoie", répondre : "Je propose le draft. Tu valides dans Klaviyo UI puis cliques Send."
- **Vocab obligatoire** : Minimum 2 mots du dictionnaire de marque (voir MEMORY.md → "Vocabulaire de marque obligatoire")
- **Pas de stéréotypes** : voir STANDING.md règle #6
- **Code promo** : suggérer SEULEMENT, ne JAMAIS créer dans Shopify (mutation interdite niveau 🔴)
- **Liens produit** : vérifier que le handle existe dans store-data/products.md AVANT de l'inclure
- **Sample size** : si campaigns_history < 5 campagnes similaires, indiquer "(baseline limitée)" dans la justification timing
- **Devise EUR** uniquement (boutique France)

## Verification

- ✅ Draft markdown contient les 7 sections (Contexte / Sujet / Aperçu / Corps / Promo / Send time / Checklist)
- ✅ Min 2 mots du vocabulaire de marque (STORE-BRAND.md) dans le corps
- ✅ Aucun appel API mutation (vérifiable via log curl POST)
- ✅ Fichier `campaigns/YYYY-Www-klaviyo-draft.md` créé
- ✅ Section ajoutée à `reports/YYYY-Www-ideas.md`
- ✅ Entrée learnings.md créée
- ✅ Le draft mentionne explicitement le mode (test/prod)

## Dependencies

- `/root/.hermes/lib/klaviyo-fetch.sh`
- Skill `shopify-cultural-calendar`
- `$HERMES_WORKSPACE/brand-knowledge.md`
- `$HERMES_WORKSPACE/store-data/products.md`
- `$HERMES_WORKSPACE/learnings.md`
