---
name: shopify-theme-editor
description: Modifie les fichiers du thème Shopify <STORE_NAME> (sections, snippets, templates, assets) en headless via Theme Access token, avec backup obligatoire, lint pré-push, diff/verify, et workflow duplicate-preview pour les modifs risquées
version: 1.1.0
author: Hermes (2026-05-24)
metadata:
  hermes:
    tags: [shopify, theme, mutation, framework, headless]
    category: ecommerce
    requires_toolsets: [terminal, file, messaging]
---

# <STORE_NAME> Theme Editor (v1.1)

Skill de modification du thème Shopify live "update 19 12 2025 Sense" (ID `$LIVE_THEME_ID`) via Theme Access token, sans dépendre des scopes OAuth manquants (`write_themes`).

**v1.1 changes :**
- Helper lib `/root/.hermes/lib/theme.sh` (DRY, sourçable)
- Lint pré-push (JSON, balises Liquid, accolades CSS)
- Backup AUTO via helper (plus de pattern manuel)
- Diff pré-push affiché systématiquement
- Verify post-push (re-fetch + compare)
- **Workflow duplicate-preview** pour modifs risquées (header, footer, layout, refonte sections critiques)
- Multi-file atomic push avec rollback transactionnel
- Distingue clairement "édition incrémentale" (push direct) et "refonte" (preview obligatoire)

## When to Use

- Modif incrémentale d'un fichier thème : "ajoute du CSS", "modifie cette section", "change le footer", "édite le template product.json"
- Création de templates produit/page custom (ex. `templates/product.test-returns.json` du 2026-05-24)
- Refonte visuelle (header, footer, palette, typo) → **duplicate-preview obligatoire**
- JAMAIS pour modifier le contenu des produits, pages, blogs, collections (utiliser les skills dédiés)
- JAMAIS pour basculer un templateSuffix (action sur le produit, pas le thème)

## Configuration

### Variables d'environnement requises
Lit depuis `/root/.hermes/.env` :
- `SHOPIFY_CLI_THEME_TOKEN` (commence par `shptka_`) — créé 2026-05-24
- `SHOPIFY_STORE=<your_store_handle>`
- `TELEGRAM_BOT_TOKEN` (pour /yes)

Si `SHOPIFY_CLI_THEME_TOKEN` absent : STOP avec message `[THEME_FAIL: missing SHOPIFY_CLI_THEME_TOKEN — see reference_shopify_theme_access.md to recreate via Theme Access app]`.

### Constantes (dans helper lib)
- `LIVE_THEME_ID=$LIVE_THEME_ID`
- `THEME_BACKUP_DIR=$HERMES_WORKSPACE/theme-backups/`
- `THEME_WORK_BASE=/tmp/theme-work` (dirs temporaires `theme-work.XXXXXX`)

### Helper lib
```bash
set -a; . /root/.hermes/.env; set +a
. /root/.hermes/lib/theme.sh
theme_check_env || exit 1
```

Fonctions exposées :
- `theme_get FILENAME [OUTPUT] [THEME_ID]` — fetch contenu
- `theme_backup FILENAME [THEME_ID]` — backup horodaté, echoes path
- `theme_lint LOCAL_FILE` — vérifie JSON valide, balises Liquid balancées, accolades CSS
- `theme_diff LOCAL_FILE REMOTE [THEME_ID]` — unified diff sur stdout (rc=0 no diff, 1 diff, 2 err)
- `theme_push LOCAL_FILE REMOTE [THEME_ID]` — push 1 fichier
- `theme_push_many WORK_DIR [THEME_ID]` — push N fichiers atomique avec rollback
- `theme_verify LOCAL_FILE REMOTE [THEME_ID]` — re-fetch et compare (rc=0 si match)
- `theme_safety_level PATH` — echoes green|yellow|red-block|red-forbidden
- `theme_duplicate [NAME]` — duplique le live, echoes new theme ID
- `theme_preview_url THEME_ID` — URL preview
- `theme_delete THEME_ID` — refuse si == LIVE
- `theme_publish THEME_ID` — set as live
- `theme_list` — liste id|name|role

