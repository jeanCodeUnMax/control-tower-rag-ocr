# PRD — Control Tower RAG V0

## Problème

Les expérimentations OCR/RAG contaminent facilement une collection commune : schémas instables, chunks incompatibles, tags incohérents et impossibilité de comparer les variantes.

## Objectif

Créer une tour de contrôle où chaque expérimentation vit dans un projet isolé, avec des contrats versionnés, une ingestion testable et une promotion explicite vers un socle validé.

## Utilisateur principal

Créateur technique qui souhaite tester rapidement une chaîne documentaire complète sans perdre la traçabilité ni reconstruire toute l'infrastructure à chaque essai.

## Parcours V0

1. Créer un projet.
2. Sélectionner un template d'ingestion.
3. Faire valider l'action par le Policy Checker.
4. Extraire le texte via un port OCR.
5. Atomiser le contenu.
6. Enrichir chaque atome : tags, concepts, questions maïeutiques, tensions « Gant de Kant ».
7. Persister les objets et leurs dépendances.
8. Interroger le projet.
9. Hydrater uniquement le contexte utile.
10. Inspecter les décisions et les erreurs.

## Exigences fonctionnelles

- Isolation stricte des workspaces.
- Schémas JSON versionnés.
- Templates déclaratifs.
- Modules activables par configuration.
- Résultat standardisé pour chaque module.
- Invalidation ciblée par graphe de dépendances.
- Journal d'événements append-only.
- Politique de refus explicite.
- Consolidation différée, jamais silencieuse.

## Non-objectifs V0

- Entraîner ou fine-tuner un modèle.
- Fournir un OCR industriel.
- Garantir une compréhension philosophique parfaite.
- Exécuter des agents autonomes sans validation.

## Mesures de réussite

- Un nouveau projet est créé en moins d'une commande.
- Deux projets peuvent ingérer le même document avec des configurations différentes sans collision.
- Un changement d'atome n'invalide que ses dépendants.
- Toute action critique retourne une décision de politique traçable.
- Le pipeline de démonstration fonctionne hors ligne.
