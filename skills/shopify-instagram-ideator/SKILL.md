---
name: shopify-instagram-ideator
description: Génère une idée de post Instagram complète (format, caption FR/EN, hashtags, visuel)
version: 1.0.0
author: Hermes (initial scaffold)
metadata:
  hermes:
    tags: [instagram, content, growth, framework]
    category: marketing
---
# Idéateur Posts Instagram <STORE_NAME>

## When to Use
Chaque samedi à 10h (cron `shopify-samedi-ideas`), ou sur demande "idée Insta".

## Procedure
1. Lis `brand-knowledge.md` (style visuel, hashtags performants, posts récents)
2. Lis `learnings.md` pour posts précédents et leur engagement
3. Décide format : carrousel | reel | single | story
4. Décide thème : storytelling / éducation culturelle / mise en scène / témoignage
5. Rédige caption complète (hook, corps, CTA) en FR (+ EN si pertinent)
6. 15 hashtags optimisés (mix gros/niches)
7. Décris le visuel OU description visuelle textuelle (génération image indisponible Phase 1)
8. Date/heure de pub recommandée

## Pitfalls
- Vocabulaire de marque obligatoire (voir STORE-BRAND.md)
- Pas de stéréotypes
- Pas de génération directe via API IG — TOUJOURS proposer (validation au tuteur)

## Verification
Output structuré : Format / Thème / Caption / Hashtags / Visuel / Date / CTA
