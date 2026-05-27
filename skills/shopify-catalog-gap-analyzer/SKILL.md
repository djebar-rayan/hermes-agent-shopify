---
name: shopify-catalog-gap-analyzer
description: Audit lecture seule du catalogue <STORE_NAME> - identifie produits sans tags suffisants et sans bloc livraison en debut de description, priorise par impact business
version: 1.0.0
author: Hermes (Phase 2 scaffold)
metadata:
  hermes:
    tags: [shopify, audit, phase2, framework]
    category: ecommerce
    requires_toolsets: [terminal, file]
---
# Catalog Gap Analyzer <STORE_NAME>

## When to Use
- Au demarrage de Phase 2 (action mutative basique 🟢)
- Avant chaque batch d execution pour cibler les produits prioritaires
- Sur demande explicite : "fais une gap analysis catalogue"
- Cron hebdomadaire en complement du rapport perf

## Procedure
1. Lis MEMORY.md ligne "Phase courante" pour confirmer Phase 2+ (sinon ce skill est informationnel uniquement).

2. Charge les sources existantes :
   - $HERMES_WORKSPACE/audits/initial-catalog-audit.md (baseline initiale)
   - $HERMES_WORKSPACE/brand-knowledge.md (contexte marque)

3. Via toolkit Shopify (shopify store execute --query-file, JAMAIS --query inline), recupere :
   - products(first: 250) avec id, handle, title, status, tags, descriptionHtml(first 600 chars), images.edges.node.id, productType
   - Pour chaque produit, calcule :
     - tagsCount = len(tags)
     - hasShippingBlockFirst = bool(regex /📦|livraison|expedition/i match dans first 300 chars descriptionHtml)
     - imagesCount = len(images.edges)

4. Categorise les produits par catégorie metier (textile, accessoire, bijou, deco, livre, coque) via productType + heuristique sur title si besoin.

5. Pour chaque categorie, definis le set de tags cibles obligatoires (ex. textile = (vocab depuis STORE-BRAND.md), coque = (vocab catégorie)). Calcule les tags manquants par produit.

6. Genere $HERMES_WORKSPACE/audits/phase2-gap-analysis-YYYY-MM-DD.md avec :
   - Stats globales : X/96 produits sans bloc livraison en debut, Y/96 avec moins de 5 tags
   - Liste detaillee par produit (handle, action proposee, severite)
   - Batches suggeres : decoupage en groupes de 10 produits avec impact estime

7. Resume Telegram court (max 12 lignes) : nombre de gaps detectes, top 5 actions vertes par impact, propose batch 1.

## Pitfalls
- INTERDICTION inventer des chiffres : si pas de data sessions/conversion, marque "(N/A)"
- Pas de mutation Shopify dans ce skill : 100 percent lecture seule
- Le regex bloc livraison peut faux-positif sur descriptions qui mentionnent "livraison" en milieu de texte sans bloc dedie. Verifie le contexte (debut 300 chars).
- Si plus de 250 produits, paginer via cursors GraphQL (pour le moment <STORE_NAME> = 96 produits, OK)

## Verification
- Fichier audits/phase2-gap-analysis-YYYY-MM-DD.md cree, taille >= 2 KB
- Stats globales coherentes avec les 96 produits du catalogue
- Top 10 priorise par signal client reel (sessions/conversion Shopify natives)
- Telegram resume envoye, max 12 lignes
