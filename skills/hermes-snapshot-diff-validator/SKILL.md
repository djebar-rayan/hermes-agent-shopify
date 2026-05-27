---
name: hermes-snapshot-diff-validator
description: Pattern de validation pour batchs Shopify avec apply+rollback.
version: 0.1.0
author: Hermes auto-meta grand-run-2026-W20
category: devops
tags:
  - auto-proposed
  - grand-run-2026-W20

---

### When to Use
Utiliser ce pattern lorsque vous effectuez des mutations test (productUpdate, collectionCreate, etc.) sur Shopify qui doivent être impérativement annulées (rollback) pour garder un environnement clean.

### Procedure
1. Requêter l'état actuel des entités (snapshot BEFORE).
2. Appliquer la mutation attendue.
3. Vérifier le succès de la mutation (snapshot AFTER-APPLY).
4. Appliquer le rollback (mutation inverse ou `fileUpdate` restaurateur).
5. Vérifier que l'état final est identique au snapshot BEFORE (snapshot AFTER-ROLLBACK).
6. Comparez BEFORE et AFTER-ROLLBACK pour confirmer qu'aucun résidu n'est présent (diff vide).

### Pitfalls
- Oublier de capturer un état complet avant la mutation.
- Ne pas vérifier le `null` retourné en cas d'erreur API, ce qui fausse le rollback.
- Confondre GID et Handle (priorisez toujours les GIDs pour les mutations).

### Verification
- `Diff BEFORE vs AFTER-ROLLBACK == VIDE`.
- Retourner systématiquement l'ID de l'entité rollbackée pour confirmation.
