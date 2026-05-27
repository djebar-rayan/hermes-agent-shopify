# STORE-BRAND.md — Azamoul (cas d'étude)

> Exemple complet de `STORE-BRAND.md` rempli pour Azamoul, marque française qui valorise la culture amazighe (berbère).
> Voir [`../../config/STORE-BRAND.md.template`](../../config/STORE-BRAND.md.template) pour le template vierge.

---

## Identité boutique

| Champ | Valeur |
|---|---|
| Nom marque | Azamoul |
| Domaine | azamoul.com |
| URL Shopify | azamoul-symboles-berberes.myshopify.com |
| Email contact | contact.azamoul@gmail.com |
| Plan Shopify | Basic |
| Devise | EUR |
| Fuseau | Europe/Paris |
| Catalogue | ~96 produits, 19 collections, 11 pages |
| Domaine métier | Mode, bijoux, déco, accessoires culture amazighe/berbère/kabyle |

---

## Règle 6 — Vocabulaire de marque obligatoire

Liste de mots-clés qui DOIVENT apparaître dans tout contenu généré (descriptions, alt-texts, captions, emails). Hermes refuse de publier du contenu sans au moins 1-2 de ces termes.

### Vocabulaire culturel obligatoire (~20 mots)

```
amazigh, berbère, tifinagh, imazighen, yaz (ⵣ), azamoul, kabyle, djurdjura,
thilelli, dihya, aza, afzim, tiseghnest, tafaska, tamghra, asseggas, amegaz,
tafsut, tamejja, lawan, tameddurt
```

### Interprétation

- **amazigh / imazighen** : nom du peuple (préférer à "berbère" qui peut être considéré dépréciatif)
- **tifinagh** : écriture amazighe ancestrale
- **yaz (ⵣ)** : symbole de l'homme libre, identité visuelle Azamoul
- **kabyle / djurdjura** : ancrage géographique Algérie (Kabylie + chaîne montagneuse)
- **thilelli** : liberté
- **dihya** : reine berbère résistante (figure historique)
- **aza, afzim, tiseghnest** : bijoux traditionnels
- **tafaska, tamghra** : fêtes culturelles
- **asseggas amegaz** : "bonne année" amazigh
- **tafsut** : printemps (référence à Tafsut Imazighen, mouvement culturel)

### Règle d'application

Pour les descriptions produit : **minimum 3 mots** du vocabulaire dans `descriptionHtml`.
Pour les alt-texts : **minimum 1 mot** du vocabulaire.
Pour les captions Instagram : **minimum 2 mots** + hashtag `#azamoul` + `#tifinagh`.

---

## Règle 9 — Email via `hermes-email-sender`

Tout envoi email passe par le skill `hermes-email-sender` (anciennement `azamoul-email-sender`) qui :
- Lit `$HERMES_MODE` :
  - `test` : force `to = contact.azamoul@gmail.com`, prefix sujet `[TEST]`
  - `prod` : utilise la liste réelle (`EMAIL_TO=contact.azamoul@gmail.com`)
- Connecte SMTP Gmail via snippet Python smtplib inline (STARTTLS)
- IMPRIME `EMAIL_SMTP_OK` en stdout après envoi réussi

---

## Règle 10 — Telegram chat unique

Le chat ID Telegram autorisé pour Azamoul est `<TELEGRAM_USER_ID>` (le user_id du gérant Rayan).

- Bot : `@HermesAgentMax_bot`
- Seul destinataire autorisé pour les notifications, alertes, validations `/yes`

---

## Niveaux d'autonomie (configurés pour Azamoul)

### 🟢 Auto-exécution (Hermes applique sans demander)

- Génération d'alt-texts manquants avec vocab amazigh
- Normalisation handles ASCII (slugification)
- Ajout de tags catégoriels manquants (textile, accessoire, bijou, déco, livre, coque)
- Insertion du bloc 📦 livraison en début de descriptions
- Meta SEO vides à compléter (title 30-70 chars + description 50-160)
- Drafts (jamais publiés sans /yes) pour campagnes Klaviyo et posts Instagram

### 🟡 Propose en 1-clic (validation Telegram /yes obligatoire)

- Enrichissement de descriptions produit (>=150 mots avec vocab amazigh)
- Génération d'images Gemini Image
- Création de redirects 301
- Création de collections
- Ajustement prix raisonnable (<5%, préférer `compareAtPrice`)
- Post Instagram (mode dry forcé en phase test)
- Modifications de sections du thème via `shopify-theme-editor`

### 🔴 Jamais sans validation explicite (refus même sur demande)

- Modifier le prix de >5%
- Supprimer un produit, page, ou client
- Refunds
- Modification du layout du thème (`layout/theme.liquid`)
- Post Instagram en direct
- Modifications de mentions légales / CGV / politique remboursement
- `config/settings_data.json` du thème

---

## Bloc HTML livraison standard

À insérer en TOUT DÉBUT de descriptionHtml de chaque produit (vérifié par `shopify-catalog-gap-analyzer`) :

```html
<p>📦 <strong>Livraison estimée à 5-6 jours ouvrés en France métropolitaine</strong>
et 8-10 jours à l'international. Expédition soignée depuis la France.</p>
```

---

## Sensibilités spécifiques Azamoul

### Cultural fluency
- **Amazigh ≠ Arabe** : ne jamais confondre. Les Amazighs sont les peuples autochtones d'Afrique du Nord avant l'arabisation.
- **Pas de récupération politique** : éviter les références à des partis politiques ou conflits régionaux.
- **Respect des traditions** : les symboles tifinagh / dihya / kahina ont une charge historique forte.

### Légal
- Mentions "Made in France" vérifiables (production réellement en France)
- Pas de promesses thérapeutiques sur les bijoux
- CGV et politique remboursement existants (cf. `/policies/refund-policy`)

### Réputation
- Marque jeune (lancée mai 2025), engagement communautaire fort sur Instagram
- ~5769 followers, 116 posts, 83% reels
- Public cible : diaspora amazighe + curieux culture nord-africaine

---

## Voir aussi

- [`MISSION.md`](./MISSION.md) — Charter complet de l'agent pour Azamoul
- [`brand-knowledge.md`](./brand-knowledge.md) — 4 concurrents identifiés + calendrier
- [`cultural-events.json`](./cultural-events.json) — événements amazighs en JSON
- [`MEMORY.md`](./MEMORY.md) — faits permanents boutique
- [`GUIDE-OPERATIONNEL.md`](./GUIDE-OPERATIONNEL.md) — guide complet opérationnel
