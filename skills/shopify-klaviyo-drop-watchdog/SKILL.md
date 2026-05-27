---
name: shopify-klaviyo-drop-watchdog
description: Watchdog silencieux toutes les 6h — alerte Telegram si chute open rate >20% ou click rate >30% sur fenêtre 7j Klaviyo
version: 1.0.0
metadata:
  hermes:
    tags: [klaviyo, monitoring, alerting, watchdog, framework]
    category: monitoring
    requires_toolsets: [terminal, messaging]
---

# <STORE_NAME> Klaviyo Drop Watchdog

Skill no-agent par design : exécuté toutes les 6h par le cron `shopify-watchdog-conversion`. Reste silencieux tant que les KPI Klaviyo sont stables, déclenche une alerte Telegram + wake-agent quand une dérive significative est détectée.

## When to Use

- **Cron `shopify-watchdog-conversion` (dd4a59c29a88)** : chaque 6h, en parallèle du check conversion Shopify existant
- **JAMAIS sur demande user direct** (pas pertinent en interactif)

## Configuration

Variables `.env` lues :
- `$KLAVIYO_API_KEY`
- `$TELEGRAM_HOME_CHANNEL` ($TELEGRAM_HOME_CHANNEL)
- `$HERMES_MODE` (test : alerte sans wake, prod : alerte + wake-agent)

Seuils d'alerte (configurables dans le skill) :
- **Open rate drop > 20 points** sur 7j vs 7j précédents
- **Click rate drop > 30 points**
- **Revenue attribué drop > 40%**
- **Désabonnements** : > 5% des envois sur 7j

**N min envois = 50** sur la fenêtre 7j avant de calculer (sinon : sample trop faible, silence forcé).

## Procedure

### 1. Charger l'environnement
```bash
set -a; . /root/.hermes/.env; set +a
LIB=/root/.hermes/lib/klaviyo-fetch.sh
TG_BOT_API="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"
```

### 2. Récupérer metric IDs
```bash
METRICS=$($LIB metrics)
# Extraire les ids correspondant à : Opened Email, Clicked Email, Placed Order, Unsubscribed
```

### 3. Calculer agrégats 7j N et 7j N-1

```bash
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
SINCE_N=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)
SINCE_N1=$(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%SZ)

OPEN_N=$($LIB metric-aggregate $OPENED_ID day $SINCE_N $NOW | jq '.data.attributes.data[0].measurements.count // [] | add')
OPEN_N1=$($LIB metric-aggregate $OPENED_ID day $SINCE_N1 $SINCE_N | jq '.data.attributes.data[0].measurements.count // [] | add')
# Idem pour CLICK, REVENUE, UNSUBSCRIBE
```

### 4. Calculer deltas

```bash
# Si SENT_N < 50, abort (sample trop faible)
if [ "$SENT_N" -lt 50 ]; then
  echo '{"wakeAgent": false, "reason": "sample_too_small"}'
  exit 0
fi

# Open rate delta (points de pourcentage)
OPEN_RATE_N=$(echo "scale=4; $OPEN_N / $SENT_N * 100" | bc)
OPEN_RATE_N1=$(echo "scale=4; $OPEN_N1 / $SENT_N1 * 100" | bc)
OPEN_DROP=$(echo "scale=2; $OPEN_RATE_N1 - $OPEN_RATE_N" | bc)
```

### 5. Décision

```bash
ALERTS=()
[ $(echo "$OPEN_DROP > 20" | bc -l) -eq 1 ] && ALERTS+=("OPEN_DROP: -${OPEN_DROP}pp")
[ $(echo "$CLICK_DROP > 30" | bc -l) -eq 1 ] && ALERTS+=("CLICK_DROP: -${CLICK_DROP}pp")
[ $(echo "$REV_DROP_PCT > 40" | bc -l) -eq 1 ] && ALERTS+=("REVENUE_DROP: -${REV_DROP_PCT}%")
[ $UNSUB_RATE_N -gt 5 ] && ALERTS+=("UNSUB_HIGH: ${UNSUB_RATE_N}%")
```

### 6. Notification