## Niveaux de sécurité

`theme_safety_level $PATH` retourne :

| Pattern | Niveau | Action |
|---|---|---|
| `assets/*`, `snippets/*` | 🟢 **green** | Backup + lint + push direct |
| `sections/*.liquid`, `templates/*`, `locales/*` | 🟡 **yellow** | Backup + lint + diff + /yes Telegram + push + verify |
| `layout/*.liquid`, `config/settings_schema.json` | 🔴 **red-block** | Refuse sauf override écrit explicite tuteur : "I confirm <action> on <file>" |
| `config/settings_data.json` | 🔴 **red-forbidden** | JAMAIS modifier (corruption garantie des réglages theme editor) |

**Override pour red-block** : le user doit écrire mot pour mot "I confirm <action> on <file>" dans le chat (ex. "I confirm layout edit on theme.liquid"). Sinon refus.

## Workflows

### Workflow A : Édition incrémentale (single file, low risk)

Pour 🟢 green ou 🟡 yellow concernant 1 fichier avec changement ciblé.

```bash
set -a; . /root/.hermes/.env; set +a
. /root/.hermes/lib/theme.sh
theme_check_env || exit 1

FILE="assets/theme.css"  # ou tout autre fichier
LEVEL=$(theme_safety_level "$FILE")

# 1. Fetch + backup
mkdir -p /tmp/edit && theme_get "$FILE" /tmp/edit/current
BACKUP=$(theme_backup "$FILE")
echo "Backup: $BACKUP"

# 2. Appliquer la modif (string replace, JSON edit, ou append)
node -e "
  const fs = require('fs');
  let c = fs.readFileSync('/tmp/edit/current', 'utf8');
  // ... transformation ...
  fs.writeFileSync('/tmp/edit/new', c);
"

# 3. Lint
theme_lint /tmp/edit/new || { echo "Lint failed, abort"; exit 1; }

# 4. Diff (affichage)
echo "=== DIFF ==="
theme_diff /tmp/edit/new "$FILE"
DIFF_RC=$?
[ $DIFF_RC -eq 0 ] && { echo "No-op (identique)"; exit 0; }

# 5. /yes Telegram si yellow
if [ "$LEVEL" = "yellow" ]; then
  DIFF_TEXT=$(diff -u /tmp/edit/current /tmp/edit/new | head -100)
  curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d "chat_id=$TELEGRAM_ALLOWED_USERS" \
    --data-urlencode "text=🎨 Thème modif demandée
Fichier: $FILE (niveau: $LEVEL)
Backup: $BACKUP
Diff (extrait):
\`\`\`
$DIFF_TEXT
\`\`\`
Réponds /yes pour appliquer, /no pour annuler."
  # Attendre /yes — utiliser le pattern wait_for_telegram_yes() de shopify-batch-executor
  wait_for_telegram_yes 600 || { echo "Timeout ou /no"; exit 2; }
fi

# 6. Push + verify
theme_push /tmp/edit/new "$FILE" || exit 1
theme_verify /tmp/edit/new "$FILE" || { echo "VERIFY_FAIL — rollback"; theme_push "$BACKUP" "$FILE"; exit 1; }

echo "[OK] $FILE updated"

# 7. Log
echo "- [$(date -u +%Y-%m-%d)] Theme edit: $FILE ($LEVEL) — backup: $BACKUP" >> /root/.hermes/memories/learnings.md
```

### Workflow B : Création nouveau fichier (low risk)

Création = pas de risque pour l'existant. Procédure plus courte :
```bash
FILE="templates/product.<suffix>.json"   # nouveau fichier
# 1. Préparer /tmp/edit/new avec contenu généré
# 2. Lint
theme_lint /tmp/edit/new || exit 1
# 3. Push direct (pas de backup possible — fichier inexistant remote)
theme_push /tmp/edit/new "$FILE" || exit 1
# 4. Verify
theme_verify /tmp/edit/new "$FILE" || exit 1
# 5. Log
```

