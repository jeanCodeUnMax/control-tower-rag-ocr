# Découpage des tâches V0.5

| Lot | Sortie | Critère d'acceptation | État |
|---|---|---|---|
| A1 | Modèles de providers | validation YAML et valeurs bornées | terminé |
| A2 | Accès aux listes par `config-set` | `vision.providers.1.enabled` modifiable | terminé |
| B1 | Contrat OpenAI-compatible | image base64 + JSON Schema | terminé |
| B2 | Contrat Gemini | image inline + schéma JSON | terminé |
| C1 | Limiteur RPM | aucune requête hors fenêtre configurée | terminé |
| C2 | Retries | un 429 temporaire peut réussir sans perdre la page | terminé |
| C3 | Circuit breaker | provider instable court-circuité | terminé |
| C4 | Budget | fallback ou arrêt explicite | terminé |
| D1 | Routage adaptatif | local, cloud et deferred distingués | terminé |
| D2 | Préflight | aucune requête cloud | terminé |
| D3 | Benchmark | rapport persistant et débit calculé | terminé |
| E1 | File différée | pages visibles dans provider_report | terminé |
| E2 | Enrichissement | seules les pages signalées sont reprises | terminé |
| E3 | Réindexation | même document_id, chunks remplacés | terminé |
| F1 | Tests de non-régression | suite V0.4 toujours verte | terminé |
| F2 | Tests V0.5 | panne, budget, payload, enrichissement | terminé |
| G1 | Mistral OCR Batch | provider OCR documentaire natif | prochaine version |
| G2 | PaddleOCR | benchmark local rapide | prochaine version |
| G3 | concurrence inter-lots | plusieurs lots en vol avec checkpoint thread-safe | prochaine version |
