# Audit contradictoire — Control Tower RAG V0.5

## Verdict

La V0.5 est un prototype avancé et testable, mais elle n'est pas terminée ni prête pour une exploitation longue sans surveillance.

- Architecture / séparation des responsabilités : 3.5/5
- Ingestion PDF locale : 3.5/5
- Résilience dans un même processus : 3.5/5
- Reprise après arrêt/redémarrage : 1/5
- Déduplication globale : 2/5
- RAG sémantique / vectoriel : 1/5
- Auditabilité / observabilité : 2.5/5
- Sécurité API : 1.5/5
- Tests : 4/5 unitaires, 1.5/5 intégration réelle cloud
- Note globale : 3.0/5

## Preuves exécutées

- `pytest -q` : 30 tests réussis.
- Couverture : 82 % globale.
- Compilation Python : réussie.
- Avertissements observés : connexions SQLite non fermées.
- Test supplémentaire : ingestion deux fois du même fichier => deux documents, deux chunks canoniques, deux résultats de recherche. La déduplication ne traverse pas les documents.

## Défauts bloquants ou importants

### P0 — Connexions SQLite non fermées

`SQLiteStore._connect()` retourne une connexion utilisée par `with`, mais le context manager SQLite commit/rollback sans garantir la fermeture. La campagne de couverture a produit de nombreux `ResourceWarning: unclosed database`.

Correction : créer un context manager qui ferme explicitement la connexion, et ajouter un test avec warnings transformés en erreurs.

### P0 — Aucune reprise réelle après redémarrage

Le registre `ingestion_ledger.json` est écrit après chaque lot, mais `LongPDFProcessor.process()` crée toujours un nouveau registre et ne recharge jamais l'ancien. Un arrêt à la page 437 ne reprend pas à 438.

Correction : commande `resume-ingestion`, identifiant de job persistant, rechargement du ledger, validation du hash source/config, réexécution uniquement des pages non terminées.

### P0 — Déduplication limitée au document courant

Le `Consolidator` ne reçoit que les chunks du document en cours. Réingérer le même fichier produit un nouveau `document_id`; les doublons restent tous indexables dans SQLite.

Correction : registre documentaire par SHA-256, idempotence, versions, consolidation inter-documents et canonique au niveau projet.

### P0 — Ce n'est pas encore un RAG sémantique

La recherche charge tous les chunks et calcule un recouvrement lexical en Python. Il n'existe pas de vector store ni d'embeddings de recherche. Les embeddings présents servent uniquement à une consolidation sémantique optionnelle.

Correction : abstraction `Retriever`, FTS5 comme base rapide, puis embeddings + index vectoriel, évaluation rappel/précision.

### P1 — Preuve 800 pages insuffisamment représentative

La preuve 800 pages utilise un PDF synthétique avec texte natif répétitif, mode vision local, seulement quelques images simples. Elle valide la couverture des pages et la consolidation, pas 800 pages scannées, manuscrites ou multimodales.

Correction : corpus de référence annoté avec scans, tableaux, graphes, schémas, manuscrit et pages corrompues.

### P1 — Succès partiels d'un lot perdus

Si une page cloud échoue dans `analyze_batch`, l'exception remonte pour tout le lot. Des pages déjà réussies peuvent être facturées mais non persistées, puis retraitées après division du lot.

Correction : persistance page par page, résultat partiel structuré, retry uniquement des pages fautives.

### P1 — Budget estimé, pas réellement garanti

Le coût par page est codé en configuration. Les retries ne réservent pas chaque coût et une requête échouée peut être facturée malgré la libération du budget local.

Correction : lire l'usage réel des réponses, comptabiliser chaque tentative, marge de sécurité, arrêt avant soumission.

### P1 — API non sécurisée

L'API ne possède ni authentification ni autorisation et accepte un chemin de fichier arbitraire du serveur. Exposée sur un réseau, elle peut lire des fichiers accessibles au processus et modifier la configuration.

