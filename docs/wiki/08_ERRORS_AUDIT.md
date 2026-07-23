# 8. Gestion des erreurs et audit

## Mécanismes disponibles

- retries exponentiels ;
- jitter ;
- timeout par provider ;
- circuit breaker ;
- fallback vers un autre provider ;
- registre page par page ;
- statut explicite des échecs ;
- refus d'indexer un document incomplet ;
- logs JSONL ;
- artefacts JSON de preuve.

## Fichiers d'audit

- `ingestion_ledger.json` : statut de chaque page ;
- `provider_report.json` : providers, retries, pages différées ;
- `extraction.json` : extraction page par page ;
- `consolidation_report.json` : canoniques et occurrences ;
- `events.jsonl` : événements applicatifs.

## Points à améliorer

- reprise réelle après redémarrage ;
- fermeture systématique des connexions SQLite ;
- coût réel retourné par les APIs ;
- authentification API ;
- idempotence et versionnement des documents ;
- métriques de production.
