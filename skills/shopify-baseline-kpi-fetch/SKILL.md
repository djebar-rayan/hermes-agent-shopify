---
name: shopify-baseline-kpi-fetch
description: Extraction standardisée des KPI Shopify (CA, AOV, abandon) via GraphQL pour rapports hebdo
category: e-commerce
---

# <STORE_NAME> Baseline KPI Fetch
Pattern récurrent identifié durant Q2 et Q4.

## When to Use
Quand le prompt demande "récupérer les metrics Shopify", "baseline KPI" ou "taux d'abandon".

## Configuration
La variable SHOPIFY_STORE est dans /root/.hermes/.env (`<store_handle>.myshopify.com`). Charge-la systématiquement avant tout appel CLI.

## Procedure
1. Créer la requête GraphQL dans un fichier `--query-file` (`/tmp/kpi-query.graphql`).
2. Appeler le CLI Shopify avec le flag --store obligatoire :
   ```bash
   set -a; . /root/.hermes/.env; set +a
   shopify store execute --store="$SHOPIFY_STORE" --query-file /tmp/kpi-query.graphql --json
   ```
3. Requêter les `orders` (last 30 days) pour extraire CA et AOV.
4. Requêter les `checkouts` pour calculer le taux d'abandon de panier.
5. Compiler dans le format standard tabulaire requis par MISSION-HERMES.md.

## Pitfalls
- Ne JAMAIS utiliser `--query` inline, toujours un fichier.
- Ne JAMAIS oublier le flag `--store=$SHOPIFY_STORE` — sinon erreur 'Missing required flag store'.
- Ne pas oublier de filtrer les commandes annulées/remboursées.
- Si $SHOPIFY_STORE est vide, source d'abord /root/.hermes/.env via `set -a; . /root/.hermes/.env; set +a`.

## Verification
- Le JSON renvoyé doit contenir un champ `data` non-null. Si `errors` présent, log la cause exacte dans le rapport (NE PAS halluciner les KPI).
