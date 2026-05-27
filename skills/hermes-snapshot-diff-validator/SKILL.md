---
name: hermes-snapshot-diff-validator
description: Validation pattern for Shopify batches with apply+rollback.
version: 0.1.0
author: Hermes auto-meta grand-run-2026-W20
category: devops
tags:
  - auto-proposed
  - grand-run-2026-W20

---

### When to Use
Use this pattern when performing test mutations (productUpdate, collectionCreate, etc.) on Shopify that must be reverted (rollback) to keep a clean environment.

### Procedure
1. Query the current state of the entities (BEFORE snapshot).
2. Apply the expected mutation.
3. Verify the mutation succeeded (AFTER-APPLY snapshot).
4. Apply the rollback (inverse mutation or restoring `fileUpdate`).
5. Verify the final state matches the BEFORE snapshot (AFTER-ROLLBACK snapshot).
6. Compare BEFORE and AFTER-ROLLBACK to confirm no residue remains (empty diff).

### Pitfalls
- Forgetting to capture a complete state before the mutation.
- Not checking the `null` returned on API error, which falsifies the rollback.
- Confusing GID and Handle (always prioritize GIDs for mutations).

### Verification
- `Diff BEFORE vs AFTER-ROLLBACK == EMPTY`.
- Always return the rolled-back entity ID for confirmation.
