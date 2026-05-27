# Prompt Phase 0 — Finalisation (résolution des 8 bloqueurs)

> À donner à Hermes **après** le récap "PHASE 0 TERMINÉE" pour résoudre les bloqueurs avant le GO Phase 1.
>
> Procédure :
> 1. `ssh azamoul-vps`
> 2. `hermes chat --continue` (reprendre la session Phase 0)
> 3. Coller le bloc ci-dessous tel quel.

---

## État des 8 bloqueurs et stratégie

| Bloqueur | Stratégie | Action attendue |
|---|---|---|
| **SMTP_PASSWORD** | ✅ Credentials fournis → à brancher maintenant | Étape 1 |
| **GEMINI_API_KEY** | Expirée (connu) → reporté, pas bloquant Phase 1 (audit non destructif) | Étape 4 documentation |
| **FIRECRAWL_API_KEY** | Optionnel free tier → reporté, fallback sur scraping toolkit local | Étape 4 documentation |
| **GSC non connectée** | Nécessite OAuth interactif → reporté Phase 2 | Étape 4 documentation |
| **App reviews non identifiée** | Détectable par Hermes via scraping du thème Shopify | Étape 3 |
| **Instagram @azamoul** | Détectable via meta sociales / footer Shopify | Étape 3 |
| **brand-knowledge.md** | Livraison de Phase 1, pas un prérequis | Étape 4 documentation |
| **GITHUB_TOKEN** | Optionnel → seulement pour versionner reports | Étape 4 documentation |

---

## Prompt à coller

````
Tu reprends la session Phase 0. 4 actions à exécuter dans cet ordre.
Ne passe pas à la suivante avant d'avoir validé la précédente.

═══════════════════════════════════════════════════════════════════
ÉTAPE 1 — Brancher SMTP Gmail et tester l'envoi
═══════════════════════════════════════════════════════════════════

Les credentials SMTP sont confirmés par l'utilisateur :
  - Compte expéditeur : djebar.rayan75@gmail.com (compte développeur Rayan)
  - App Password Gmail : rlig iuea zwak uzbr   (16 chars, espaces optionnels)
  - Destinataire des cron : contact.azamoul@gmail.com (gérant Azamoul)

1.1 — Ajoute / met à jour ces variables dans /root/.hermes/.env
     (n'écrase pas les autres clés existantes, fais un grep + ajout
     ou un sed -i propre) :

       EMAIL_SMTP_HOST=smtp.gmail.com
       EMAIL_SMTP_PORT=587
       EMAIL_SMTP_USER=djebar.rayan75@gmail.com
       EMAIL_SMTP_PASSWORD=***REDACTED***
       EMAIL_FROM=djebar.rayan75@gmail.com
       EMAIL_TO=contact.azamoul@gmail.com
       EMAIL_HOME_ADDRESS=contact.azamoul@gmail.com

     ⚠ Note : Gmail App Password fonctionne avec OU sans espaces.
     Je l'écris sans espaces ci-dessus pour éviter les soucis de
     quoting dans .env.

1.2 — Re-vérifie les permissions :
       chmod 600 /root/.hermes/.env

1.3 — TEST D'ENVOI réel (c'est le test H qui était PENDING) :
     Compose et envoie un email test depuis Hermes :

       Sujet : [TEST] Hermes SMTP ready — $(date +%Y-%m-%d %H:%M)
       Destinataire : contact.azamoul@gmail.com
       Corps :
         Phase 0 — Finalisation
         SMTP Gmail branché et opérationnel.
         Expéditeur : djebar.rayan75@gmail.com
         Le cron samedi 10h pourra désormais livrer l'email
         créatif (idées produit + post Instagram).
         — Hermes Agent

1.4 — Confirme la réception : demande à l'utilisateur de checker
     contact.azamoul@gmail.com (inbox + spam Gmail) et de répondre
     par "email reçu" ou "rien reçu".

