from __future__ import annotations

import logging
from typing import Protocol, Any

logger = logging.getLogger(__name__)


class EmbeddingProvider(Protocol):
    """Protocole pour la génération d'embeddings à partir de texte."""
    
    def embed_text(self, text: str) -> list[float]:
        """Convertit un texte en vecteur."""
        ...
        
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Convertit une liste de textes en vecteurs."""
        ...
        
    @property
    def dimension(self) -> int:
        """Retourne la dimension du vecteur généré."""
        ...


class BaseAPIEmbeddingProvider:
    """Classe de base commune pour les providers API (OpenRouter, Mistral, Gemini)."""
    
    def __init__(self, model_name: str, api_key: str | None = None) -> None:
        self.model_name = model_name
        self.api_key = api_key
        # Ces valeurs doivent être surchargées par les classes filles
        self._dimension = 768  # Valeur par défaut
        
    @property
    def dimension(self) -> int:
        return self._dimension


class LocalEmbeddingProvider(EmbeddingProvider):
    """Provider utilisant SentenceTransformers ou llama.cpp en local."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        try:
            import os
            hf_token = os.environ.get("HF_TOKEN")
            if hf_token and hf_token.startswith("hf_"):
                try:
                    from huggingface_hub import login
                    import logging
                    logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
                    login(token=hf_token)
                except Exception as e:
                    print(f"⚠️ Erreur d'authentification HuggingFace (Token ignoré) : {e}")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers n'est pas installé. "
                "Exécutez : pip install sentence-transformers"
            ) from exc

    def embed_text(self, text: str) -> list[float]:
        vector = self.model.encode(text, show_progress_bar=False)
        return vector.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, show_progress_bar=False)
        return vectors.tolist()
        
    @property
    def dimension(self) -> int:
        return self.model.get_embedding_dimension()


class HephaistosBridgeProvider(EmbeddingProvider):
    """Provider factice : l'embedding est déporté au serveur MCP Zvec."""
    
    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension
        
    def embed_text(self, text: str) -> list[float]:
        return []
        
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[] for _ in texts]
        
    @property
    def dimension(self) -> int:
        return self._dimension

def get_embedding_provider(provider_type: str, model_name: str, **kwargs: Any) -> EmbeddingProvider:
    """Factory pour obtenir le bon provider d'embeddings."""
    if provider_type == "local":
        return LocalEmbeddingProvider(model_name)
    if provider_type == "zvec":
        return HephaistosBridgeProvider(dimension=384)
    if provider_type == "qdrant_bridge":
        return HephaistosBridgeProvider(dimension=1536)
        
    raise NotImplementedError(f"Le provider d'embedding '{provider_type}' n'est pas encore totalement implémenté.")