Correction : localhost par défaut, authentification, racine d'import autorisée, upload contrôlé, validation MIME, limites et permissions.

### P1 — Écritures non transactionnelles

Le ledger est atomique, mais plusieurs artefacts, le YAML, le journal JSONL et l'index SQLite ne forment pas une transaction globale. Un crash peut laisser des artefacts et une base incohérents.

Correction : manifeste de job avec phase/commit, fichiers temporaires, commit final atomique, réconciliation au démarrage.

### P2 — Fonctions d'orchestration trop longues et dupliquées

- `IngestionPipeline.ingest` : environ 280 lignes.
- `ControlTowerService.enrich_document` : environ 225 lignes.
- `LongPDFProcessor.process` : environ 184 lignes.

L'atomisation, l'enrichissement sémantique et la consolidation sont dupliqués entre ingestion et enrichissement.

Correction : extraire `ChunkBuildService`, `ArtifactRepository`, `DocumentIndexTransaction`, `PageJobRunner`.

### P2 — Observabilité incomplète

Le JSONL ne possède pas de lock, pas d'ID de job cohérent propagé, pas de métriques persistantes normalisées, pas de logs structurés avec niveaux. Les statistiques concurrentes des providers ne sont pas protégées intégralement.

Correction : `job_id`, `trace_id`, événements versionnés, writer sérialisé, métriques par page/provider, export JSON/Prometheus optionnel.

### P2 — Base SQLite non durcie

Pas de WAL, `busy_timeout`, migrations, index `document_id/content_hash`, ni gestion explicite de concurrence. `replace_document_chunks` construit une clause `IN` de taille proportionnelle au nombre de chunks.

Correction : migrations versionnées, WAL, index, transactions explicites, suppression par sous-requête/document_id.

### P2 — Modules conceptuels surévalués

Le pseudocode est une extraction regex, la maïeutique ajoute deux ou trois questions fixes, et le Gant de Kant applique quelques mots-clés. Le Brain ne fait qu'énumérer un plan fixe. Le consensus-less n'est pas relié au pipeline.

Correction : renommer ces modules en `heuristic_*` ou implémenter de vrais contrats d'analyse avec évaluations mesurées.

## Patterns récurrents observés

1. Ajouter une nouvelle capacité avant de durcir la précédente.
2. Créer un artefact de contrôle sans implémenter tout le cycle de vie associé : checkpoint sans reprise.
3. Valider les contrats avec des fakes, puis présenter l'intégration comme presque opérationnelle.
4. Dupliquer la logique lors de l'ajout d'un second parcours au lieu d'extraire un service commun.
5. Employer des noms ambitieux pour des heuristiques simples.
6. Confondre complétude technique (800 numéros de pages) et qualité sémantique (800 pages réellement comprises).
7. Transformer les exceptions en fallback local, ce qui protège le flux mais peut masquer une baisse majeure de qualité.

## Problèmes ponctuels, non structurels

- Ancienne installation éditable chargée pendant une validation.
- Environnement virtuel incomplet pour `setuptools`.
- Ruff absent du conteneur.

Ces incidents sont ponctuels, mais ils justifient un environnement reproductible avec lockfile et CI.

## Découpage recommandé de la V0.6 — durcissement uniquement

1. Fermer SQLite et activer warnings-as-errors.
2. Ajouter idempotence SHA-256 et versions documentaires.
3. Implémenter reprise après redémarrage.
4. Persister chaque page avant de terminer un lot.
5. Refactoriser la construction des chunks partagée ingestion/enrichissement.
6. Sécuriser l'API et borner les chemins d'entrée.
7. Ajouter FTS5 et préparer l'interface vectorielle.
8. Construire un benchmark représentatif de 50 pages annotées.
9. Exécuter une vraie API cloud avec quota minimal et enregistrer coût/latence/qualité.
10. Mettre en place CI : tests, couverture minimale, lint, type-check, sécurité dépendances.

Aucune nouvelle brique conceptuelle ne devrait être ajoutée avant la clôture de ces dix points.
