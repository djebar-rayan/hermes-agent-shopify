---
name: shopify-theme-editor
description: Modifies <STORE_NAME> Shopify theme files (sections, snippets, templates, assets) headlessly via Theme Access token, with mandatory backup, pre-push lint, diff/verify, and duplicate-preview workflow for risky changes
version: 1.1.0
author: Hermes (2026-05-24)
metadata:
  hermes:
    tags: [shopify, theme, mutation, framework, headless]
    category: ecommerce
    requires_toolsets: [terminal, file, messaging]
---

# <STORE_NAME> Theme Editor (v1.1)

Skill for modifying the live Shopify theme "update 19 12 2025 Sense" (ID `$LIVE_THEME_ID`) via Theme Access token, without depending on missing OAuth scopes (`write_themes`).

**v1.1 changes:**
- Helper lib `/root/.hermes/lib/theme.sh` (DRY, sourceable)
- Pre-push lint (JSON, Liquid tags, CSS braces)
- AUTO backup via helper (no more manual pattern)
- Pre-push diff displayed systematically
- Post-push verify (re-fetch + compare)
- **Duplicate-preview workflow** for risky changes (header, footer, layout, critical section overhaul)
- Multi-file atomic push with transactional rollback
- Clearly distinguishes "incremental edit" (direct push) and "overhaul" (mandatory preview)

## When to Use

- Incremental edit of a theme file: "add some CSS", "modify this section", "change the footer", "edit the product.json template"
- Custom product/page template creation (e.g. `templates/product.test-returns.json` of 2026-05-24)
- Visual overhaul (header, footer, palette, typography) → **mandatory duplicate-preview**
- NEVER to modify product, page, blog, or collection content (use dedicated skills)
- NEVER to toggle a templateSuffix (product action, not theme)

## Configuration

### Required environment variables
Reads from `/root/.hermes/.env`:
- `SHOPIFY_CLI_THEME_TOKEN` (starts with `shptka_`) — created 2026-05-24
- `SHOPIFY_STORE=<your_store_handle>`
- `TELEGRAM_BOT_TOKEN` (for /yes)

If `SHOPIFY_CLI_THEME_TOKEN` is missing: STOP with message `[THEME_FAIL: missing SHOPIFY_CLI_THEME_TOKEN — see reference_shopify_theme_access.md to recreate via Theme Access app]`.

### Constants (in helper lib)
- `LIVE_THEME_ID=$LIVE_THEME_ID`
- `THEME_BACKUP_DIR=$HERMES_WORKSPACE/theme-backups/`
- `THEME_WORK_BASE=/tmp/theme-work` (temporary `theme-work.XXXXXX` dirs)

### Helper lib
```bash
set -a; . /root/.hermes/.env; set +a
. /root/.hermes/lib/theme.sh
theme_check_env || exit 1
```

Exposed functions:
- `theme_get FILENAME [OUTPUT] [THEME_ID]` — fetch content
- `theme_backup FILENAME [THEME_ID]` — timestamped backup, echoes path
- `theme_lint LOCAL_FILE` — checks valid JSON, balanced Liquid tags, CSS braces
- `theme_diff LOCAL_FILE REMOTE [THEME_ID]` — unified diff on stdout (rc=0 no diff, 1 diff, 2 err)
- `theme_push LOCAL_FILE REMOTE [THEME_ID]` — push 1 file
- `theme_push_many WORK_DIR [THEME_ID]` — atomic push of N files with rollback
- `theme_verify LOCAL_FILE REMOTE [THEME_ID]` — re-fetch and compare (rc=0 if match)
- `theme_safety_level PATH` — echoes green|yellow|red-block|red-forbidden
- `theme_duplicate [NAME]` — duplicates live, echoes new theme ID
- `theme_preview_url THEME_ID` — preview URL
- `theme_delete THEME_ID` — refuses if == LIVE
- `theme_publish THEME_ID` — set as live
- `theme_list` — lists id|name|role

## Safety levels

`theme_safety_level $PATH` returns:

| Pattern | Level | Action |
|---|---|---|
| `assets/*`, `snippets/*` | 🟢 **green** | Backup + lint + direct push |
| `sections/*.liquid`, `templates/*`, `locales/*` | 🟡 **yellow** | Backup + lint + diff + /yes Telegram + push + verify |
| `layout/*.liquid`, `config/settings_schema.json` | 🔴 **red-block** | Refuses except with explicit written operator override: "I confirm <action> on <file>" |
| `config/settings_data.json` | 🔴 **red-forbidden** | NEVER modify (guaranteed corruption of theme editor settings) |

**Override for red-block**: the user must write word-for-word "I confirm <action> on <file>" in chat (e.g. "I confirm layout edit on theme.liquid"). Otherwise refused.

## Workflows

### Workflow A: Incremental edit (single file, low risk)

For 🟢 green or 🟡 yellow concerning 1 file with a targeted change.

