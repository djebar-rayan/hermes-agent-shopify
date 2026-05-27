---
name: shopify-kpi-drop-watchdog
description: Surveille les KPI Shopify sur 24h et alerte Telegram si chute > 30% sur conversion, sessions ou commandes
category: monitoring
version: 1.0.0
metadata:
  hermes:
    tags: [shopify, monitoring, alert, telegram]
    requires_toolsets: [terminal]
---

# <STORE_NAME> KPI Drop Watchdog

## When to Use
- Cron `shopify-watchdog-conversion` (toutes les 6h)
- À la demande pour une vérification ponctuelle santé boutique

## Procedure
1. Charge env : `set -a; . /root/.hermes/.env; set +a`
2. Récupère les KPI 24h glissant via GraphQL `orders(query: "created_at:>...")` :
   - nb commandes 24h actuelles
   - nb commandes 24h précédentes (J-1 même fenêtre)
   - CA correspondant
3. Calcule deltas en % : `(actuel - precedent) / precedent * 100`
4. Si delta < -30% sur AU MOINS UN KPI critique :
   - Compose un message Telegram court (< 500 chars) :
     "ALERTE KPI <STORE_NAME> : <KPI> a chute de <X>% sur 24h. Actuel: <val>, J-1: <val>. Action recommandee : verifier flow checkout + statut services."
   - Envoie au chat $TELEGRAM_HOME_CHANNEL via tool messaging Hermes
5. Si tout est OK : retourne `[SILENT]` (suppression delivery cron).
6. Log dans `$HERMES_WORKSPACE/learnings.md` avec timestamp + verdict.

## Pitfalls
- Ne pas alerter si commandes precedentes < 3 (signal faible). Utilise `[SILENT]`.
- Ne pas alerter si écart < 30 % (bruit normal). Seuil dur.
- Ne JAMAIS envoyer email pour alerte 24h (réservé à rapport hebdo). Telegram uniquement.
- Si GraphQL échoue, retourne `[SILENT]` plutôt que d alerter sur fausse donnée.

## Verification
- Message Telegram reçu uniquement quand chute réelle > 30%
- 0 alerte sur trafic faible (< 3 commandes baseline)
- Log learnings.md mentionne chaque check (alerte ou silent)
