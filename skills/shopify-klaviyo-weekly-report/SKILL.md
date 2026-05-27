---
name: shopify-klaviyo-weekly-report
description: Génère section markdown Klaviyo (flows, campagnes, engagement email) à injecter dans le rapport hebdo lundi
version: 1.0.0
metadata:
  hermes:
    tags: [klaviyo, email, monitoring, framework, weekly-report]
    category: monitoring
    requires_toolsets: [terminal, file]
---

# <STORE_NAME> Klaviyo Weekly Report

Skill d'analyse hebdomadaire Klaviyo : produit une section markdown structurée (KPI emails, top flows, top campagnes, delta vs N-1) à injecter dans le rapport `shopify-lundi-perf`.

## When to Use

- **Cron `shopify-lundi-perf` (9b3edc604e0d)** : chaque lundi 9h, après la section KPI Shopify et avant Top wins/pertes
- Sur demande explicite user : "rapport Klaviyo de la semaine", "stats emails", "performance email marketing"

## Configuration

Lit `$KLAVIYO_API_KEY` depuis `/root/.hermes/.env`. Si absente, retourne `[KLAVIYO_FAIL: missing API key]`.

Utilise le helper `/root/.hermes/lib/klaviyo-fetch.sh` (cache TTL 6h, retry exponentiel sur 429).

## Procedure

### 1. Charger l'environnement
```bash
set -a; . /root/.hermes/.env; set +a
LIB=/root/.hermes/lib/klaviyo-fetch.sh
```

### 2. Fetcher les données de base
```bash
FLOWS_JSON=$($LIB flows)
METRICS_JSON=$($LIB metrics)
CAMPAIGNS_JSON=$($LIB campaigns)
```

### 3. Calculer fenêtres temporelles

- `SEMAINE_N` = 7 derniers jours (today-7 → today)
- `SEMAINE_N-1` = 7 jours précédents (today-14 → today-7)

### 4. Pour CHAQUE flow live (status=live), récupérer engagement N et N-1

Métriques à agréger via `metric-aggregate <metric_id> day <since> <until>` :
- `Opened Email` (metric_id à trouver dans METRICS_JSON via name="Opened Email")
- `Clicked Email`
- `Bounced Email`
- `Unsubscribed`
- `Placed Order` (attribution revenue)

Pour chaque flow, calculer :
- Sent (estimé via filtrage flow_id sur metric Placed Order ou via attribution)
- Open rate = Opened / Sent
- Click rate = Clicked / Sent
- Revenue attribué (via Placed Order avec attribution flow)

### 5. Calculer deltas

Pour chaque KPI : `delta_pct = (N - N1) / N1 * 100`. Si N-1 = 0, afficher "n/a".

### 6. Produire section markdown

Format à injecter dans `reports/YYYY-Www-perf.md` :

```markdown
## 📧 Performance Klaviyo (Email Marketing)

### Snapshot KPI N vs N-1

| Métrique | Semaine N | Semaine N-1 | Δ |
|----------|-----------|-------------|---|
| Total envois | X | Y | +Z% |
| Taux ouverture moyen | X% | Y% | +Z pp |
| Taux clic moyen | X% | Y% | +Z pp |
| Revenue attribué | X€ | Y€ | +Z% |
| Désabonnements | X | Y | +Z |

### Top flows actifs (7j)

| Flow | Sent | Open % | Click % | Revenue | Statut |
|------|------|--------|---------|---------|--------|
| Bienvenue Club+ | … | … | … | …€ | 🟢/🟡/🔴 |
| Paniers abandonnés | … | … | … | …€ | … |
| Browse Abandonment | … | … | … | …€ | … |
| Ansuf Flow | … | … | … | …€ | … |
| Winback | … | … | … | …€ | … |
| Flow achat coque | … | … | … | …€ | … |
| Merci premier achat | … | … | … | …€ | … |

Statut : 🟢 si open>20% ET click>2%, 🟡 si entre, 🔴 si en-dessous.

### Campagnes récentes (30j)

| Date | Nom | Open % | Click % | Revenue |
|------|-----|--------|---------|---------|
| YYYY-MM-DD | … | …% | …% | …€ |

### Diagnostic

- **Top win** : <flow/campagne avec meilleure progression>
- **Top perte** : <flow/campagne avec dégradation>
- **Recommandation niveau 🟢 (Hermes peut faire seul)** : <action concrète si applicable>
- **Recommandation niveau 🟡 (validation tuteur)** : <action proposée>

```

### 7. Sauvegarder en deux endroits

- **Section complète** : append à `$HERMES_WORKSPACE/reports/$(date +%Y-W%V)-perf.md` après marqueur `<!-- KLAVIYO_SECTION_START -->`
- **Cache section** : `/root/.hermes/cache/klaviyo/last-weekly-section-$(date +%Y-W%V).md` (pour le drop-watchdog comparer)

### 8. Log into learnings.md

Ajouter entrée dans `$HERMES_WORKSPACE/learnings.md` :

```markdown
## $(date -u +%Y-%m-%dT%H:%M:%SZ) — Klaviyo weekly report
- Flows analysés : X live + Y draft
- Open rate moyen : Z%
- Revenue attribué N vs N-1 : delta_pct
- Top win : <flow_name>
- Top perte : <flow_name>
```

## Pitfalls

- **Rate-limit** : le helper gère le backoff. Ne JAMAIS contourner le cache TTL.
- **Sample size** : si Sent < 50 sur la fenêtre, marquer "(sample faible)" dans la cellule au lieu de calculer un %.
- **Données manquantes** : si metric-aggregate retourne 0 partout (clé sans permission, période vide), afficher "n/a" (PAS halluciner des valeurs).
- **Flow draft** : exclure les flows avec `status=draft` ou `archived=true` du calcul.
- **Anti-hallucination** : chaque chiffre DOIT venir de `klaviyo-fetch.sh` (cache JSON traçable). Pas de "valeurs typiques".
- **Devise** : toujours EUR (boutique France). Si l'API retourne USD, convertir ou logger.
- **Timezone** : fenêtres en UTC pour cohérence avec Shopify, mais afficher "(semaine W21 : 2026-05-18 → 2026-05-24)" en local.

## Verification

À la fin du run :
- ✅ Section markdown générée commence par `## 📧 Performance Klaviyo`
- ✅ Tableau snapshot KPI à 5 lignes, chaque cellule a une valeur (ou "n/a")
- ✅ Tableau flows à 7 lignes (les 7 live, draft Anniversaire exclu)
- ✅ Fichier `reports/YYYY-Www-perf.md` contient le marqueur `<!-- KLAVIYO_SECTION_END -->`
- ✅ Entrée learnings.md créée
- ✅ Cache section sauvegardé pour drop-watchdog
- ✅ Aucune mention "(donnée fictive)" ou similaire — toujours valeur réelle ou "n/a"

## Dependencies

- `/root/.hermes/lib/klaviyo-fetch.sh` — helper API
- `$HERMES_WORKSPACE/learnings.md` — auto-log
- `$HERMES_WORKSPACE/reports/` — output

## Read-only contract

Ce skill est **strictement read-only** côté Klaviyo. Aucune mutation POST/PUT/DELETE n'est autorisée. Si l'utilisateur veut créer une campagne, déléguer au skill `shopify-klaviyo-campaign-ideator` qui produit un draft markdown (jamais d'appel API mutation).
