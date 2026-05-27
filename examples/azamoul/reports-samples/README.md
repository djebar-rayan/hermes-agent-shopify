# Reports samples — Cas d'étude Azamoul

> Extraits réels (sanitized) des rapports auto-générés par Hermes pour la boutique Azamoul.
>
> Ces fichiers montrent à quoi ressemble la **sortie concrète** de chacun des 4 crons après plusieurs semaines de tournage.

---

## Fichiers présents

| Fichier | Cron source | Date | Contenu |
|---|---|---|---|
| [`2026-W21-perf.md`](./2026-W21-perf.md) | `azamoul-lundi-perf` (lundi 9h) | 18 mai 2026 | Rapport perf hebdo : KPI Shopify, section Klaviyo, top wins/pertes, diagnostic, actions proposées |
| [`2026-W21-ideas.md`](./2026-W21-ideas.md) | `azamoul-samedi-ideas` (samedi 10h) | 23 mai 2026 | Email créatif : 1 idée produit + 1 idée Insta + 1 draft Klaviyo |
| [`2026-W21-meta.md`](./2026-W21-meta.md) | `azamoul-dimanche-meta` (dimanche 20h) | 24 mai 2026 | Méta-revue : patterns identifiés, mesure impact actions semaine, propositions skills auto |

---

## À quoi ça sert ?

- **Démontrer la qualité du livrable** : un nouveau marchand voit avant de s'engager
- **Inspirer la rédaction** : structures markdown, ton, niveau de détail
- **Mesurer la progression** : comparer les rapports W20, W21, W22 pour voir l'évolution

---

## Convention de nommage

- `YYYY-Www-perf.md` : rapport perf hebdo
- `YYYY-Www-ideas.md` : email créatif samedi
- `YYYY-Www-meta.md` : méta-revue dominicale

Où `Www` = numéro de semaine ISO (ex : `W21` = 21e semaine de l'année).

---

## Sanitization appliquée

Les rapports originaux ne contiennent ni secret ni mot de passe (le hook `log-learning` redacte automatiquement). Les seules transformations appliquées ici :

- `<VPS_IP>` à la place de l'IP du VPS
- `<VPS_HOSTNAME>` à la place du hostname OVH
- `<TELEGRAM_USER_ID>` à la place du user_id Telegram du gérant
- Emails publics conservés (`contact.azamoul@gmail.com` est listé sur azamoul.com)

---

## Pour produire les tiens

Une fois ton instance Hermes configurée, ces fichiers se génèrent automatiquement chaque semaine dans `$HERMES_WORKSPACE/reports/` et `$HERMES_WORKSPACE/meta-reviews/`.
