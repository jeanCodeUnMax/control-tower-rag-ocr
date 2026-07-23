# Découpage des tâches — V0.4

## T1 — Profiler chaque page — TERMINÉ

**Entrée :** PDF.  
**Sortie :** `page_profiles.json`.  
**Critère :** une entrée pour chaque page avec caractères, images, dessins, blocs et charge estimée.

## T2 — Planifier les lots adaptatifs — TERMINÉ

**Sortie :** `batch_plan.json`.  
**Critère :** lots contigus, jamais plus de cinq pages, respect du budget estimé.

## T3 — Registre de complétude — TERMINÉ

**Sortie :** `ingestion_ledger.json`.  
**Critère :** chaque page possède un état et la condition finale vérifie exactement `1..N`.

## T4 — Exécution, retry et division — TERMINÉ

**Critère :** un lot fautif est divisé jusqu'à la page seule ; les autres pages continuent.

## T5 — Analyse page par page — TERMINÉ

**Sortie :** `pages/page_XXXXX.json` et `page_analyses.json`.  
**Critère :** une analyse structurée par page avec provider et avertissements.

## T6 — Actifs visuels — TERMINÉ

**Sortie :** `visual_assets.json` et fichiers extraits.  
**Critère :** images embarquées et dessins vectoriels reliés à leur page.

## T7 — Pseudocode, maïeutique et Kant — TERMINÉ

**Critère :** modules pilotés par configuration et injectés dans les chunks.

## T8 — Consolidation avant indexation — TERMINÉ

**Sortie :** `consolidation.json`.  
**Critère :** doublons non indexables, canonique indexable et occurrences conservées.

## T9 — Recherche canonique — TERMINÉ

**Critère :** les doublons ne remontent pas dans la recherche par défaut.

## T10 — Preuve 800 pages — TERMINÉ

**Critère :** 800 terminées, aucune page manquante ou en échec, assertion automatique.

## T11 — Reprise après redémarrage — À FAIRE

Lire un registre existant et reprendre uniquement les pages non terminées.

## T12 — Validation multimodale réelle — À FAIRE CHEZ L'UTILISATEUR

Nécessite `OPENAI_API_KEY`, un PDF représentatif et un budget API mesuré.
