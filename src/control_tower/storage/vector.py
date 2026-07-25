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
        
    def delete(self, collection_name: str, point_ids: list[str]) -> None:
        """Supprime des vecteurs par leur ID."""
        ...


class QdrantVectorStore(VectorStore):
    """Implémentation de VectorStore pour Qdrant."""
    
    def __init__(self, path: str | None = None, url: str = "http://localhost:6333", api_key: str | None = None) -> None:
        try:
            from qdrant_client import QdrantClient
            if path:
                self.client = QdrantClient(path=path)
            elif url == "local":
                # Fallback legacy
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

    def delete(self, collection_name: str, point_ids: list[str]) -> None:
        from qdrant_client import models
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=point_ids)
            )
        except Exception as exc:
            logging.getLogger(__name__).warning(f"Impossible de supprimer de Qdrant ({exc}).")

    def delete_by_document_id(self, collection_name: str, document_id: str) -> None:
        from qdrant_client import models
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=document_id),
                            )
                        ]
                    )
                )
            )
        except Exception as exc:
            logging.getLogger(__name__).warning(f"Impossible de purger les vecteurs de Qdrant pour {document_id} ({exc}).")

class ZvecRestStore(VectorStore):
    """Implémentation de VectorStore qui délègue à rag_rest_bridge.py (port 8001)."""
    
    def __init__(self, url: str = "http://localhost:8001") -> None:
        self.url = url.rstrip("/")
        
    def init_collection(self, collection_name: str, dimension: int) -> None:
        import urllib.request
        import json
        try:
            req = urllib.request.Request(
                f"{self.url}/collections",
                data=json.dumps({"name": collection_name, "enableHybrid": True}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            logger.warning(f"Zvec init_collection failed: {e}")

    def upsert(self, collection_name: str, point_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        import urllib.request
        import json
        try:
            text = payload.get("text", "")
            req = urllib.request.Request(
                f"{self.url}/collections/{collection_name}/documents",
                data=json.dumps({
                    "id": point_id,
                    "text": text,
                    "metadata": payload
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            logger.warning(f"Zvec upsert failed: {e}")

    def search(self, collection_name: str, query_vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
        # La vraie requête texte n'est pas passée dans query_vector
        return []

    def delete(self, collection_name: str, point_ids: list[str]) -> None:
        import urllib.request
        import json
        try:
            req = urllib.request.Request(
                f"{self.url}/collections/{collection_name}/documents",
                data=json.dumps({"ids": point_ids}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="DELETE"
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            logger.warning(f"Zvec delete failed: {e}")

    def delete_by_document_id(self, collection_name: str, document_id: str) -> None:
        # Zvec n'a pas forcément de route delete_by_payload standard dans le bridge actuel
        logger.info(f"Purge par document_id non supportée nativement par ZvecRestStore (document_id: {document_id}).")
