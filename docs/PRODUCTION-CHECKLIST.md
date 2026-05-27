# Production Checklist — Bascule `HERMES_MODE=test` → `prod`

> Checklist à valider AVANT de basculer ton instance Hermes en mode production. La bascule active les mutations Shopify persistantes — le retour arrière est possible mais coûte du temps.

---

## 1. Vérifications avant bascule

### Phase test : durée minimale recommandée

Avant de passer en prod, faire tourner Hermes en `HERMES_MODE=test` pendant au minimum :
- **2 cycles complets de cron lundi-perf** (= 2 semaines)
- **2 cycles complets de cron samedi-ideas**
- **2 cycles complets de cron dimanche-meta**
- **~10 runs de watchdog** (= ~2-3 jours)

Cela permet d'observer :
- Les rapports hebdo sont-ils précis et utiles ?
- Les propositions samedi-ideas sont-elles pertinentes pour ta marque ?
- La méta-revue identifie-t-elle de vrais patterns ?
- Le watchdog alerte-t-il sur les bons signaux ?

### Checklist technique

- [ ] **`.env` complet** : toutes les vars critiques remplies (SHOPIFY_STORE, OPENROUTER_API_KEY, EMAIL_*, TELEGRAM_*, LIVE_THEME_ID, etc.)
- [ ] **Shopify CLI auth OK** : `shopify store info` fonctionne
- [ ] **Theme Access token actif** : `theme_check_env && theme_list` fonctionne
- [ ] **OpenViking healthy** : `curl http://localhost:1933/health` retourne 200
- [ ] **Hermes gateway Telegram up** : bot répond à `/start`
- [ ] **Hooks v0.14 actifs** : test session interactive, vérifier que STANDING est injecté
- [ ] **Crons exécutés au moins 2 fois sans erreur** : `cat /root/.hermes/cron/jobs.json | jq '.jobs[] | {name, last_status}'`
- [ ] **`learnings.md` contient des entrées** : preuve que le hook `log-learning` fonctionne
- [ ] **App Password Gmail valide** : envoi de test email avec sentinelle `EMAIL_SMTP_OK`

### Checklist contenu

- [ ] **`MISSION.md` rempli** : charter spécifique à ta boutique
- [ ] **`STORE-BRAND.md` rempli** : vocab obligatoire + niveaux 🟢/🟡/🔴 + sensibilités
- [ ] **`brand-knowledge.md` rempli** : 5-10 concurrents identifiés avec URL + niche + différenciation
- [ ] **`cultural-events.json` rempli** : au moins les 3-5 prochains événements importants pour ta marque
- [ ] **`MEMORY.md` rempli** : faits boutique (catalogue size, devise, fuseau, plan Shopify)
- [ ] **Baseline KPI 30j capturée** : `$HERMES_WORKSPACE/baseline-kpi-30j.md` existe

### Checklist sécurité

- [ ] **`.env` chmod 600** : pas accessible aux autres users
- [ ] **`~/.hermes/` chmod 700**
- [ ] **Aucun secret en clair** dans les rapports déjà générés (re-lire 1-2 rapports test)
- [ ] **`TELEGRAM_ALLOWED_USERS` = ton user_id uniquement** : pas d'autre destinataire autorisé
- [ ] **Validation Telegram /yes testée** : faire un dry-run mutation, recevoir le message, valider /yes, vérifier que la mutation a bien été appliquée (en mode test)

---

## 2. Bascule effective

Quand toute la checklist est validée :

```bash
# 1. Backup .env actuel
cp /root/.hermes/.env /root/.hermes/.env.bak.$(date +%Y%m%d)

# 2. Modifier le mode
sed -i 's/^HERMES_MODE=test$/HERMES_MODE=prod/' /root/.hermes/.env

# 3. Vérifier
grep ^HERMES_MODE /root/.hermes/.env
# Doit afficher : HERMES_MODE=prod

# 4. Loguer la bascule dans learnings.md
cat >> $HERMES_WORKSPACE/learnings.md << EOF

- [$(date -u +%Y-%m-%dT%H:%M:%SZ)] PHASE TRANSITION : HERMES_MODE=test → HERMES_MODE=prod
  Avant: phase test exclusive (apply+rollback même run depuis l'install)
  Après: mode production activé, mutations persistantes après /yes Telegram
  Conclusion: décision marchand après <N> semaines de test validé
  Futur: surveiller le premier vrai run cron en mode prod
EOF

# 5. Mettre à jour MEMORY.md
sed -i "s/Phase courante.*/Phase courante : PRODUCTION (depuis $(date -u +%Y-%m-%d))/" $HERMES_WORKSPACE/MEMORY.md
```

---

## 3. Surveillance post-bascule

### Premier jour (J)

- [ ] **Vérifier que le prochain cron tourne sans erreur** : observer `last_status: ok` après le premier run
- [ ] **Lire le rapport généré** : aucune mutation Shopify inattendue ? Tous les chiffres ont une source citée ?
- [ ] **Vérifier les notifications Telegram** : reçues, formattées correctement
- [ ] **Vérifier l'email** : sentinelle `EMAIL_SMTP_OK` présente

