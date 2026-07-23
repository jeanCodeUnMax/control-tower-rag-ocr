# 7. BDD et séparation par project_id

La racine est définie par `CONTROL_TOWER_HOME`.

```text
.control_tower/
└── projects/
    ├── projet-a/
    │   ├── config.yaml
    │   ├── project.json
    │   ├── documents/
    │   ├── artifacts/
    │   ├── logs/events.jsonl
    │   ├── benchmarks/
    │   └── state/knowledge.db
    └── projet-b/
        └── ...
```

## Garanties

- une BDD SQLite par projet ;
- aucun mélange de chunks entre deux `project_id` ;
- configuration indépendante ;
- artefacts et journaux indépendants ;
- suppression ou archivage possible projet par projet.

## Tables principales

- `documents` : métadonnées du document ;
- `chunks` : unités atomiques ;
- `events` ou journal JSONL : opérations ;
- états de consolidation et dépendances selon les modules.

## Limite actuelle

La consolidation globale inter-documents doit encore être durcie. Le hash et le versionnement documentaire sont prioritaires dans la V0.6.