```bash
set -a; . /root/.hermes/.env; set +a
. /root/.hermes/lib/theme.sh
theme_check_env || exit 1

FILE="assets/theme.css"  # or any other file
LEVEL=$(theme_safety_level "$FILE")

# 1. Fetch + backup
mkdir -p /tmp/edit && theme_get "$FILE" /tmp/edit/current
BACKUP=$(theme_backup "$FILE")
echo "Backup: $BACKUP"

# 2. Apply the modification (string replace, JSON edit, or append)
node -e "
  const fs = require('fs');
  let c = fs.readFileSync('/tmp/edit/current', 'utf8');
  // ... transformation ...
  fs.writeFileSync('/tmp/edit/new', c);
"

# 3. Lint
theme_lint /tmp/edit/new || { echo "Lint failed, abort"; exit 1; }

# 4. Diff (display)
echo "=== DIFF ==="
theme_diff /tmp/edit/new "$FILE"
DIFF_RC=$?
[ $DIFF_RC -eq 0 ] && { echo "No-op (identical)"; exit 0; }

# 5. /yes Telegram if yellow
if [ "$LEVEL" = "yellow" ]; then
  DIFF_TEXT=$(diff -u /tmp/edit/current /tmp/edit/new | head -100)
  curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d "chat_id=$TELEGRAM_ALLOWED_USERS" \
    --data-urlencode "text=🎨 Theme modification requested
File: $FILE (level: $LEVEL)
Backup: $BACKUP
Diff (excerpt):
\`\`\`
$DIFF_TEXT
\`\`\`
Reply /yes to apply, /no to cancel."
  # Wait for /yes — use the wait_for_telegram_yes() pattern from shopify-batch-executor
  wait_for_telegram_yes 600 || { echo "Timeout or /no"; exit 2; }
fi

# 6. Push + verify
theme_push /tmp/edit/new "$FILE" || exit 1
theme_verify /tmp/edit/new "$FILE" || { echo "VERIFY_FAIL — rollback"; theme_push "$BACKUP" "$FILE"; exit 1; }

echo "[OK] $FILE updated"

# 7. Log
echo "- [$(date -u +%Y-%m-%d)] Theme edit: $FILE ($LEVEL) — backup: $BACKUP" >> /root/.hermes/memories/learnings.md
```

### Workflow B: Create new file (low risk)

Creation = no risk to existing content. Shorter procedure:
```bash
FILE="templates/product.<suffix>.json"   # new file
# 1. Prepare /tmp/edit/new with generated content
# 2. Lint
theme_lint /tmp/edit/new || exit 1
# 3. Direct push (no backup possible — remote file non-existent)
theme_push /tmp/edit/new "$FILE" || exit 1
# 4. Verify
theme_verify /tmp/edit/new "$FILE" || exit 1
# 5. Log
```

### Workflow C: Overhaul / multi-file / high risk → duplicate-preview

For header/footer/palette overhauls, or >2 files modified together, or structural changes:

```bash
set -a; . /root/.hermes/.env; set +a
. /root/.hermes/lib/theme.sh
theme_check_env || exit 1

# 1. Duplicate the live theme
PREVIEW_NAME="Hermes-Preview-$(date -u +%Y%m%dT%H%M%SZ)"
PREVIEW_ID=$(theme_duplicate "$PREVIEW_NAME") || exit 1
echo "Preview theme: $PREVIEW_ID ($PREVIEW_NAME)"
PREVIEW_URL=$(theme_preview_url "$PREVIEW_ID")

# 2. Prepare all modifications in a work dir
WD=$(mktemp -d "$THEME_WORK_BASE.refonte.XXXXXX")
mkdir -p "$WD/assets" "$WD/sections" "$WD/snippets"  # as needed
# ... generate all modified files in $WD ...

# 3. Atomic push to the preview (with auto lint + backup)
theme_push_many "$WD" "$PREVIEW_ID" || {
  echo "Push preview failed — deleting preview theme"
  theme_delete "$PREVIEW_ID"
  exit 1
}

# 4. Screenshot for user validation (playwright via pw CLI)
pw screenshot "$PREVIEW_URL" "/tmp/preview-home.png" --full-page
pw screenshot "${PREVIEW_URL}/products/<sample-product-handle>" "/tmp/preview-product.png" --full-page

# 5. /yes Telegram with preview URL and screenshots
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendPhoto" \
  -F chat_id="$TELEGRAM_ALLOWED_USERS" \
  -F photo="@/tmp/preview-home.png" \
  -F caption="🎨 Overhaul preview ready
Preview URL: $PREVIEW_URL
Theme ID: $PREVIEW_ID
Reply /yes to publish to live, /no to reject (preview will be deleted)."

wait_for_telegram_yes 1800  # 30 min for this kind of validation
case $? in
  0)
    # /yes: push the same files to live
    theme_push_many "$WD" "$LIVE_THEME_ID" || {
      echo "Push live failed after preview validated — anomaly, preview kept for debug"
      exit 1
    }
    # Delete the preview (no longer useful)
    theme_delete "$PREVIEW_ID"
    echo "[OK] Overhaul applied to live"
    ;;
  2)
    # /no: delete preview
    theme_delete "$PREVIEW_ID"
    echo "[CANCELLED] Overhaul refused, preview deleted"
    exit 2
    ;;
  *)
    echo "[TIMEOUT] preview $PREVIEW_ID kept for later validation"
    exit 3
    ;;
esac

rm -rf "$WD"

# Log
echo "- [$(date -u +%Y-%m-%d)] Theme overhaul multi-file via preview $PREVIEW_ID → live $LIVE_THEME_ID" >> /root/.hermes/memories/learnings.md
```

