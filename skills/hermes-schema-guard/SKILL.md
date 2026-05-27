---
name: hermes-schema-guard
description: Validated Shopify Admin GraphQL fragments — reference to load BEFORE any mutation to prevent field hallucinations
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
BEFORE any Shopify mutation (productCreate, productUpdate, productDelete, collectionCreate, collectionDelete, productVariantsBulkUpdate, urlRedirectCreate, urlRedirectDelete, etc.). Load this skill, copy the EXACT fragment, invent NOTHING.

Automatic trigger: if your next action involves `shopify store execute --allow-mutations`, this skill is mandatory.

## Procedure
1. Identify the target mutation.
2. Find its fragment below.
3. Copy EXACTLY the structure (fields and types).
4. If the mutation is not listed:
   - first run introspection: `{ __type(name: "<TypeName>") { fields { name type { name } } } }`
   - then attempt the mutation
   - if it succeeds, ADD IT to this skill with a validation timestamp
5. Always use `--allow-mutations` on `shopify store execute`.

---

## Validated fragments

### productCreate (validated 2026-05-13 P3.9)
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
Notes: `createdAt`/`updatedAt` are NOT exposed here. Use `product(id:).createdAt` separately if needed.

### productDelete (validated 2026-05-13 P3.9)
```graphql
mutation { productDelete(input: { id: "gid://shopify/Product/..." }) {
  deletedProductId
  userErrors { field message }
} }
```

### productUpdate (validated 2026-05-13 P2 preparation Batch 1)
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

### collectionCreate (validated 2026-05-13 P3.4)
```graphql
mutation { collectionCreate(input: { title: "...", descriptionHtml: "..." }) {
  collection { id title handle }
  userErrors { field message }
} }
```
Notes: NO `createdAt` on Collection type (error observed P3.4 1st run). Also don't try `publishedAt` (different endpoint).

### collectionDelete (validated 2026-05-13 P3.4)
```graphql
mutation { collectionDelete(input: { id: "gid://shopify/Collection/..." }) {
  deletedCollectionId
  userErrors { field message }
} }
```

### productVariantsBulkUpdate (validated 2026-05-13 P3.6)
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
Notes:
- Modifying `compareAtPrice` = 🟡 safe action (marketing strike-through price).
- Modifying `price` directly = 🔴 action (never without operator /yes + price audit).
- Rollback: pass `compareAtPrice: null` to clear.


### fileUpdate (validated 2026-05-13 P4.2 introspection)
```graphql
mutation { fileUpdate(files: [
  { id: "gid://shopify/MediaImage/...", alt: "..." }
]) {
  files { ... on MediaImage { id alt } }
  userErrors { field message code }
} }
```
Notes:
- To modify a MediaImage alt-text: use fileUpdate (NOT productUpdate with media field).
- FileUpdateInput accepts: id, alt, originalSource, previewImageSource, filename, referencesToAdd, referencesToRemove.
- Rollback: pass alt: null OR alt: "" (Shopify accepts both for clearing).
- To retrieve actual image_id: query product(handle).media(first:10) { edges { node { ... on MediaImage { id alt } } } }.

### urlRedirectCreate (blocked 2026-05-13 P3.5)
```graphql
mutation { urlRedirectCreate(urlRedirect: { path: "/...", target: "/..." }) {
  urlRedirect { id path target }
  userErrors { field message }
} }
```
Required scope: `write_online_store_navigation` — to activate on Shopify admin side (Apps > Custom > Configure scopes > re-install). As long as the scope is missing: skill unusable.

### urlRedirectDelete (documented schema, to validate after scope activation)
```graphql
mutation { urlRedirectDelete(id: "gid://shopify/UrlRedirect/...") {
  deletedUrlRedirectId
  userErrors { field message }
} }
```

---

## Useful read queries (read-only, no specific scope)

### List products with empty alt-text
```graphql
{ products(first: 50, query: "status:active") { edges { node {
  id handle title
  media(first: 10) { edges { node { ... on MediaImage { id alt image { url } } } } }
} } } }
```

### List variants with their compareAtPrice
```graphql
{ products(first: 50, query: "status:active") { edges { node {
  id handle title
  variants(first: 5) { edges { node { id price compareAtPrice } } }
} } } }
```

### Type introspection (always safe)
```graphql
{ __type(name: "Collection") { fields { name type { name kind } } } }
```

---

## Pitfalls
- **Field hallucination**: NEVER ADD a field you haven't seen in this skill or validated via introspection. The `createdAt` pattern exists on Order/Product but NOT on Collection.
- **Missing scope**: before attempting `urlRedirectCreate`, check via a simple mutation if the scope is OK. If `ACCESS_DENIED` → stop, alert operator, do not guess another endpoint.
- **userErrors non-empty**: do NOT retry by blindly modifying the payload. Log the error, alert operator, wait for instruction.
- **--allow-mutations**: forgotten = silent `Mutations not allowed` error. Always add this flag for productUpdate/Create/Delete/collectionCreate/Delete/variantsBulkUpdate.
- **Idempotence**: Shopify rejects Updates without actual change (sometimes empty userErrors but no modification). Re-query after mutation to confirm.
- **Rate limit**: Shopify limits to ~2 mutations/s. For batch > 10 products, space by 500ms.

## Verification
Each fragment above has its "validated" timestamp indicating it was successfully executed in a documented Hermes test. When you add a new fragment:
1. Manually execute via `shopify store execute --allow-mutations` in sandbox/draft
2. Capture the full response (including empty userErrors)
3. Add the fragment here with date + test reference (e.g. "validated 2026-05-14 P3.X")
4. Commit to OpenViking memory for cross-session persistence

## Forbidden mutations (never to execute without explicit operator validation)
- `shopOptionsUpdate`, `shopUpdate`, `shopBillingUpdate` — global changes 🔴
- `bulkOperationRunQuery` with massive mutations 🔴
- Any mutation on `customer`, `order`, `refund` 🔴
- `themeUpdate`, `themePublish` 🔴
