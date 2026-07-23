# 4. Comment régler

Chaque projet possède son propre `config.yaml`.

```bash
control-tower config-show --project mon-projet
control-tower config-set --project mon-projet atomizer.max_chars 700
control-tower config-set --project mon-projet retrieval.top_k 8
control-tower config-set --project mon-projet vision.max_cost_per_document_usd 15
```

## Réglages importants

- `atomizer.max_chars` : taille maximale des chunks ;
- `atomizer.overlap_chars` : chevauchement ;
- `ocr.mode` : `auto`, `text_only`, `force_ocr` ;
- `ocr.languages` : par exemple `fra+eng` ;
- `processing.max_pages_per_batch` : limite haute des lots ;
- `vision.profile` : stratégie d'analyse ;
- `vision.max_cost_per_document_usd` : plafond estimé ;
- `retrieval.top_k` : résultats retournés.

## Règle de réglage

Ne jamais ajuster 10 paramètres simultanément. Modifier un paramètre, ingérer un petit corpus, observer les artefacts, puis comparer.