## When to choose A vs B vs C

| Case | Workflow |
|---|---|
| Add a few CSS rules to theme.css | A (green) |
| Modify an existing snippet | A (green) |
| Edit content of a block in templates/product.test-returns.json | A (yellow) |
| Create a new product.X.json template | B |
| Rename the header nav | C (mandatory preview) |
| Color palette overhaul (CSS + possibly settings_schema) | C |
| Add a new homepage section | C |
| Replace the entire footer | C |

**Simple rule**: if >1 file modified OR the change touches a visible zone >25% of the page → workflow C.

## `wait_for_telegram_yes` pattern (to share)

Reference: `shopify-batch-executor` already uses this pattern. If not yet extracted to helper, copy it here:

```bash
wait_for_telegram_yes() {
  local timeout="${1:-600}"
  local start=$(date +%s)
  local last_update_id=0
  while [ $(($(date +%s) - start)) -lt "$timeout" ]; do
    local resp
    resp=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates?offset=$((last_update_id+1))&timeout=10")
    local update_id text
    update_id=$(echo "$resp" | node -e "let b='';process.stdin.on('data',d=>b+=d).on('end',()=>{const r=JSON.parse(b);if(r.result?.length){console.log(r.result[r.result.length-1].update_id);}})")
    [ -n "$update_id" ] && last_update_id=$update_id
    text=$(echo "$resp" | node -e "let b='';process.stdin.on('data',d=>b+=d).on('end',()=>{const r=JSON.parse(b);if(r.result?.length){const m=r.result[r.result.length-1].message;console.log(m?.text||'');}})")
    case "$text" in
      "/yes"|"/YES") return 0 ;;
      "/no"|"/NO")   return 2 ;;
    esac
    sleep 2
  done
  return 1  # timeout
}
```

## Pitfalls (consolidated)

- The `shptka_` token does NOT work with REST API (`X-Shopify-Access-Token` → 401). Only via Shopify CLI.
- `--allow-live` is mandatory for push to live.
- The "Cleaning your remote theme" message during push is misleading: `--only` deletes nothing else.
- `config/settings_data.json` contains all theme editor config — FORBIDDEN.
- `sections/main-product.liquid` is 98KB+: ALWAYS targeted string-replace on a unique marker, NEVER rewrite entirely.
- The GraphQL `themeFilesUpsert` API is BLOCKED on this store (write_themes missing). Only Shopify CLI + Theme Access works.
- To add a block to a specific product: create `templates/product.<suffix>.json` and toggle the `templateSuffix` (product action, in another skill or via productUpdate).
- `theme_push_many` rollback is best-effort — if multiple files fail and rollback fails, alert the user immediately.
- Before a `theme_publish` on validated preview: VERIFY the correct theme ID (race conditions possible if multiple previews in parallel).
- Shopify CDN cache: after push, render may take 30-60s to propagate. Always wait 30s before `theme_verify` (or use `?v=$(date +%s)` cache-bust).

## Verification (checklist per run)

- [ ] `theme_check_env` passed OK
- [ ] Safety level respected (green direct, yellow /yes, red-block override, red-forbidden refused)
- [ ] Lint OK before push
- [ ] Backup created (except for new file creation)
- [ ] Diff displayed (and non-empty, otherwise abort no-op)
- [ ] /yes received for yellow / red-block
- [ ] Push returned success (shop name in JSON response)
- [ ] Post-push verify OK (re-fetch == local)
- [ ] If preview workflow: preview deleted after /yes (or kept if timeout)
- [ ] Entry logged in `learnings.md`
- [ ] Playwright screenshot produced if visual modification (suggest to user)

## Manual rollback (emergency)

If a post-verify change causes an undetected regression:

```bash
. /root/.hermes/lib/theme.sh
# Identify the most recent backup
ls -t $HERMES_WORKSPACE/theme-backups/ | grep "$(echo $FILE | sed 's|/|__|g')" | head -1
BACKUP=$HERMES_WORKSPACE/theme-backups/<the right backup>
theme_push "$BACKUP" "$FILE"
theme_verify "$BACKUP" "$FILE" && echo "Rollback OK"
```

## Changelog

- **v1.1.0** (2026-05-24): helper lib `/root/.hermes/lib/theme.sh`, lint, auto diff/verify, duplicate-preview workflow (C), multi-file atomic push with rollback.
- **v1.0.0** (2026-05-24): initial version, direct push via shopify CLI + Theme Access token.