### Workflow C : Refonte / multi-file / haut risque → duplicate-preview

Pour les refontes de header/footer/palette, ou >2 fichiers modifiés ensemble, ou changement structurel :

```bash
set -a; . /root/.hermes/.env; set +a
. /root/.hermes/lib/theme.sh
theme_check_env || exit 1

# 1. Dupliquer le thème live
PREVIEW_NAME="Hermes-Preview-$(date -u +%Y%m%dT%H%M%SZ)"
PREVIEW_ID=$(theme_duplicate "$PREVIEW_NAME") || exit 1
echo "Preview theme: $PREVIEW_ID ($PREVIEW_NAME)"
PREVIEW_URL=$(theme_preview_url "$PREVIEW_ID")

# 2. Préparer toutes les modifs dans un work dir
WD=$(mktemp -d "$THEME_WORK_BASE.refonte.XXXXXX")
mkdir -p "$WD/assets" "$WD/sections" "$WD/snippets"  # selon besoin
# ... générer tous les fichiers modifiés dans $WD ...

# 3. Push atomique sur le preview (avec lint + backup auto)
theme_push_many "$WD" "$PREVIEW_ID" || {
  echo "Push preview failed — deleting preview theme"
  theme_delete "$PREVIEW_ID"
  exit 1
}

# 4. Screenshot pour validation user (playwright via pw CLI)
pw screenshot "$PREVIEW_URL" "/tmp/preview-home.png" --full-page
pw screenshot "${PREVIEW_URL}/products/<exemple-product-handle>" "/tmp/preview-product.png" --full-page

# 5. /yes Telegram avec preview URL et screenshots
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendPhoto" \
  -F chat_id="$TELEGRAM_ALLOWED_USERS" \
  -F photo="@/tmp/preview-home.png" \
  -F caption="🎨 Refonte preview prête
Preview URL: $PREVIEW_URL
Theme ID: $PREVIEW_ID
Réponds /yes pour publier sur le live, /no pour rejeter (preview sera supprimé)."

wait_for_telegram_yes 1800  # 30 min pour ce genre de validation
case $? in
  0)
    # /yes : push les mêmes fichiers sur le live
    theme_push_many "$WD" "$LIVE_THEME_ID" || {
      echo "Push live failed après preview validée — anomalie, le preview reste pour debug"
      exit 1
    }
    # Supprime le preview (plus utile)
    theme_delete "$PREVIEW_ID"
    echo "[OK] Refonte appliquée sur live"
    ;;
  2)
    # /no : supprime preview
    theme_delete "$PREVIEW_ID"
    echo "[CANCELLED] Refonte refusée, preview supprimé"
    exit 2
    ;;
  *)
    echo "[TIMEOUT] preview $PREVIEW_ID conservé pour validation ultérieure"
    exit 3
    ;;
esac

rm -rf "$WD"

# Log
echo "- [$(date -u +%Y-%m-%d)] Theme refonte multi-file via preview $PREVIEW_ID → live $LIVE_THEME_ID" >> /root/.hermes/memories/learnings.md
```

## Quand choisir A vs B vs C

| Cas | Workflow |
|---|---|
| Ajouter quelques règles CSS au theme.css | A (green) |
| Modifier un snippet existant | A (green) |
| Éditer le contenu d'un bloc dans templates/product.test-returns.json | A (yellow) |
| Créer un nouveau template product.X.json | B |
| Renommer la nav du header | C (preview obligatoire) |
| Refonte palette couleurs (CSS + settings_schema éventuellement) | C |
| Ajouter une nouvelle section homepage | C |
| Remplacer le footer entier | C |

**Règle simple** : si >1 fichier modifié OU si le change touche une zone visible >25% de la page → workflow C.

## Pattern `wait_for_telegram_yes` (à mutualiser)

Référence : `shopify-batch-executor` utilise déjà ce pattern. Si pas encore extrait en helper, le copier ici :

