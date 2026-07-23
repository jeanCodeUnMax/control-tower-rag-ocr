# Dev Book

## Contrat universel

Chaque module retourne `ModuleResult` : statut, données, erreurs, avertissements, métriques, traçabilité et version du contrat.

## Registry

Catalogue les modules, schémas, templates, politiques et versions disponibles. Il ne lance aucun traitement.

## Brain

Construit un plan d'exécution à partir de l'intention, de la configuration du projet et des capacités déclarées dans le Registry.

## Policy Checker

Évalue l'action, le projet, la ressource et le contexte. Une décision contient : effet, raisons, règle déclenchée et obligations éventuelles.

## Ingestion

Orchestre extraction, normalisation, atomisation, enrichissement et persistance.

## Atomic Chunk

Unité minimale stable : texte, provenance, ordre, hash, tags, concepts, relations et version.

## Maïeutique

Produit des questions qui révèlent hypothèses, ambiguïtés et informations manquantes. Elle ne prétend pas découvrir une vérité cachée.

## Gant de Kant

Nom de travail pour une grille de tensions : faits/interprétations, moyens/fins, causalité/corrélation, universalisabilité et contradictions. Le résultat reste une annotation explicable.

## Consensus-less

Ne cherche pas un vote majoritaire. Compare des évaluations indépendantes, conserve les désaccords et calcule une confiance à partir de preuves et de contraintes.

## State Manager

Maintient un graphe de dépendances. Une mutation invalide uniquement les nœuds descendants concernés.

## Hydration Engine

Reconstruit une vue de travail à partir d'identifiants, de champs demandés et d'un budget de contexte.

## Consolidator

Tâche différée : détecte doublons, liens possibles, tags faibles et fragments obsolètes. Toute proposition doit être approuvée ou réversible.
