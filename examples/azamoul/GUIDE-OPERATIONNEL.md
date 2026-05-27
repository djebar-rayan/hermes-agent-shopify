# Guide Hermès pour Azamoul

> Documentation destinée à **toute l'équipe Azamoul** (M. Lyes Ameddah, mainteneurs, futurs collaborateurs).
>
> Vous y trouverez : ce qu'est Hermès, comment il fonctionne, comment l'utiliser au quotidien, comment réagir en cas de problème.
>
> Ce document remplace toute documentation antérieure et reflète l'état du projet au **14 mai 2026** (post-Grand Run Test, prêt pour Phase Production).

---

## Sommaire

1. [Hermès en une phrase](#1-hermès-en-une-phrase)
2. [À quoi il est branché](#2-à-quoi-il-est-branché)
2.5. [**Infrastructure VPS & services techniques**](#25-infrastructure-vps--services-techniques)
3. [Les 4 rendez-vous hebdomadaires](#3-les-4-rendez-vous-hebdomadaires)
4. [Les 3 niveaux d'autonomie (🟢🟡🔴)](#4-les-3-niveaux-dautonomie)
5. [Les KPIs — les chiffres expliqués](#5-les-kpis--les-chiffres-expliqués)
6. [Le scoring des actions (mémoire intelligente)](#6-le-scoring-des-actions)
7. [Les phases de déploiement](#7-les-phases-de-déploiement)
8. [Comment lire un rapport](#8-comment-lire-un-rapport-dhermès)
9. [Comment lui répondre](#9-comment-répondre-à-hermès)
10. [En cas de problème](#10-en-cas-de-problème)
10.5. [**Procédures opérationnelles courantes**](#105-procédures-opérationnelles-courantes)
11. [**Les 21 skills atomiques**](#11-les-21-skills-atomiques)
12. [**Sécurité & garde-fous techniques**](#12-sécurité--garde-fous-techniques)
13. [**État actuel du projet (mai 2026)**](#13-état-actuel-du-projet-mai-2026)
14. [**Piloter Hermès au quotidien (cheat-sheet)**](#14-piloter-hermès-au-quotidien-cheat-sheet)
    - 14.5 [Faire évoluer Hermès](#145-faire-évoluer-hermès)
    - 14.6 [Coûts récurrents et budget](#146-coûts-récurrents-et-budget)
    - 14.7 [Sauvegardes et disaster recovery](#147-sauvegardes-et-disaster-recovery)
    - 14.8 [Continuité du projet et escalade](#148-continuité-du-projet-et-escalade)
15. [Mini-glossaire e-commerce](#15-mini-glossaire-e-commerce)
16. [Mini-glossaire IA](#16-mini-glossaire-ia)
17. [Pour aller plus loin](#17-pour-aller-plus-loin)

---

## 1. Hermès en une phrase

**Hermès est un assistant IA autonome** qui surveille la boutique Azamoul 24 h sur 24, produit chaque lundi un rapport de performance, propose chaque samedi deux idées créatives (un nouveau produit et un post Instagram), applique en autonomie de petites améliorations SEO, et alerte en cas d'anomalie.

Il n'est pas un robot magique : il fait ce qui est écrit dans son contrat (`MISSION-HERMES.md`), pas plus. Il a trois niveaux de permission — vert, jaune, rouge — qui définissent ce qu'il peut décider seul, ce qu'il doit faire valider, et ce qu'il ne fait jamais.

---

## 2. À quoi il est branché

Imaginez Hermès comme un employé virtuel au bureau, branché à plusieurs services :

```
                  ┌────────────────────────┐
                  │     L'équipe Azamoul   │
                  │   Smartphone Telegram  │
                  │   Boîte mail Gmail     │
                  └───────────┬────────────┘
                              │
              ┌───────────────┴─────────────────┐
              │                                 │
       (lit / répond)                    (envoie rapports)
              │                                 │
              ▼                                 ▼
        ┌─────────────────────────────────────────┐
        │              HERMÈS                     │
        │     (sur un petit serveur Linux         │
        │      loué 24h/24, basé à Paris)         │
        └────┬────────────┬───────────┬───────────┘
             │            │           │
             ▼            ▼           ▼
       ┌──────────┐ ┌──────────┐ ┌──────────────┐
       │ Shopify  │ │ Cerveau  │ │  Mémoire     │
       │ (Admin)  │ │   IA     │ │  OpenViking  │
       │          │ │ Gemini   │ │ (sur même    │
       │ lit les  │ │ 3.1 Flash│ │  serveur)    │
       │ ventes,  │ │  Lite    │ │              │
       │ modifie  │ │  via     │ │ se souvient  │
       │ fiches   │ │OpenRouter│ │ d'une        │
       │ produit  │ │          │ │ semaine sur  │
       │          │ │ (fallback│ │ l'autre      │
       │          │ │swappable)│ │              │
       └──────────┘ └──────────┘ └──────────────┘
```

| Brique | Rôle | Pourquoi celle-là |
|---|---|---|
| **Serveur VPS** | Ordinateur loué 24h/24 où Hermès vit (Ubuntu 24.04, IP <VPS_IP>) | Pour qu'il puisse tourner même quand votre PC est éteint |
| **Hermes Agent** | Le programme orchestrateur (open source, NousResearch) | Gère seul tout le travail répétitif et l'enchaînement des skills |
| **Gemini 3.1 Flash Lite Preview** (via OpenRouter) | Le « cerveau » qui rédige et raisonne | Contexte 256 k, latence faible, coût très faible (free tier OpenRouter avec rate limit modéré). Swappable en 5 min avec DeepSeek v4 Pro ou Copilot Gemini en cas de besoin |
| **OpenViking** | La mémoire long terme (port 1933) | Pour qu'il se souvienne des décisions d'une semaine à l'autre, des concurrents, du vocabulaire amazigh |
| **Telegram** | Le canal de discussion immédiat (chat <TELEGRAM_USER_ID>) | Notifications rapides, validation des actions 🟡 en un clic |
| **Gmail SMTP** | Le canal des rapports formels | Email créatif du samedi et rapport du lundi |
| **Shopify Admin GraphQL** | La boutique | Source de vérité pour ventes, produits, clients |

**Note sur le LLM** : Hermès n'est pas marié à un modèle IA spécifique. Le modèle actuellement actif est **Gemini 3.1 Flash Lite Preview via OpenRouter** (`google/gemini-3.1-flash-lite-preview`), choisi pour son contexte de 256 k, sa latence faible et son coût très faible (free tier OpenRouter, rate limit modéré). La capacité de **swap entre fournisseurs** (Gemini Flash Lite ↔ DeepSeek v4 Pro ↔ Copilot Gemini ↔ OpenAI) est intégrée — si un fournisseur rencontre un rate-limit ou une panne, le tuteur peut basculer en 5 minutes via le fichier `config.yaml`. Le Grand Run Test du 14 mai 2026 a validé cette portabilité : le test a démarré sur Copilot Gemini (Gemini 3.1 Pro Preview), basculé en cours vers DeepSeek v4 Pro (OpenRouter) comme preuve de portabilité, puis la prod a été stabilisée sur Gemini 3.1 Flash Lite — les résultats étaient équivalents entre modèles.

---

## 2.5 Infrastructure VPS & services techniques

> Cette section regroupe **tout ce qu'il faut savoir au niveau système** pour reprendre la main sur le VPS de production sans avoir à fouiller dans les autres documents. Source : lecture SSH directe du VPS le 16 mai 2026 (`VPS_SNAPSHOT_2026-05-16.md`).

### 2.5.1 Accès au VPS

| Donnée | Valeur |
|---|---|
| Hostname réel | `<VPS_HOSTNAME>` |
| Alias SSH côté dev | `azamoul-vps` |
| IP publique | `<VPS_IP>` |
| OS | Ubuntu 24.04 LTS, kernel Linux 6.8.0-111-generic x86_64 |
| User principal | `root` (toutes les configs vivent sous `/root/`) |
| Authentification | Clé Ed25519 (mot de passe désactivé) |

**Pour se connecter** depuis un poste où la clé du dev actuel est configurée :

```bash
ssh azamoul-vps
```

**Pour ajouter une nouvelle clé** (nouveau mainteneur, deuxième poste) :

```bash
# Depuis le nouveau poste (option simple)
ssh-copy-id azamoul-vps

# Ou édition manuelle (depuis une session SSH déjà ouverte)
nano /root/.ssh/authorized_keys   # coller la clé publique sur une nouvelle ligne
```

### 2.5.2 Services systemd actifs

Deux services tournent en permanence sur le VPS — **avec un piège** : ils ne sont pas dans le même scope systemd.

**`hermes-gateway.service`** (user service)
- Lancé via `systemctl --user`, pas `systemctl` tout court
- ExecStart : `/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace`
- WorkingDirectory : `/usr/local/lib/hermes-agent`
- Restart=always, RestartSec=60
- Rôle : gateway Telegram + scheduler des 4 crons
- Suivi temps réel : `journalctl --user -u hermes-gateway -f`
- Log fichier : `cat /root/.hermes/logs/gateway.log`
- Redémarrage : `systemctl --user restart hermes-gateway`

**`openviking.service`** (system service)
- Lancé via `systemctl` normal
- Définition : `/etc/systemd/system/openviking.service`
- ExecStart : `/opt/openviking/bin/openviking-server`
- User=root, Restart=on-failure, RestartSec=10
- Port : 1933 (mémoire vectorielle)
- Suivi temps réel : `journalctl -u openviking -f`
- Redémarrage : `systemctl restart openviking`

> **Piège classique** : `systemctl status hermes-gateway` (sans `--user`) renvoie « Unit not found ». Toujours passer le flag `--user` pour le gateway Hermes, pas pour OpenViking.

### 2.5.3 Chemins critiques sur le VPS

| Chemin | Contenu | Quoi y trouver |
|---|---|---|
| `/root/.hermes/.env` | 45 variables d'env (LLM, SMTP, Telegram…) | Tous les secrets, `chmod 600` |
| `/root/.hermes/config.yaml` | Config Hermes (LLM actif, agent settings, terminal) | À éditer pour swap LLM |
| `/root/.hermes/cron/jobs.json` | Les 4 crons (id, prompt, schedule, runs) | Source de vérité crons |
| `/root/.hermes/cron/output/<job-id>/` | Sortie horodatée de chaque run de cron | Lire la dernière exécution |
| `/root/.hermes/skills/` | 45 dossiers (21 azamoul + 24 système) | Logique métier de l'agent |
| `/root/.hermes/standing/STANDING.md` | 14 règles immuables injectées chaque session | Garde-fous comportement |
| `/root/.hermes/memories/MEMORY.md` | Mémoire persistante de Hermès | Phase courante, décisions |
| `/root/.hermes/sessions/` | Transcripts JSON des conversations | Debug fin d'une session |
| `/root/.hermes/logs/agent.log` | Log principal Hermes | Debug LLM/skills |
| `/root/.hermes/logs/errors.log` | Erreurs uniquement | Triage rapide |
| `/root/.hermes/logs/gateway.log` | Log du gateway Telegram | Debug réception messages |
| `/root/.hermes/state.db` | SQLite (+ WAL + SHM) état Hermes | NE PAS éditer à la main |
| `/root/.hermes/hooks/log-learning.sh` | Hook append à learnings.md | Trace observabilité |
| `/root/.hermes/hooks/inject-standing.sh` | Hook injection STANDING.md | Garantit règles immuables |
| `/root/azamoul-shopify/MISSION-HERMES.md` | Charte technique de la mission | Référence Hermes |
| `/root/azamoul-shopify/learnings.md` | Journal append-only des actions | Audit méta-revue |
| `/root/azamoul-shopify/brand-knowledge.md` | Carte d'identité marque + concurrents | Skill brand-knowledge |
| `/root/azamoul-shopify/baseline-kpi-30j.md` | Baseline KPI 30 jours | Référence comparatives |
| `/root/azamoul-shopify/reports/` | Rapports perf + ideas hebdo | Livrables crons lundi/samedi |
| `/root/azamoul-shopify/meta-reviews/` | Méta-revues dominicales | Auto-amélioration |
| `/root/azamoul-shopify/audits/` | Audits catalogue ponctuels | Snapshots qualité |
| `/root/azamoul-shopify/batches/` | Snapshots before/after de chaque batch | Rollback + audit mutations |
| `/root/azamoul-shopify/campaigns/` | Drafts campagnes culturelles | Aïd, Tafsut, Yennayer… |
| `/root/azamoul-shopify/tests/` | Sorties tests skills | Smoke + fonctionnel |
| `/root/azamoul-shopify/shopify-automation-toolkit/` | Toolkit Node.js réutilisable | Helpers GraphQL |
| `/opt/openviking/bin/openviking-server` | Binaire serveur mémoire | Service openviking |
| `/usr/local/lib/hermes-agent/venv/` | Python 3.11 Hermes v0.13.0 | Runtime |
| `/usr/local/lib/hermes-agent/node_modules/` | Deps Node Hermes | Runtime |
| `/etc/systemd/system/openviking.service` | Unité systemd OpenViking | System scope |
| `~/.config/systemd/user/hermes-gateway.service` | Unité systemd gateway | User scope |

### 2.5.4 Variables d'env structurantes (sans valeurs)

Le fichier `/root/.hermes/.env` contient **exactement 45 clés**, regroupées ici par catégorie. Aucune valeur n'est révélée — pour éditer en SSH : `nano /root/.hermes/.env` (le fichier est en `chmod 600`, lisible uniquement par root).

**LLM** (7 clés)
- `OPENROUTER_API_KEY` — clé du fournisseur LLM principal
- `COPILOT_GITHUB_TOKEN` — fallback Gemini via GitHub Copilot
- `OPENAI_API_KEY`, `OPENAI_TEXT_MODEL`, `OPENAI_VISION_MODEL` — endpoint OpenAI (utilisé pour vision)
- `ANTHROPIC_API_KEY`, `ANTHROPIC_TOKEN` — réservé tests cross-vendor

**Shopify** (1 clé)
- `SHOPIFY_STORE` — handle de la boutique Azamoul

**Email SMTP / IMAP** (11 clés)
- `EMAIL_FROM`, `EMAIL_TO` — expéditeur et destinataire production
- `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`, `EMAIL_SMTP_USER`, `EMAIL_SMTP_PASSWORD` — credentials sortants
- `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `EMAIL_IMAP_HOST` — credentials entrants (parsing réponses)
- `EMAIL_ALLOWED_USERS` — whitelist expéditeurs autorisés
- `EMAIL_HOME_ADDRESS` — adresse interne réservée

**Telegram** (3 clés)
- `TELEGRAM_BOT_TOKEN` — token bot HTTP API
- `TELEGRAM_HOME_CHANNEL` — chat ID principal (cohérent avec règle 10 STANDING : `<TELEGRAM_USER_ID>`)
- `TELEGRAM_ALLOWED_USERS` — whitelist user IDs autorisés

**Google Search Console** (5 clés)
- `GSC_CLIENT_EMAIL`, `GSC_PROJECT_ID` — identité service account
- `GSC_SERVICE_ACCOUNT_FILE`, `GSC_TOKEN_PATH` — chemins credentials
- `GSC_SITE_URL` — propriété GSC suivie

**Mode application** (2 clés)
- `AZAMOUL_MODE` — `test` ou `prod` (voir §12, flag central)
- `AZAMOUL_TEST_EMAIL_TO` — destinataire forcé en mode test (`contact.azamoul@gmail.com`)

**OpenViking & outils périphériques** (16 clés)
- `OPENVIKING_ENDPOINT` — endpoint mémoire vectorielle locale
- `FIRECRAWL_API_KEY` — scraping concurrent
- `BROWSERBASE_ADVANCED_STEALTH`, `BROWSERBASE_PROXIES` — browser headless cloud
- `BROWSER_INACTIVITY_TIMEOUT`, `BROWSER_SESSION_TIMEOUT` — timeouts headless
- `HASS_URL` — Home Assistant (réservé futur)
- `TERMINAL_LIFETIME_SECONDS`, `TERMINAL_MODAL_IMAGE`, `TERMINAL_PERSISTENT_SHELL`, `TERMINAL_TIMEOUT` — sandbox terminal Hermes
- `IMAGE_TOOLS_DEBUG`, `MOA_TOOLS_DEBUG`, `VISION_TOOLS_DEBUG`, `WEB_TOOLS_DEBUG` — flags debug par catégorie d'outils

> **Sécurité** : `.env` est en `chmod 600` (lisible uniquement par root) et n'est ni dans Git ni dans un backup public. Toute modification se fait directement en SSH via `nano /root/.hermes/.env`. La nouvelle config est lue à la volée par le prochain run — pas de redémarrage du gateway.

---

## 3. Les 4 rendez-vous hebdomadaires

> **IDs des crons** (utiles pour `hermes cron run <id>` ou consulter `/root/.hermes/cron/output/<id>/`) :
>
> | Cron | ID |
> |---|---|
> | `azamoul-lundi-perf` (lundi 9 h) | `9b3edc604e0d` |
> | `azamoul-samedi-ideas` (samedi 10 h) | `7936943cee39` |
> | `azamoul-dimanche-meta` (dimanche 20 h) | `8450eef5fde8` |
> | `azamoul-watchdog-conversion` (toutes les 6 h) | `dd4a59c29a88` |

### 3.1 Lundi 9 h — Le rapport de performance

**Ce qu'Hermès fait avant 9 h** :
- Connecte à Shopify, télécharge les 7 derniers jours (ventes, commandes, paniers abandonnés, sessions, top produits, top pages).
- Compare à la semaine d'avant.
- Lit `learnings.md` (son journal) pour voir l'impact des actions passées.
- Rédige un rapport complet (~ 1 page) et un résumé court.

**Ce que vous recevez à 9 h** :
- Un **message Telegram** de 20 lignes maximum avec les chiffres clés, les top wins/pertes de la semaine et les actions qu'il propose.
- Un **email** avec le rapport complet (plus détaillé).

**À quoi ça sert pour vous** : voir l'état de la boutique en 30 secondes, savoir si la semaine était bonne ou non, valider d'un coup d'œil les actions 🟡 proposées.

---

### 3.2 Samedi 10 h — L'email créatif

**Ce qu'Hermès fait** :
- Lit la fiche `brand-knowledge.md` (carte d'identité de la marque + concurrents + actualité culturelle amazighe).
- Analyse ce qui marche déjà (posts les plus likés sur @azamoul, produits les plus vendus).
- Décide d'**exactement 2 propositions** :
  1. **Une idée de nouveau produit** : nom (avec déclinaison Tifinagh si pertinent), catégorie, prix cible, marge estimée, concurrents qui font similaire, visuel de référence.
  2. **Une idée de post Instagram** : format (carrousel/reel/story), caption complète FR/EN prête à copier, 15 hashtags optimisés, visuel, date de publication recommandée, CTA.

**Ce que vous recevez à 10 h** :
- Un **email** à `contact.azamoul@gmail.com` (sujet : *« Azamoul — Idées de la semaine — YYYY-MM-DD »*).
- Un **ping court** sur Telegram pour signaler que l'email est parti.

**À quoi ça sert pour vous** : alimenter le calendrier éditorial sans avoir à réfléchir vous-même, avoir 2 idées clé en main que vous validez (ou rejetez) en 5 minutes.

> **Important** : Hermès **ne publie jamais** sur Instagram tout seul (action 🔴). Même en mode production, l'**approval gate** Instagram envoie d'abord un preview email+Telegram et attend votre `/yes_insta <container_id>` avant publication réelle.

---

### 3.3 Dimanche 20 h — La méta-revue

**Ce qu'Hermès fait** :
- Relit `learnings.md` des 7 derniers jours.
- Pour chaque action exécutée, regarde si elle a eu un impact mesurable sur les ventes.
- Identifie 3 motifs : ce qui a marché, ce qui a échoué, ce qui mérite un **nouveau skill** (mini-programme).
- Si un même type d'action revient plus de 3 fois en 4 semaines, il **crée un skill `.PROPOSED`** pour l'industrialiser.

**Ce que vous recevez à 20 h** :
- Un **message Telegram** de 15 lignes max intitulé *« Méta-revue semaine 20 »*.
- Liste des nouveaux skills proposés, des patterns confirmés, et des ajustements de stratégie pour la semaine à venir.

**À quoi ça sert pour vous** : voir qu'Hermès s'améliore tout seul. Plus les semaines passent, plus il devient efficace sans qu'il faille le re-paramétrer.

> **Validation des skills `.PROPOSED`** : ils ne s'activent **jamais** automatiquement. Vous (ou Rayan) devez renommer le fichier `SKILL.md.PROPOSED` en `SKILL.md` pour qu'il soit chargé par Hermès. Filet de sécurité contre l'auto-modification non supervisée.

---

### 3.4 Toutes les 6 heures — Le watchdog (silencieux)

**Ce qu'Hermès fait** :
- Vérifie les indicateurs critiques (sessions, commandes, conversion).
- Si tout est dans les clous → **silence radio**, zéro notification.
- Si un seuil est franchi (par exemple 0 commande sur 7 jours, ou chute > 30 % en 24 h) → **alerte Telegram immédiate**.

**Ce que vous recevez** :
- **Rien** la plupart du temps. C'est normal.
- **Une alerte** uniquement en cas d'anomalie réelle.

**À quoi ça sert pour vous** : être prévenu en temps réel d'un problème sans avoir à surveiller manuellement, sans recevoir 4 notifications par jour pour rien.

---

## 4. Les 3 niveaux d'autonomie

Hermès classe chaque action possible en trois couleurs. Ce code est le **contrat de confiance** : il définit ce qu'il peut décider seul.

### 🟢 VERT — Hermès le fait seul

Actions à **faible risque** et **réversibles**. Pas besoin de vous demander :

- Ajouter un *alt text* manquant à une image (texte alternatif lu par Google)
- Convertir une URL avec caractères Tifinagh en caractères latins (handle ASCII)
- Repositionner le bloc *Livraison 📦* en haut d'une description
- Ajouter des *tags* manquants à un produit
- Corriger une *meta description* vide
- Générer un rapport, un audit, un export

**Pourquoi le faire seul** : ce sont des centaines de micro-corrections qui demanderaient des semaines à faire manuellement. Et chacune est trivialement réversible en un clic.

---

### 🟡 JAUNE — Hermès propose, vous décidez

Actions à **impact réel** mais réversibles. Il vous envoie la proposition sur Telegram :

- Réécriture complète d'une description produit (enrichie par IA)
- Remplacement d'une image de mauvaise qualité
- Modification d'un meta title existant
- Création d'une redirection 301
- Création ou modification d'une collection
- Modification de prix raisonnable (≤ 5 %)
- Envoi d'un email à un segment via Shopify Email
- Création d'un produit suite à une proposition validée

**Comment vous répondez** : sur Telegram, vous tapez simplement `/yes`, `/no`, ou `/edit` (suivi de votre correction). Hermès applique selon votre choix.

---

### 🔴 ROUGE — Hermès NE FAIT PAS sans accord explicite

Actions à **fort impact** ou **irréversibles**. Il ne les fera **jamais** seul, même si vous lui dites « fais ce que tu veux ». Il faut une instruction explicite de votre part :

- Modification de prix importante (> 5 %)
- Suppression d'un produit, d'une page, d'un client
- Remboursement client
- Changement de thème, de passerelle de paiement, de livraison
- Modifications légales (CGV, mentions légales, politique de retours)
- **Publication directe sur Instagram** (même en mode prod, l'approval gate impose `/yes_insta`)

---

## 5. Les KPIs — les chiffres expliqués

Hermès suit 8 indicateurs chaque semaine. Voici à quoi ils correspondent en clair, et pourquoi ils comptent.

### 5.1 Chiffre d'affaires (CA)

**Définition** : la somme totale en euros des ventes réalisées sur la période.

**Comment Hermès le récupère** : via l'API Shopify GraphQL, somme des commandes payées des 7 derniers jours.

**Cible** : **+5 % de croissance par semaine**, en glissant.

**Comment Hermès l'utilise** : si le CA stagne ou baisse, il propose des actions 🟡 (envoi d'email à un segment, mise en avant d'un produit dans une collection, code promo limité dans le temps).

---

### 5.2 Taux de conversion

**Définition** : sur 100 visiteurs de la boutique, combien achètent ?

**Formule** : `nombre de commandes / nombre de sessions × 100`.

**Norme du marché** : 1 à 3 % est considéré comme bon pour une boutique de niche.

**Cible** : **+ 0,5 point chaque mois** (par exemple passer de 0,6 % à 1,1 % en un mois).

**Comment Hermès l'utilise** : si la conversion d'un produit décroche, il diagnostique en 12 points (qualité photo, longueur description, prix, avis, etc.) puis propose des corrections.

---

### 5.3 Panier moyen (AOV — *Average Order Value*)

**Définition** : montant moyen dépensé par un client qui passe commande.

**Formule** : `CA / nombre de commandes`.

**Comment Hermès l'utilise** : si le panier moyen est faible, il propose des produits complémentaires ("acheté avec…"), une collection "Pack famille", ou un seuil de livraison gratuite à 50 €.

---

### 5.4 Taux d'abandon de panier

**Définition** : sur 100 paniers créés, combien partent sans payer ?

**Norme du marché** : ~70 % d'abandon est la moyenne.

**Cible** : **− 5 points chaque mois** (par exemple passer de 75 % à 70 % en un mois).

**Comment Hermès l'utilise** : analyse les paniers abandonnés sur 30 jours, identifie les produits qui sont les plus souvent abandonnés (souvent un signal de prix ou de friction au checkout), propose des actions.

---

### 5.5 Score qualité catalogue (créé sur mesure pour Azamoul)

**Définition** : pourcentage de produits qui ont **TOUS** les quatre éléments suivants :
- une description ≥ 150 mots
- un *meta title* renseigné
- une *meta description* renseignée
- ≥ 3 images

**Cible** : **100 % dans 4 semaines**.

**Pourquoi c'est important** : un produit qui coche les 4 cases est correctement indexable par Google ET inspire confiance dès le premier coup d'œil. C'est l'indicateur le plus actionable des 8 (Hermès peut agir directement dessus via ses actions 🟢).

---

### 5.6 Note moyenne des avis

**Définition** : moyenne des étoiles laissées par les clients (suivi via metafields Shopify natif).

**Cible** : **+ 0,2 par mois**.

**Comment Hermès l'utilise** : repère les produits dont la note **baisse sur 30 jours** (signal d'un problème : taille incorrecte, qualité d'impression, photo trompeuse, etc.) et propose un diagnostic.

---

### 5.7 Actions 🟢 exécutées

**Définition** : nombre d'actions autonomes réalisées par Hermès dans la semaine.

**Cible** : **10 à 20 par semaine**.

**Pourquoi c'est mesuré** : un agent qui n'agit pas n'apporte aucune valeur. Mais un agent qui agit trop sans qu'on lise les rapports devient un risque. La cible 10–20 est un équilibre.

---

### 5.8 Revenus par canal

**Définition** : ventilation du CA par source de trafic :
- **Organique** : Google, recherches non payantes (suivi via Google Search Console connectée)
- **Paid** : publicité Google Ads, Meta Ads (si campagnes actives)
- **Social** : visites depuis Instagram, TikTok
- **Email** : ouvertures et clics depuis Shopify Email

**Comment Hermès l'utilise** : si le trafic organique baisse alors qu'on a corrigé le SEO, il y a un signal à creuser (mise à jour algorithme Google, concurrent qui a pris une position, etc.).

---

## 6. Le scoring des actions

C'est le mécanisme **d'apprentissage** d'Hermès. Plus il fonctionne longtemps, plus il devient malin.

### Comment ça marche

Quand Hermès fait une action (par exemple « réécrire la description du Mug Yaz »), il :
1. Note la situation **avant** (vues du produit, ventes, conversion).
2. Applique l'action.
3. Sept jours plus tard, mesure l'**après**.
4. Calcule un *impact moyen* sur un grand nombre d'actions du même type.
5. La semaine suivante, il **priorise les actions au score le plus élevé**.

### Exemple concret (fictif, illustratif)

| Type d'action | Occurrences | Impact moyen | Score |
|---|---:|---|---:|
| Bloc *Livraison* en début de description | 12 | + 4,2 % conversion produit | **0,91** |
| Réécriture description par IA | 8 | + 2,3 % conversion produit | **0,82** |
| Ajout *alt text* | 24 | + 1,1 % impressions Google | 0,71 |
| Ajout tag *Made in France* | 18 | + 0,3 % rien de mesurable | 0,12 |

**Conclusion qu'Hermès en tire** : la semaine prochaine, il faut commencer par compléter les blocs livraison manquants (score 0,91), puis enchaîner les réécritures de descriptions (score 0,82). L'ajout de tags *Made in France* sans impact mesurable est déprioritisé.

### Pourquoi c'est important

Sans scoring, un agent IA répèterait éternellement les mêmes actions parce qu'on lui a dit de les faire. **Avec scoring, l'agent ajuste son comportement en fonction de ce qui marche réellement sur votre boutique** — pas sur une boutique générique.

---

## 7. Les phases de déploiement

Le déploiement a été volontairement **progressif** pour éviter que l'agent ne casse quelque chose avant qu'on ait validé son fonctionnement. **Les 4 phases test sont terminées au 14 mai 2026**, voici l'historique :

### Phase 0 — Setup initial (mai 2026) — ✅ TERMINÉE

- Nettoyage des pollutions, configuration LLM (départ Gemini via Copilot, swap DeepSeek validé en cours de Grand Run, puis stabilisation sur Gemini 3.1 Flash Lite via OpenRouter)
- Authentification Shopify CLI, Google Search Console OAuth2, Gmail SMTP App Password
- 4 crons configurés (lundi, samedi, dimanche, watchdog)

### Phase 1 — Fondation read-only (terminée 2026-05-13) — ✅

- Collecte baseline 30 jours
- Audit catalogue (score initial 64%)
- Construction `brand-knowledge.md` (concurrents amazighs, calendrier culturel)
- Premier rapport de constat

### Phase 2 — Actions basiques (préparation, terminée 2026-05-13) — ✅

- Batch 1 (10 produits tags) préparé + script rollback testé
- Drafts campagne Aïd al-Adha 2026 (5 fichiers)

### Phase 3 — Couverture autonomie (terminée 2026-05-13) — ✅

- 17 skills atomiques validés smoke + fonctionnel
- 9/10 PASS (1 SKIP technique : scope `write_online_store_navigation` manquant pour redirects 301)
- Installation du skill `azamoul-shopify-schema-guard`

### Phase 4 — Autonomie complète (terminée 2026-05-14) — ✅

- 8/10 PASS authentique + 2/10 PASS comportemental sur retest strict
- **0 hallucination** au retest v2 (Hermès échoue honnêtement sans cible éligible plutôt qu'inventer)
- Choix architectural : **sous-prompts orchestrés** (mega-prompt rejeté, triche systématique)

### Grand Run Test — validation finale (terminée 2026-05-14) — ✅ GO

6 blocs exécutés, **9/9 critères globaux PASS**, **12 signaux d'autonomie observés** :

- B1 (4 crons) ✅, B2 (mutations éphémères) ✅, B3 (campagne Tafsut) ✅
- B4 (méta-revue + 2 `.PROPOSED`) ✅, B5 (5/5 refus adversariaux) ✅
- B6 (inventaire readiness) ⚠️ PARTIAL OK

**Verdict : ✅ GO Phase Production.** Hermès est techniquement prêt à basculer en mode prod, c'est désormais une décision business du tuteur.

### Phase Production — à déclencher (état actuel)

- Décisions tuteur restantes (toutes optionnelles, voir §13)
- Bascule = changement d'1 ligne dans `.env` : `AZAMOUL_MODE=test` → `AZAMOUL_MODE=prod`

> **Règle dure** : la bascule prod est une décision business, plus une question technique. Hermès est prêt — le tuteur choisit quand.

---

## 8. Comment lire un rapport d'Hermès

Exemple de rapport Telegram type que vous recevrez le lundi :

```
📊 RAPPORT AZAMOUL — Semaine 20 (12 → 18 mai)

KPI (vs S-1)
  CA          : 247 €  ↑  +27 %
  Commandes   : 4      ↑  +33 %
  Conversion  : 0,8 %  ↑  +0,2 pt
  Panier      : 62 €   ↓  −5 €
  Sessions    : 503    ↓  −8 %
  Score cat.  : 67 %   ↑  +12 pts

Top 3 wins
  1. T-shirt Yaz Femme : 3 ventes (vs 0 S-1)
  2. Mug Djurdjura : +47 vues (post Insta du 14)
  3. Description Coussin Imilchil enrichie : +18 % conv.

Top 3 pertes
  1. Coque iPhone : 0 vente, 0 vue (panneau vide ?)
  2. Trafic IG : −22 % (cycle algo ou pause posts ?)
  3. Bonnet Aza : taux abandon panier 89 %

Actions exécutées (3 actions 🟢)
  ✓ alt-texts manquants : 5
  ✓ meta description tronquée corrigée : 2
  ✓ tag "Made in France" ajouté : 4

Actions proposées (3 actions 🟡) → /yes /no /edit
  🟡 Réécrire desc. Bonnet Aza (89 % abandon — suspect prix)
  🟡 Republier post IG du 14 mai (best engagement S-1)
  🟡 Créer collection "Fête des mères 2026"

Prédictions S+1
  CA cible : 290 €    (basé sur tendance N-4 → N)
  Conversion cible : 1,0 %
  Hypothèse : la réécriture Bonnet améliore la conv.
```

**Comment réagir** :
1. Lecture en 30 secondes des chiffres principaux (haut du message).
2. Lecture en 1 minute des wins/pertes et du diagnostic.
3. Validation des 🟡 en 3 clics (`/yes` ou `/no` pour chaque).
4. Si une perte vous semble grave, vous répondez en français normal : « Pourquoi le bonnet Aza est à 89 % d'abandon ? Tu as un détail ? » → Hermès répond.

---

## 9. Comment répondre à Hermès

| Vous voulez… | Vous écrivez sur Telegram |
|---|---|
| Valider une action 🟡 | `/yes <id-action>` ou simplement `/yes` si c'est la dernière proposée |
| Refuser une action 🟡 | `/no <id-action>` (Hermès retient le refus) |
| Modifier une proposition 🟡 | `/edit <id-action> <votre version>` |
| **Approuver un post Instagram** (en prod) | `/yes_insta <container_id>` (après preview email+Telegram) |
| **Annuler un post Instagram en attente** | `/no_insta <container_id>` |
| Approuver un batch préparé (ex. Phase 2 batch 1) | `/yes batch1` |
| Poser une question | écrire en français normal (« Pourquoi tel chiffre baisse ? ») |
| Lui donner une mission ponctuelle | « Hermès, peux-tu auditer le produit X et me proposer 3 améliorations ? » |
| Mettre en pause un cron | (côté technique) `hermes cron pause <id>` — exemple concret : `hermes cron pause 9b3edc604e0d` met en pause le cron lundi-perf (voir tableau des IDs en §3) |
| Tout arrêter en urgence | (côté technique) `systemctl --user stop hermes-gateway` |

> **Note sur l'Instagram approval gate** : depuis la version 2.0.0 du skill `azamoul-instagram-publisher`, MÊME EN MODE PROD, Hermès ne publie JAMAIS un post Instagram sans validation explicite. Il génère le container Meta, envoie une preview par email + Telegram, et attend `/yes_insta <container_id>`. Cela garantit que vous gardez le contrôle total sur chaque publication, même quand Hermès est en autonomie complète.

---

## 10. En cas de problème

| Symptôme | Cause probable | Action |
|---|---|---|
| Pas de rapport lundi 9 h | Cron en pause, ou agent crashé | Vérifier `hermes cron list`, `hermes cron status` |
| OpenViking down (Hermès perd la mémoire) | Service système arrêté | `systemctl restart openviking` |
| Hermès offline sur Telegram | Gateway arrêtée | `systemctl --user restart hermes-gateway` |
| Hermès envoie 10 messages d'erreur d'affilée | Rate-limit LLM atteint | Voir bloc ci-dessous "Rate-limit LLM" |
| Email samedi non reçu | App Password Gmail expiré ou révoqué | Regénérer sur [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords), mettre à jour `EMAIL_SMTP_PASSWORD` dans `.env` |
| Hermès dit « Email envoyé » mais rien reçu | Bug : `EMAIL_SMTP_OK` absent du stdout | Vérifier dans `learnings.md` la dernière session — il doit écrire « Email NON envoyé » si SMTP a échoué |
| Vous voulez mettre Hermès en vacances | Pause de tous les crons | `hermes cron pause --all`, puis `hermes cron resume --all` au retour |
| Vous voulez basculer en prod | Décision tuteur | `sed -i 's/AZAMOUL_MODE=test/AZAMOUL_MODE=prod/' /root/.hermes/.env` puis surveiller premier cron |
| Vous voulez revenir en test (urgence) | Rollback prod | `sed -i 's/AZAMOUL_MODE=prod/AZAMOUL_MODE=test/' /root/.hermes/.env` + pause crons sensibles |

> **Bug connu** : le gateway IMAP/SMTP intégré de Hermes Agent est en panne depuis Phase 1. Les crons LLM contiennent un snippet Python `smtplib` inline qui se connecte directement au SMTP Gmail et émet `EMAIL_SMTP_OK` en stdout (voir STANDING.md règle 9). Ne pas tenter de réparer le gateway intégré — c'est la procédure officielle.

### Rate-limit LLM : procédure de swap

Hermès tourne actuellement sur **Gemini 3.1 Flash Lite Preview via OpenRouter** (`google/gemini-3.1-flash-lite-preview`). Si le free tier OpenRouter sature ou si la latence dégrade :

1. Sur VPS, ouvrir `/root/.hermes/config.yaml`
2. Modifier la section `model:` pour pointer vers un fallback déjà testé. Exemple **depuis Gemini Flash Lite vers DeepSeek v4 Pro** (toujours sur OpenRouter) :
   ```yaml
   model:
     default: deepseek/deepseek-chat-v4-pro
     provider: openrouter
     context_length: 131072
     request_timeout_seconds: 1800
     base_url: https://openrouter.ai/api/v1
     api_mode: chat_completions
   ```
   Ou alternative **vers Copilot Gemini 3.1 Pro Preview** (autre fournisseur, autre quota) :
   ```yaml
   model:
     provider: copilot
     base_url: https://api.githubcopilot.com
     model: gemini-3.1-pro-preview
   ```
3. Sauvegarder, le swap est effectif au prochain run (zéro redémarrage)
4. Test : `hermes chat -q 'echo ok'` doit répondre en < 5 secondes

Le swap inverse (retour vers Gemini Flash Lite) se fait pareil en remettant la config OpenRouter d'origine.

Dans tous les autres cas, contactez Rayan — il a un accès SSH au serveur et peut diagnostiquer en quelques minutes.

---

## 10.5 Procédures opérationnelles courantes

> Cette section regroupe les **commandes exactes** que vous (ou un nouveau mainteneur) lancerez le plus souvent en SSH sur le VPS. Toutes les commandes ci-dessous supposent une session ouverte via `ssh azamoul-vps`.

### 10.5.1 Lister et surveiller les crons

```bash
# Vue d'ensemble : 4 crons + état (enabled, last_status, next_run_at)
hermes cron list

# Le scheduler du gateway tourne-t-il ?
hermes cron status

# Lecture brute du fichier source de vérité (id, schedule, runs)
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | {id, name, schedule_display, last_run_at, last_status, next_run_at}'
```

Les 4 IDs (snapshot 2026-05-16) :

| ID | Nom | Schedule |
|---|---|---|
| `9b3edc604e0d` | `azamoul-lundi-perf` | `0 9 * * 1` |
| `7936943cee39` | `azamoul-samedi-ideas` | `0 10 * * 6` |
| `8450eef5fde8` | `azamoul-dimanche-meta` | `0 20 * * 0` |
| `dd4a59c29a88` | `azamoul-watchdog-conversion` | `0 */6 * * *` |

### 10.5.2 Forcer un cron immédiatement

```bash
# Forcer le rapport lundi maintenant (sans attendre 9h du prochain lundi)
hermes cron run 9b3edc604e0d --accept-hooks

# Forcer l'email créatif samedi
hermes cron run 7936943cee39 --accept-hooks

# Forcer la méta-revue dominicale
hermes cron run 8450eef5fde8 --accept-hooks

# Forcer un check watchdog (action no_agent, bash direct)
hermes cron run dd4a59c29a88 --accept-hooks
```

La sortie atterrit dans `/root/.hermes/cron/output/<job-id>/<timestamp>/`. Pour la lire :

```bash
# Lister les 5 derniers runs (plus récent en haut)
ls -lat /root/.hermes/cron/output/9b3edc604e0d/ | head -5

# Lire la réponse du run le plus récent
cat /root/.hermes/cron/output/9b3edc604e0d/<timestamp>/response.md
```

### 10.5.3 Mettre en pause / reprendre un cron

```bash
# Pause unitaire avec raison (la raison est tracée dans jobs.json)
hermes cron pause 9b3edc604e0d --reason "vacances tuteur"

# Reprise unitaire
hermes cron resume 9b3edc604e0d

# Pause / reprise globale (utile départs en vacances)
hermes cron pause --all
hermes cron resume --all
```

### 10.5.4 Swap LLM (rate-limit, panne fournisseur)

La config LLM est dans `/root/.hermes/config.yaml`, section `model:`. Modèle actif au snapshot : `google/gemini-3.1-flash-lite-preview` via OpenRouter.

```bash
nano /root/.hermes/config.yaml
```

Exemples de bascules validées :

```yaml
# Variante A — Gemini 3.1 Pro Preview via GitHub Copilot
model:
  default: gemini-3.1-pro-preview
  provider: copilot
  base_url: https://api.githubcopilot.com

# Variante B — DeepSeek v4 Pro via OpenRouter
model:
  default: deepseek/deepseek-chat-v4-pro
  provider: openrouter
  base_url: https://openrouter.ai/api/v1
```

Pas de redémarrage nécessaire — la config est relue au prochain run. Test :

```bash
hermes chat -q 'echo ok'
```

### 10.5.5 Tester l'envoi SMTP manuellement

Le gateway IMAP/SMTP interne est en panne (voir §10 « Bug connu »). Pour tester que les credentials du `.env` permettent toujours d'envoyer un email :

```bash
python3 -c "
import smtplib
env = {l.split('=',1)[0]: l.strip().split('=',1)[1] for l in open('/root/.hermes/.env') if '=' in l and not l.startswith('#')}
with smtplib.SMTP(env['EMAIL_SMTP_HOST'], int(env['EMAIL_SMTP_PORT']), timeout=15) as s:
    s.ehlo(); s.starttls(); s.ehlo()
    s.login(env['EMAIL_SMTP_USER'], env['EMAIL_SMTP_PASSWORD'])
    print('SMTP_LOGIN_OK')
"
```

Si `SMTP_LOGIN_OK` s'affiche, l'envoi marche. Sinon, l'App Password Gmail est probablement expiré → regénérer sur `myaccount.google.com/apppasswords` et mettre à jour `EMAIL_SMTP_PASSWORD` dans `.env`.

### 10.5.6 Vérifier qu'OpenViking tourne

```bash
# Statut du service
systemctl status openviking

# Healthcheck HTTP (port 1933)
curl -s http://127.0.0.1:1933/health
```

Si pas de réponse : `systemctl restart openviking` puis re-test.

### 10.5.7 Lire les derniers learnings

`learnings.md` est le journal append-only de toutes les actions exécutées par Hermès. Le hook `log-learning.sh` y ajoute une entrée à chaque appel de tool.

```bash
# Les 50 dernières lignes (suffisant pour la dernière session)
tail -50 /root/azamoul-shopify/learnings.md

# Recherche d'une action spécifique
grep -i "snapshot-diff-validator" /root/azamoul-shopify/learnings.md | tail -20

# Suivi temps réel pendant qu'un cron tourne
tail -f /root/azamoul-shopify/learnings.md
```

### 10.5.8 Diagnostiquer une mutation Shopify qui a échoué

Chaque batch crée un dossier horodaté dans `/root/azamoul-shopify/batches/` avec les snapshots BEFORE / AFTER-APPLY / AFTER-ROLLBACK. C'est le filet de sécurité du mode test.

```bash
# Lister les 5 derniers batches
ls -lat /root/azamoul-shopify/batches/ | head -5

# Lire le snapshot avant mutation
cat /root/azamoul-shopify/batches/<dernier_batch>/before.json

# Lire le diff (lisible humain)
cat /root/azamoul-shopify/batches/<dernier_batch>/diff.md

# Si le snapshot-diff-validator a FAIL : voir AFTER-ROLLBACK
cat /root/azamoul-shopify/batches/<dernier_batch>/after-rollback.json
```

En mode test, le diff entre `before.json` et `after-rollback.json` **doit être vide**. S'il ne l'est pas, c'est un échec critique du rollback — alerter immédiatement.

---

## 11. Les 21 skills atomiques

Hermès ne fait rien d'un seul bloc : il décompose ses tâches en **skills** atomiques (mini-programmes spécialisés). Chaque skill a un objectif précis et est invoqué automatiquement quand le contexte le demande.

### Référence / contexte (2 skills)

| Skill | Rôle |
|-------|------|
| `azamoul-cultural-calendar` | Calendrier culturel amazigh (Yennayer, Tafsut, Aïd al-Adha, Imilchil, etc.) pour timing campagnes |
| `azamoul-shopify-schema-guard` | Fragments GraphQL Shopify validés par introspection — consulté avant chaque mutation pour éviter hallucination de syntaxe |

> Note : la carte d'identité de marque (concurrents, vocabulaire amazigh, top hashtags) n'est pas un skill mais un fichier de connaissance lu par Hermès : `/root/azamoul-shopify/brand-knowledge.md`.

### Lecture / audit (3 skills)

| Skill | Rôle |
|-------|------|
| `azamoul-baseline-kpi-fetch` | Récupère KPI standardisés Shopify (CA, AOV, abandon, sessions) via GraphQL |
| `azamoul-catalog-gap-analyzer` | Identifie les gaps catalogue (alt-text vide, descriptions < 150 mots, etc.) priorisés |
| `azamoul-low-conversion-diagnostic` | Diagnostic 12 points sur un produit à faible conversion (image, prix, description, etc.) |

### Génération de contenu (4 skills)

| Skill | Rôle |
|-------|------|
| `azamoul-product-ideator` | Génère 1 idée de nouveau produit (nom, catégorie, prix cible, marge, visuel ref) — utilisé samedi |
| `azamoul-instagram-ideator` | Génère 1 idée de post Instagram (format, caption, hashtags, visuel, date) — utilisé samedi |
| `azamoul-cultural-campaign-drafter` | Génère bundle complet campagne culturelle (brief visuel + captions + email + handles + planning) |
| `azamoul-description-enricher` | Réécrit une description produit en l'enrichissant (bloc livraison, vocab amazigh, ≥150 mots) |

### Génération SEO (3 skills)

| Skill | Rôle |
|-------|------|
| `azamoul-altext-generator` | Génère un alt-text pour image produit (vocab amazigh, ≤125 chars, contexte produit) |
| `azamoul-metatitle-generator` | Génère un meta title (30-70 chars, contient mot-clé principal) |
| `azamoul-seo-mutation-batcher` ⭐ | Orchestre `productUpdate.seo` en batch de N produits avec snapshot+apply+rollback systématique |

### Mutation Shopify (3 skills)

| Skill | Rôle |
|-------|------|
| `azamoul-batch-executor` | Orchestrateur générique apply+rollback pour mutations Shopify |
| `azamoul-batch-rollback` | Procédure standardisée de rollback complet (utilise snapshot BEFORE) |
| `azamoul-snapshot-diff-validator` ⭐ | Garde-fou central du mode test : compare snapshot BEFORE vs AFTER-ROLLBACK, FAIL si diff non vide |

### Monitoring (3 skills)

| Skill | Rôle |
|-------|------|
| `azamoul-kpi-drop-watchdog` | Détecte drop > 30% sur KPI critiques (utilisé par cron watchdog */6h) |
| `azamoul-cron-output-watcher` ⭐ | Suit l'exécution d'un cron déclenché manuellement (poll output dir + parse `## Response`) |
| `azamoul-storefront-http-verifier` ⭐ | Vérifie HTTP 200/404 sur URL Shopify storefront après création/suppression |

### Messaging / output (2 skills)

| Skill | Rôle |
|-------|------|
| `azamoul-email-sender` | Envoie emails via Gmail SMTP avec rule `EMAIL_SMTP_OK` obligatoire — destinataire forcé en mode test |
| `azamoul-instagram-publisher` v2.0.0 | Crée container Meta + preview email+Telegram + **attend `/yes_insta` validation tuteur** avant publication réelle |

### Reporting (1 skill)

| Skill | Rôle |
|-------|------|
| `azamoul-weekly-perf-report` | Génère le rapport perf hebdo (utilisé par cron lundi-perf 9h) |

⭐ = skills créés autonomement par Hermès via méta-revue après détection de patterns récurrents ≥3 occurrences, **validés et activés le 14 mai 2026 (post-Grand Run Test)**. Ces 4 skills (`azamoul-seo-mutation-batcher`, `azamoul-storefront-http-verifier`, `azamoul-snapshot-diff-validator`, `azamoul-cron-output-watcher`) sont aujourd'hui **chargés et opérationnels** : le suffix `.PROPOSED` a été retiré, ils tournent au même titre que les 17 autres. **Aucun skill `.PROPOSED` n'est en attente de validation au 16 mai 2026.** La procédure `.PROPOSED` → `.md` reste documentée car la méta-revue dominicale peut en générer de nouveaux dans les semaines à venir.

---

## 12. Sécurité & garde-fous techniques

Hermès est **autonome mais pas libre**. Plusieurs garde-fous bloquent les comportements dangereux ou non désirés, indépendamment de ce que vous lui demandez.

### Le flag central `AZAMOUL_MODE`

Dans `/root/.hermes/.env`, une variable contrôle tout :

- `AZAMOUL_MODE=test` (état actuel) → toutes les mutations sont **éphémères** (apply + rollback dans le même run). Tous les emails sont redirigés vers `contact.azamoul@gmail.com`. L'Instagram reste en mode `dry` (génère payload sans publier). **Impossible de faire un dégât persistant en mode test.**
- `AZAMOUL_MODE=prod` → les mutations sont persistantes, les emails partent à la liste cliente, Instagram active l'approval gate (preview puis `/yes_insta`).

**Bascule** : changement d'une ligne dans `.env`. **Rollback** : changement inverse. Pas de redémarrage requis.

### Le schema-guard (anti-hallucination GraphQL)

Hermès consultait des fragments GraphQL Shopify avant chaque mutation. Le skill `azamoul-shopify-schema-guard` contient **uniquement des mutations validées par introspection du schéma Shopify réel**. Cela empêche Hermès d'inventer une syntaxe (ex. il avait halluciné `productUpdate(input: {media: [...]})` pour modifier les alt-text — corrigé en `fileUpdate(files: [{id, alt}])` après introspection).

### Vocabulaire amazigh obligatoire

Liste de 21 mots culturels dans `MEMORY.md` (amazigh, berbère, tifinagh, imazighen, yaz ⵣ, azamoul, kabyle, djurdjura, thilelli, dihya, aza, afzim, tiseghnest, tafaska, tamghra, asseggas, amegaz, tafsut, tamejja, lawan, tameddurt). Hermès doit en mobiliser **≥10 mots distincts par campagne**, avec **max 3 répétitions par mot** (anti-padding). Vérifié pendant le Grand Run B3 : 13 mots distincts utilisés, 0 padding.

### L'approval gate Instagram (skill v2.0.0)

Même en `AZAMOUL_MODE=prod`, Hermès **n'a pas le droit** de publier directement sur Instagram. Il :
1. Crée le container Meta via Graph API
2. Envoie le preview par email + Telegram avec `container_id`
3. **Attend votre réponse `/yes_insta <container_id>` (publier) ou `/no_insta <container_id>` (annuler)**
4. Publie SEULEMENT après votre OK explicite

Vous gardez ainsi le contrôle absolu sur chaque post Instagram, même quand Hermès est en pleine autonomie.

### La règle `EMAIL_SMTP_OK`

Avant de prétendre avoir envoyé un email, Hermès doit imprimer en stdout la chaîne exacte `EMAIL_SMTP_OK`. Si elle n'apparaît pas, Hermès doit écrire dans son rapport : `Email NON envoyé (cause : <message exact>)`. Cela empêche de prétendre faussement qu'un email a été envoyé alors qu'il a échoué silencieusement.

### Le snapshot-diff-validator

Skill activé le 14 mai 2026. À chaque batch en mode test, Hermès doit :
1. Snapshot BEFORE
2. Apply mutation
3. Snapshot AFTER-APPLY
4. Rollback
5. Snapshot AFTER-ROLLBACK
6. **Comparer BEFORE vs AFTER-ROLLBACK → doit être VIDE**

Si la comparaison montre une différence (un résidu non rollback), le test FAIL automatiquement. Garantie zéro mutation persistante en mode test.

### Hooks de logging

Deux hooks tournent en arrière-plan :
- `log-learning.sh` : à chaque appel de tool, log l'action dans `learnings.md`
- `inject-standing.sh` : à chaque démarrage de session, injecte les 14 règles immuables (`STANDING.md`) dans le contexte de Hermès

Cela rend l'agent **observable** (chaque action laisse une trace) et **discipliné** (les règles sont rappelées à chaque session).

---

## 13. État actuel du projet (mai 2026)

### Ce qui est fait

✅ **Toutes les phases test sont terminées** (Phase 0 → Phase 4) — 4 mois de travail concentrés en quelques semaines.

✅ **Grand Run Test passé** le 14 mai 2026 — 9/9 critères globaux PASS, 12 signaux d'autonomie observés, 0 hallucination, 0 mutation persistante en test. Verdict : **✅ GO Phase Production**.

✅ **21 skills atomiques actifs** (les 17 historiques + 4 validés et chargés le 14 mai 2026 après détection autonome par méta-revue — aucun `.PROPOSED` en attente au 16 mai 2026).

✅ **Architecture portable LLM** validée : swap Copilot Gemini ↔ DeepSeek v4 Pro effectué en cours de Grand Run sans perte d'autonomie, puis stabilisation prod sur **Gemini 3.1 Flash Lite Preview via OpenRouter**. Hermès n'est plus dépendant d'un fournisseur unique.

✅ **4 crons opérationnels** : lundi-perf 9h, samedi-ideas 10h, dimanche-meta 20h, watchdog */6h.

✅ **Documentation complète** : ce guide, `MISSION-HERMES.md`, `HERMES-VPS-SPEC.md`, `HERMES-PROJECT-OVERVIEW.md`, `RAPPORT-PHASE-4.md`, `GRAND-RUN-RESULTS.md`, `PHASE-PRODUCTION-CHECKLIST.md`.

### Ce qui reste (décisions tuteur, toutes optionnelles)

| Action | Effet si fait | Effet si pas fait |
|--------|---------------|-------------------|
| Régénérer les 3 clés sensibles | Sécurité long terme | Risque accepté tant qu'on est en test |
| Activer scope Shopify `write_online_store_navigation` | Hermès peut créer/supprimer des redirects 301 (utile au renommage de handle) | Hermès évite les renommages de handle (perte SEO mineure) |
| Configurer Instagram Graph API | Hermès peut publier des posts via approval gate | Mode `dry` : Hermès génère le payload mais ne publie pas |
| Basculer `AZAMOUL_MODE=test` → `prod` | Hermès opère en réel (vraies mutations, vrais envois clients) | Reste en mode test exclusif (zero risque) |

**Aucune de ces décisions n'est bloquante.** Hermès peut tourner en mode test indéfiniment (les 4 crons s'exécutent, les rapports arrivent, les KPI sont suivis). La bascule prod active simplement les actions sur le monde réel.

### Métriques actuelles

- **Score qualité catalogue** : 64% (cible 100% en 4 semaines avec actions automatisées)
- **Catalogue** : ~96 produits actifs, 4 archives, 19 collections, 11 pages
- **CA 30j** : 83.74 EUR (2 commandes, AOV 41.87 EUR) — données réelles Shopify GraphQL
- **Instagram** : @azamoul, 5 769 followers, engagement 68 likes / 6.3 commentaires
- **Bloqueurs métiers** (hors scope Hermès) : 33 produits < 3 images (génération images auto indisponible), 44 produits en rupture stock (décision business)

---

## 14. Piloter Hermès au quotidien (cheat-sheet)

### Semaine type d'un employé Azamoul

**Lundi matin (9h)**
1. Telegram vibre : rapport perf de la semaine arrivé
2. Lecture en 30 sec : CA, conversion, top wins/pertes
3. 3-5 clics : valider les actions 🟡 proposées par `/yes`
4. Email parallèle : rapport détaillé dans la boîte si besoin de creuser

**Samedi matin (10h)**
1. Email "Idées de la semaine" arrivé dans `contact.azamoul@gmail.com`
2. Lecture en 2 min : proposition produit + proposition Instagram
3. Décision business :
   - Idée produit intéressante ? Notifier l'équipe production
   - Idée Instagram bonne ? Valider via Telegram (Hermès attend `/yes` pour préparer le post, puis `/yes_insta` pour publier)

**Dimanche soir (20h)**
1. Telegram : méta-revue de la semaine (15 lignes max)
2. Lecture rapide : Hermès a-t-il proposé un nouveau skill `.PROPOSED` ?
3. Si oui : ouvrir `/root/.hermes/skills/azamoul-<nom>/SKILL.md.PROPOSED`, lire, valider en renommant `.PROPOSED` → activation

**Au quotidien**
- Question business → écrire à Hermès sur Telegram en français normal
- Watchdog silencieux la plupart du temps, sauf alerte critique

### Commandes type que vous pouvez utiliser

| Pour… | Sur Telegram, vous écrivez |
|-------|----------------------------|
| Connaître l'état actuel boutique | « Hermès, donne-moi en 3 lignes l'état boutique aujourd'hui » |
| Auditer un produit spécifique | « Hermès, audite le produit `t-shirt-yaz-femme` et propose 3 améliorations » |
| Préparer une campagne culturelle | « Hermès, prépare une campagne complète pour la fête de Tafsut » |
| Investiguer un KPI suspect | « Hermès, pourquoi le bonnet Aza est à 89% d'abandon panier ? » |
| Forcer un rapport hors planning | (via tuteur : `hermes cron run 9b3edc604e0d --accept-hooks`) |
| Mettre Hermès en vacances | (via tuteur : `hermes cron pause --all`) |
| Réactiver Hermès | (via tuteur : `hermes cron resume --all`) |

### Surveillance hebdomadaire (1er mois prod)

Si vous basculez en mode prod, vérifier chaque semaine :
- [ ] Rapport lundi reçu avec KPI réels (pas « donnée non disponible »)
- [ ] Email samedi reçu avec idées créatives
- [ ] Méta-revue dimanche reçue ≤15 lignes
- [ ] Aucun email/Telegram suspect non prévu
- [ ] Spot-check 2-3 produits dans Shopify Admin (aucune mutation imprévue)

Si KPI drop > 30% → alerte Telegram watchdog → investigation manuelle requise.

---

## 14.5 Faire évoluer Hermès

Hermès n'est pas figé : on peut lui ajouter de nouvelles compétences, valider celles qu'il propose tout seul, ou faire évoluer ses crons. Voici les trois opérations les plus fréquentes.

### 14.5.1 Ajouter un nouveau skill manuellement

Les skills vivent dans `/root/.hermes/skills/`. Pour en créer un nouveau, créer un dossier `/root/.hermes/skills/azamoul-<nom>/` puis un fichier `SKILL.md` à l'intérieur. Le format est strict :

```markdown
---
name: azamoul-<nom>
description: <une phrase qui dit quand utiliser ce skill>
metadata:
  hermes:
    tags: [azamoul, <catégorie>]
---

## When to Use
...

## Procedure
...

## Pitfalls
...

## Verification
...
```

Le skill est **chargé dynamiquement** au prochain démarrage de session Hermes — pas besoin de redémarrer le gateway. Pour tester immédiatement, il suffit de relancer un cron (`hermes cron run <id> --accept-hooks`).

**Test de présence** : `hermes chat -q "Liste les skills azamoul disponibles"` doit faire apparaître le nouveau skill dans sa réponse.

### 14.5.2 Valider un skill `.PROPOSED` créé par méta-revue

La méta-revue dominicale (cron `8450eef5fde8`) peut générer un fichier `SKILL.md.PROPOSED` dans `/root/.hermes/skills/azamoul-<nom>/` quand elle détecte qu'un même motif d'action revient ≥ 3 fois en 4 semaines. **Tant qu'il garde l'extension `.PROPOSED`, Hermes ne le charge pas** — c'est le filet de sécurité contre l'auto-modification non supervisée.

Procédure de validation :

1. Lire le contenu : `cat /root/.hermes/skills/azamoul-<nom>/SKILL.md.PROPOSED`
2. Si OK : `mv /root/.hermes/skills/azamoul-<nom>/SKILL.md.PROPOSED /root/.hermes/skills/azamoul-<nom>/SKILL.md`
3. Au prochain cron Hermes, le skill est actif.

Si pas OK : supprimer le fichier (`rm .../SKILL.md.PROPOSED`) ou éditer avant de renommer.

**État au 16 mai 2026** : 0 skill `.PROPOSED` en attente. Les 4 derniers (`azamoul-seo-mutation-batcher`, `azamoul-storefront-http-verifier`, `azamoul-snapshot-diff-validator`, `azamoul-cron-output-watcher`) ont été validés post-Grand Run et sont aujourd'hui actifs.

### 14.5.3 Créer ou modifier un cron

```bash
# Créer un nouveau cron Hermes
hermes cron create \
  --name azamoul-mon-nouveau-cron \
  --schedule "0 14 * * 5" \
  --prompt "Tu es Hermès, exécute X..." \
  --skill azamoul-<skill-utilisé> \
  --workdir /root/azamoul-shopify

# Modifier un cron existant (édite jobs.json interactivement)
hermes cron edit <id>

# Supprimer un cron
hermes cron delete <id>
```

Le fichier source est `/root/.hermes/cron/jobs.json`. Toujours **tester avec `hermes cron run <id> --accept-hooks`** avant le 1er déclenchement automatique — vérifier que la sortie dans `/root/.hermes/cron/output/<id>/` est conforme et que le résumé Telegram arrive bien.

---

## 14.6 Coûts récurrents et budget

Hermès tourne avec un budget volontairement modeste. Voici les postes mensuels :

| Poste | Coût estimé | Comment surveiller |
|---|---|---|
| **VPS OVH** (`<VPS_HOSTNAME>`, Ubuntu 24.04) | ~5 €/mois (engagement annuel) | Facture OVH sur `manager.ovh.com` |
| **OpenRouter** (LLM principal Gemini 3.1 Flash Lite Preview) | 0-10 €/mois selon volume | Dashboard `openrouter.ai/credits` — facturation au token |
| **GitHub Copilot** (LLM fallback Gemini 3.1 Pro Preview) | inclus dans abonnement Copilot personnel | Quota hebdo 30-35 prompts / 5 h |
| **OpenAI** (text + vision fallback rare) | 0-5 €/mois | `platform.openai.com/usage` |
| **Gmail SMTP** (envoi rapports lundi + email samedi) | gratuit | Quota 500 emails/jour (Hermes en envoie 3-4/semaine, OK) |
| **Firecrawl** (veille concurrentielle, free tier) | gratuit | Dashboard `firecrawl.dev` |
| **Domaine azamoul.com** | ~15 €/an | Facturation Shopify ou registrar |

**Total mensuel estimé : 8-20 €/mois** selon usage LLM.

**Surveillance** : se créer un agenda mensuel pour relever les factures, et surveiller le dashboard OpenRouter chaque semaine (c'est le seul poste réellement variable — un cron qui boucle ou un Grand Run peut faire bondir la consommation d'un jour sur l'autre). Si OpenRouter dépasse 10 €/mois, c'est qu'il y a un comportement anormal à investiguer (cron qui retry en boucle, prompt qui balaye l'historique complet, etc.).

---

## 14.7 Sauvegardes et disaster recovery

Le VPS OVH a un uptime correct mais rien ne remplace une sauvegarde régulière. Voici quoi sauvegarder, à quelle fréquence, et comment restaurer.

### Que sauvegarder

- **`/root/.hermes/`** (sauf logs lourds) — environ 50 Mo. Contient skills, `config.yaml`, `cron/jobs.json`, `state.db` (SQLite + WAL + SHM), `memories/MEMORY.md`, `standing/STANDING.md`, `sessions/`.
- **`/root/azamoul-shopify/`** — environ 20 Mo. Contient `MISSION-HERMES.md`, `learnings.md`, `brand-knowledge.md`, `baseline-kpi-30j.md`, `reports/`, `meta-reviews/`, `audits/`, `batches/`, `campaigns/`, `tests/`, `shopify-automation-toolkit/`.
- **`/opt/openviking/`** n'a pas besoin de backup régulier (le binaire est réinstallable), mais sauvegarder la base de données vectorielle si elle existe sur disque.

### À quelle fréquence

- **Hebdomadaire** : backup complet via `hermes backup --output /root/backups/hermes-YYYY-MM-DD.tar.gz`
- **Quotidien** : backup de `learnings.md` seul (append-only) via un cron simple — c'est le fichier le plus précieux du projet (journal complet des actions Hermès depuis Phase 0).
- **Avant chaque bascule prod** : backup complet du catalogue Shopify via `shopify store export --query-file products.graphql > backup-catalog-YYYY-MM-DD.json`

### Où stocker

- Localement sur le VPS dans `/root/backups/`
- **Recommandé** : copier vers un stockage externe (Google Drive du tuteur, S3, rclone vers un cloud) via cron quotidien. Une sauvegarde qui reste sur le serveur défaillant ne sert à rien.

### Restaurer

```bash
# Restaurer une archive Hermes complète
hermes import /root/backups/hermes-YYYY-MM-DD.tar.gz

# Restaurer le catalogue Shopify (manuel via Shopify CLI ou Admin)
# Le JSON exporté contient l'état exact des produits — comparable diff par diff
```

Après restauration, toujours relancer `hermes cron list` pour vérifier que les 4 crons (IDs `9b3edc604e0d`, `7936943cee39`, `8450eef5fde8`, `dd4a59c29a88`) sont bien en état `scheduled` et `enabled: true`.

---

## 14.8 Continuité du projet et escalade

Le stage de Rayan Djebar se termine le **13 juin 2026**. Voici les contacts et ressources pour que le projet continue à tourner ensuite.

### Contacts d'urgence

- **Rayan Djebar (développeur initial)** : `djebar.rayan75@gmail.com` — disponible pour questions techniques au-delà de la fin de stage (13 juin 2026)
- **Lyes Ameddah (président Azamoul)** : `contact.azamoul@gmail.com` — décideur business
- **Senouci Dinar (enseignant référent IUT Paul Sabatier)** : pour escalade pédagogique uniquement

### Ressources externes

- **Hermes Agent (framework, open source)** : `https://github.com/NousResearch/hermes-agent` — issues, releases, docs upstream
- **OpenViking** : `https://github.com/openviking/openviking` — serveur de mémoire vectorielle
- **OpenRouter support** : `support@openrouter.ai` — pour problèmes de facturation ou panne LLM
- **Shopify Partner Dashboard** : pour gérer l'app custom et ses scopes (notamment activer `write_online_store_navigation` quand on voudra autoriser les redirects 301)
- **OVH Manager** : `manager.ovh.com` — pour rebooter le VPS, ouvrir un ticket support

### Archive des décisions

Toutes les décisions architecturales structurantes (choix Hermes Agent, swap LLM Copilot → DeepSeek → Gemini Flash Lite, modèle d'autonomie sous-prompts orchestrés au lieu de mega-prompt) sont tracées dans :

- `RAPPORT-PHASE-4.md` (décisions Phase 4 : sous-prompts, anti-hallucination, retest v2)
- `GRAND-RUN-RESULTS.md` (décisions Grand Run du 14 mai 2026 : verdict GO Phase Production)
- `/root/azamoul-shopify/learnings.md` (journal append-only des actions, alimenté par le hook `log-learning.sh`)

En cas de doute sur « pourquoi a-t-on fait ça ? », commencer par lire ces 3 fichiers. Ils contiennent les arbitrages et leur justification — pas seulement les conclusions.

---

## 15. Mini-glossaire e-commerce

| Terme | Définition simple |
|---|---|
| **Boutique Shopify** | Site de vente en ligne hébergé chez Shopify (l'éditeur) |
| **Catalogue** | L'ensemble des produits que vous vendez (~ 96 chez Azamoul) |
| **Collection** | Regroupement thématique de produits (ex: *Made in France*, *Symboles*) |
| **Conversion** | Le fait qu'un visiteur achète vraiment (= passe à la caisse) |
| **CA / Chiffre d'affaires** | Somme totale des ventes en euros |
| **Panier abandonné** | Un visiteur ajoute au panier, met son email, mais ne paie pas |
| **AOV / Panier moyen** | Montant moyen d'une commande |
| **Meta title / meta description** | Le titre et le texte qui apparaissent dans les résultats Google |
| **Alt text** | Texte alternatif d'une image (lu par Google et les lecteurs d'écran) |
| **Handle / URL** | L'adresse d'un produit (ex: `t-shirt-yaz-femme`) |
| **Tag** | Étiquette posée sur un produit pour le retrouver dans une collection |
| **SEO** | Tout ce qui aide Google à bien classer la boutique dans ses résultats |
| **Redirect 301** | Redirection permanente d'une ancienne URL vers une nouvelle (préserve le SEO) |
| **Shopify Email** | L'outil natif de Shopify pour envoyer des emails aux clients |
| **GSC / Google Search Console** | Outil Google qui montre les requêtes des internautes |
| **GraphQL Admin API** | L'interface de programmation utilisée par Hermès pour lire et modifier Shopify |

---

## 16. Mini-glossaire IA

| Terme | Définition simple |
|---|---|
| **LLM** (*Large Language Model*) | Le « cerveau » d'Hermès — un modèle IA qui sait lire, écrire et raisonner sur du texte. Exemples : ChatGPT, Claude, DeepSeek, Gemini |
| **Gemini 3.1 Flash Lite Preview** | Le LLM actuellement actif sur Hermès (depuis stabilisation post-Grand Run), accédé via OpenRouter — contexte 256 k, latence faible, coût très faible |
| **DeepSeek v4 Pro** | LLM testé pendant le Grand Run du 14 mai 2026 (preuve de portabilité du swap OpenRouter), pas le modèle de prod actuel |
| **OpenRouter** | Place de marché qui route les requêtes vers Gemini Flash Lite, DeepSeek et autres LLM, facturation au token |
| **Gemini 3.1 Pro Preview** | LLM testé via GitHub Copilot pendant les premières phases, conservé comme fallback secondaire |
| **GitHub Copilot** | Endpoint OpenAI-compatible donnant accès à Gemini ; pay-as-you-go ; rate-limit hebdomadaire ~30-35 prompts |
| **LLM swap** | Capacité de basculer entre fournisseurs (Gemini Flash Lite ↔ DeepSeek ↔ Copilot ↔ OpenAI) via `config.yaml` en ~5 min |
| **Embedding** | Une "empreinte numérique" d'un texte qui permet de retrouver des choses similaires |
| **Agent autonome** | Programme qui sait planifier, exécuter et corriger seul ses actions (vs un script qui exécute bêtement) |
| **Prompt** | Une instruction donnée à l'IA en langage naturel |
| **Cron** | Tâche programmée qui se déclenche automatiquement à une heure précise |
| **Hook** | Petit programme qui se déclenche automatiquement à un événement (par exemple à la fin d'une action) |
| **Skill** | Module spécialisé d'Hermès qui sait faire une chose précise (ex: générer une idée Instagram). Azamoul en a 21 actifs. |
| **OpenViking** | La mémoire long terme d'Hermès — il s'en sert pour se souvenir d'une semaine sur l'autre |
| **VPS** | Le petit serveur loué 24h/24 où Hermès tourne (Ubuntu 24.04 chez OVH) |
| **Telegram** | L'app de messagerie utilisée pour discuter avec Hermès depuis votre téléphone |
| **Approval gate** | Mécanisme qui bloque une action sensible (ex: post Instagram) jusqu'à validation explicite tuteur |
| **Hallucination** | Quand un LLM invente une information plausible mais fausse — Hermès a des garde-fous pour éviter ça |
| **`.PROPOSED` (suffix)** | Marque un skill créé autonomement par Hermès en attente de validation tuteur avant chargement |

---

## 17. Pour aller plus loin

Si vous voulez voir Hermès en action :

- **Lui poser une question** : ouvrez Telegram, écrivez à votre bot Hermès « Hermès, donne-moi en 3 lignes l'état de la boutique aujourd'hui. »
- **Lire un rapport** : tous les rapports sont sauvegardés dans `/root/azamoul-shopify/reports/YYYY-Www-perf.md` sur le serveur.
- **Vérifier qu'il tourne** : sur votre téléphone, demandez sur Telegram « Hermès, status ? » — il vous répondra en quelques secondes.
- **Consulter ses apprentissages** : `/root/azamoul-shopify/learnings.md` contient le journal de bord chronologique de Hermès depuis Phase 0.
- **Explorer ses skills** : `ls /root/.hermes/skills/azamoul-*/SKILL.md` liste les 21 skills actifs. Chaque `SKILL.md` est lisible (markdown + frontmatter YAML).
- **Suivre ses sessions** : `/root/.hermes/sessions/` contient les transcripts JSON de chaque conversation. Utile pour diagnostiquer un comportement.

### Documents complémentaires (dans ce dossier)

- `MISSION-HERMES.md` — Charte technique de la mission Hermès (à jour Phase 4)
- `HERMES-VPS-SPEC.md` — Spec technique infra (45 env vars, arborescence, cron config)
- `HERMES-PROJECT-OVERVIEW.md` — Vue narrative du projet
- `RAPPORT-PHASE-4.md` — Rapport complet Phase 4 v2
- `GRAND-RUN-RESULTS.md` — Synthèse du Grand Run Test final (GO Phase Production)
- `PHASE-PRODUCTION-CHECKLIST.md` — Procédure de bascule vers `AZAMOUL_MODE=prod`

---

*Document mis à jour le 16 mai 2026 par Rayan Djebar (stagiaire BUT2 Informatique à l'IUT Paul Sabatier), après lecture SSH directe du VPS (snapshot `VPS_SNAPSHOT_2026-05-16.md`), dans le cadre du stage chez Azamoul.*

*Pour toute question technique : `djebar.rayan75@gmail.com`.*
