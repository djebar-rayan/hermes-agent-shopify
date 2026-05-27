---
name: shopify-batch-executor
description: Execute a batch of max 10 Shopify productUpdate calls with before/after snapshot, operator validation via Telegram+email, and rollback available
version: 1.0.0
author: Hermes (Phase 2 scaffold)
metadata:
  hermes:
    tags: [shopify, mutation, phase2, framework, validation]
    category: ecommerce
    requires_toolsets: [terminal, file, messaging]
---
# Batch Executor <STORE_NAME>

## When to Use
- After gap analysis to apply targeted green 🟢 actions
- On explicit request: "execute batch 1" or "apply fixes on these products"
- Dedicated Phase 2 cron if configured
- NEVER without prior operator Telegram /yes validation

## Test mode flag

MANDATORY: read `$HERMES_MODE` from `/root/.hermes/.env` before any action:
- If `HERMES_MODE=test`: apply the mutation THEN execute the rollback in the SAME run (apply+rollback same run). Before/intermediate/after snapshots emailed to operator via hermes-email-sender.
- If `HERMES_MODE=prod`: persistent apply + rollback script available. Requires prior Telegram /yes.
- If the variable is missing or has another value: default TEST behavior (safety).

## Mandatory dependency
**Also load the `hermes-schema-guard` skill before any mutation**, and copy EXACTLY the validated GraphQL fragments listed there (productUpdate, productVariantsBulkUpdate, etc.). NEVER invent a field that isn't listed there. If you need a mutation not listed in schema-guard, first run a `__type` introspection to validate the schema, then ADD the fragment to the schema-guard skill after success.

## Procedure
1. Check MEMORY.md: current Phase = Phase 2 or above. If Phase 1 read-only: STOP, this skill is forbidden.

2. Identify the batch to execute:
   - Either the user specified a batch ("batch 1")
   - Or auto-derive: top 10 priority products from phase2-gap-analysis-YYYY-MM-DD.md

3. For each product in the batch (max 10):
   a. Capture snapshot via GraphQL: product(id) { id, handle, title, tags, descriptionHtml, updatedAt }
   b. Save to $HERMES_WORKSPACE/batches/YYYY-Www-batchN-before.json (JSON array)
   c. Determine precise changes:
      - tags: add missing tags identified by gap-analyzer
      - descriptionHtml: if shipping block absent at start, prepend "<p><strong>📦 Livraison :</strong> Expedition sous 2-3 jours ouvres depuis la France. Livraison standard offerte des 50€ d'achat. Délais 3-5 jours en France métropolitaine.</p>" at the very beginning

4. Generate JSON preview diff in $HERMES_WORKSPACE/batches/YYYY-Www-batchN-preview.json
   Format: array of {handle, before: {tags, descriptionExcerpt}, after: {tags, descriptionExcerpt}}

5. Generate rollback script $HERMES_WORKSPACE/batches/phase2-rollback-batchN.sh
   - Bash script that reads before.json, re-runs productUpdate with original values for each product
   - chmod +x

6. Send OPERATOR VALIDATION (mandatory before mutation):
   a. Telegram chat $TELEGRAM_HOME_CHANNEL: clear message with short preview (10 products, action per product, link to VPS files)
   b. Email to $EMAIL_TO via inline Python smtplib (see EMAIL SENDING procedure in cron prompts) with detailed preview
   c. Message explicitly includes: "Reply /yes to apply, /no to cancel, /edit <handle> <details> to adjust"

7. WAIT for user response (skill pauses, user responds via Telegram). If no response within 10 min, abandon and send alert message.

8. If response = /yes:
   a. Execute the 10 productUpdate calls via shopify store execute in sequence (2s spacing to avoid rate-limit)
   b. Capture after-snapshot in batches/YYYY-Www-batchN-after.json
   c. Generate real diff in batches/YYYY-Www-batchN-diff.md (readable markdown)
   d. tool_call_completed hook automatically logs each productUpdate in learnings.md
   e. Telegram + email confirmation: "Batch N applied. X/10 success. Rollback available: phase2-rollback-batchN.sh"

9. If response = /no: clean cancel, keep preview and rollback files for future retry. Telegram + email message.

10. If response = /edit: apply the adjustment, regenerate preview, ask for validation again.

## Pitfalls
- NEVER execute without explicit operator /yes. The pause is mandatory.
- 2s spacing between productUpdate calls to avoid Shopify rate-limit (1.4 req/s default).
- If a mutation fails: STOP the batch, log the exact error, rollback previous ones via the script, alert via Telegram.
- The shipping block must be INJECTED at the VERY START of descriptionHtml. NEVER replace existing HTML.
- batch > 10 products is FORBIDDEN. If more than 10 to do: split into multiple batches.
- Brand vocabulary mandatory in any modified description (see STANDING.md).

## Verification
- before.json file exists before mutation
- rollback.sh file generated and chmod +x
- Telegram + email preview received by operator
- If /yes: 10/10 productUpdate success, after.json + diff.md generated
- log-learning hook has added 10 entries in learnings.md
- Mutation queries (`productUpdate`, `collectionCreate`, etc.) can fail due to the Admin API's strict schema (e.g. `createdAt` field incorrectly included).
  **GUARD:** During exploratory tests or mutations, use a *guard try/catch* mechanism (e.g. test with/without `createdAt` on schema errors).
