# Automation — Crons, Hooks, STANDING, Memory

> Câblage complet de l'automation Hermes : 4 crons hebdomadaires, hooks v0.14, 14 règles immuables STANDING, memory system OpenViking.

---

## 1. Les 4 crons

Configuration dans `/root/.hermes/cron/jobs.json` — fuseau **Europe/Paris** (configurable via `config.yaml`).

| Nom (template) | Cron expression | Décodage | Skills invoqués |
|---|---|---|---|
| `<store>-weekly-perf-report` | `0 9 * * 1` | Lundi 9h00 | `shopify-weekly-perf-report` + `shopify-baseline-kpi-fetch` + `shopify-low-conversion-diagnostic` + `shopify-klaviyo-weekly-report` |
| `<store>-weekly-ideas` | `0 10 * * 6` | Samedi 10h00 | `shopify-instagram-ideator` + `shopify-product-ideator` + `shopify-cultural-calendar` + `shopify-klaviyo-campaign-ideator` |
| `<store>-weekly-meta-review` | `0 20 * * 0` | Dimanche 20h00 | `shopify-weekly-perf-report` + `shopify-cultural-calendar` |
| `<store>-watchdog-conversion` | `0 */6 * * *` | Toutes les 6h | Script bash + `shopify-klaviyo-drop-watchdog` |

Remplacer `<store>` par ton handle dans `cron-jobs.json`.

---

### Cron 1 : Rapport hebdo performance (lundi 9h)

**Mission** : rapport hebdomadaire constat-actions intégrant KPI Shopify + section Klaviyo.

**Skills invoqués** :
- `shopify-weekly-perf-report` — orchestre, génère le markdown
- `shopify-baseline-kpi-fetch` — fetch KPI N et N-1 (sessions, conversions, AOV, CA, paniers abandonnés)
- `shopify-low-conversion-diagnostic` — détecte produits avec >50 vues/7j sans add-to-cart
- `shopify-klaviyo-weekly-report` — section markdown KPI emails (open/click/bounce/unsub/order)

**Livrables** :
- `$HERMES_WORKSPACE/reports/YYYY-Www-perf.md` — rapport complet
- Résumé Telegram chat `$TELEGRAM_HOME_CHANNEL` (max 20 lignes)
- Email SMTP Gmail via snippet Python inline avec sentinelle `EMAIL_SMTP_OK`

**Garde-fou phase** : Si `HERMES_MODE=test`, aucune mutation Shopify exécutée. Phase 2+ (= `HERMES_MODE=prod`) : actions vertes 🟢 après /yes Telegram.

**Anti-hallucination** : règles dures embedded dans le prompt — chaque KPI doit avoir source citée, `(donnée non disponible)` sinon.

---

### Cron 2 : Email créatif hebdomadaire (samedi 10h)

**Mission** : email créatif avec EXACTEMENT 3 propositions :

**Proposition 1 — Nouveau produit** :
- Nom (+ déclinaison culturelle si pertinent pour ta marque)
- Catégorie
- Description 50 mots (concept + univers de marque)
- Pourquoi maintenant (signal marché, niche identifiée dans `brand-knowledge.md`)
- Prix cible + marge estimée
- Concurrents similaires + différenciation
- Description visuelle textuelle pour moodboard

**Proposition 2 — Post Instagram** :
- Format (reel/carrousel/single/story)
- Thème (storytelling marque / éducation / témoignage client)
- Caption FR + EN
- 15 hashtags (5 gros >100k + 5 moyens 10k-100k + 5 niches <10k)
- Description visuelle textuelle
- Date + heure recommandée (créneau optimal selon ta marque, ex: 18-22h Paris)
- CTA explicite

**Proposition 3 — Draft campagne Klaviyo** :
- Aligné `shopify-cultural-calendar` événement J-21 à J-7 (lu depuis `cultural-events.json`)
- Format markdown read-only (jamais POST direct vers Klaviyo)
- Sortie : section dans `reports/YYYY-Www-ideas.md` + archive `campaigns/YYYY-Www-klaviyo-draft.md`

**Garde-fou** : aucune publication automatique, DRAFTS uniquement, copier-coller manuel par le marchand.

---

### Cron 3 : Méta-revue auto-amélioration (dimanche 20h)

**Mission** : méta-revue hebdomadaire avec auto-création de skills.

