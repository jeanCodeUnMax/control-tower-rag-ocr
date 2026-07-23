# Parcours du code — V0.2

Ce document montre le chemin réellement exécuté. Aucun composant marqué `available` ou
`not_implemented` n'est présenté comme actif.

## 1. Création d'un projet

Commande :

```bash
control-tower init-project demo
```

Chemin : `cli.py -> ControlTowerService.init_project() -> WorkspaceManager.create()`.

Effets réels :

- création de `.control_tower/projects/demo/` ;
- création de `project.json` ;
- création de `config.yaml` ;
- création de `documents/`, `artifacts/`, `logs/`, `state/`.

## 2. Modification d'un réglage

```bash
control-tower config-set --project demo atomizer.max_chars 350
control-tower config-set --project demo features.maieutic false
control-tower config-show --project demo
```

`WorkspaceManager.update_config()` modifie le YAML, puis `ProjectConfig.model_validate()`
refuse une valeur invalide. Le pipeline recharge ce fichier à chaque ingestion.

## 3. Ingestion

Chemin :

```text
CLI/API
  -> ControlTowerService.ingest
  -> IngestionPipeline.ingest
  -> WorkspaceManager.load_config
  -> Brain.plan_ingestion (plan journalisé)
  -> PolicyChecker.check_ingestion
  -> TextOCRProvider.extract
  -> AtomicChunker(config.atomizer.*)
  -> MaieuticAnalyzer si activé
  -> KantGloveAnalyzer si activé
  -> SQLiteStore.save_chunks
  -> events.jsonl
```

## 4. Recherche

Chemin :

```text
ControlTowerService.query
  -> WorkspaceManager.load_config
  -> SQLiteStore.search (lexical, pas vectoriel)
  -> HydrationEngine.hydrate(config.retrieval.hydration_budget_chars)
```

## 5. Voir la vérité du système

```bash
control-tower inspect-project --project demo
```

La sortie distingue :

- `wired` : utilisé par le chemin principal ;
- `available` : code présent mais pas encore branché ;
- `not_implemented` : port prévu, aucun faux traitement.

## 6. Preuve automatisée

`tests/test_project_config.py` change la taille des chunks et désactive les enrichissements.
Le test vérifie ensuite dans SQLite que les fragments ont réellement changé et que les champs
`questions` et `tensions` sont vides.
