---
name: shopify-altext-generator
description: Generate 3 propositions d alt-text SEO FR+EN pour une image produit, basees sur titre + vocabulaire de marque (STORE-BRAND.md)
category: e-commerce-seo
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, seo, alt-text, accessibility, llm-generation]
---

# <STORE_NAME> Alt-Text Generator

## When to Use
- Skill compagnon de `shopify-catalog-gap-analyzer` quand un produit a alt-text vide
- Avant `shopify-batch-executor` pour preparer un batch alt-texts
- A la demande pour 1 produit specifique

## Procedure
Input attendu : `{handle, title, product_id, image_id, productType?}` (extrait via GraphQL READ-ONLY).

Genere 3 propositions JSON :
```json
{
  "alt_options": [
    {"id": 1, "fr": "...", "en": "..."},
    {"id": 2, "fr": "...", "en": "..."},
    {"id": 3, "fr": "...", "en": "..."}
  ],
  "selected_option": <1|2|3>,
  "rationale": "..."
}
```

Regles de generation :
- Chaque alt-text : max 125 chars (limite SEO Google)
- FR ET EN obligatoires
- AU MOINS 1 mot du vocabulaire de marque (STORE-BRAND.md) par alt : voir liste dans STORE-BRAND.md
- Si le titre contient "Made in France" : mentionne-le dans au moins 1 alt
- Decrit ce qui est VISIBLE sur l image (couleur, symbole, format) + contexte culturel
- Option selectionnee = celle qui combine SEO + accessibilite + contexte culturel

Output : JSON valide ecrit dans le chemin demande par l invocateur (typiquement `/tmp/altext-<handle>.json` ou `tests/p3.X-...json` en mode test).

NE PAS appliquer la mutation. C est `shopify-batch-executor` qui le fera apres validation tuteur.

## Pitfalls
- Alt-text > 125 chars = SEO degrade, refuse.
- Sans mot du vocabulaire de marque = perte d identité.
- Eviter formules generiques ("belle creation", "produit unique") — sois specifique sur ce que l image montre.
- Ne reutilise pas exactement le title du produit (Google penalise la duplication).

## Verification
- 3 propositions distinctes (pas de doublons FR ou EN)
- Chaque alt <= 125 chars
- Chaque alt contient >= 1 mot du vocabulaire de marque
- selected_option pointe vers une des 3 options
- rationale explique le choix en 1-2 phrases