**Procédure** :
1. Pour chaque action exécutée cette semaine (lue dans `learnings.md`), vérifie impact KPI (avant/après) si data dispo, sinon flag pour mesure W+1
2. Lance `hermes insights --days 7` → capture tokens / coût / modèles
3. Identifie 3 patterns : ce qui a marché / ce qui a échoué / ce qui mérite un skill
4. **Si pattern récurrent > 3 occurrences sur 4 semaines** → crée automatiquement le SKILL.md correspondant dans `/root/.hermes/skills/<store>-<nom>/`
5. Met à jour `brand-knowledge.md` (max 5 lignes ajoutées par semaine pour éviter inflation)
6. Vérifie via `shopify-cultural-calendar` si événement à J-21 → alerte préavis Telegram avec cadence J-21/J-14/J-10/J-3
7. Met à jour `MEMORY.md` ligne Phase courante si transition Phase

**Livrables** :
- `$HERMES_WORKSPACE/meta-reviews/YYYY-Www-meta.md` (résumé écrit complet)
- Telegram chat `$TELEGRAM_HOME_CHANNEL` (max 15 lignes)
- Éventuellement : 1 nouveau `SKILL.md` créé
- Éventuellement : 1 alerte préavis culturel

**Garde-fou** : aucune mutation Shopify. Seules écritures autorisées : SKILL.md, brand-knowledge.md, MEMORY.md, meta-reviews/.

---

### Cron 4 : Watchdog conversion (toutes les 6h)

**Mode** : `no_agent: true` — exécute un script bash direct, pas une session agent LLM. **Économie tokens** : pas de session ouverte si rien à signaler.

**Mission** : surveille KPI clés :
- Sessions Shopify (chute > 30% / 24h)
- Conversions (chute > 30% / 24h)
- Alertes Klaviyo drop (open ↓>20pp, click ↓>30pp, revenue ↓>40%, unsub >5%)
- OpenRouter quota probe (alerte si >80% consommé)

