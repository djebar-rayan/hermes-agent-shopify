---
name: shopify-seo-mutation-batcher
description: Automatise la mise a jour en lot des SEO title et description
category: seo
version: 0.1.0-PROPOSED
metadata:
  hermes:
    tags: [seo, graphql, batch, shopify]
  proposed:
    date: 2026-05-14
    based_on_pattern: "Mutations seo:{title,description} sur produits via GraphQL productUpdate"
    occurrences_found: 8
    sources: [
      "$HERMES_WORKSPACE/tests/p4-batch-metatitle-before.json",
      "$HERMES_WORKSPACE/tests/p4-batch-metatitle-after.json",
      "$HERMES_WORKSPACE/tests/p4-batch-desc-before.json",
      "$HERMES_WORKSPACE/tests/p3.1-seo-mutation.md"
    ]
    proposed_by: "meta-revue-auto P4.4"
    requires_validation: true
---

# shopify-seo-mutation-batcher

## When to Use
Utilisez ce skill lorsque vous devez mettre à jour les balises SEO (meta title, meta description) pour plusieurs produits en même temps. Ce pattern a été observé de nombreuses fois lors de la phase 3 et de la phase 4.2b/4.2c, justifiant l'automatisation par un skill dédié.

## Procedure
1. Extraire les handles cibles.
2. Utiliser une requête GraphQL `productUpdate` pour chaque ID de produit.
3. Le champ cible est `seo: { title: "...", description: "..." }`.
4. Effectuer les requêtes par lots (batch) de maximum 10 produits pour éviter les blocages de l'API Admin de Shopify.
5. Sauvegarder l'état précédent dans un fichier `snapshot-before.json` pour permettre un rollback éventuel.

## Pitfalls
- **Limites de l'API :** Ne pas dépasser le quota GraphQL. Toujours utiliser un throttle ou un délai si le lot dépasse 10 éléments.
- **Ecrasement :** Bien vérifier qu'on n'écrase pas une meta description déjà optimisée (vérifier l'état avant mutation).
- **Format des SEO :** Le title doit idéalement faire moins de 60 caractères, et la description moins de 160 caractères.

## Verification
1. Lancer la requête `product(id) { seo { title description } }` post-mutation.
2. Vérifier que la réponse correspond exactement aux valeurs envoyées.
