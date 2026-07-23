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
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers n'est pas installé. "
                "Exécutez : pip install sentence-transformers"
            ) from exc

    def embed_text(self, text: str) -> list[float]:
        vector = self.model.encode(text)
        return vector.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts)
        return vectors.tolist()
        
    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()


def get_embedding_provider(provider_type: str, model_name: str, **kwargs: Any) -> EmbeddingProvider:
    """
    Factory pour obtenir le bon provider d'embeddings.
    provider_type: 'local', 'gemini', 'openrouter', 'mistral'
    """
    if provider_type == "local":
        return LocalEmbeddingProvider(model_name)
    # Les autres providers (API) nécessiteront une implémentation réseau via httpx
    # Pour l'instant, on lève une NotImplementedError pour indiquer le reste du travail.
    raise NotImplementedError(f"Le provider d'embedding '{provider_type}' n'est pas encore totalement implémenté.")
