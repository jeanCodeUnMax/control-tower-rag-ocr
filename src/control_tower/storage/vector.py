from __future__ import annotations

import logging
from typing import Protocol, Any

logger = logging.getLogger(__name__)


class VectorStore(Protocol):
    """Protocole pour stocker et rechercher des vecteurs."""
    
    def init_collection(self, collection_name: str, dimension: int) -> None:
        """Crée la collection si elle n'existe pas."""
        ...
        
    def upsert(self, collection_name: str, point_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        """Insère ou met à jour un vecteur avec ses métadonnées."""
        ...
        
    def search(self, collection_name: str, query_vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
        """Recherche les vecteurs les plus proches."""
        ...


class QdrantVectorStore(VectorStore):
    """Implémentation de VectorStore pour Qdrant."""
    
    def __init__(self, url: str = "http://localhost:6333", api_key: str | None = None) -> None:
        try:
            from qdrant_client import QdrantClient
            if url == "local":
                # Mode local sur disque (pas de serveur requis)
                self.client = QdrantClient(path=".control_tower/qdrant_db")
            else:
                self.client = QdrantClient(url=url, api_key=api_key)
        except ImportError as exc:
            raise RuntimeError(
                "qdrant-client n'est pas installé. "
                "Exécutez : pip install qdrant-client"
            ) from exc

    def init_collection(self, collection_name: str, dimension: int) -> None:
        from qdrant_client.models import Distance, VectorParams
        
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            )

    def upsert(self, collection_name: str, point_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        from qdrant_client.models import PointStruct
        
        self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

    def search(self, collection_name: str, query_vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
        try:
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit
            )
            # On renvoie les payloads avec le score
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    **(hit.payload or {})  # type: ignore
                }
                for hit in response.points
            ]
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Impossible de contacter Qdrant ({exc}). Retour de sources vides.")
            return []
