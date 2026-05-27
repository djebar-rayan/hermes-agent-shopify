# Contributing to Hermes Shopify Framework

Merci de l'intérêt ! Ce projet est né d'un besoin opérationnel concret et a été généralisé pour servir d'autres marchands. Les contributions sont les bienvenues.

---

## 🧱 Convention de nommage des skills

Hermes distingue 2 préfixes :

| Préfixe | Usage | Exemples |
|---|---|---|
| `shopify-*` | Skill domaine Shopify (catalogue, theme, KPI, Klaviyo, Instagram, SEO, content...) | `shopify-theme-editor`, `shopify-batch-executor`, `shopify-klaviyo-weekly-report` |
| `hermes-*` | Utility framework pure (pas spécifique à Shopify) | `hermes-email-sender`, `hermes-schema-guard`, `hermes-snapshot-diff-validator` |

**Règle simple** : si ton skill manipule des entités Shopify (product, collection, theme, customer, order) ou des APIs e-commerce (Klaviyo, Instagram, GSC) → `shopify-*`. Sinon → `hermes-*`.

---

## 📝 Structure d'un SKILL.md

Tout skill suit ce format :

```markdown
---
name: shopify-mon-skill
description: Description condensée 1 ligne — quoi fait ce skill et quand l'invoquer
version: 1.0.0
author: Ton nom
metadata:
  hermes:
    tags: [shopify, monitoring, mutation]
    category: ecommerce
    requires_toolsets: [terminal, file, messaging]
---

# Mon Skill

Description courte (1-2 paragraphes) de ce que fait le skill.

## When to Use

- Trigger 1 (ex: cron lundi-perf)
- Trigger 2 (ex: demande user explicite "fais X")
- NE PAS utiliser pour : Y, Z

## Configuration

Vars requises depuis `.env` :
- `VAR_1` (ex: `SHOPIFY_STORE`)
- `VAR_2`

Helpers dépendances :
- `lib/theme.sh` (si applicable)

Skill compagnons :
- `hermes-schema-guard` (à charger AVANT toute mutation)

## Procedure

1. Étape 1 (avec commande bash si applicable)
2. Étape 2
3. ...

## Pitfalls

- Piège 1 connu
- Piège 2

## Verification

Checklist post-exécution :
- [ ] Critère 1 vérifié
- [ ] Critère 2 vérifié
- [ ] Entrée loggée dans `learnings.md`
```

---

## 🔌 Ajouter une nouvelle intégration API

1. Créer un helper dans `lib/<service>-fetch.sh` (suivre le pattern de `lib/klaviyo-fetch.sh`)
   - Cache disque avec TTL (anti rate-limit)
   - Retry exponentiel sur 429
   - Exit codes documentés (0=succès, 1=missing key, 2=API error, 3=usage)
   - Sous-commandes claires
2. Ajouter la variable d'env dans `config/.env.template` avec un commentaire
3. Documenter dans `docs/INTEGRATIONS.md` (ajouter une ligne au tableau)
4. Créer le skill correspondant dans `skills/shopify-<service>-*/SKILL.md`
5. Ajouter un test dans le smoke test si applicable

---

## 🛠️ Ajouter un helper réutilisable

Les helpers vivent dans `lib/`. Conventions :

- **Bash** par défaut (sourçable + executable)
- En-tête : commentaire avec `# Requires in env: VAR_1, VAR_2`
- Fonction `<helper>_check_env` qui valide la présence des vars critiques
- Fonctions préfixées par le nom du helper (`theme_get`, `theme_push`, `klaviyo_fetch`, ...)
- Toutes les fonctions exportées via `export -f` à la fin du fichier
- Gestion d'erreur explicite avec préfixe `[<HELPER>_FAIL: ...]` sur stderr

---

## 🚀 Soumettre une PR

### Workflow

1. **Fork** le repo
2. **Branche** depuis `main` : `git checkout -b add-shopify-X`
3. Implémenter + tester localement
4. **Lint** : pas de secret hardcodé, pas de référence à une boutique spécifique
5. **Commit** : message clair (cf. format ci-dessous)
6. **Push** + ouvrir une PR vers `main`

### Format de commit

```
<type>: <description courte 50 chars>

<description détaillée si nécessaire>

<footer ex: closes #42>
```

Types : `feat` (nouveau skill/feature), `fix` (correction), `docs` (doc), `refactor`, `test`, `chore`.

Exemples :
- `feat(skill): add shopify-product-bulk-importer`
- `fix(theme.sh): handle empty theme list gracefully`
- `docs(getting-started): clarify Theme Access setup`

### Critères d'acceptation

- [ ] Le skill / helper / doc a un nom suivant la convention
- [ ] Pas de secret en clair (les vars d'env sont référencées, pas leurs valeurs)
- [ ] Pas de référence à une boutique spécifique dans le code générique (sauf dans `examples/`)
- [ ] Tests / smoke tests passent
- [ ] Documentation mise à jour (`docs/SKILLS-REFERENCE.md` si nouveau skill, `docs/INTEGRATIONS.md` si nouvelle API)
- [ ] Aucune régression sur les skills existants

---

## 📐 Code style

### Bash

- 2 espaces pour l'indentation
- `set -euo pipefail` en début de script (sauf si raison documentée)
- Variables en `UPPER_CASE` pour les constants, `lower_case` pour les locales
- Toujours quoter les variables : `"$var"` pas `$var`
- Helper functions retournent via `echo` (capturable) ou via fichier (`$1` = output path)
- `local` pour toutes les variables internes à une fonction

### Markdown

- En-têtes : `#` pour le titre, `##` pour les sections principales, `###` pour les sous-sections (max 4 niveaux)
- Tableaux : aligner les `|` pour la lisibilité
- Code blocks : avec language tag (` ```bash `, ` ```json `, ...)
- Liens internes : utiliser des paths relatifs (`./docs/X.md` plutôt que des URL absolus)

---

## 🤝 Code of Conduct

- Respect mutuel
- Pas de spam / promotion
- Les issues sont pour des bugs / features / questions techniques
- Pas de question de support gratuit (consulting privé en MP si besoin)
- Reviews constructives, pas de "ça marche pas" sans détails

---

## 🙏 Crédits

Ce framework a été créé par **Rayan Djebar** lors d'un stage chez Azamoul (marque française culture amazighe), puis généralisé pour servir d'autres marchands. Les contributeurs sont listés dans la section "Contributors" de la page repo GitHub.

---

## ❓ Questions

- Issue GitHub pour bug / feature / proposition de skill
- Pour les contributions importantes (nouveau skill complet, nouvelle intégration majeure), ouvre d'abord une issue de discussion avant de coder
- Pas de canal de chat dédié (Discord/Slack) pour l'instant
