# 6. Architecture des dossiers et services

```text
control-tower-rag/
├── frontend/                 Interface web statique
├── src/control_tower/
│   ├── api/                  API FastAPI
│   ├── brain/                Planification logique
│   ├── consolidation/        Contrats de consolidation
│   ├── hydration/            Construction du contexte utile
│   ├── ingestion/            Pipeline principal
│   ├── knowledge/            État et dépendances
│   ├── models/               Objets métier Pydantic
│   ├── ocr/                  Texte, PDF, image, Tesseract
│   ├── optimization/         Déduplication et canonisation
│   ├── policies/             Policy Checker
│   ├── processing/           Lots, vision, providers, retries
│   ├── rag/                  Recherche et hydratation
│   ├── reasoning/            Maïeutique, Kant, pseudocode
│   ├── registry/             Registre de modules
│   ├── storage/              SQLite et workspaces
│   └── validation/           Consensus et validation
├── config/                   Configuration par défaut
├── schemas/                  JSON Schemas
├── templates/                Templates d'analyse
├── scripts/                  Installation et preuves
├── tests/                    Tests automatisés
├── docs/                     Documentation et wiki
├── proofs/                   Rapports de validation
└── deploy/                   Fichiers de déploiement
```

## Front

Le front est volontairement léger. Il appelle l'API et ne contient aucune logique métier.

## Back

Le back FastAPI expose les opérations du service. Le `ControlTowerService` sert de façade applicative. Le pipeline orchestre les composants métier.
