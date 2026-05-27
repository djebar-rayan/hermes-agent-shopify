---
name: shopify-batch-rollback
description: Revert a productUpdate batch via before.json snapshot - safety usage if a batch broke products
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
- After batch-executor execution if a regression is detected
- On explicit request: "rollback batch N" or "revert yesterday's batch"
- After D+7 impact measurement if impact is significantly negative
- Idempotence test (running rollback then rollback of rollback = no-op)

## Procedure
1. Identify the batch to rollback: receives batchId parameter (e.g. "2026-W20-batch1") or asks the user if ambiguous.

2. Verify before.json snapshot exists: $HERMES_WORKSPACE/batches/<batchId>-before.json. If missing: STOP, cannot rollback without snapshot.

3. Load the JSON snapshot (array of products with their original tags + descriptionHtml + updatedAt values).

4. For each product in the snapshot:
   a. Capture CURRENT state via GraphQL product(id) (to compare and verify there was indeed a mutation since the snapshot)
   b. If current == snapshot: skip (already at original state, idempotent)
   c. Otherwise: execute productUpdate with snapshot values (tags + descriptionHtml)
   d. 2s spacing between mutations

5. Generate $HERMES_WORKSPACE/batches/<batchId>-rollback-YYYY-MM-DDTHH:MM.md with:
   - List of rollback products (success / skip / failure)
   - Current vs snapshot diff for audit

6. Notify Telegram + email:
   "Rollback batch <batchId> completed. X/10 products restored, Y skipped (already at origin), Z failures."

7. Log in learnings.md: add entry "Rollback batch <batchId>" with results.

## Pitfalls
- Idempotent mandatory: a product already at origin state is SKIPPED, not re-mutated (avoids unnecessary updates).
- If the product was modified manually by the user in the meantime: log a warning but proceed with rollback (snapshot safety takes priority).
- On productUpdate failure: continue with others, log the exact error. NEVER abandon mid-rollback.
- No operator validation required for rollback (safety action, must be fast).

## Verification
- <batchId>-rollback-YYYY-MM-DDTHH:MM.md file created
- Telegram + email sent with stats
- learnings.md has a rollback entry
- shopify store execute confirms post-rollback state == snapshot for non-skip products