### Première semaine

- [ ] **2-3 demandes de validation `/yes` Telegram reçues** : workflow validation fonctionnel
- [ ] **Au moins 1 mutation persistante appliquée** après /yes : vérifier dans Shopify admin que le changement est bien en place
- [ ] **Rollback testé au moins 1 fois** : utiliser `shopify-batch-rollback` sur un batch récent pour confirmer que le snapshot before.json + script rollback fonctionnent
- [ ] **Méta-revue dominicale** : confirmer qu'elle identifie correctement les patterns de la semaine

### Premier mois

- [ ] **Aucune mutation Shopify non-validée** : auditer la timeline des mutations dans learnings.md
- [ ] **KPI baseline vs M+1** : comparer les KPI 30j avant vs 30j après bascule
- [ ] **Coût OpenRouter en ligne avec attendu** : `hermes insights --days 30`, vérifier que le coût reste sous le quota
- [ ] **Aucun secret leaké** dans les rapports / logs (audit grep)

---

## 4. Procédure de retour arrière (rollback prod → test)

Si tu détectes un problème majeur :

```bash
# 1. Retour mode test immédiat
sed -i 's/^HERMES_MODE=prod$/HERMES_MODE=test/' /root/.hermes/.env

# 2. (Optionnel) Désactiver tous les crons pendant l'investigation
# Éditer /root/.hermes/cron/jobs.json et mettre "enabled": false sur chaque job

# 3. Rollback des dernières mutations si problème grave
# Pour chaque batch récent :
node /root/.hermes/skills/shopify-batch-rollback/run.js <batch_id>
# OU directement :
bash $HERMES_WORKSPACE/batches/YYYY-Www-batchN-rollback.sh

# 4. Loguer
cat >> $HERMES_WORKSPACE/learnings.md << EOF

- [$(date -u +%Y-%m-%dT%H:%M:%SZ)] PHASE TRANSITION URGENTE : HERMES_MODE=prod → HERMES_MODE=test
  Avant: production active
  Après: retour test exclusive
  Conclusion: <cause exacte du rollback>
  Futur: investigation + correctif avant nouvelle bascule
EOF
```

---

## 5. Indicateurs de succès / d'échec

### Succès (bascule réussie après 1 mois)
- ✅ 4 cycles cron lundi-perf passés sans erreur
- ✅ Au moins 5 mutations persistantes appliquées et validées
- ✅ KPI 30j vs baseline : pas de régression
- ✅ Coût OpenRouter dans le budget
- ✅ Aucune alerte watchdog non triviale
- ✅ Tuteur (marchand) satisfait des livrables

### Échec (signaux qui justifient rollback)
- ❌ Mutation persistante non-validée appliquée par erreur
- ❌ KPI 30j en chute de >20% vs baseline sans cause externe
- ❌ Sentinelle `EMAIL_SMTP_OK` régulièrement absente (emails perdus)
- ❌ Validation Telegram /yes ne fonctionne plus (gateway down)
- ❌ Coût OpenRouter dépasse 2x le budget
- ❌ Secrets exposés dans les rapports

---

## 6. Communication au marchand

Pour le marchand qui supervise Hermes en prod, communiquer chaque semaine :
- Résumé Telegram automatique (cron lundi-perf)
- Email automatique (idem)
- Méta-revue dominicale (Telegram + résumé)

Et chaque mois (manuel ou cron supplémentaire à créer) :
- Audit mensuel : KPI M-1 vs M, coût, top wins/échecs
- Décision : continuer / ajuster / désactiver des crons / créer de nouveaux skills

---

## 7. Versionning et evolution

À chaque évolution majeure de la config en prod :
- Backup `.env`, `config.yaml`, `cron/jobs.json`, `STANDING-CORE.md`, `STORE-BRAND.md`, `MISSION.md`
- Loguer dans `learnings.md` avec une entrée structurée
- (Optionnel) Pusher la nouvelle config dans un repo git privé (jamais public sauf si entièrement sanitized)

---

## 8. Decision matrix : faut-il basculer en prod ?

Réponds aux questions suivantes après la phase test :

| Question | Réponse souhaitée |
|---|---|
| Les rapports hebdo lundi sont-ils précis et actionnables ? | Oui |
| Les propositions samedi-ideas correspondent-elles à ton univers de marque ? | Oui |
| Les niveaux d'autonomie 🟢/🟡/🔴 sont-ils calibrés correctement ? | Oui |
| Hermes a-t-il déjà proposé une mutation cohérente avec ta stratégie ? | Oui (au moins 1) |
| As-tu testé une validation /yes manuelle sur une mutation ? | Oui |
| As-tu testé un rollback manuel d'une mutation ? | Oui |
| Tu fais confiance à Hermes pour appliquer des mutations sans intervention immédiate ? | Oui |

Si TOUTES les réponses sont "Oui" → tu es prêt pour la bascule.
Si UNE seule est "Non" → continuer la phase test + résoudre le point bloquant avant bascule.
