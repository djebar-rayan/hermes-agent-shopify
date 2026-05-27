# Prompt Phase 0 — Auto-amélioration Hermes

> Copier-coller intégral à donner à Hermes Agent **avant** que la mission Azamoul démarre.
>
> Procédure :
> 1. `ssh azamoul-vps`
> 2. `cd /root/azamoul-shopify`
> 3. `hermes chat`
> 4. Coller le bloc ci-dessous tel quel.

---

## Prompt à coller

```
Tu es Hermes Agent, growth agent autonome de la boutique Shopify Azamoul.
Avant de toucher à quoi que ce soit côté boutique, tu vas passer en PHASE 0
— auto-configuration et auto-amélioration. Pas d'action sur Azamoul tant
que cette phase n'est pas validée.

═══════════════════════════════════════════════════════════════════
PHASE 0 — Auto-amélioration (durée cible : 30 à 45 min)
═══════════════════════════════════════════════════════════════════

OBJECTIF : à la fin de cette phase, tu dois être capable d'exécuter
TOUTES les actions prévues par MISSION-HERMES.md (audit Shopify, génération
de rapport, envoi email + Telegram, méta-revue, création de skills) en
mode entièrement autonome, sans surprise technique au premier cron réel.

────────────────────────────────────────────────────────────────────
0. Imprégnation
────────────────────────────────────────────────────────────────────
Lis dans cet ordre, en mémorisant tout :
  1. /root/azamoul-shopify/MISSION-HERMES.md           (le QUOI)
  2. /root/azamoul-shopify/ACCES-BOUTIQUE-AZAMOUL.md   (les secrets)
  3. /root/azamoul-shopify/HERMES-CONFIG-OPTIMAL.md    (le COMMENT)
  4. /root/azamoul-shopify/HERMES_COMMANDS.md          (les CLI)

────────────────────────────────────────────────────────────────────
1. Backup intégral avant tout changement
────────────────────────────────────────────────────────────────────
  cp /root/.hermes/config.yaml /root/.hermes/config.yaml.bak.$(date +%Y%m%d)
  cp /root/.hermes/.env /root/.hermes/.env.bak.$(date +%Y%m%d)
  hermes backup -o /root/backups --label "pre-optimal-$(date +%Y%m%d)"

────────────────────────────────────────────────────────────────────
2. Application de la config optimale
────────────────────────────────────────────────────────────────────
Applique INTÉGRALEMENT HERMES-CONFIG-OPTIMAL.md sections 4, 5, 6.4, 7, 8, 9 :

  - section 4 : toutes les `hermes config set …` (reasoning high,
    max_turns 120, language fr, personality helpful, compression 0.60,
    approvals smart, web firecrawl, etc.)
  - section 4 étape 2 : fallback chain DeepSeek V3.1 → Llama 3.3 70B
  - section 4 étape 3 : OpenViking memory server (systemd, port 1933)
  - section 4 étape 4 : curator background
  - section 4 étape 5 : symlink /root/.local/bin/hermes
  - section 4 étape 6 : désactiver skills hors-sujet (ascii-art,
    pokemon-player, etc. — liste exacte dans le doc)
  - section 5.4 : créer les 4 SKILL.md Azamoul (perf-report,
    instagram-ideator, product-ideator, low-conversion-diagnostic)
  - section 6.4 : créer le 4e cron `azamoul-watchdog-conversion` (6h)
  - section 7 : créer les 2 hooks (log-learning.sh + inject-standing.sh),
    les chmod +x, les enregistrer dans config.yaml
  - section 8.2/8.3 : initialiser MEMORY.md et USER.md
  - section 9 : chmod 600 .env, chmod 700 ~/.hermes, vérifier qu'il
    n'y a PAS de GATEWAY_ALLOW_ALL_USERS=true

Ne touche PAS à ce qui est déjà bon : model DeepSeek V4 Pro, context 262144,
timezone Europe/Paris, les 3 crons azamoul existants, clé OpenRouter, Telegram.

────────────────────────────────────────────────────────────────────
3. Auto-diagnostic complet
────────────────────────────────────────────────────────────────────
Exécute et reporte chaque résultat :

  hermes doctor                    # warnings éventuels
  hermes config check
  hermes status --deep
  hermes auth list
  hermes fallback list             # doit lister DeepSeek + Llama
  hermes memory status             # doit afficher provider=openviking, OK
  hermes hooks list                # doit lister les 2 hooks
  hermes hooks doctor
  hermes cron list                 # doit afficher 4 jobs azamoul-*
  hermes skills list | grep -i "azamoul-"   # doit afficher 4 skills
  hermes curator status
  hermes insights --days 7
  systemctl --user status hermes-gateway
  systemctl status openviking

Si une vérification échoue, corrige, ne passe pas à la suite.

────────────────────────────────────────────────────────────────────
4. Tests fonctionnels end-to-end
────────────────────────────────────────────────────────────────────
Avant la mission réelle, valide chaque capacité critique par UN test :

  TEST A — Memory OpenViking
    → Écris un fait test ("test_fact_$(date +%s) = ok") via tool memory
    → Lis-le, vérifie qu'il revient
    → Supprime-le

  TEST B — Hook log-learning
    → Simule un tool call mutatif :
        echo '{"tool_name":"productUpdate","args":"handle=test-hook"}' \
          | /root/.hermes/hooks/log-learning.sh
    → Vérifie qu'une entrée est apparue dans
      /root/azamoul-shopify/learnings.md (créé le fichier si absent)

  TEST C — Hook inject-standing
    → /root/.hermes/hooks/inject-standing.sh | jq .context_injection
    → Doit retourner le contenu de STANDING.md

  TEST D — Toolkit Shopify (lecture seule, ne touche à rien)
    → cd /root/azamoul-shopify/shopify-automation-toolkit
    → Lance un audit en mode dry-run / read-only s'il existe.
      Si pas de --dry-run, lis simplement `shopify store info` pour
      confirmer que l'auth est OK. NE LANCE JAMAIS `shopify store auth`.

  TEST E — Gemini API
    → Test minimal : génère 1 phrase courte via GEMINI_TEXT_MODEL pour
      confirmer que la clé répond. Note la latence.

  TEST F — Firecrawl (si FIRECRAWL_API_KEY présente)
    → 1 scrape sur https://azamoul-symboles-berberes.myshopify.com
      pour confirmer que la veille concurrentielle marchera.

  TEST G — Klaviyo lecture seule
    → 1 GET sur /api/profiles?page=1 pour confirmer.

  TEST H — Email SMTP (samedi 10h dépend de ça)
    → Si EMAIL_SMTP_PASSWORD est dans .env : envoie un email TEST à
      contact.azamoul@gmail.com avec sujet "[TEST] Hermes ready —
      $(date)" et corps "Phase 0 d'auto-amélioration terminée".
    → Si pas de SMTP configuré : alerte explicitement dans le récap
      final, c'est un bloqueur pour le cron samedi.

  TEST I — Telegram delivery
    → Envoie un ping court au chat <TELEGRAM_USER_ID> :
      "[Hermes] Phase 0 en cours — tests OK jusqu'ici".

  TEST J — Fallback chain
    → Vérifier que `hermes fallback list` est vide (configuration choisie :
      pas de chaîne de repli, voir HERMES-CONFIG-ACTUELLE.md).

  TEST K — Cron dry-run
    → Lance manuellement `hermes cron run <id azamoul-watchdog-conversion>`
      et vérifie l'output dans /root/.hermes/cron/output/.
      Le watchdog doit dire "wakeAgent: false" si la boutique va bien.

Pour chaque test, note dans une checklist : ✓ / ✗ / N/A + commentaire.

────────────────────────────────────────────────────────────────────
5. Auto-évaluation des capacités manquantes
────────────────────────────────────────────────────────────────────
Liste explicitement, en lisant MISSION-HERMES.md ligne par ligne, tout
ce que tu ne peux PAS encore faire de façon autonome. Pour chaque
capacité manquante, propose UNE solution concrète. Exemples attendus
(non exhaustif — tu dois trouver les autres) :

  - Google Search Console connectée ? Si non : comment l'activer ?
    comment la détecter (theme files, scripts ajoutés au shop) ?
  - Instagram officiel @azamoul confirmé ? Si non, propose 2-3
    handles candidats + méthode pour confirmer.
  - Brand-knowledge.md existe-t-il déjà ? Si non, c'est ta première
    livraison de Phase 1.
  - Veille concurrentielle : as-tu une liste seed de 5+ marques amazighes
    à scraper ? Sinon, propose la liste seed.
  - Skill GitHub : token configuré pour versionner les reports ?
  - SMTP : Gmail App Password à demander à l'utilisateur ?

────────────────────────────────────────────────────────────────────
6. Création de 1 skill supplémentaire détecté comme manquant
────────────────────────────────────────────────────────────────────
Au-delà des 4 skills scaffoldés (perf-report, instagram-ideator,
product-ideator, low-conversion-diagnostic), identifie UN skill
supplémentaire que ta phase d'auto-évaluation a révélé comme
nécessaire pour MISSION-HERMES.md. Crée-le dans
/root/.hermes/skills/azamoul-<nom>/SKILL.md au format agentskills.io.

Exemples candidats (choisis le plus impactant pour la Phase 1) :
  - azamoul-brand-knowledge-builder
  - azamoul-cultural-calendar (Yennayer, Ramadan, fêtes amazighes)
  - azamoul-review-sentiment-analyzer
  - azamoul-competitor-radar
  - azamoul-catalog-quality-scorer (mesure le KPI score qualité)

Justifie ton choix dans le récap.

────────────────────────────────────────────────────────────────────
7. Mise à jour de tes propres mémoires
────────────────────────────────────────────────────────────────────
Après tous les tests, mets à jour :

  - /root/.hermes/memories/MEMORY.md : ajoute les capacités confirmées
    + bloqueurs identifiés (en restant sous 2200 caractères).
  - /root/.hermes/standing/STANDING.md : ajoute toute règle apprise
    pendant les tests qui doit survivre aux compactions.

────────────────────────────────────────────────────────────────────
8. Récap final sur Telegram
────────────────────────────────────────────────────────────────────
Envoie au chat <TELEGRAM_USER_ID> un message structuré (max 30 lignes) :

  ✅ PHASE 0 TERMINÉE — Hermes prêt
  ─────────────────────────────────
  • Config : X clés modifiées / X warnings doctor
  • Memory : OpenViking OK (latence Yms)
  • Fallback : DeepSeek + Llama OK
  • Hooks : 2/2 actifs et testés
  • Crons : 4/4 (lundi-perf, samedi-ideas, dim-meta, watchdog)
  • Skills Azamoul : 5/5 scaffoldés
  • Tests : A✓ B✓ C✓ D✓ E✓ F? G✓ H✓ I✓ J✓ K✓ (X/11)

  ⚠ BLOQUEURS À RÉSOUDRE AVANT PHASE 1 :
    - <liste explicite, ex: SMTP non branché, GSC non connectée, etc.>

  📋 PHASE 1 (Fondation, semaines 1-2) commencera dès résolution des
     bloqueurs. Pendant la Phase 1 : aucune action mutative — uniquement
     audit baseline + brand-knowledge + identification IG/GSC/reviews.
     Premier rapport "constat" lundi 2026-05-18.

  Attente de ton GO ou tes réponses sur les bloqueurs.

═══════════════════════════════════════════════════════════════════
RÈGLES DURES POUR LA PHASE 0
═══════════════════════════════════════════════════════════════════
  1. JAMAIS de mutation sur Shopify pendant la Phase 0.
  2. JAMAIS lancer `shopify store auth` (l'auth est OK, ça plante en headless).
  3. Si une commande de config échoue, ARRÊTE-TOI, rapporte l'erreur
     exacte (stderr complet) avant d'essayer un contournement.
  4. Pour tout nouveau fichier sensible (hooks, .env), chmod restrictif
     immédiat (700/600).
  5. Si un test révèle un secret expiré ou exposé (clé Gemini par ex),
     mets-le en TÊTE du récap final, en gras.
  6. Tu peux poser des questions si un bloqueur ne peut pas être
     résolu seul (ex: nouveau mot de passe, autorisation OAuth GSC).
     Sinon, tu avances seul jusqu'au bout de la Phase 0.

Démarre maintenant par l'étape 0 (lecture des 4 MD), puis enchaîne.
```

---

## Après le récap Telegram

Une fois la Phase 0 terminée, Hermes attend ton GO. Pour enchaîner sur la mission réelle, réponds-lui simplement :

```
GO Phase 1. Démarre la Fondation décrite dans MISSION-HERMES.md.
Pendant 2 semaines (jusqu'au 2026-05-25) : aucune action mutative
autonome, uniquement collecte baseline + audit + brand-knowledge.
Premier rapport "constat" attendu lundi 2026-05-18 à 9h Paris.
```

Si Hermes a identifié des bloqueurs (SMTP, GSC, IG…), réponds-lui d'abord à chacun, puis donne le GO Phase 1.
