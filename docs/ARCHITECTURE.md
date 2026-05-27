# Hermes — Charter Framework (Architecture)

> Charter générique du framework Hermes. Cette doc décrit le **pattern** de fonctionnement de l'agent. Chaque marchand le personnalise via `$HERMES_WORKSPACE/MISSION.md` qui est son instance concrète.
>
> La version Azamoul complète de ce charter est disponible dans [`../examples/azamoul/MISSION.md`](../examples/azamoul/MISSION.md).

---

## 1. Mission d'un agent Hermes

Un agent Hermes est responsable de la **croissance commerciale autonome** d'une boutique Shopify. Sans plafond. Il optimise en continu :
- **SEO** : meta titles, descriptions, alt-texts, internal linking, performance GSC
- **Contenu** : descriptions produit, blogs, pages
- **Images** : génération, audit visuel, alt-texts
- **UX** : analyse conversion, frictions, A/B test propositions
- **Emailing** : drafts Klaviyo, segments, séquences
- **Posts Instagram** : idéation, drafts, calendrier
- **Code du thème Liquid** : modifications sections/snippets/templates via Theme Access

Il propose des **idées créatives chaque semaine** (1 nouveau produit + 1 post Instagram + 1 draft campagne email).

---

## 2. Sources surveillées (chaque cycle)

Avant toute action, Hermes lit OBLIGATOIREMENT :

1. **`$HERMES_WORKSPACE/MISSION.md`** — son charter spécifique à la boutique
2. **`$HERMES_WORKSPACE/MEMORY.md`** — phase courante + faits permanents
3. **`/root/.hermes/standing/STANDING-CORE.md`** + **`$HERMES_WORKSPACE/STORE-BRAND.md`** — règles immuables (14 au total)
4. **Les 7 dernières entrées de `$HERMES_WORKSPACE/learnings.md`** — apprentissages récents

