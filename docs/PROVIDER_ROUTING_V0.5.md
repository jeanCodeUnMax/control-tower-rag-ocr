# Routage des providers — V0.5

## Principe

Une page est l'unité d'appel multimodal. Le lot de 1 à 5 pages reste une unité d'orchestration et de contrôle, mais aucune réponse cloud ne doit fusionner silencieusement plusieurs pages.

## Décision

```text
page simple + texte natif
  → local

page complexe en local_fast
  → local + deferred

page complexe en balanced/cloud_turbo
  → cascade de providers

page en night_deep
  → cascade de providers, quelle que soit sa complexité
```

## États observables

Chaque `PageAnalysis.raw.routing` contient :

```json
{
  "decision": "cloud",
  "selected_provider": "openrouter_qwen",
  "profile": "cloud_turbo",
  "fallback_errors": []
}
```

## Résilience

Chaque provider possède :

- sémaphore de concurrence ;
- fenêtre glissante RPM ;
- retries ;
- backoff exponentiel ;
- jitter ;
- circuit breaker ;
- coût estimé par page.

Une erreur `408`, `409`, `425`, `429` ou `5xx` est considérée comme réessayable. Les erreurs permanentes passent immédiatement au provider suivant.

## Budget

Le budget est réservé avant l'appel et libéré si le provider échoue. Il empêche les appels concurrents de dépasser silencieusement le plafond configuré.

## Enrichissement différé

`enrich-document` ne crée pas un nouveau document. Il reprend le PDF stocké, analyse les pages signalées, met à jour les artefacts, reconstruit les chunks et appelle `replace_document_chunks` dans une transaction SQLite.
