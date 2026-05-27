---
name: shopify-cultural-calendar
description: Planning et alertes sur les événements culturels (lus depuis cultural-events.json)
version: 1.0.0
author: Hermes (Phase 0 scaffold)
metadata:
  hermes:
    tags: [culture, calendar, marketing, framework]
    category: ecommerce
    requires_toolsets: [web]
---
# Calendrier Cultural Amazigh <STORE_NAME>

## When to Use
- Avant chaque saison commerciale (Yennayer = janvier, Ramadan, fetes)
- Dans le rapport perf lundi : mentionner evenement prochain (< 14 jours)
- Dans l'email samedi : proposer campagne thematique

## Procedure
1. Verifier calendrier événements culturels (lus depuis cultural-events.json)
2. Calculer jours restants avant prochain evenement
3. Si < 14 jours : alerter et proposer campagne (email + Insta + produit)
4. Enregistrer dans brand-knowledge.md les evenements des 6 prochains mois

## Evenements clefs (recurrents)
- <événement nouvel an depuis cultural-events.json>
- Festival Imilchil : septembre
- <événement culturel local depuis cultural-events.json>
- Ramadan : variable (hijri)
- Événements culturels locaux (festivals, etc.)

## Pitfalls
- Dates islamiques variable (calculees avec hijri)
- Pas de stereotypes / cultural appropriation
- Aligner avec les produits du catalogue (matching produits par catégorie d événement)

## Verification
- table brand-knowledge.md mis a jour avec dates des 6 prochains mois
- Alertes Telegram envoyees (> 2 semaines)
