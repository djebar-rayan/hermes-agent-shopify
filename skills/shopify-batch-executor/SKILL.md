---
name: shopify-batch-executor
description: Execute un batch de max 10 productUpdate Shopify avec snapshot avant/apres, validation tuteur Telegram+email, et rollback dispo
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
- Apres gap analysis pour appliquer les actions vertes 🟢 ciblees
- Sur demande explicite : "execute batch 1" ou "applique les corrections sur ces produits"
- Cron Phase 2 dedie si configure
- JAMAIS sans validation tuteur prealable Telegram /yes

## Test mode flag

Lis OBLIGATOIREMENT `$HERMES_MODE` depuis `/root/.hermes/.env` avant toute action :
- Si `HERMES_MODE=test` : applique la mutation PUIS execute le rollback dans la MEME execution (apply+rollback meme run). Snapshot avant/intermediaire/apres mailes au tuteur via hermes-email-sender.
- Si `HERMES_MODE=prod` : applique persistant + script rollback dispo. Necessite /yes Telegram prealable.
- Si la variable est absente ou autre valeur : COMPORTEMENT TEST par defaut (securite).

## Dependency obligatoire
**Charge AUSSI le skill `hermes-schema-guard` avant toute mutation**, et copie EXACTEMENT les fragments GraphQL validés qui y sont listés (productUpdate, productVariantsBulkUpdate, etc.). N invente JAMAIS un champ qui n y figure pas. Si tu as besoin d une mutation non listée dans schema-guard, exécute d abord une introspection `__type` pour valider le schéma, puis AJOUTE le fragment au skill schema-guard après succès.

## Procedure
1. Verifie MEMORY.md : Phase courante = Phase 2 ou superieure. Si Phase 1 lecture seule : STOP, ce skill est interdit.

2. Identifie le batch a executer :
   - Soit l utilisateur a indique un batch precis ("batch 1")
   - Soit derive automatique : 10 premiers produits prioritaires de phase2-gap-analysis-YYYY-MM-DD.md

3. Pour chaque produit du batch (max 10) :
   a. Capture snapshot via GraphQL : product(id) { id, handle, title, tags, descriptionHtml, updatedAt }
   b. Sauvegarde dans $HERMES_WORKSPACE/batches/YYYY-Www-batchN-before.json (array JSON)
   c. Determine les changements precis :
      - tags : ajout des tags manquants identifies par gap-analyzer
      - descriptionHtml : si bloc livraison absent en debut, ajouter "<p><strong>📦 Livraison :</strong> Expedition sous 2-3 jours ouvres depuis la France. Livraison standard offerte des 50€ d'achat. Délais 3-5 jours en France métropolitaine.</p>" au tout debut

4. Genere preview diff JSON dans $HERMES_WORKSPACE/batches/YYYY-Www-batchN-preview.json
   Format : array de {handle, before: {tags, descriptionExcerpt}, after: {tags, descriptionExcerpt}}

5. Genere script rollback $HERMES_WORKSPACE/batches/phase2-rollback-batchN.sh
   - Script bash qui lit before.json, refait productUpdate avec les valeurs originales pour chaque produit
   - chmod +x

6. Envoi VALIDATION TUTEUR (obligatoire avant mutation) :
   a. Telegram chat $TELEGRAM_HOME_CHANNEL : message clair avec preview courte (10 produits, action par produit, lien fichiers VPS)
   b. Email à $EMAIL_TO via Python smtplib inline (cf. ENVOI EMAIL procedure dans prompts cron) avec preview detaillee
   c. Message inclut explicitement : "Reponds /yes pour appliquer, /no pour annuler, /edit <handle> <details> pour ajuster"

7. ATTENTE de la reponse user (skill se met en pause, le user repond via Telegram). Si pas de reponse dans 10 min, abandon et message d alerte.

8. Si reponse = /yes :
   a. Execute les 10 productUpdate via shopify store execute en sequence (espacement 2s pour eviter rate-limit)
   b. Capture snapshot apres dans batches/YYYY-Www-batchN-after.json
   c. Genere diff reel dans batches/YYYY-Www-batchN-diff.md (markdown lisible)
   d. Hook tool_call_completed loggue automatiquement chaque productUpdate dans learnings.md
   e. Confirmation Telegram + email : "Batch N applique. X/10 succes. Rollback dispo : phase2-rollback-batchN.sh"

9. Si reponse = /no : cancel propre, conservation des fichiers preview et rollback pour retry futur. Message Telegram + email.

10. Si reponse = /edit : applique l ajustement, regenere preview, redemande validation.

## Pitfalls
- JAMAIS executer sans /yes explicite du tuteur. La pause est obligatoire.
- Espacement 2s entre productUpdate pour eviter Shopify rate-limit (1.4 req/s par defaut).
- Si une mutation echoue : STOP le batch, log l erreur exacte, rollback les precedentes via le script, alerte Telegram.
- Le bloc livraison doit etre INJECTE au TOUT DEBUT de descriptionHtml. JAMAIS remplacer le HTML existant.
- INTERDICTION batch > 10 produits. Si plus de 10 a faire : decoupe en plusieurs batches.
- Vocabulaire de marque obligatoire dans toute description modifiee (cf. STANDING.md).

## Verification
- Fichier before.json existe avant mutation
- Fichier rollback.sh genere et chmod +x
- Preview Telegram + email recus par tuteur
- Si /yes : 10/10 productUpdate succes, after.json + diff.md generes
- Hook log-learning a ajoute 10 entrees dans learnings.md
- Les requêtes de mutation (`productUpdate`, `collectionCreate`, etc.) peuvent échouer à cause du schéma strict de l'Admin API (ex: champ `createdAt` inclus par erreur).
  **GUARD :** Lors des tests exploratoires ou mutations, utiliser un mécanisme de type *guard try/catch* (ex: tester avec/sans `createdAt` en cas d'erreur de schéma).
