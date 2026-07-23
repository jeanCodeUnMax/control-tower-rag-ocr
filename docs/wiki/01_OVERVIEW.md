# 1. Vue d'ensemble

Control Tower RAG est une tour de contrôle documentaire destinée à ingérer des PDF longs sans perdre de pages, à extraire leur contenu, à isoler les données par projet, puis à consolider les répétitions avant recherche.

## Objectif

Transformer un document entrant en artefacts contrôlables :

```text
PDF / image / texte
  -> préflight
  -> extraction page par page
  -> OCR ou vision selon le besoin
  -> modules d'analyse
  -> chunks atomiques
  -> consolidation
  -> stockage isolé par project_id
  -> recherche et hydratation
```

## Principes

- aucune page silencieusement ignorée ;
- un projet correspond à un workspace et une BDD dédiés ;
- les appels cloud sont optionnels et configurables ;
- les répétitions sont rattachées à une connaissance canonique ;
- tous les résultats importants sont persistés en JSON ;
- un document n'est indexé que si les critères de complétude sont satisfaits.
