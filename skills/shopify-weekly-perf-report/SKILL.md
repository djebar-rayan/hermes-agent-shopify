---
name: shopify-weekly-perf-report
description: Génère le rapport de performance hebdomadaire <STORE_NAME> (KPI, top wins/pertes, diagnostic)
version: 1.0.0
author: Hermes (initial scaffold)
metadata:
  hermes:
    tags: [shopify, growth, report, framework]
    category: ecommerce
    requires_toolsets: [terminal]
---
# Rapport Performance Hebdomadaire <STORE_NAME>

## When to Use
Chaque lundi à 9h (cron `shopify-lundi-perf`), ou sur demande explicite.

## Procedure
1. `cd $HERMES_WORKSPACE/shopify-automation-toolkit`
2. Si `store-data/` a plus de 7 jours, lance `node fetch-store-data.js` (115s)
3. Extrais KPI semaine N et N-1 : sessions, conversions, commandes, AOV, CA, panier abandonné
4. Lis `learnings.md` des 7 derniers jours
5. Compare vs semaine N-1 : calculer les deltas %
6. Génère le rapport dans `$HERMES_WORKSPACE/reports/$(date +%Y-W%V)-perf.md`
7. Résumé Telegram (max 20 lignes) : KPI snapshot, top 3 wins/pertes, diagnostic, actions exécutées + impact, actions proposées

## Pitfalls
- Si store-data/ vide → fetch obligatoire
- Comparer N vs N-1 nécessite >= 2 semaines d'historique, sinon mentionner "baseline"
- Éviter chiffres absolus très petits dans Telegram → preferer %

## Verification
- Fichier `reports/YYYY-Www-perf.md` créé
- Message Telegram envoyé
- `learnings.md` mis à jour
