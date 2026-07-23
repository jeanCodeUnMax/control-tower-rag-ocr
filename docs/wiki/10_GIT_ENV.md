# 10. Git, environnements et secrets

## Démarrer le dépôt

```bash
git init
git add .
git commit -m "feat: initial Control Tower RAG repository"
```

## Branches

- `main` : stable ;
- `develop` : intégration ;
- `feature/...` : fonctionnalité ;
- `fix/...` : correction ;
- `docs/...` : documentation.

## Secrets

Copier `.env.example` vers `.env`. Ne jamais committer `.env`.

Variables :

- `CONTROL_TOWER_HOME`
- `CONTROL_TOWER_API_KEY`
- `OPENROUTER_API_KEY`
- `GEMINI_API_KEY`
- `OLLAMA_API_KEY`
- `OPENAI_API_KEY`

## Fichiers ignorés

`.gitignore` exclut les environnements virtuels, caches, données runtime, secrets, logs et fichiers IDE.
