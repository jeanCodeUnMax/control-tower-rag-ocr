from __future__ import annotations

import os
from typing import Protocol

from control_tower.config import ConsolidationConfig


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIEmbeddingProvider:
    name = "openai"

    def __init__(self, config: ConsolidationConfig, client: object | None = None) -> None:
        self.config = config
        self.client = client or self._build_client()

    def _build_client(self) -> object:
        api_key = os.getenv(self.config.embedding_api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Clé API absente: définir {self.config.embedding_api_key_env} "
                "pour la consolidation sémantique."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "Les embeddings OpenAI nécessitent: pip install -e '.[vision]'."
            ) from exc
        return OpenAI(api_key=api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float]] = []
        batch_size = 128
        for start in range(0, len(texts), batch_size):
            response = self.client.embeddings.create(
                model=self.config.embedding_model,
                input=texts[start : start + batch_size],
                encoding_format="float",
            )
            vectors.extend([item.embedding for item in response.data])
        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Embeddings incomplets: attendu={len(texts)}, reçu={len(vectors)}"
            )
        return vectors
