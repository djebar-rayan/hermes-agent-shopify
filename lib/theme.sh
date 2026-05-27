#!/usr/bin/env bash
# lib/theme.sh — Helper library for Shopify theme operations (Hermes Framework)
# Sourced by skills like shopify-theme-editor.
#
# Requires in env:
#   SHOPIFY_CLI_THEME_TOKEN (shptka_...)   — Theme Access token (see GETTING-STARTED.md)
#   SHOPIFY_STORE                          — store handle (without .myshopify.com)
#   LIVE_THEME_ID                          — numeric ID of the live theme (via `shopify theme list`)
#   HERMES_WORKSPACE                       — workspace path (defaults to /root/shopify-store)
#
# All functions print errors prefixed with [THEME_FAIL: ...] and return non-zero.
# All mutating functions create backups first.

set -uo pipefail

# === CONSTANTS ============================================================
# Required env vars (no store-specific defaults — fail fast if missing)
: "${SHOPIFY_STORE:?SHOPIFY_STORE not set — see .env}"
: "${LIVE_THEME_ID:?LIVE_THEME_ID not set — discover via 'shopify theme list'}"
: "${HERMES_WORKSPACE:=/root/shopify-store}"

# Derived defaults (paramétrable mais bons defaults)
: "${LIVE_THEME_GID:=gid://shopify/OnlineStoreTheme/$LIVE_THEME_ID}"
: "${THEME_BACKUP_DIR:=$HERMES_WORKSPACE/theme-backups}"
: "${THEME_WORK_BASE:=/tmp/theme-work}"
: "${TOOLKIT_LIB:=$HERMES_WORKSPACE/shopify-automation-toolkit/lib/shopify-graphql.js}"

mkdir -p "$THEME_BACKUP_DIR" 2>/dev/null

# === GUARDS ===============================================================
theme_check_env() {
  if [ -z "${SHOPIFY_CLI_THEME_TOKEN:-}" ]; then
    echo "[THEME_FAIL: missing SHOPIFY_CLI_THEME_TOKEN — see docs/INTEGRATIONS.md for Theme Access setup]" >&2
    return 1
  fi
  if [ ! -f "$TOOLKIT_LIB" ]; then
    echo "[THEME_FAIL: toolkit lib not found at $TOOLKIT_LIB — install shopify-automation-toolkit in HERMES_WORKSPACE]" >&2
    return 1
  fi
  return 0
}