```bash
wait_for_telegram_yes() {
  local timeout="${1:-600}"
  local start=$(date +%s)
  local last_update_id=0
  while [ $(($(date +%s) - start)) -lt "$timeout" ]; do
    local resp
    resp=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates?offset=$((last_update_id+1))&timeout=10")
    local update_id text
    update_id=$(echo "$resp" | node -e "let b='';process.stdin.on('data',d=>b+=d).on('end',()=>{const r=JSON.parse(b);if(r.result?.length){console.log(r.result[r.result.length-1].update_id);}})")
    [ -n "$update_id" ] && last_update_id=$update_id
    text=$(echo "$resp" | node -e "let b='';process.stdin.on('data',d=>b+=d).on('end',()=>{const r=JSON.parse(b);if(r.result?.length){const m=r.result[r.result.length-1].message;console.log(m?.text||'');}})")
    case "$text" in
      "/yes"|"/YES") return 0 ;;
      "/no"|"/NO")   return 2 ;;
    esac
    sleep 2
  done
  return 1  # timeout
}
```

## Pitfalls (consolidés)

- Le token `shptka_` ne fonctionne PAS avec REST API (`X-Shopify-Access-Token` → 401). Uniquement via Shopify CLI.
- `--allow-live` est obligatoire pour push sur live.
- Le message "Cleaning your remote theme" pendant push est trompeur : `--only` ne supprime rien d'autre.
- `config/settings_data.json` contient toute la config du theme editor — INTERDIT.
- `sections/main-product.liquid` fait 98KB+ : TOUJOURS string-replace ciblé sur un marqueur unique, JAMAIS réécrire en entier.
- L'API GraphQL `themeFilesUpsert` est BLOQUÉE sur cette boutique (write_themes manquant). Seul Shopify CLI + Theme Access fonctionne.
- Pour ajouter un bloc à un produit spécifique : créer `templates/product.<suffix>.json` et basculer le `templateSuffix` (action sur le produit, dans un autre skill ou via productUpdate).
- `theme_push_many` rollback est best-effort — si plusieurs fichiers échouent et rollback échoue, alerter immédiatement le user.
- Avant un `theme_publish` sur preview validé : VÉRIFIER que c'est bien la bonne theme ID (race conditions possibles si plusieurs preview en parallèle).
- Cache CDN Shopify : après push, le rendu peut prendre 30-60s à se propager. Toujours laisser passer 30s avant `theme_verify` (ou utiliser `?v=$(date +%s)` cache-bust).

## Verification (checklist par run)

- [ ] `theme_check_env` passé OK
- [ ] Niveau de sécurité respecté (green direct, yellow /yes, red-block override, red-forbidden refusé)
- [ ] Lint OK avant push
- [ ] Backup créé (sauf création nouveau fichier)
- [ ] Diff affiché (et non-vide, sinon abort no-op)
- [ ] /yes reçu pour yellow / red-block
- [ ] Push retourné succès (shop name dans réponse JSON)
- [ ] Verify post-push OK (re-fetch == local)
- [ ] Si preview workflow : preview supprimé après /yes (ou conservé si timeout)
- [ ] Entrée loggée dans `learnings.md`
- [ ] Screenshot playwright produit si modif visuelle (suggérer au user)

## Rollback manuel (cas d'urgence)

Si une modif post-verify cause une régression non détectée :

```bash
. /root/.hermes/lib/theme.sh
# Identifier le backup le plus récent
ls -t $HERMES_WORKSPACE/theme-backups/ | grep "$(echo $FILE | sed 's|/|__|g')" | head -1
BACKUP=$HERMES_WORKSPACE/theme-backups/<le bon backup>
theme_push "$BACKUP" "$FILE"
theme_verify "$BACKUP" "$FILE" && echo "Rollback OK"
```

## Changelog

- **v1.1.0** (2026-05-24) : helper lib `/root/.hermes/lib/theme.sh`, lint, diff/verify auto, workflow duplicate-preview (C), multi-file atomic push avec rollback.
- **v1.0.0** (2026-05-24) : version initiale, push direct via shopify CLI + Theme Access token.
