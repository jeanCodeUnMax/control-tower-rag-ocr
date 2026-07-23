# 11. Runbook d'exploitation

## Avant une ingestion longue

1. lancer `pytest -q` ;
2. créer ou vérifier le projet ;
3. exécuter `plan-document` ;
4. lancer un benchmark de 10 à 20 pages ;
5. vérifier les clés et le budget ;
6. sauvegarder le workspace ;
7. lancer l'ingestion ;
8. contrôler le ledger et les pages manquantes ;
9. inspecter quelques pages faciles et difficiles ;
10. seulement ensuite utiliser la recherche.

## En cas d'erreur

- ne pas supprimer les artefacts ;
- lire `events.jsonl` et `provider_report.json` ;
- vérifier les statuts de pages ;
- réduire la concurrence en cas de 429 ;
- désactiver le provider défaillant ;
- basculer en `local_fast` pour terminer le texte ;
- conserver le `document_id` pour l'enrichissement.
