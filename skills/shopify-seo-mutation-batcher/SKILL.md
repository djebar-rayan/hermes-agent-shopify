---
name: shopify-seo-mutation-batcher
description: Automates batch updates of SEO title and description
category: seo
version: 0.1.0-PROPOSED
metadata:
  hermes:
    tags: [seo, graphql, batch, shopify]
  proposed:
    date: 2026-05-14
    based_on_pattern: "Mutations seo:{title,description} on products via GraphQL productUpdate"
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
Use this skill when you need to update SEO tags (meta title, meta description) for multiple products at once. This pattern was observed many times during phase 3 and phase 4.2b/4.2c, justifying automation through a dedicated skill.

## Procedure
1. Extract the target handles.
2. Use a GraphQL `productUpdate` query for each product ID.
3. The target field is `seo: { title: "...", description: "..." }`.
4. Perform requests in batches of maximum 10 products to avoid Shopify Admin API throttling.
5. Save the previous state in a `snapshot-before.json` file to enable potential rollback.

## Pitfalls
- **API limits:** Don't exceed the GraphQL quota. Always use throttling or a delay if the batch exceeds 10 items.
- **Overwriting:** Verify you're not overwriting an already-optimized meta description (check state before mutation).
- **SEO format:** Title should ideally be under 60 characters, and description under 160 characters.

## Verification
1. Run the `product(id) { seo { title description } }` query post-mutation.
2. Verify the response exactly matches the values sent.
