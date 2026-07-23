# 9. Front, back et API

## Front

Le dossier `frontend/` contient une interface statique sans framework. Elle permet :

- vérifier la santé de l'API ;
- créer un projet ;
- planifier un document ;
- lancer une ingestion ;
- interroger un projet ;
- afficher les réponses JSON.

## Back

FastAPI démarre avec :

```bash
uvicorn control_tower.api.app:app --host 0.0.0.0 --port 8000
```

## Endpoints principaux

- `GET /health`
- `POST /projects`
- `POST /plan-document`
- `POST /ingest`
- `POST /query`
- `POST /benchmark-vision`
- `POST /enrich-document`
- `GET /projects/{project_id}/inspect`
- `GET /projects/{project_id}/documents/{document_id}`
- `GET/PATCH /projects/{project_id}/config`

Le front est servi sur `/ui/`.
