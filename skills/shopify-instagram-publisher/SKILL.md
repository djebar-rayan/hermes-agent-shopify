---
name: shopify-instagram-publisher
description: Generates Instagram Graph API payload with MANDATORY operator approval (email + Telegram) before actual publication
category: social-media
version: 2.0.0
metadata:
  hermes:
    tags: [instagram, meta-graph, approval-gate, dry-run]
    requires_toolsets: [terminal]
---

# <STORE_NAME> Instagram Publisher

## When to Use
- After `shopify-instagram-ideator` or reading a draft `campaigns/<event>/insta-post-*.md`
- 4 modes:
  - **dry**: generate offline payload, ZERO API call (Phase 3/4 test or offline validation)
  - **container**: call `POST /{ig-id}/media` to create container, NEVER `/media_publish` (Graph API auth validation)
  - **approval**: container + send preview email+Telegram, WAIT for operator /yes <container_id> before publish (RECOMMENDED in prod)
  - **publish_now**: container + direct publish_media (forbidden in autonomous mode — operator escape hatch only)

## Test mode flag

MANDATORY: read `$HERMES_MODE` from `/root/.hermes/.env` before any action:
- If `HERMES_MODE=test` or absent: force `mode=dry` regardless of supplied parameter. Offline payload generation only, ZERO Graph API call.
- If `HERMES_MODE=prod`:
  - **Default = `mode=approval`**: no publish without explicit operator /yes
  - `mode=publish_now` allowed ONLY if the operator explicitly specifies it in the prompt

## Approval gate workflow (default prod mode)

When `HERMES_MODE=prod` and `mode=approval` (default):

1. **Build the payload** (caption + hashtags + image_url or video_url) per Graph API format
2. **Offline validation** (caption < 2200, hashtags <= 30, https URLs, image dimensions)
3. **Create the Meta container** via `POST /{IG_BUSINESS_ACCOUNT_ID}/media` (without publish)
4. **Retrieve container_id** returned by Graph API
5. **Send preview to operator via 2 simultaneous channels**:
   - **Email** via `hermes-email-sender` (mode=prod, recipient = $EMAIL_TO):
     - Subject: `[APPROVAL REQUIRED] <STORE_NAME> Insta post to validate - container <container_id>`
     - Body: full payload + clickable image_url + Telegram command to validate/reject
   - **Telegram** chat $TELEGRAM_HOME_CHANNEL:
     - Short message (< 1500 chars) with preview + container_id + instructions
     - "To publish: reply `/yes_insta <container_id>` on Telegram. To cancel: `/no_insta <container_id>`."
6. **DO NOT PUBLISH**. The container expires on its own after 24h if not published (Meta limit).
7. **Log in learnings.md**: `INSTA-APPROVAL-PENDING container=<id> sent=<timestamp>`

## Publish when /yes received (dedicated cron or manual prompt)

A `shopify-insta-publish-on-yes` cron (to be created, 5 minute frequency) or manual prompt checks pending containers and publishes those that received `/yes_insta <id>`:

1. Reads `$HERMES_WORKSPACE/insta-approvals.log` (new file, append-only via Telegram webhook or polling)
2. For each approved container_id:
   - `POST /{IG_BUSINESS_ACCOUNT_ID}/media_publish` with `creation_id=<container_id>`
   - Capture final media_id
3. Notify operator of effective publication: email + Telegram "Post published on @<store_handle>: <permalink>"
4. Log in `learnings.md`: `INSTA-PUBLISHED media=<id> permalink=<url>`

## Detailed procedure per mode

### Dry mode (test or offline validation)
1. Build JSON payload
2. Offline validation (4 criteria)
3. Save in `$HERMES_WORKSPACE/tests/insta-payload-<timestamp>.json`
4. **STOP**. No network call.

### Container mode
1. Build payload + offline validation
2. `curl -X POST "https://graph.facebook.com/v18.0/${IG_BUSINESS_ACCOUNT_ID}/media" -d "..."`
3. Capture container_id, log
4. **STOP**. No media_publish.

### Approval mode (DEFAULT in prod)
1. Container mode (steps 1-3 above)
2. Email approval + Telegram approval (see §Approval gate workflow)
3. **STOP**. Wait for operator /yes_insta.

### Publish_now mode (forbidden autonomous)
1. Container mode
2. `POST /media_publish?creation_id=<container_id>`
3. Email + Telegram notification of effective publication
4. **Requires explicit "mode=publish_now" operator mention in the prompt**

## Pitfalls
- **HERMES_MODE=prod without explicit mode = approval** (NEVER publishes without operator /yes)
- Without `INSTAGRAM_GRAPH_TOKEN` or `IG_BUSINESS_ACCOUNT_ID` in .env: container/approval/publish modes impossible. Stay on dry and flag (see INSTAGRAM-SETUP-TODO.md)
- Caption > 2200 chars = refused by Meta. Truncate or regenerate
- > 30 hashtags = refused. Reduce
- On Meta API error (`OAuthException`, rate limit): DO NOT retry blindly, log and alert
- CAROUSEL: strictly 2-10 children. More = refused
- **Meta container TTL = 24h unpublished**. If the operator doesn't validate within 24h, the container expires and you must restart from scratch.

## Verification
- Dry mode: valid JSON payload written, parseable by `json.loads`, 0 network calls
- Container mode: container_id returned by Graph API, 0 calls to media_publish (verifiable via log)
- Approval mode: container_id + email sent (EMAIL_SMTP_OK) + Telegram sent + 0 calls to media_publish
- Publish_now mode: final media_id returned, permalink emailed, "/yes_insta" operator mention present in the prompt
