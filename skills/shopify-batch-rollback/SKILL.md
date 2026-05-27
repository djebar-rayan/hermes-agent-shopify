---
name: shopify-batch-rollback
description: Revert un batch productUpdate via snapshot before.json - usage de securite si batch a casse des produits
version: 1.0.0
author: Hermes (Phase 2 scaffold)
metadata:
  hermes:
    tags: [shopify, rollback, phase2, safety, framework]
    category: ecommerce
    requires_toolsets: [terminal, file]
---
# Batch Rollback <STORE_NAME>

## When to Use
- Apres execution batch-executor si on detecte une regression
- Sur demande explicite : "rollback batch N" ou "revert le batch d hier"
- Apres mesure d impact J+7 si impact significativement negatif
- Test d idempotence (lancer le rollback puis le rollback du rollback = no-op)

## Procedure
1. Identifie le batch a rollback : recoit en parametre batchId (ex. "2026-W20-batch1") ou demande au user si ambigu.

2. Verifie l existence du snapshot before.json : $HERMES_WORKSPACE/batches/<batchId>-before.json. Si absent : STOP, impossible de rollback sans snapshot.

3. Charge le snapshot JSON (array de produits avec leurs valeurs originales tags + descriptionHtml + updatedAt).

4. Pour chaque produit dans le snapshot :
   a. Capture l etat ACTUEL via GraphQL product(id) (pour comparer et verifier qu il y a bien eu mutation depuis le snapshot)
   b. Si actuel == snapshot : skip (deja a l etat d origine, idempotent)
   c. Sinon : execute productUpdate avec les valeurs du snapshot (tags + descriptionHtml)
   d. Espacement 2s entre mutations

5. Genere $HERMES_WORKSPACE/batches/<batchId>-rollback-YYYY-MM-DDTHH:MM.md avec :
   - Liste produits rollback (succes / skip / echec)
   - Diff actuel vs snapshot pour audit

6. Notifie Telegram + email :
   "Rollback batch <batchId> termine. X/10 produits restaures, Y skip (deja a l origine), Z echecs."

7. Log dans learnings.md : ajout entree "Rollback batch <batchId>" avec resultats.

## Pitfalls
- Idempotent obligatoire : un produit deja a l etat d origine est SKIP, pas re-mute (evite des updates inutiles).
- Si le produit a ete modifie manuellement par l utilisateur entre temps : log un warning mais procede au rollback (priorite a la securite du snapshot).
- En cas d echec productUpdate : continue les autres, log l erreur exacte. Ne JAMAIS abandonner en milieu de rollback.
- Aucune validation tuteur requise pour rollback (action de securite, doit etre rapide).

## Verification
- Fichier <batchId>-rollback-YYYY-MM-DDTHH:MM.md cree
- Telegram + email envoyes avec stats
- learnings.md a une entree rollback
- shopify store execute confirme l etat post-rollback == snapshot pour les produits non-skip
