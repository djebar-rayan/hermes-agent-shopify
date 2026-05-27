---
name: shopify-description-enricher
description: Enrichit un descriptionHtml court Shopify (>=150 mots, bloc livraison en debut, vocabulaire de marque (STORE-BRAND.md))
category: e-commerce-content
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, content, description, llm-generation]
---

# <STORE_NAME> Description Enricher

## When to Use
- Skill compagnon `shopify-catalog-gap-analyzer` quand un descriptionHtml a moins de 150 mots OU manque de bloc livraison en debut
- Avant `shopify-batch-executor` pour batch descriptions
- A la demande pour 1 produit

## Procedure
Input : `{handle, title, descriptionHtml_actuel, productType?, tags?}`

Output JSON :
```json
{
  "descriptionHtml_before": "...",
  "descriptionHtml_after": "...",
  "word_count_before": <n>,
  "word_count_after": <n>,
  "brand_vocab_used": ["...", "..."],
  "block_livraison_position": 0
}
```

Regles de generation `descriptionHtml_after` :
- COMMENCE OBLIGATOIREMENT par le bloc livraison dans les chars 0-300 :
  `<p>📦 <strong>Livraison estimee 5-6 jours France metropolitaine</strong>, 8-10 jours international. Expedition soignee depuis la France.</p>`
- Puis paragraphes : histoire culturelle + lien marque + description produit + materiaux/usage + appel imaginaire (offrir, porter, partager)
- >= 150 mots au total (texte sans tags HTML)
- >= 3 mots du vocabulaire de marque (voir STORE-BRAND.md)
- HTML valide : balises fermees (p, strong, h2, ul/li ok), pas de div/script/style
- TON <STORE_NAME> : sobre, fier, ancre dans l identite, sans superlatifs gratuits

NE PAS appliquer la mutation. C est `shopify-batch-executor` qui le fera via productUpdate.

## Pitfalls
- Bloc livraison ailleurs qu en debut (>300 chars) = REFUSE.
- Word count < 150 = REFUSE.
- HTML mal forme (balise non fermee) = REFUSE, regenere.
- Repetitions excessives du nom du produit = penalisee Google.
- Inventer des materiaux non-confirmes (ex: "soie") sans preuve dans titre/tags = INTERDIT.

## Verification
- word_count_after >= 150
- block_livraison_position == 0 (ou <= 300)
- brand_vocab_used.length >= 3
- HTML parsable (lxml/beautifulsoup ne leve aucune erreur)
