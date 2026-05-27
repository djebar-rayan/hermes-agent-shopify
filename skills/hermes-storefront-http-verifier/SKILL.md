---
name: hermes-storefront-http-verifier
description: Verifies the public HTTP rendering of the Shopify storefront after a mutation
category: monitoring
version: 0.1.0-PROPOSED
metadata:
  hermes:
    tags: [monitoring, http, storefront, verification]
  proposed:
    date: 2026-05-14
    based_on_pattern: "Storefront HTTP verification after mutation"
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
Use this skill immediately after performing critical mutations (such as changing a product status, modifying prices or descriptions) to make sure the changes are properly reflected on the public site (storefront), bypassing any local caches.

## Procedure
1. Identify the public URL of the product or page (e.g. `https://${SHOP_DOMAIN}/products/handle`).
2. Issue an HTTP GET request (via `curl` or a Python library).
3. Parse the returned HTML source to look for the target tags (e.g. `<title>`, `<meta name="description">`, or price elements).
4. Compare the found values with those expected after the mutation.

## Pitfalls
- **CDN / Shopify cache:** Shopify sometimes takes a few minutes to purge its cache. If verification fails immediately, you may need to wait 1 to 2 minutes and retry.
- **Bot blocking:** Watch User-Agents. Use a standard browser User-Agent for the `curl` request.
- **Dynamic theme:** Some themes load data via client-side JavaScript. In that case, a simple `curl` may not be sufficient.

## Verification
- HTTP return code must be 200 (or 404 if the goal was to verify draft status).
- Expected content must be strictly present in the response body.