# === SAFETY LEVELS ========================================================
# Echoes one of: green, yellow, red-block, red-forbidden
theme_safety_level() {
  local path="$1"
  case "$path" in
    config/settings_data.json)            echo "red-forbidden" ;;
    config/settings_schema.json)          echo "red-block" ;;
    layout/*.liquid)                       echo "red-block" ;;
    sections/*.liquid|templates/*)         echo "yellow" ;;
    locales/*)                             echo "yellow" ;;
    assets/*|snippets/*)                   echo "green" ;;
    *)                                     echo "yellow" ;;  # safe default
  esac
}

# === FETCH ================================================================
# theme_get FILENAME [OUTPUT_PATH] [THEME_ID]
# If OUTPUT_PATH omitted: prints content to stdout
theme_get() {
  local filename="$1"
  local output="${2:-}"
  local theme_id="${3:-$LIVE_THEME_ID}"
  local script
  script=$(mktemp)
  cat > "$script" << EOF
const { execGql } = require('$TOOLKIT_LIB');
const r = execGql(\`query(\$id: ID!, \$f: [String!]!) {
  theme(id: \$id) { files(first: 1, filenames: \$f) {
    nodes { body { ... on OnlineStoreThemeFileBodyText { content } } }
  }}
}\`, { id: 'gid://shopify/OnlineStoreTheme/$theme_id', f: ['$filename'] });
const node = r.theme?.files?.nodes?.[0];
if (!node) { console.error('[THEME_FAIL: file not found: $filename in theme $theme_id]'); process.exit(2); }
const content = node.body.content;
if (process.argv[2]) { require('fs').writeFileSync(process.argv[2], content); }
else { process.stdout.write(content); }
EOF
  if [ -n "$output" ]; then
    node "$script" "$output" 2>&1
  else
    node "$script" 2>&1
  fi
  local rc=$?
  rm -f "$script"
  return $rc
}

# === BACKUP ===============================================================
# theme_backup FILENAME [THEME_ID] → echoes backup file path
theme_backup() {
  local filename="$1"
  local theme_id="${2:-$LIVE_THEME_ID}"
  local ts
  ts=$(date -u +%Y-%m-%dT%H%M%SZ)
  local safe
  safe=$(echo "$filename" | sed 's|/|__|g')
  local backup="$THEME_BACKUP_DIR/${safe}.theme${theme_id}.${ts}.bak"
  if theme_get "$filename" "$backup" "$theme_id" >&2; then
    chmod 600 "$backup"
    echo "$backup"
    return 0
  else
    echo "[THEME_FAIL: backup failed for $filename]" >&2
    return 1
  fi
}

# === DIFF =================================================================
# theme_diff LOCAL_FILE REMOTE_FILENAME [THEME_ID]
# Prints unified diff to stdout. Returns 0 if no diff, 1 if diff exists, 2 on error.
theme_diff() {
  local local_file="$1"
  local remote="$2"
  local theme_id="${3:-$LIVE_THEME_ID}"
  local tmp
  tmp=$(mktemp)
  if ! theme_get "$remote" "$tmp" "$theme_id" >/dev/null 2>&1; then
    rm -f "$tmp"; return 2
  fi
  if diff -q "$tmp" "$local_file" >/dev/null 2>&1; then
    rm -f "$tmp"; return 0
  fi
  diff -u "$tmp" "$local_file" || true
  rm -f "$tmp"
  return 1
}

# === LINT =================================================================
# theme_lint LOCAL_FILE — basic syntax checks
theme_lint() {
  local f="$1"
  local errors=()
  case "$f" in
    *.json)
      if ! node -e "JSON.parse(require('fs').readFileSync('$f','utf8').replace(/^\\s*\\/\\*[\\s\\S]*?\\*\\/\\s*/,''))" 2>/dev/null; then
        errors+=("invalid JSON")
      fi
      ;;
    *.liquid)
      for tag in if for case unless capture form paginate schema style javascript; do
        local opens closes
        opens=$(grep -oE "{%[-]?\s*$tag\b" "$f" 2>/dev/null | wc -l)
        closes=$(grep -oE "{%[-]?\s*end$tag\b" "$f" 2>/dev/null | wc -l)
        [ "$opens" -ne "$closes" ] && errors+=("unbalanced {% $tag %} ($opens open vs $closes close)")
      done
      local open_objs close_objs
      open_objs=$(grep -oE "\\{\\{" "$f" 2>/dev/null | wc -l)
      close_objs=$(grep -oE "\\}\\}" "$f" 2>/dev/null | wc -l)
      [ "$open_objs" -ne "$close_objs" ] && errors+=("unbalanced {{ }} ($open_objs vs $close_objs)")
      ;;
    *.css)
      local oc cc
      oc=$(grep -oE "\\{" "$f" | wc -l)
      cc=$(grep -oE "\\}" "$f" | wc -l)
      [ "$oc" -ne "$cc" ] && errors+=("unbalanced { } in CSS ($oc vs $cc)")
      ;;
  esac
  if [ ${#errors[@]} -gt 0 ]; then
    printf '[LINT_FAIL: %s]\n' "${errors[@]}" >&2
    return 1
  fi
  return 0
}

# === PUSH =================================================================
# theme_push LOCAL_FILE REMOTE_FILENAME [THEME_ID]
theme_push() {
  local local_file="$1"
  local remote="$2"
  local theme_id="${3:-$LIVE_THEME_ID}"
  if [ ! -f "$local_file" ]; then
    echo "[THEME_FAIL: local file not found: $local_file]" >&2; return 1
  fi
  local wd
  wd=$(mktemp -d "$THEME_WORK_BASE.XXXXXX")
  mkdir -p "$wd/$(dirname "$remote")"
  cp "$local_file" "$wd/$remote"
  local log
  log=$(mktemp)
  ( cd "$wd" && shopify theme push \
      --store="$SHOPIFY_STORE" \
      --theme="$theme_id" \
      --only="$remote" \
      --allow-live --json --no-color 2>&1 ) > "$log"
  local rc=$?
  rm -rf "$wd"
  if [ $rc -ne 0 ] || ! grep -q "\"shop\":\"$SHOPIFY_STORE" "$log"; then
    echo "[THEME_FAIL: push failed for $remote (theme $theme_id)]" >&2
    cat "$log" >&2
    rm -f "$log"
    return 1
  fi
  rm -f "$log"
  return 0
}

# === MULTI-FILE ATOMIC PUSH ===============================================
# theme_push_many WORK_DIR [THEME_ID]
theme_push_many() {
  local wd="$1"
  local theme_id="${2:-$LIVE_THEME_ID}"
  if [ ! -d "$wd" ]; then
    echo "[THEME_FAIL: work dir not found: $wd]" >&2; return 1
  fi
  local files
  mapfile -t files < <(cd "$wd" && find . -type f -not -path './.git*' | sed 's|^\./||')
  if [ ${#files[@]} -eq 0 ]; then
    echo "[THEME_FAIL: no files to push in $wd]" >&2; return 1
  fi
  local f
  for f in "${files[@]}"; do
    if ! theme_lint "$wd/$f"; then
      echo "[THEME_FAIL: lint failed for $f, aborting push]" >&2; return 1
    fi
  done
  declare -A BACKUPS
  for f in "${files[@]}"; do
    local b
    b=$(theme_backup "$f" "$theme_id" 2>/dev/null) || b=""
    BACKUPS[$f]=$b
    [ -z "$b" ] && echo "[WARN: $f had no prior remote version (new file?)]" >&2
  done
  local only_args=()
  for f in "${files[@]}"; do only_args+=(--only="$f"); done
  local log
  log=$(mktemp)
  ( cd "$wd" && shopify theme push \
      --store="$SHOPIFY_STORE" \
      --theme="$theme_id" \
      "${only_args[@]}" \
      --allow-live --json --no-color 2>&1 ) > "$log"
  local rc=$?
  if [ $rc -ne 0 ] || ! grep -q "\"shop\":\"$SHOPIFY_STORE" "$log"; then
    echo "[THEME_FAIL: multi-push failed, attempting rollback of ${#files[@]} files]" >&2
    cat "$log" >&2
    for f in "${files[@]}"; do
      local b="${BACKUPS[$f]:-}"
      if [ -n "$b" ] && [ -f "$b" ]; then
        echo "[ROLLBACK: $f from $b]" >&2
        theme_push "$b" "$f" "$theme_id" >&2 || echo "[ROLLBACK_FAIL: $f]" >&2
      fi
    done
    rm -f "$log"; return 1
  fi
  rm -f "$log"
  return 0
}

# === VERIFY ===============================================================
theme_verify() {
  local local_file="$1"
  local remote="$2"
  local theme_id="${3:-$LIVE_THEME_ID}"
  local tmp
  tmp=$(mktemp)
  if ! theme_get "$remote" "$tmp" "$theme_id" >/dev/null 2>&1; then
    rm -f "$tmp"; return 1
  fi
  if diff -q "$tmp" "$local_file" >/dev/null 2>&1; then
    rm -f "$tmp"; return 0
  else
    echo "[THEME_FAIL: verify mismatch for $remote — see diff below]" >&2
    diff -u "$tmp" "$local_file" >&2 || true
    rm -f "$tmp"; return 1
  fi
}

# === DUPLICATE / PREVIEW ==================================================
theme_duplicate() {
  local name="${1:-Hermes-Preview-$(date -u +%Y%m%dT%H%M%SZ)}"
  local log
  log=$(mktemp)
  shopify theme duplicate \
    --store="$SHOPIFY_STORE" \
    --theme="$LIVE_THEME_ID" \
    --name="$name" \
    --no-color --json > "$log" 2>&1
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "[THEME_FAIL: duplicate failed]" >&2; cat "$log" >&2; rm -f "$log"; return 1
  fi
  local new_id
  new_id=$(grep -oE '"id":[0-9]+' "$log" | head -1 | grep -oE '[0-9]+')
  rm -f "$log"
  if [ -z "$new_id" ]; then
    echo "[THEME_FAIL: could not parse new theme ID from duplicate output]" >&2; return 1
  fi
  echo "$new_id"
  return 0
}

theme_preview_url() {
  echo "https://${SHOPIFY_STORE}.myshopify.com/?preview_theme_id=$1"
}

theme_delete() {
  local theme_id="$1"
  if [ "$theme_id" = "$LIVE_THEME_ID" ]; then
    echo "[THEME_FAIL: refusing to delete live theme $theme_id]" >&2; return 1
  fi
  shopify theme delete --store="$SHOPIFY_STORE" --theme="$theme_id" --force 2>&1
}

theme_publish() {
  local theme_id="$1"
  shopify theme publish --store="$SHOPIFY_STORE" --theme="$theme_id" --force --no-color 2>&1
}

# === LIST =================================================================
theme_list() {
  shopify theme list --store="$SHOPIFY_STORE" --no-color --json 2>/dev/null | \
    node -e "
      let buf=''; process.stdin.on('data',d=>buf+=d).on('end',()=>{
        try {
          const arr = JSON.parse(buf);
          arr.forEach(t => console.log(\`\${t.id}|\${t.name}|\${t.role}\`));
        } catch(e) { console.error('[THEME_FAIL: could not parse theme list]'); }
      });
    "
}

# === EXPORTS ==============================================================
export -f theme_check_env theme_safety_level theme_get theme_backup \
          theme_diff theme_lint theme_push theme_push_many theme_verify \
          theme_duplicate theme_preview_url theme_delete theme_publish theme_list
