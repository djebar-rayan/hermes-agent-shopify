#!/bin/bash
# klaviyo-fetch.sh — Helper unifié pour fetcher données Klaviyo
#
# Cache TTL 6h pour éviter rate-limit (10/s burst, 150/min Klaviyo).
# Sorties dans /root/.hermes/cache/klaviyo/<endpoint>-YYYY-MM-DD-HH.json
#
# Usage :
#   klaviyo-fetch.sh flows                       # liste 8 flows
#   klaviyo-fetch.sh campaigns                   # 30 campagnes
#   klaviyo-fetch.sh metrics                     # 78 metrics
#   klaviyo-fetch.sh segments                    # 1 segment
#   klaviyo-fetch.sh lists                       # 2 listes
#   klaviyo-fetch.sh metric-aggregate <id> <interval> <since_iso> <until_iso>
#   klaviyo-fetch.sh flow-message-stats <flow-id> <since_iso> <until_iso>
#
# Exit codes :
#   0  : succès, JSON sur stdout
#   1  : KLAVIYO_API_KEY manquante
#   2  : erreur API (rate-limit, 401, 500...)
#   3  : usage invalide
set -u

CACHE_DIR="/root/.hermes/cache/klaviyo"
CACHE_TTL_SECONDS=21600   # 6h
KLAVIYO_REV="2024-10-15"
mkdir -p "$CACHE_DIR"

# Source env (KLAVIYO_API_KEY)
set -a; . /root/.hermes/.env 2>/dev/null; set +a

if [ -z "${KLAVIYO_API_KEY:-}" ]; then
  echo '{"error":"KLAVIYO_API_KEY missing in /root/.hermes/.env"}' >&2
  exit 1
fi

ENDPOINT="${1:-}"
if [ -z "$ENDPOINT" ]; then
  echo "Usage: $0 <flows|campaigns|metrics|segments|lists|profiles-count|metric-aggregate|flow-message-stats>" >&2
  exit 3
fi

# Cache key (rounded down to nearest 6h slot)
CACHE_SLOT=$(date -u +"%Y-%m-%d-%H" | awk -F- '{slot=int($4/6)*6; printf "%s-%s-%s-%02d", $1, $2, $3, slot}')
CACHE_FILE="$CACHE_DIR/${ENDPOINT}-${CACHE_SLOT}.json"

# Custom cache key for endpoints with args
if [ "$ENDPOINT" = "metric-aggregate" ] || [ "$ENDPOINT" = "flow-message-stats" ]; then
  ARGS_HASH=$(echo "$*" | md5sum | cut -c1-8)
  CACHE_FILE="$CACHE_DIR/${ENDPOINT}-${ARGS_HASH}-${CACHE_SLOT}.json"
fi

# Hit cache if fresh
if [ -f "$CACHE_FILE" ]; then
  cat "$CACHE_FILE"
  exit 0
fi

# Helper curl avec retry exponentiel
klaviyo_get() {
  local url="$1"
  local attempt=1
  local max_attempts=3
  while [ $attempt -le $max_attempts ]; do
    HTTP_RESP=$(curl -s -w "\nHTTP_STATUS:%{http_code}" --max-time 20 \
      -H "Authorization: Klaviyo-API-Key $KLAVIYO_API_KEY" \
      -H "revision: $KLAVIYO_REV" \
      -H "Accept: application/vnd.api+json" \
      "$url")
    HTTP_CODE=$(echo "$HTTP_RESP" | tail -n1 | cut -d: -f2)
    BODY=$(echo "$HTTP_RESP" | sed '$d')
    if [ "$HTTP_CODE" = "200" ]; then
      echo "$BODY"
      return 0
    elif [ "$HTTP_CODE" = "429" ]; then
      sleep $((2 ** attempt))
      attempt=$((attempt + 1))
    else
      echo "{\"error\":\"HTTP $HTTP_CODE\",\"body\":$(echo "$BODY" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')}" >&2
      return 2
    fi
  done
  echo "{\"error\":\"rate-limit max retries\"}" >&2
  return 2
}