Si `${#ALERTS[@]} = 0` → silence total :
```bash
echo '{"wakeAgent": false}'
exit 0
```

Si alertes détectées :
```bash
MSG="⚠ KLAVIYO DROP DETECTED (<STORE_NAME>)
$(printf '%s\n' "${ALERTS[@]}")

KPI 7j N vs N-1 :
- Sent: $SENT_N vs $SENT_N1
- Open: ${OPEN_RATE_N}% vs ${OPEN_RATE_N1}%
- Click: ${CLICK_RATE_N}% vs ${CLICK_RATE_N1}%
- Revenue: ${REV_N}€ vs ${REV_N1}€

Investigate :
1. Une campagne récente a-t-elle bombé ?
2. Un flow a-t-il été paused ?
3. Deliverability OK (bounces) ?

Run /chat dans Telegram pour analyse détaillée."

# Mode test : log + Telegram alert mais wake-agent false
# Mode prod : Telegram alert + wake-agent true
if [ "${HERMES_MODE:-test}" = "test" ]; then
  curl -s -X POST "$TG_BOT_API" \
    -d "chat_id=$TELEGRAM_HOME_CHANNEL" \
    -d "text=$MSG" \
    -d "parse_mode=Markdown"
  echo "{\"wakeAgent\": false, \"alert_sent\": true, \"mode\": \"test\"}"
else
  curl -s -X POST "$TG_BOT_API" \
    -d "chat_id=$TELEGRAM_HOME_CHANNEL" \
    -d "text=$MSG" \
    -d "parse_mode=Markdown"
  echo "{\"wakeAgent\": true, \"context\": \"$MSG\"}"
fi
```

### 7. Log learnings (uniquement si alerte)

```markdown
## $(date -u +%Y-%m-%dT%H:%M:%SZ) — Klaviyo drop watchdog
- Alertes : <list>
- Open rate N vs N-1 : X% vs Y%
- Click rate N vs N-1 : X% vs Y%
- Mode : test/prod
- Wake agent : true/false
- Conclusion : (à remplir après investigation)
```

## Pitfalls

- **Faux positifs** : seuils sur fenêtre 7j ET N min envois = 50. Ne JAMAIS alerter sur point unique ou < 50 envois.
- **Mode silence** : si `${#ALERTS[@]} = 0`, retourne `{"wakeAgent": false}` SANS rien d'autre (pas de bruit Telegram).
- **Rate-limit Klaviyo** : utiliser le cache 6h du helper (et non re-fetch à chaque run).
- **Edge case "0 commandes"** : si `SENT_N = 0` (campagne envoyée pendant la fenêtre N-1 mais pas N), c'est NORMAL en mode batch. Ne pas alerter.
- **Désabonnements** : utiliser metric `Unsubscribed` filtré par flow_id, pas le total profils suppression (qui inclut bounces).
- **Mode test obligatoire** : tant que `HERMES_MODE=test`, wake-agent reste false (alerte info Telegram only).

## Verification

- ✅ Script termine en < 30s (sinon timeout cron)
- ✅ Si tout OK : stdout = `{"wakeAgent": false}` (1 ligne, JSON valide)
- ✅ Si alerte : Telegram message reçu sur $TELEGRAM_HOME_CHANNEL
- ✅ Si alerte + prod : `wakeAgent=true` avec context
- ✅ Aucun appel API mutation Klaviyo (read + metric-aggregates POST seul, qui est read sémantique)
- ✅ Cache helper utilisé (pas de re-fetch flows/metrics chaque run)

## Dependencies

- `/root/.hermes/lib/klaviyo-fetch.sh`
- `$TELEGRAM_BOT_TOKEN` (env)
- `$TELEGRAM_HOME_CHANNEL` (env)
- `$HERMES_MODE` (env)
- Outil `jq` pour parsing JSON (installé par défaut sur le VPS)
- Outil `bc` pour calculs flottants

## Read-only contract

Lecture pure côté Klaviyo. Le POST sur `/api/metric-aggregates/` est sémantiquement read (query agrégation), pas une mutation d'état. Aucune création campagne, profil, flow, segment ou liste autorisée.