Cette pré-lecture est encodée dans le hook `inject-standing.sh` (s'exécute à chaque `on_session_start`).

---

## 3. Niveaux d'autonomie

| Niveau | Description | Exemples génériques |
|---|---|---|
| 🟢 **Auto-exécution** | Hermes applique sans demander validation | Génération alt-texts manquants, normalisation handles ASCII, ajout de tags catégoriels, insertion bloc 📦 livraison au début des descriptions, drafts (non publiés) |
| 🟡 **Propose en 1-clic** | Hermes prépare la mutation + envoie pour validation Telegram `/yes` | Enrichissement de descriptions, génération d'images, redirects, création de collections, ajustement prix raisonnable (<5%), post Instagram (toujours en mode dry pendant phase test), modif de sections du thème |
| 🔴 **Jamais sans validation explicite** | Hermes refuse même sur demande directe | Modifier le prix de >5%, supprimer un produit/page/client, refunds, modification du layout du thème, post Instagram en direct, modifications légales, `config/settings_data.json` |

Le marchand CUSTOMISE ces niveaux dans `STORE-BRAND.md`. Le pattern reste identique, les actions concrètes varient selon la marque.

---

## 4. Rythme opérationnel

| Quand | Action | Skills | Output |
|---|---|---|---|
| Lundi 9h | Rapport perf hebdo | `shopify-weekly-perf-report` + KPI + diagnostic + Klaviyo | `reports/YYYY-Www-perf.md` |
| Mardi-Vendredi | Hermes dort | — | (sauf intervention manuelle via `hermes chat`) |
| Samedi 10h | Email créatif hebdo | `shopify-instagram-ideator` + `shopify-product-ideator` + `shopify-cultural-calendar` + `shopify-klaviyo-campaign-ideator` | `reports/YYYY-Www-ideas.md` |
| Dimanche 20h | Méta-revue auto-amélioration | `shopify-weekly-perf-report` + `shopify-cultural-calendar` | `meta-reviews/YYYY-Www-meta.md` (+ éventuellement nouveau skill créé) |
| Toutes les 6h | Watchdog conversion | script `<store>-watchdog-conversion.sh` + `shopify-klaviyo-drop-watchdog` | Silent (sauf alerte Telegram) |

---

## 5. Auto-amélioration — 5 mécaniques

### 5.1. Memory OpenViking (port 1933)

Service local d'embedding qui sert de RAG cross-session. Chaque fichier `MEMORY*.md` + `learnings.md` est indexé, et lors d'une nouvelle session Hermes peut récupérer du contexte pertinent.

Limites typiques :
- `memory_char_limit: 3500` (tokens injectés en début de session)
- `user_char_limit: 1375` (profil utilisateur)

### 5.2. Curator background

Mécanique de nettoyage : Hermes vérifie régulièrement la mémoire courante et compacte ou archive les entrées obsolètes pour éviter l'inflation.

### 5.3. Création automatique de skills

Dans le cron méta-revue dominicale, Hermes :
1. Lit `learnings.md` des 7 derniers jours
2. Identifie 3 patterns : ce qui a marché / ce qui a échoué / ce qui mérite un skill
3. **Si pattern récurrent > 3 occurrences sur 4 semaines** → crée automatiquement un nouveau SKILL.md dans `/root/.hermes/skills/<store>-<nom>/SKILL.md`
4. Notifie le marchand via Telegram

Format auto-généré complet : frontmatter YAML + When to Use + Procedure + Pitfalls + Verification.

### 5.4. `hermes insights --days 7`

Commande qui analyse les sessions des 7 derniers jours et affiche :
- Sessions totales (par platform : cron / cli / telegram)
- Messages échangés
- Tool calls
- Tokens consommés (input + output)
- Active time
- Top tools utilisés
- Top skills loaded

Utile pour détecter les dérives (cron qui consomme anormalement, modèle qui coûte trop, etc.).

### 5.5. Hook `post_tool_call` (log-learning.sh)

Chaque action mutative (productUpdate, collectionCreate, fileUpdate, theme push, email send, ...) déclenche automatiquement l'ajout d'une entrée dans `learnings.md` avec :
- Timestamp UTC
- Tool name + input (tronqué à 400 chars)
- 4 placeholders à compléter (avant / après / conclusion / futur)

Les placeholders sont remplis en méta-revue (W+1) pour mesurer l'impact KPI.

---

## 6. Anti-hallucination (règles dures)

1. **TOUS les chiffres** (KPI, prix, dates, comptes produits, followers, etc.) DOIVENT provenir de sources réelles vérifiables :
   - Shopify GraphQL Admin API via `shopify store execute --query-file ...`
   - Fichiers existants sur le VPS (baseline-kpi-30j.md, audits/, brand-knowledge.md, learnings.md)
   - APIs testées (Instagram via web_profile_info, Klaviyo via klaviyo-fetch.sh, ...)
2. **INTERDICTION ABSOLUE** d'inventer, estimer, ou extrapoler des chiffres. Si une donnée n'est pas disponible, écrire exactement `(donnée non disponible)` ou `(N/A - pas de data)`.
3. **Format date strict** : `datetime.date.today().isoformat()` (YYYY-MM-DD), `isocalendar()` pour year/week. JAMAIS de date inventée.
4. Si les données Shopify sont vides ou incohérentes (ex: 0 commandes sur 30j), **MENTIONNER explicitement** dans le rapport plutôt que combler avec des estimations.
5. **Citer les sources** : chaque KPI ou affirmation doit pointer vers son origine (ex: `source: baseline-kpi-30j.md ligne X`).

---

## 7. Email — procédure obligatoire

Le delivery email du cron Hermes est désactivé (telegram only). L'agent DOIT envoyer l'email lui-même via un snippet Python inline avec la sentinelle `EMAIL_SMTP_OK`.

```python
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

env = {}
for l in open('/root/.hermes/.env'):
    l = l.strip()
    if l and not l.startswith('#') and '=' in l:
        k, v = l.split('=', 1)
        env[k] = v.strip()

body = """<corps de ton email>"""
msg = MIMEText(body, 'plain', 'utf-8')
msg['Subject'] = '<sujet contextuel>'
msg['From'] = env['EMAIL_FROM']
msg['To'] = env['EMAIL_TO']
msg['Date'] = formatdate(localtime=True)
msg['Message-ID'] = make_msgid(domain='gmail.com')

with smtplib.SMTP(env['EMAIL_SMTP_HOST'], int(env['EMAIL_SMTP_PORT']), timeout=15) as s:
    s.ehlo(); s.starttls(); s.ehlo()
    s.login(env['EMAIL_SMTP_USER'], env['EMAIL_SMTP_PASSWORD'])
    s.send_message(msg)
print('EMAIL_SMTP_OK')
```

**Règle critique** : si la sentinelle `EMAIL_SMTP_OK` n'apparaît pas en stdout, l'email N'A PAS été envoyé. L'agent doit alors écrire `Email NON envoyé (cause: <message exact>)` dans son résumé Telegram. Mentir sur l'envoi = violation grave anti-hallucination.

---

## 8. Pattern de validation Telegram `/yes`

Pour les actions niveau 🟡, Hermes attend une validation explicite :

```
1. Hermes prépare la mutation (preview JSON + script rollback)
2. Envoie Telegram + email au tuteur : "Voici ce que je veux faire. /yes pour appliquer, /no pour annuler, /edit pour ajuster"
3. Pause de l'exécution (timeout 10 min standard)
4. Réception :
   - /yes → applique séquentiellement (espacement 2s anti rate-limit Shopify)
   - /no → annule, conserve preview pour retry futur
   - /edit <handle> <details> → ajuste, regénère preview, redemande validation
   - timeout → abandon + alerte
```

---

## 9. Phase courante : `HERMES_MODE`

| Mode | Comportement |
|---|---|
| `HERMES_MODE=test` (défaut) | Toute mutation Shopify est apply + rollback dans le même run (éphémère). Snapshots avant/intermédiaire/après mailés au tuteur. Aucun impact persistant. |
| `HERMES_MODE=prod` | Mutation persistante après /yes Telegram obligatoire. Script rollback disponible mais non auto-exécuté. |

Toute variable absente ou autre valeur → **comportement test par défaut (sécurité)**.

La bascule en prod est une **décision marchand** après validation des bons comportements en phase test. Voir [`PRODUCTION-CHECKLIST.md`](./PRODUCTION-CHECKLIST.md).

---

## 10. Customisation par boutique

Le framework définit le **squelette**. Chaque marchand customise dans son workspace :

| Fichier | Quoi y mettre |
|---|---|
| `MISSION.md` | Mission narrative de l'agent pour TA boutique (univers de marque, USP, objectifs) |
| `STORE-BRAND.md` | Vocabulaire obligatoire, niveaux 🟢/🟡/🔴, sensibilités |
| `brand-knowledge.md` | Concurrents (5-10), positionnement |
| `cultural-events.json` | Événements/saisons importants pour ta marque (Noël, BFCM, lancements, événements culturels...) |
| `MEMORY.md` | Faits permanents (plan Shopify, devise, fuseau, catégories produits, comptes IG/Klaviyo) |

Voir [`../examples/azamoul/`](../examples/azamoul/) pour un exemple complet d'instance configurée sur une vraie boutique.

---

## 11. Skills graph

Dépendances entre skills (à connaître pour le bon ordering des cycles) :

```
shopify-batch-executor ──→ hermes-schema-guard (dependency obligatoire)
shopify-seo-mutation-batcher ──→ hermes-schema-guard
shopify-cultural-campaign-drafter ──→ shopify-cultural-calendar
shopify-klaviyo-campaign-ideator ──→ shopify-cultural-calendar
shopify-altext-generator ──→ shopify-catalog-gap-analyzer (workflow)
shopify-description-enricher ──→ shopify-catalog-gap-analyzer (workflow)
shopify-metatitle-generator ──→ shopify-catalog-gap-analyzer (workflow)
```

Le skill `hermes-schema-guard` est **central** : tout skill qui mute Shopify doit le charger AVANT d'écrire les requêtes GraphQL pour ne pas inventer de champs.

---

## 12. Verification (par run)

Checklist standard de fin d'exécution :

- [ ] Lecture obligatoire effectuée (MISSION + MEMORY + STANDING + 7 derniers learnings)
- [ ] Niveau d'autonomie respecté (🟢 direct / 🟡 /yes obligatoire / 🔴 refus)
- [ ] Si mutation : backup avant + verify après
- [ ] Si email : `EMAIL_SMTP_OK` en stdout vérifié
- [ ] Si Telegram : message reçu par le chat autorisé
- [ ] Entrée loggée dans `learnings.md` (avec timestamp UTC + tool + 4 placeholders)
- [ ] Aucune valeur KPI inventée (toutes citées avec source)

---

## 13. Évolutions du framework

Le framework évolue par 2 mécanismes :

1. **Manuel** (humain) — ajouts de skills, refactor de helpers, mise à jour de docs via PR sur le repo
2. **Auto** (méta-revue dimanche) — création d'un nouveau skill dès qu'un pattern récurrent est détecté

Quand un nouveau skill auto-généré est validé par le marchand, il est versionné `v1.0.0` et peut être contribué upstream via PR.
