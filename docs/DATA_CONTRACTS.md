# Contrats de données

Les fichiers dans `schemas/` servent de référence inter-langages. Les modèles Pydantic dans `src/control_tower/domain/models.py` sont l'implémentation Python V0.

Toute évolution incompatible exige :

- un nouveau numéro de version;
- une migration;
- un test de compatibilité;
- une décision d'architecture si elle touche plusieurs modules.

## V0.4 — Contrats PDF long

- `schemas/ingestion_ledger.schema.json` : couverture exhaustive des pages et lots ;
- `schemas/page_analysis.schema.json` : analyse multimodale structurée d'une page ;
- `schemas/consolidation_report.schema.json` : bilan brut/canonique/doublons ;
- `schemas/visual_asset.schema.json` : image ou dessin relié à une page et à son canonique ;
- `schemas/atomic_chunk.schema.json` : provenance, statut d'indexation et occurrences de preuve.
