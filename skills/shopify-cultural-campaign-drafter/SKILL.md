---
name: shopify-cultural-campaign-drafter
description: Genere les drafts d une campagne pour un événement culturel (capsule produits + email + 2 posts Instagram + calendrier diffusion)
version: 1.0.0
author: Hermes (Phase 2 scaffold)
metadata:
  hermes:
    tags: [campaign, marketing, instagram, email, framework]
    category: ecommerce
    requires_toolsets: [terminal, file]
---
# Cultural Campaign Drafter <STORE_NAME>

## When to Use
- 2 a 4 semaines avant un événement culturel (cf. shopify-cultural-calendar)
- Sur demande explicite : "draft la campagne Aid al-Adha" ou "prepare Yennayer"
- Alerte preavis auto declenchee par cultural-calendar : ce skill prend le relais
- Toujours en mode draft, JAMAIS publication automatique

## Procedure
1. Recoit en parametre eventName (ex. "Aid al-Adha 2026", "<nouvel an culturel depuis cultural-events.json>", "1er novembre 2026")
   + dateJ0 (ex. "2026-06-26") OU calcul depuis cultural-calendar.

2. Verifie phase courante dans MEMORY.md : Phase 2+ requis. Si Phase 1, drafts uniquement (sans creation produit).

3. Lit les sources :
   - brand-knowledge.md (concurrents, ton de marque, niches sous-exploitees)
   - audits/initial-catalog-audit.md (produits dispos pour capsule)
   - reports/baseline-kpi-30j.md (volume estime)
   - cron list shopify-samedi-ideas prompt pour le format ideas

4. Selectionne 3-5 produits existants du catalogue pour la capsule (PAS de creation produit nouveau). Critere :
   - Alignement thematique avec l evenement (ex. Aid al-Adha = fete familiale = produits cadeaux + identite)
   - Stock disponible (totalInventory > 0)
   - Vocabulaire de marque respecté

5. Cree $HERMES_WORKSPACE/campaigns/<event-slug-YYYY>/ avec ces 5 fichiers :

   a. README.md : brief campagne, calendrier diffusion (J-21 / J-14 / J-10 / J-3 / J0), code promo suggere (ex. AID2026 -15 percent), KPIs cibles
   b. email-draft.txt : sujet + corps email (texte clair, max 30 lignes, vocabulaire de marque (STORE-BRAND.md), lien produits, code promo, signature)
   c. insta-post-1-reel.md : draft 1er post (J-21 teaser) format reel : storytelling, caption FR + EN, 15 hashtags (5 gros + 5 moyens + 5 niches), description visuelle textuelle, heure recommandee 18-22h Paris, CTA
   d. insta-post-2-carrousel.md : draft 2e post (J-10 produits capsule) format carrousel 3-5 slides : focus produits, prix, hashtags, visuel
   e. produit-capsule.md : 3-5 produits selectionnes avec argumentaire pourquoi chaque produit + mise en avant proposee + suggestion bundle

6. Notifie Telegram + email :
   "Drafts campagne <eventName> prets dans campaigns/<slug>/.
   Calendrier : J-21 le YYYY-MM-DD (premier post), J-14 (email), J-10 (carrousel + code promo), J-3 (reminder).
   /yes pour valider l ensemble, /edit <fichier> <ajustement>, /no pour reprendre."

7. JAMAIS de publication automatique. Ce skill produit uniquement des drafts pour validation tuteur.

## Pitfalls
- INTERDICTION creation produit nouveau via productCreate : niveau 🟡 hors perimetre.
- Code promo doit etre valide a fixer ENSUITE par le tuteur via Shopify Admin (Hermes ne cree pas le code promo automatique).
- Calendrier J-21/14/10/3 selon MISSION-HERMES.md regle preavis 2 semaines minimum.
- Vocabulaire de marque obligatoire (cf. STANDING.md liste).
- Description visuelle TEXTUELLE seulement (generation image indisponible Phase 2).

## Verification
- 5 fichiers crees dans campaigns/<event-slug-YYYY>/
- README.md contient le calendrier explicite J-21/14/10/3/0
- Hashtags posts respectent la repartition 5+5+5 (gros/moyens/niches)
- Telegram + email recus avec le brief
