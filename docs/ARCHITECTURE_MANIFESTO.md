# Manifeste d'architecture

1. **Tout est module.** Aucune capacité métier critique n'est codée dans l'orchestrateur.
2. **Tout passe par contrat.** Entrées, sorties, erreurs et versions sont explicites.
3. **Un projet est une frontière de confiance.** Données, index, logs et configuration restent isolés.
4. **Le Registry sait; le Brain choisit.** Le Registry décrit. Le Brain compose. Aucun des deux ne fait le travail métier.
5. **La politique précède l'action.** Les opérations critiques sont autorisées, refusées ou soumises à revue.
6. **Le recalcul est ciblé.** Le State Manager invalide selon les dépendances, pas selon la peur.
7. **L'hydratation est une projection.** Une vue est reconstruite à la demande depuis des objets atomiques.
8. **La consolidation est lente et réversible.** Elle propose, journalise et permet le rollback.
9. **La complexité doit être optionnelle.** Une couche peut être désactivée sans effondrement du système.
10. **Une verticale fonctionnelle vaut mieux que dix abstractions inertes.**