1.5 — Si l'email n'arrive pas : diagnose (smtplib trace complète,
     code SMTP retourné, check si Gmail demande "Less secure app"
     ou si l'App Password a expiré). Ne fabrique pas une solution
     de contournement, rapporte exactement l'erreur.

═══════════════════════════════════════════════════════════════════
ÉTAPE 2 — Test A (Memory OpenViking) à rejouer si non validé
═══════════════════════════════════════════════════════════════════

Le récap de Phase 0 montrait Test A non listé dans les ✓. Re-teste :

  - Écris un fait via le tool memory : "phase0_smtp_validated_at_$(date +%s) = ok"
  - Liste les faits récents
  - Confirme que le fait est bien retrouvé
  - Supprime-le

Si OpenViking n'est pas accessible en lecture/écriture depuis Hermes,
flagge-le — c'est critique pour l'auto-amélioration cross-session.

═══════════════════════════════════════════════════════════════════
ÉTAPE 3 — Investigations autonomes (sans credentials externes)
═══════════════════════════════════════════════════════════════════

Tu peux résoudre 2 bloqueurs sans aucune clé API externe, juste avec
le toolkit Shopify et un fetch HTTP du site public.

3.1 — IDENTIFIER L'APP REVIEWS
     - Récupère l'HTML de la home page :
         curl -sL https://azamoul-symboles-berberes.myshopify.com/ \
           -o /tmp/azamoul-home.html
     - Cherche les signatures connues d'apps reviews :
         * Judge.me   : "judgeme", "jdgm-", "judge.me"
         * Yotpo      : "yotpo", "staticw2.yotpo.com"
         * Stamped    : "stamped.io", "stamped-reviews"
         * Okendo     : "okendo.io"
         * Shopify Product Reviews (native, déprécié) : "spr-"
     - Idem sur une page produit (prends le premier produit du sitemap
       /sitemap_products_1.xml) — les widgets reviews sont souvent
       chargés sur la page produit, pas la home.
     - Rapporte : app détectée + version + sélecteur DOM utilisé.
     - Si AUCUNE app détectée : c'est aussi un constat précieux —
       proposer à l'utilisateur d'installer Judge.me (gratuit jusqu'à

3.2 — CONFIRMER INSTAGRAM @azamoul
     - Cherche dans /tmp/azamoul-home.html les balises sociales :
         <meta property="og:see_also">
         <link rel="me" href="https://instagram.com/...">
         href="https://instagram.com/...
         href="https://www.instagram.com/...
     - Cherche aussi dans le footer (rendu côté serveur la plupart du temps).
     - Si trouvé : note le handle exact + URL.
     - Si pas trouvé sur la home, vérifie aussi :
         * /pages/contact
         * /policies/shipping-policy
     - Si toujours rien : propose 2-3 handles candidats à l'utilisateur :
         @azamoul / @azamoul.shop / @azamoul.symboles_berberes
       basés sur les conventions de nommage Shopify usuelles.

═══════════════════════════════════════════════════════════════════
ÉTAPE 4 — Documenter les bloqueurs reportés et leur impact Phase 1
═══════════════════════════════════════════════════════════════════

Crée /root/azamoul-shopify/PHASE0-BLOCKERS-STATUS.md avec ce format :

```markdown
# Bloqueurs Phase 0 — État au YYYY-MM-DD

## Résolus
- [x] SMTP Gmail (App Password fourni, testé le YYYY-MM-DD)
- [x] App reviews : <résultat étape 3.1>
- [x] Instagram : <résultat étape 3.2>

## Reportés (non bloquants pour Phase 1 audit)
- [ ] GEMINI_API_KEY — expirée (connu par utilisateur).
      Impact Phase 1 : aucun (audit baseline ne génère pas de texte AI).
      Impact Phase 2+ : enrichissement descriptions impossible.
      Action : régénérer une clé sur https://aistudio.google.com/app/apikey

- [ ] FIRECRAWL_API_KEY — absente.
      Impact Phase 1 : veille concurrentielle limitée (scraping local
                       toujours possible via curl + sélecteurs CSS).
      Impact Phase 2+ : pas critique, fallback HTTP local OK.
      Action : free tier 500 crawls/mois sur https://firecrawl.dev

- [ ] GSC non connectée.
      Impact Phase 1 : aucun (KPI SEO mesurés depuis Shopify Admin).
      Impact Phase 2+ : pas d'analyse "impressions/clics requêtes".
      Action : OAuth via https://search.google.com/search-console
               + ajout du domaine Shopify + service account JSON.

- [ ] GITHUB_TOKEN — absent.
      Impact Phase 1 : aucun (reports locaux dans /root/azamoul-shopify/reports/).
      Impact Phase 2+ : pas de versioning automatique des reports.
      Action : PAT classique scopes repo + read:user.

- [ ] brand-knowledge.md — pas un bloqueur, c'est la PREMIÈRE LIVRAISON
      de la Phase 1. Sera créé pendant la fondation.
```

═══════════════════════════════════════════════════════════════════
ÉTAPE 5 — Récap Telegram + demande de GO
═══════════════════════════════════════════════════════════════════

Envoie au chat <TELEGRAM_USER_ID> :

  ✅ PHASE 0 — Finalisation
  ─────────────────────────
  SMTP : branché et testé (envoi vers contact.azamoul@gmail.com)
  Memory OpenViking : <OK/KO selon test A>
  App reviews détectée : <nom ou "aucune">
  Instagram confirmé : <handle ou "à valider">

  Bloqueurs reportés (non critiques pour Phase 1) :
    • Gemini expirée (à régénérer pour Phase 2+)
    • Firecrawl, GSC, GitHub : optionnels Phase 2+
  Détail complet : /root/azamoul-shopify/PHASE0-BLOCKERS-STATUS.md

  Phase 1 prête à démarrer (Fondation, semaines 1-2).
  En attente : ta confirmation "email reçu" + ton GO Phase 1.

═══════════════════════════════════════════════════════════════════
RÈGLES DURES
═══════════════════════════════════════════════════════════════════
1. JAMAIS de mutation Shopify pendant cette finalisation Phase 0.
2. Le mot de passe SMTP qui t'a été fourni est SENSIBLE — il ne doit
   apparaître QUE dans /root/.hermes/.env (chmod 600). Ne le log
   nulle part, ne le mentionne dans aucun message Telegram, aucun
   rapport, aucune mémoire.
3. Si Gmail rejette l'auth SMTP (erreur 535 ou 534) :
   - rapporte exactement le code retour
   - suggère à l'utilisateur de vérifier que 2FA est activée sur le
     compte Gmail (prérequis pour générer un App Password)
   - n'essaie PAS de stocker le password en clair ailleurs.
4. Si Test A (memory) re-échoue : tente un redémarrage du service
   openviking (systemctl restart openviking), retest, et rapporte.

Démarre par l'étape 1.
````

---

## Après le récap Telegram

Une fois Hermes confirme l'envoi et que tu as vu l'email arriver dans `contact.azamoul@gmail.com`, donne-lui le GO Phase 1 :

```
"email reçu" + GO Phase 1.
Démarre la Fondation décrite dans MISSION-HERMES.md §"Première mission"
+ §"Phases de déploiement / Phase 1".
Pendant 2 semaines (jusqu'au 2026-05-25) : AUCUNE action mutative
autonome — uniquement collecte baseline + audit catalogue + construction
de brand-knowledge.md + identification GSC (si OAuth possible).
Premier rapport "constat" attendu lundi 2026-05-18 à 9h Paris,
livré sur Telegram + en draft dans reports/2026-W20-perf.md.
```

## Notes de sécurité

- Une fois confirmé que le cron samedi marche, **révoque l'App Password Gmail** partagé en clair dans ce chat et génère-en un nouveau : [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- Quand tu régénères la clé Gemini, mets-la directement dans `/root/.hermes/.env` sur le VPS (pas en clair dans un chat), et n'oublie pas `chmod 600`.
- Idée pour plus tard : déplacer tous les secrets dans un vrai gestionnaire (Vault, sops, ou même `pass`) plutôt que `.env` plain text.
