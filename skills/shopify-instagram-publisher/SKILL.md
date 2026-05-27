---
name: shopify-instagram-publisher
description: Genere payload Instagram Graph API avec APPROBATION TUTEUR obligatoire (email + Telegram) avant publication reelle
category: social-media
version: 2.0.0
metadata:
  hermes:
    tags: [instagram, meta-graph, approval-gate, dry-run]
    requires_toolsets: [terminal]
---

# <STORE_NAME> Instagram Publisher

## When to Use
- Apres `shopify-instagram-ideator` ou lecture d un draft `campaigns/<event>/insta-post-*.md`
- 4 modes :
  - **dry** : genere payload offline, ZERO appel API (Phase 3/4 test ou validation hors-ligne)
  - **container** : appel `POST /{ig-id}/media` pour creer container, JAMAIS `/media_publish` (validation auth Graph API)
  - **approval** : container + envoi preview email+Telegram, ATTENTE /yes <container_id> tuteur avant publish (RECOMMANDE en prod)
  - **publish_now** : container + publish_media direct (interdit en autonome — escape hatch tuteur seulement)

## Test mode flag

Lis OBLIGATOIREMENT `$HERMES_MODE` depuis `/root/.hermes/.env` avant toute action :
- Si `HERMES_MODE=test` ou absent : force `mode=dry` quel que soit le parametre fourni. Generation payload offline uniquement, ZERO appel Graph API.
- Si `HERMES_MODE=prod` :
  - **Defaut = `mode=approval`** : aucun publish sans /yes tuteur explicite
  - `mode=publish_now` autorise SEULEMENT si tuteur le specifie explicitement dans le prompt

## Approval gate workflow (mode prod par defaut)

Quand `HERMES_MODE=prod` et `mode=approval` (default) :

1. **Construit le payload** (caption + hashtags + image_url ou video_url) selon le format Graph API
2. **Validation offline** (caption < 2200, hashtags <= 30, https URLs, dimensions image)
3. **Cree le container Meta** via `POST /{IG_BUSINESS_ACCOUNT_ID}/media` (sans publish)
4. **Recupere container_id** retourne par Graph API
5. **Envoie preview a tuteur via 2 canaux simultanes** :
   - **Email** via `hermes-email-sender` (mode=prod, destinataire = $EMAIL_TO) :
     - Sujet : `[APPROBATION REQUISE] Insta post <STORE_NAME> a valider - container <container_id>`
     - Corps : payload complet + image_url cliquable + commande Telegram pour valider/rejeter
   - **Telegram** chat $TELEGRAM_HOME_CHANNEL :
     - Message court (< 1500 chars) avec preview + container_id + instructions
     - "Pour publier : repondre `/yes_insta <container_id>` sur Telegram. Pour annuler : `/no_insta <container_id>`."
6. **NE PUBLIE PAS**. Le container expire de lui-meme apres 24h s'il n'est pas publie (limite Meta).
7. **Log dans learnings.md** : `INSTA-APPROVAL-PENDING container=<id> sent=<timestamp>`

## Publish quand /yes recu (cron dedie ou prompt manuel)

Un cron `shopify-insta-publish-on-yes` (a creer, frequence 5 minutes) ou prompt manuel verifie les containers en attente et publie ceux qui ont recu `/yes_insta <id>` :

1. Lit `$HERMES_WORKSPACE/insta-approvals.log` (nouveau fichier, append-only via webhook Telegram ou polling)
2. Pour chaque container_id approuve :
   - `POST /{IG_BUSINESS_ACCOUNT_ID}/media_publish` avec `creation_id=<container_id>`
   - Capture media_id final
3. Notifie tuteur publication effective : email + Telegram "Post publie sur @<store_handle> : <permalink>"
4. Log dans `learnings.md` : `INSTA-PUBLISHED media=<id> permalink=<url>`

## Procedure detaillee par mode

### Mode dry (test ou validation offline)
1. Construit payload JSON
2. Validation offline (4 criteres)
3. Sauve dans `$HERMES_WORKSPACE/tests/insta-payload-<timestamp>.json`
4. **STOP**. Aucun appel reseau.

### Mode container
1. Construit payload + validation offline
2. `curl -X POST "https://graph.facebook.com/v18.0/${IG_BUSINESS_ACCOUNT_ID}/media" -d "..."`
3. Capture container_id, log
4. **STOP**. Pas de media_publish.

### Mode approval (DEFAUT en prod)
1. Mode container (steps 1-3 ci-dessus)
2. Email approbation + Telegram approbation (cf. workflow §Approval gate)
3. **STOP**. Attend /yes_insta du tuteur.

### Mode publish_now (interdit autonome)
1. Mode container
2. `POST /media_publish?creation_id=<container_id>`
3. Email + Telegram notification publication effective
4. **Necessite mention explicite "mode=publish_now" du tuteur dans le prompt**

## Pitfalls
- **HERMES_MODE=prod sans mode explicite = approval** (NE publie JAMAIS sans /yes tuteur)
- Sans `INSTAGRAM_GRAPH_TOKEN` ou `IG_BUSINESS_ACCOUNT_ID` dans .env : modes container/approval/publish impossibles. Reste sur dry et signale (cf. INSTAGRAM-SETUP-TODO.md)
- Caption > 2200 chars = refusee par Meta. Tronque ou regenere
- > 30 hashtags = refusee. Reduit
- En cas d erreur API Meta (`OAuthException`, rate limit) : NE PAS reessayer aveuglement, log et alerte
- CAROUSEL : 2-10 enfants strict. Plus = refuse
- **Container Meta TTL = 24h non-publie**. Si tuteur ne valide pas dans les 24h, le container expire et il faut relancer depuis zero.

## Verification
- Mode dry : payload JSON valide ecrit, parseable par `json.loads`, 0 appel reseau
- Mode container : container_id retourne par Graph API, 0 appel a media_publish (verifie via log)
- Mode approval : container_id + email envoye (EMAIL_SMTP_OK) + Telegram envoye + 0 appel media_publish
- Mode publish_now : media_id final retourne, permalink email envoye, mention "/yes_insta" du tuteur presente dans le prompt
