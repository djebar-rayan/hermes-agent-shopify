---
name: hermes-storefront-http-verifier
description: Verifie le rendu HTTP public du storefront Shopify apres mutation
category: monitoring
version: 0.1.0-PROPOSED
metadata:
  hermes:
    tags: [monitoring, http, storefront, verification]
  proposed:
    date: 2026-05-14
    based_on_pattern: "Verification HTTP storefront apres mutation"
    occurrences_found: 4
    sources: [
      "$HERMES_WORKSPACE/tests/p3.4-http-verification.md",
      "$HERMES_WORKSPACE/tests/p3.9-storefront-check.md",
      "$HERMES_WORKSPACE/tests/p3.10-visibility-check.md"
    ]
    proposed_by: "meta-revue-auto P4.4"
    requires_validation: true
---

# hermes-storefront-http-verifier

## When to Use
Utilisez ce skill immédiatement après avoir effectué des mutations critiques (comme le changement de statut d'un produit, la modification des prix ou des descriptions) pour vous assurer que les changements sont bien reflétés sur le site public (storefront), en contournant les éventuels caches locaux.

## Procedure
1. Identifier l'URL publique du produit ou de la page (ex: `https://${SHOP_DOMAIN}/products/handle`).
2. Effectuer une requête HTTP GET (via `curl` ou une librairie Python).
3. Analyser le code source HTML retourné pour y chercher les balises cibles (par exemple, `<title>`, `<meta name="description">`, ou des éléments de prix).
4. Comparer les valeurs trouvées avec celles attendues suite à la mutation.

## Pitfalls
- **Cache CDN / Shopify :** Il arrive que Shopify mette quelques minutes à purger son cache. Si la vérification échoue immédiatement, il faut parfois attendre 1 à 2 minutes et réessayer.
- **Blocage par bot :** Faire attention aux User-Agents. Il est préférable d'utiliser un User-Agent standard de navigateur web pour la requête `curl`.
- **Thème dynamique :** Certains thèmes chargent les données via JavaScript côté client. Dans ce cas, un simple `curl` peut ne pas suffire.

## Verification
- Le code de retour HTTP doit être 200 (ou 404 si le but était de vérifier la mise en brouillon).
- Le contenu attendu doit être strictement présent dans le corps de la réponse.