klaviyo_post() {
  local url="$1"
  local body="$2"
  HTTP_RESP=$(curl -s -w "\nHTTP_STATUS:%{http_code}" --max-time 30 \
    -X POST \
    -H "Authorization: Klaviyo-API-Key $KLAVIYO_API_KEY" \
    -H "revision: $KLAVIYO_REV" \
    -H "Accept: application/vnd.api+json" \
    -H "Content-Type: application/vnd.api+json" \
    -d "$body" \
    "$url")
  HTTP_CODE=$(echo "$HTTP_RESP" | tail -n1 | cut -d: -f2)
  BODY=$(echo "$HTTP_RESP" | sed '$d')
  if [ "$HTTP_CODE" = "200" ]; then
    echo "$BODY"
    return 0
  else
    echo "{\"error\":\"HTTP $HTTP_CODE\",\"body\":$(echo "$BODY" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')}" >&2
    return 2
  fi
}

case "$ENDPOINT" in
  flows)
    OUT=$(klaviyo_get "https://a.klaviyo.com/api/flows/?fields%5Bflow%5D=name,status,trigger_type,created,updated,archived")
    ;;
  campaigns)
    SINCE=$(date -u -d '30 days ago' +"%Y-%m-%dT00:00:00Z")
    OUT=$(klaviyo_get "https://a.klaviyo.com/api/campaigns/?filter=equals(messages.channel,%27email%27)&sort=-created_at&fields%5Bcampaign%5D=name,status,scheduled_at,send_time,created_at,updated_at")
    ;;
  metrics)
    OUT=$(klaviyo_get "https://a.klaviyo.com/api/metrics/?fields%5Bmetric%5D=name,integration,created,updated")
    ;;
  segments)
    OUT=$(klaviyo_get "https://a.klaviyo.com/api/segments/?fields%5Bsegment%5D=name,created,updated,is_active,is_processing")
    ;;
  lists)
    OUT=$(klaviyo_get "https://a.klaviyo.com/api/lists/?fields%5Blist%5D=name,created,updated")
    ;;
  profiles-count)
    # Endpoint léger pour avoir le total (utilise pagination meta)
    OUT=$(klaviyo_get "https://a.klaviyo.com/api/profiles/?page%5Bsize%5D=1")
    ;;
  metric-aggregate)
    # Args: metric_id interval since_iso until_iso
    METRIC_ID="${2:-}"
    INTERVAL="${3:-day}"
    SINCE_ISO="${4:-}"
    UNTIL_ISO="${5:-}"
    if [ -z "$METRIC_ID" ] || [ -z "$SINCE_ISO" ] || [ -z "$UNTIL_ISO" ]; then
      echo '{"error":"metric-aggregate requires: metric_id interval since_iso until_iso"}' >&2
      exit 3
    fi
    BODY=$(python3 -c "
import json
body = {
  'data': {
    'type': 'metric-aggregate',
    'attributes': {
      'metric_id': '$METRIC_ID',
      'interval': '$INTERVAL',
      'page_size': 500,
      'measurements': ['count'],
      'filter': ['greater-or-equal(datetime,$SINCE_ISO)', 'less-than(datetime,$UNTIL_ISO)']
    }
  }
}
print(json.dumps(body))
")
    OUT=$(klaviyo_post "https://a.klaviyo.com/api/metric-aggregates/" "$BODY")
    ;;
  flow-message-stats)
    FLOW_ID="${2:-}"
    if [ -z "$FLOW_ID" ]; then
      echo '{"error":"flow-message-stats requires flow_id"}' >&2
      exit 3
    fi
    OUT=$(klaviyo_get "https://a.klaviyo.com/api/flows/$FLOW_ID/flow-actions/?fields%5Bflow-action%5D=action_type,status&include=flow-messages")
    ;;
  *)
    echo "{\"error\":\"unknown endpoint: $ENDPOINT\"}" >&2
    exit 3
    ;;
esac

# Cache successful result
if echo "$OUT" | python3 -c 'import sys,json; json.load(sys.stdin)' >/dev/null 2>&1; then
  if ! echo "$OUT" | grep -q '"error"'; then
    echo "$OUT" > "$CACHE_FILE"
  fi
fi

echo "$OUT"
