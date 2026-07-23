# Carte du système

```mermaid
flowchart LR
    U[CLI / API] --> B[Brain]
    B --> R[Registry]
    B --> P[Policy Checker]
    P --> I[Ingestion]
    I --> O[OCR Port]
    O --> A[Atomic Chunker]
    A --> S[Semantic Enrichment]
    S --> DB[(Project SQLite)]
    DB --> SM[State Manager]
    DB --> H[Hydration Engine]
    H --> Q[Query Result]
    DB -. propositions .-> C[Deferred Consolidator]
    C -. review / rollback .-> DB
```

## Frontières

- Le Brain produit un plan; il n'exécute pas les capacités métier.
- Le Registry décrit les capacités; il ne les orchestre pas.
- Le Policy Checker décide avant l'effet de bord.
- Chaque projet possède sa propre base SQLite, ses documents et ses logs.
- Le Consolidator propose; il ne réécrit jamais silencieusement la connaissance.
