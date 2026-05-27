---
name: hermes-schema-guard
description: Fragments GraphQL Shopify Admin validés — référence à charger AVANT toute mutation pour éviter les hallucinations de champs
category: e-commerce
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, schema, reference, mutation-safety]
    category: reference
    requires_toolsets: [terminal]
---

# <STORE_NAME> Shopify Schema Guard

## When to Use
AVANT toute mutation Shopify (productCreate, productUpdate, productDelete, collectionCreate, collectionDelete, productVariantsBulkUpdate, urlRedirectCreate, urlRedirectDelete, etc.). Charge ce skill, copie le fragment EXACT, n'invente RIEN.

Trigger automatique : si ta prochaine action implique `shopify store execute --allow-mutations`, ce skill est obligatoire.

## Procedure
1. Identifie la mutation cible.
2. Trouve son fragment ci-dessous.
3. Copie EXACTEMENT la structure (champs et types).
4. Si la mutation n'est pas listée :
   - exécute d'abord l'introspection : `{ __type(name: "<TypeName>") { fields { name type { name } } } }`
   - puis tente la mutation
   - si elle réussit, AJOUTE-LA à ce skill avec timestamp de validation
5. Toujours utiliser `--allow-mutations` sur `shopify store execute`.

---

## Fragments validés

### productCreate (validé 2026-05-13 P3.9)
```graphql
mutation {
  productCreate(product: {
    title: "...",
    descriptionHtml: "...",
    productType: "...",
    vendor: "<STORE_NAME>",
    status: DRAFT,
    tags: ["..."]
  }) {
    product { id title handle status }
    userErrors { field message }
  }
}
```
Notes : `createdAt`/`updatedAt` ne sont PAS exposés ici. Utilise `product(id:).createdAt` séparément si besoin.

### productDelete (validé 2026-05-13 P3.9)
```graphql
mutation { productDelete(input: { id: "gid://shopify/Product/..." }) {
  deletedProductId
  userErrors { field message }
} }
```

### productUpdate (validé 2026-05-13 P2 préparation Batch 1)
```graphql
mutation { productUpdate(input: {
  id: "gid://shopify/Product/...",
  tags: ["..."],
  descriptionHtml: "..."
}) {
  product { id title handle tags }
  userErrors { field message }
} }
```

### collectionCreate (validé 2026-05-13 P3.4)
```graphql
mutation { collectionCreate(input: { title: "...", descriptionHtml: "..." }) {
  collection { id title handle }
  userErrors { field message }
} }
```
Notes : PAS de `createdAt` sur type Collection (erreur observée P3.4 1er run). Ne tente pas non plus `publishedAt` (différent endpoint).

### collectionDelete (validé 2026-05-13 P3.4)
```graphql
mutation { collectionDelete(input: { id: "gid://shopify/Collection/..." }) {
  deletedCollectionId
  userErrors { field message }
} }
```

### productVariantsBulkUpdate (validé 2026-05-13 P3.6)
```graphql
mutation {
  productVariantsBulkUpdate(
    productId: "gid://shopify/Product/...",
    variants: [{
      id: "gid://shopify/ProductVariant/...",
      compareAtPrice: "23.00"
    }]
  ) {
    product { id }
    productVariants { id compareAtPrice price }
    userErrors { field message }
  }
}
```
Notes :
- Modifier `compareAtPrice` = action 🟡 sûre (prix barré marketing).
- Modifier `price` directement = action 🔴 (jamais sans /yes tuteur + audit prix).
- Rollback : passer `compareAtPrice: null` pour effacer.


### fileUpdate (validé 2026-05-13 P4.2 introspection)
```graphql
mutation { fileUpdate(files: [
  { id: "gid://shopify/MediaImage/...", alt: "..." }
]) {
  files { ... on MediaImage { id alt } }
  userErrors { field message code }
} }
```
Notes :
- Pour modifier alt-text d une MediaImage : utiliser fileUpdate (PAS productUpdate avec media field).
- FileUpdateInput accepte : id, alt, originalSource, previewImageSource, filename, referencesToAdd, referencesToRemove.
- Rollback : passer alt: null OU alt: "" (Shopify accepte les deux pour vider).
- Pour récupérer les image_id réels : query product(handle).media(first:10) { edges { node { ... on MediaImage { id alt } } } }.

### urlRedirectCreate (bloqué 2026-05-13 P3.5)
```graphql
mutation { urlRedirectCreate(urlRedirect: { path: "/...", target: "/..." }) {
  urlRedirect { id path target }
  userErrors { field message }
} }
```
Scope requis : `write_online_store_navigation` — à activer côté admin Shopify (Apps > Custom > Configure scopes > re-install). Tant que le scope manque : skill non utilisable.

### urlRedirectDelete (schéma documenté, à valider après activation scope)
```graphql
mutation { urlRedirectDelete(id: "gid://shopify/UrlRedirect/...") {
  deletedUrlRedirectId
  userErrors { field message }
} }
```

---

## Queries de lecture utiles (read-only, pas de scope spécifique)

### Lister produits avec alt-text vide
```graphql
{ products(first: 50, query: "status:active") { edges { node {
  id handle title
  media(first: 10) { edges { node { ... on MediaImage { id alt image { url } } } } }
} } } }
```

### Lister variantes avec leur compareAtPrice
```graphql
{ products(first: 50, query: "status:active") { edges { node {
  id handle title
  variants(first: 5) { edges { node { id price compareAtPrice } } }
} } } }
```

### Introspection d'un type (toujours sûre)
```graphql
{ __type(name: "Collection") { fields { name type { name kind } } } }
```

---

## Pitfalls
- **Hallucination de champs** : N'AJOUTE JAMAIS un champ que tu n'as pas vu dans ce skill ou validé via introspection. Le pattern `createdAt` existe sur Order/Product mais PAS sur Collection.
- **Scope manquant** : avant de tenter `urlRedirectCreate`, vérifie via une mutation simple si le scope est OK. Si `ACCESS_DENIED` → arrête, signale tuteur, ne devine pas un autre endpoint.
- **userErrors non vide** : ne réessaie PAS en modifiant aveuglément le payload. Log l'erreur, alerte tuteur, attend instruction.
- **--allow-mutations** : oublié = erreur silencieuse `Mutations not allowed`. Toujours ajouter ce flag pour productUpdate/Create/Delete/collectionCreate/Delete/variantsBulkUpdate.
- **Idempotence** : Shopify rejette les Update sans changement réel (parfois userErrors vide mais aucune modif). Re-query après mutation pour confirmer.
- **Rate limit** : Shopify limite à ~2 mutations/s. Pour batch > 10 produits, espacer de 500ms.

## Verification
Chaque fragment ci-dessus a son timestamp "validé" indiquant qu'il a été exécuté avec succès dans un test Hermes documenté. Quand tu ajoutes un nouveau fragment :
1. Exécute manuellement via `shopify store execute --allow-mutations` en sandbox/draft
2. Capture la réponse complète (incluant userErrors vide)
3. Ajoute le fragment ici avec date + référence test (ex: "validé 2026-05-14 P3.X")
4. Commit en mémoire OpenViking pour persistance cross-session

## Mutations interdites (jamais à exécuter sans validation explicite tuteur)
- `shopOptionsUpdate`, `shopUpdate`, `shopBillingUpdate` — changements globaux 🔴
- `bulkOperationRunQuery` avec mutations massives 🔴
- Toute mutation sur `customer`, `order`, `refund` 🔴
- `themeUpdate`, `themePublish` 🔴
