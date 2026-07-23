# ADR-0001 — Monolithe modulaire avant microservices

## Décision

Démarrer par un monolithe modulaire Python, avec frontières internes strictes et contrats sérialisables.

## Raisons

Les microservices ajouteraient réseau, déploiement, observabilité distribuée et cohérence éventuelle avant la validation du produit. Les ports définis permettront d'extraire plus tard les modules réellement sous pression.
