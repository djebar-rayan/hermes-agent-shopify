---
name: shopify-metatitle-generator
description: Genere meta title + meta description SEO pour un produit Shopify (60/160 chars cible)
category: e-commerce-seo
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, seo, meta-title, meta-description, llm-generation]
---

# <STORE_NAME> Meta Title/Description Generator

## When to Use
- Skill compagnon `shopify-catalog-gap-analyzer` quand `seo.title` ou `seo.description` est vide ou < 30 chars
- Avant `shopify-batch-executor` pour batch meta-titles
- A la demande pour 1 produit

## Procedure
Input : `{handle, title, productType, descriptionHtml_excerpt, current_seo: {title, description}}`

Genere :
```json
{
  "meta_title": "...",        // <= 60 chars cible (max 70)
  "meta_description": "...",  // <= 160 chars cible (max 170)
  "rationale": "..."
}
```

Regles meta_title :
- 50-60 chars optimal (Google tronque au-dela ~580px)
- Inclut le nom produit + mot cle principal + marque "<STORE_NAME>" si possible
- Au moins 1 mot du vocabulaire de marque (STORE-BRAND.md)
- Format type : "<Nom produit> - <Symbole/Caractere> | <STORE_NAME>"

Regles meta_description :
- 140-160 chars optimal
- Inclut une CTA implicite (decouvrez, offrez, portez)
- Mentionne "Made in France" si applicable
- Au moins 1 mot du vocabulaire de marque (STORE-BRAND.md)
- Ne reprend PAS mot pour mot le meta_title (Google penalise)

NE PAS appliquer la mutation. C est `shopify-batch-executor` (via productUpdate avec seo: {title, description}) qui le fera.

## Pitfalls
- Titre > 70 chars = tronque dans SERP, refuse.
- Description > 170 chars = tronquee, refuse.
- Sans mot du vocabulaire de marque = identité perdue.
- Eviter mots-vides ("le meilleur", "incroyable") — Google les ignore.

## Verification
- meta_title <= 70 chars
- meta_description <= 170 chars
- Tous deux contiennent >= 1 mot du vocabulaire de marque
- Pas de duplication entre title et description
- rationale precise le mot cle principal cible
