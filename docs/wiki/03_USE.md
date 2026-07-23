# 3. Comment utiliser

## Créer un projet

```bash
control-tower init-project mon-projet
```

## Prévoir le traitement

```bash
control-tower plan-document --project mon-projet ./documents/manuel.pdf
```

## Choisir un profil

```bash
control-tower profile-set --project mon-projet local_fast
# ou balanced, cloud_turbo, night_deep
```

## Ingérer

```bash
control-tower ingest --project mon-projet ./documents/manuel.pdf
```

Conserver le `document_id` retourné.

## Contrôler le résultat

```bash
control-tower inspect-project --project mon-projet
control-tower inspect-document --project mon-projet --document-id DOCUMENT_ID
```

## Interroger

```bash
control-tower query --project mon-projet --text "Comment fonctionne le système ?" --top-k 5
```

## Enrichir plus tard

```bash
control-tower enrich-document --project mon-projet --document-id DOCUMENT_ID --profile night_deep
```
