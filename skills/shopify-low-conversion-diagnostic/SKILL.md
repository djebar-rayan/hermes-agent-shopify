---
name: shopify-low-conversion-diagnostic
description: Diagnostique pourquoi un produit Shopify ne convertit pas (checklist 12 points)
version: 1.0.0
author: Hermes (initial scaffold)
metadata:
  hermes:
    tags: [diagnostic, conversion, shopify, framework]
    category: ecommerce
---
# Diagnostic Faible Conversion Produit

## When to Use
Produit > 50 vues/7j mais 0 add-to-cart, ou flag dans rapport hebdo.

## Procedure
Pour le produit ciblé, vérifie les 12 points :
1. Image principale : qualité >= 800×800, >= 3 images, alt text rempli
2. Description : >= 150 mots, HTML structuré (h2+ul), vocabulaire culturel
3. SEO : meta title (30-70 chars), meta description (50-160 chars)
4. Prix : aligné avec catégorie
5. Variantes : toutes ont leur image dédiée
6. Livraison : bloc 📦 en DÉBUT de description
7. Reviews : >= 3 si app installée
8. Stock : affiché disponible
9. Tags : >= 5 pertinents
10. Position dans collections
11. Mobile preview lisible
12. Internal linking dans description

## Output
Tableau : {check, statut ✓/⚠/✗, recommandation, niveau 🟢/🟡/🔴}

## Pitfalls
- Ne pas modifier sans validation (sauf actions 🟢)

## Verification
- 12 points vérifiés
- >= 1 action 🟢 exécutée si présente
- >= 1 proposition 🟡 documentée
