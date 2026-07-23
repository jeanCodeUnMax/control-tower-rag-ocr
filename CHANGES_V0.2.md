# Changements V0.2

Corrections réalisées après audit du premier ZIP :

- `config.yaml` créé dans chaque workspace ;
- chargement et validation Pydantic du YAML à chaque ingestion/requête ;
- commandes `config-show`, `config-set` et `inspect-project` ;
- Policy Checker piloté par la configuration du projet ;
- taille et chevauchement des chunks réellement configurables ;
- activation/désactivation réelle de `maieutic` et `kant_glove` ;
- budget d'hydratation et `top_k` réellement configurables ;
- plan du Brain journalisé dans `events.jsonl` ;
- statuts explicites `wired`, `available`, `not_implemented` ;
- correction du chevauchement qui pouvait couper un mot ;
- normalisation de la ponctuation dans la recherche lexicale ;
- endpoint API de lecture/modification de config et inspection ;
- script reproductible `python scripts/prove_it.py` ;
- 7 tests automatisés.

## Limites conservées volontairement

PDF/image OCR, embeddings vectoriels et réponse LLM ne sont pas implémentés. Le consensus-less
et la consolidation existent mais ne sont pas branchés automatiquement.
