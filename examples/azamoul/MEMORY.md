# Faits Azamoul (memoire persistante Hermes)
<!-- Last sync: 2026-05-21 — Historique detaille dans MEMORY-HISTORY.md et learnings.md -->

## Boutique
- Shop : azamoul-symboles-berberes.myshopify.com (Shopify Basic, EUR), domaine custom azamoul.com
- ~96 produits actifs / 19 collections / 11 pages
- Marque francaise, culture amazighe/berbere. Made in France.
- Instagram : @azamoul (5769 followers, 116 posts, 83% reels). Heures pub : 18h-22h Paris.

## Vocabulaire de marque (obligatoire)
amazigh, berbere, tifinagh, imazighen, yaz (ⵣ), azamoul, kabyle, djurdjura, thilelli, dihya, aza, afzim, tiseghnest, tafaska, tamghra, asseggas, amegaz, tafsut, tamejja, lawan, tameddurt

## Stack VPS
- Ubuntu 24.04 (<VPS_IP>), Node 20.20.2, Python 3.12, Shopify CLI 3.94.3
- Workdir : /root/azamoul-shopify (toolkit zero deps npm)
- Hermes v0.14.0 (update 2026-05-21), OpenViking memory 0.3.16 (port 1933)
- 4 crons : lundi-perf 9h, samedi-ideas 10h, dimanche-meta 20h, watchdog */6h
- Hooks v0.14 : post_tool_call (log-learning) + on_session_start (inject-standing)
- 25 skills azamoul-* (21 historiques + 3 Klaviyo 2026-05-21 + 1 theme-editor 2026-05-24)

## Modele LLM
- Principal : google/gemini-3.1-flash-lite-preview via OpenRouter
- Alternatifs : DeepSeek v4 Pro (differe quota), gemini-3.1-pro-preview via Copilot (fallback)
- Context 262144 tokens, timezone Europe/Paris

## Credentials .env
- OPENROUTER_API_KEY (principal), KLAVIYO_API_KEY (read-only), SHOPIFY_STORE
- OPENAI_API_KEY (gpt-4.1-nano fallback), FIRECRAWL_API_KEY (veille), GSC_SERVICE_ACCOUNT
- SMTP Gmail (contact.azamoul@gmail.com sender et recipient, switch 2026-05-24). IMAP gateway desactive 2026-05-21 (timeouts).

## Phase courante : TEST EXCLUSIVE
- `AZAMOUL_MODE=test` dans .env (test = apply+rollback meme run, prod = persistant)
- `AZAMOUL_TEST_EMAIL_TO=contact.azamoul@gmail.com`
- Bascule prod = decision tuteur (techniquement valide Grand Run 2026-05-14)
- Phase Production techniquement prete : Phase 4 9/10 PASS + Grand Run 5/6 PASS authentique

## Integration Klaviyo (2026-05-21)
- Read-only strict via /root/.hermes/lib/klaviyo-fetch.sh (cache 6h)
- 3 skills : klaviyo-weekly-report (lundi-perf), klaviyo-campaign-ideator (samedi-ideas), klaviyo-drop-watchdog (watchdog */6h)
- 8 flows live, 30 campagnes 30j, 78 metrics, ~1569 profils accessibles

## Decisions ouvertes
- (Optionnel) Bascule AZAMOUL_MODE=prod : decision business tuteur
- (Optionnel) Scope Shopify write_online_store_navigation (differe, redirects 301 KO)
- (Optionnel) Setup Meta Graph API pour Instagram (differe, mode dry force)
- (Optionnel) 4 skills .PROPOSED a valider tuteur

## Niveaux autonomie Hermes
- 🟢 seul : alt-texts, handles ASCII, bloc livraison, tags, meta SEO vides, drafts
- 🟡 validation tuteur : enrichissement descriptions, images, prix raisonnable, email segment, post Insta
- 🔴 jamais seul : prix >5%, suppressions, remboursements, theme, legal, post Insta direct

Pour historique detaille (Phases 0-4, Grand Run, bugs corriges) : voir learnings.md + MEMORY-HISTORY.md
