---
name: shopify-cron-output-watcher
description: Pattern pour monitorer et valider l'exécution autonome des crons déclenchés.
version: 0.1.0
author: Hermes auto-meta grand-run-2026-W20
category: devops
tags:
  - auto-proposed
  - grand-run-2026-W20

---

### When to Use
Utiliser ce pattern lorsque vous déclenchez un des 4 crons principaux d'<STORE_NAME> (lundi-perf, samedi-ideas, dimanche-meta, watchdog-conversion) pour valider leur exécution réussie.

### Procedure
1. Déclencher le script ou la commande du cron.
2. Poll (surveiller) le répertoire de sortie défini (ex: /root/shopify-cron-logs/).
3. Parser le fichier de résultat généré (ex: ## Response header).
4. Confirmer que la sortie est formatée correctement et que les actions (email/log) ont bien été déclenchées.

### Pitfalls
- Ne pas attendre la génération du fichier de log (prévoir un léger délai de polling).
- Ne pas purger les anciens logs avant le trigger, ce qui induit en erreur sur le timestamp.
- Ignorer les erreurs silencieuses dans stderr si le code de sortie est 0.

### Verification
- Fichier de sortie présent et horodaté.
- Contenu du fichier sans erreur de type "Traceback" ou "AuthenticationError".
- Les actions décrites dans le rapport (ex: email sent) correspondent à l'attente du test.
