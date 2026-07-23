# Policy Checker

## Effets

- `allow` : exécution autorisée.
- `deny` : exécution bloquée.
- `review` : validation humaine requise.

## Règles V0

1. Refuser toute écriture hors du workspace du projet.
2. Refuser les extensions exécutables dans l'ingestion documentaire.
3. Soumettre à revue les fichiers dépassant la limite configurée.
4. Refuser une action sans identifiant de projet valide.
5. Journaliser la règle et la raison.

## Principe

Le Policy Checker ne « sécurise » pas magiquement le système. Il rend les décisions explicites, testables et auditées.
