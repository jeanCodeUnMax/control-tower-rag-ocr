# Déploiement

- Local : `uvicorn ... --reload`
- Docker : `docker compose up --build`
- Production : placer l'API derrière HTTPS, authentification, reverse proxy et stockage persistant.

Ne pas exposer la V0.5 publiquement sans appliquer les points de sécurité décrits dans le wiki.