**Livrable** : **Silencieux par défaut** — Telegram uniquement si alerte. Si zéro alerte : `{"wakeAgent":false}` (l'agent ne se réveille pas).

---

## 2. Hooks v0.14

Migration v0.13 → v0.14 a changé le format (list → dict) et l'event (`tool_call_completed` → `post_tool_call`).

Configuration dans `/root/.hermes/config.yaml` section `hooks:` :

```yaml
hooks:
  on_session_start:
    - command: /root/.hermes/hooks/inject-standing.sh
      matcher: ".*"
      timeout: 10
  post_tool_call:
    - command: /root/.hermes/hooks/log-learning.sh
      matcher: ".*Update|.*Create|.*Delete|.*publish.*|.*email.*"
      timeout: 30
hooks_auto_accept: true
```

### `inject-standing.sh`

Lit `STANDING-CORE.md` + `$HERMES_WORKSPACE/STORE-BRAND.md`, concatène, renvoie `{"continue": true, "context_injection": "<contenu>"}` via jq.

```bash
#!/bin/bash
STANDING_CORE=$(cat /root/.hermes/standing/STANDING-CORE.md)
STORE_BRAND=$([ -f "$HERMES_WORKSPACE/STORE-BRAND.md" ] && cat "$HERMES_WORKSPACE/STORE-BRAND.md" || echo "")
COMBINED="$STANDING_CORE

## Brand-Specific Rules
$STORE_BRAND"
jq -n --arg s "$COMBINED" '{"continue": true, "context_injection": $s}'
```

### `log-learning.sh`

Append automatique dans `$HERMES_WORKSPACE/learnings.md` pour chaque action mutative :
- Compatible v0.13 (`args`) + v0.14 (`tool_input` + `hook_event_name`)
- Skip si event = `pre_tool_call` (log uniquement post-exec)
- Filtre regex sur tool/input : `Update|Create|Delete|publish|email_send|productCreate|productUpdate|customerCreate|webhookCreate|fileUpdate|collectionCreate`
- Crée `learnings.md` avec header si absent, puis append timestamp UTC + tool + input tronqué 400 chars + 4 placeholders (avant/après/conclusion/futur)

---

## 3. STANDING.md — 14 règles immuables

Injecté à chaque session via le hook `inject-standing`. Décomposé en :
- **`STANDING-CORE.md`** (11 règles universelles) — vit dans `/root/.hermes/standing/`
- **`STORE-BRAND.md`** (3 règles brand-specific) — vit dans `$HERMES_WORKSPACE/`

### 11 règles universelles (STANDING-CORE)

| # | Règle | Explication |
|---|---|---|
| 1 | **Pré-lecture obligatoire** | Avant toute mutation : MISSION + MEMORY + STANDING + 7 dernières entrées learnings |
| 2 | **Jamais `shopify store auth`** | Auth déjà OK, relancer = plantage headless (port 13387 + TTY requis) |
| 3 | **Jamais publier Instagram sans validation** | Toujours proposer en mode `dry` forcé pendant phase test |
| 4 | **Prix +5% interdit sans /yes** | Modifier `price` direct = 🔴, préférer `compareAtPrice` |
| 5 | **Aucune suppression** | Produit / page / client : interdit total |
| 7 | **Impact mesurable en N+1** | Toute action documentée dans learnings.md la semaine suivante |
| 8 | **Token Shopify expiré = notify** | Ne pas tenter de réauth seul |
| 11 | **Anti-hallucination KPI** | Chaque chiffre doit avoir source vérifiable citée |
| 12 | **Pas de padding répété** | Interdit de répéter un mot N fois pour atteindre un seuil |
| 13 | **Pas d'invention de champ GraphQL** | Toujours lire `hermes-schema-guard` AVANT toute mutation, introspecter sinon |
| 14 | **Pas de PASS sur Exception** | Try/except qui retourne PASS = interdit, toujours `EMAIL_FAIL: <cause exacte>` |

### 3 règles brand-specific (STORE-BRAND.md à customiser)

| # | Règle (template) | À customiser |
|---|---|---|
| 6 | **Vocabulaire de marque obligatoire** | Liste de mots-clés qui DOIVENT apparaître dans tout contenu généré (univers culturel, nom marque, USP). Ex: "amazigh, berbère, tifinagh, yaz" pour Azamoul ; "artisanal, terroir, biodynamie" pour un domaine viticole ; etc. |
| 9 | **Email via skill `hermes-email-sender`** | Définit le skill canonique pour l'envoi email (utilise smtplib inline + sentinelle `EMAIL_SMTP_OK`) |
| 10 | **Telegram chat unique** | Le `$TELEGRAM_HOME_CHANNEL` (= user_id du marchand) est le SEUL destinataire autorisé pour les notifications |

---

## 4. Memory system

### Architecture

```
/root/.hermes/memories/        [framework — partagé]
├── MEMORY.md                  ← peut rester vide ou pointer vers le workspace
└── USER.md                    ← profil utilisateur (configuré au setup)

$HERMES_WORKSPACE/             [user-facing — instance boutique]
├── MISSION.md                 ← charter spécifique à la boutique
├── MEMORY.md                  ← mémoire courante (faits permanents)
├── STORE-BRAND.md             ← vocab + niveaux autonomie + sensibilités
├── brand-knowledge.md         ← concurrents + USP
├── cultural-events.json       ← événements/saisons importants
└── learnings.md               ← journal append-only auto-logué par hook
```

**Provider** : OpenViking 0.3.16 sur port 1933 (embedding local pour RAG cross-session).

**Limites typiques** :
- `memory_char_limit: 3500` (tokens injectés en début de session)
- `user_char_limit: 1375` (profil utilisateur)

### Contenu type `MEMORY.md`

Template fourni dans `config/MEMORY.md.template`. Sections recommandées :

- **Boutique** : handle Shopify, domaine, plan, devise, fuseau, catégories
- **Stack** : version Hermes, Python/Node, provider LLM
- **Phase courante** : `HERMES_MODE=test|prod`, date dernière transition
- **Niveaux autonomie** : récap 🟢/🟡/🔴 (peut référencer STORE-BRAND.md)
- **Decisions ouvertes** : ce qui attend une décision du marchand

### `learnings.md`

Journal append-only. Le hook `log-learning.sh` y ajoute automatiquement chaque action mutative. Le marchand peut aussi ajouter manuellement des notes.

Format type d'entrée :
```
- [YYYY-MM-DD HH:MM UTC] toolName: <inputTronqué400chars>
  Avant: <à compléter en W+1 via méta-revue>
  Après: <à compléter en W+1>
  Conclusion: <à compléter en W+1>
  Futur: <à compléter en W+1>
```

---

## 5. Gateway Telegram

| Élément | Valeur (à configurer dans `.env`) |
|---|---|
| Bot token | `TELEGRAM_BOT_TOKEN` (via @BotFather) |
| Allowed users | `TELEGRAM_ALLOWED_USERS=<user_id>` (via @userinfobot) |
| Home channel | `TELEGRAM_HOME_CHANNEL=<user_id>` |
| Commande de lancement | `hermes gateway run --replace` |
| Lock file | `/root/.hermes/gateway.lock` |
| Restart drain timeout | 180s |
| Auto-continue freshness | 3600s |

Le gateway répond aux messages du `TELEGRAM_HOME_CHANNEL` uniquement. Les commandes `/yes`, `/no`, `/edit` reçues pendant qu'un cron attend une validation déclenchent l'action correspondante.

---

## 6. Insights & monitoring

Source : `hermes insights --days N` — analyse les sessions des N derniers jours.

Métriques exposées :
- Sessions par platform (cron / cli / telegram)
- Messages échangés (total + user)
- Tool calls
- Tokens (input + output + total)
- Active time (total + moyenne par session)
- Top tools utilisés
- Top skills loaded
- Pattern d'activité (jours + heures pics)

**Utilité** : détecter les dérives (cron qui consomme anormalement, modèle qui coûte trop, skill qui se charge inutilement).

---

## 7. Pattern de validation `/yes`

Pour les actions niveau 🟡 :

```
1. Hermes prépare la mutation
   - Snapshot avant → batches/YYYY-Www-batchN-before.json
   - Preview diff JSON → batches/YYYY-Www-batchN-preview.json
   - Script rollback bash auto-généré → batches/YYYY-Www-batchN-rollback.sh
2. Envoi VALIDATION TUTEUR (obligatoire avant mutation) :
   - Telegram chat $TELEGRAM_HOME_CHANNEL : message avec preview courte + lien fichiers
   - Email à $EMAIL_TO via Python smtplib inline avec preview détaillée
   - Message inclut : "Réponds /yes pour appliquer, /no pour annuler, /edit pour ajuster"
3. ATTENTE de la réponse user (skill se met en pause, le user répond via Telegram)
   - Timeout 10 min standard (configurable)
4. Si réponse = /yes :
   - Exécute les mutations en séquence (espacement 2s anti rate-limit Shopify 1.4 req/s)
   - Snapshot après → batches/YYYY-Www-batchN-after.json
   - Diff réel → batches/YYYY-Www-batchN-diff.md
   - Hook auto-log dans learnings.md
   - Confirmation Telegram + email
5. Si réponse = /no : cancel propre, conservation fichiers preview + rollback pour retry futur
6. Si réponse = /edit <handle> <details> : ajuste, regénère preview, redemande validation
7. Si timeout : abandon + alerte Telegram
```

---

## 8. Pitfalls connus

- **`/yes` arrivé pendant que l'agent n'attend pas** → ignoré (sécurité). Le marchand doit attendre le message qui demande /yes.
- **Rate-limit Shopify** (1.4 req/s par défaut) → espacer mutations de 2s minimum. Si batch > 100 items, prévoir cooldown 30s tous les 50 items.
- **Cache Klaviyo 6h** → ne pas s'attendre à du temps réel sur les KPI emails. Pour forcer un refresh, supprimer le fichier cache correspondant dans `/root/.hermes/cache/klaviyo/`.
- **Cache CDN Shopify post-push thème** → laisser passer 30-60s avant `theme_verify` pour propagation, ou utiliser cache-bust `?v=$(date +%s)`.
- **App Password Gmail expiré** → l'envoi email échoue silencieusement. Toujours vérifier la sentinelle `EMAIL_SMTP_OK` en stdout.
- **Token Shopify expiré** → Hermes ne tente PAS de réauth seul (règle 8). Il notifie le marchand qui doit réauth manuellement depuis son poste Windows (port 13387 + TTY requis).

---

## 9. Verification (checklist par run de cron)

- [ ] Hook `inject-standing` exécuté en début de session (STANDING + STORE-BRAND injectés)
- [ ] Pré-lecture obligatoire effectuée (MISSION + MEMORY + 7 derniers learnings)
- [ ] Niveau d'autonomie respecté (🟢 direct, 🟡 /yes, 🔴 refus)
- [ ] Anti-hallucination : tous les chiffres ont une source citée
- [ ] Si email : sentinelle `EMAIL_SMTP_OK` vérifiée en stdout
- [ ] Si Telegram : message reçu par le chat autorisé
- [ ] Hook `log-learning` a ajouté une entrée dans learnings.md pour chaque action mutative
- [ ] `last_status: ok` dans `jobs.json` après le run
