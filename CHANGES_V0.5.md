# Changements V0.5

## Objectif

Proposer une alternative réelle entre ingestion immédiate économique et enrichissement multimodal performant, sans transformer une panne API ou une limite de débit en perte de pages.

## Ajouts

- profils `local_fast`, `balanced`, `cloud_turbo`, `night_deep` ;
- routeur page par page ;
- providers OpenAI-compatibles pour OpenRouter et Ollama ;
- provider Gemini REST ;
- configuration de plusieurs endpoints dans le YAML ;
- limiteur RPM et concurrence par provider ;
- retries exponentiels, jitter et prise en compte de `Retry-After` ;
- circuit breaker ;
- cascade et fallback local ;
- budget maximal par document ;
- rapport `provider_report.json` ;
- commande `plan-document` ;
- commande `benchmark-vision` ;
- commande `profile-set` ;
- commande `enrich-document` ;
- remplacement atomique des chunks d'un document ;
- prise en charge des index de liste dans `config-set` ;
- endpoints API correspondants ;
- tests des contrats HTTP et scénarios de panne.

## Comportement par défaut

- `vision.provider=router` ;
- `vision.profile=local_fast` ;
- aucun provider externe activé ;
- aucune clé API nécessaire ;
- les pages complexes sont différées, jamais masquées.

## Validation

- 30 tests automatisés réussis ;
- tests V0.2, V0.3 et V0.4 conservés ;
- preuve locale ingestion → pages différées → enrichissement → remplacement de l'index ;
- wheel Python 0.5.0 construit et inspecté.
