from __future__ import annotations

import logging
from typing import Any

from control_tower.generation.llm import LLMProvider
from control_tower.semantics.embeddings import EmbeddingProvider
from control_tower.storage.vector import VectorStore

logger = logging.getLogger(__name__)


class RAGEngine:
    """Moteur central pour orchestrer le Retrieval-Augmented Generation (RAG)."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingProvider,
        llm: LLMProvider,
        collection_name: str,
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.llm = llm
        self.collection_name = collection_name

    def ask(self, question: str, top_k: int = 5, paradigm: str = "executive") -> dict[str, Any]:
        """Pose une question au système et retourne la réponse augmentée par les documents."""
        # 1. Vectoriser la question
        query_vector = self.embedder.embed_text(question)

        # 2. Rechercher dans le Vector Store
        results = self.vector_store.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
        )

        if not results:
            return {
                "answer": "Je suis désolé, je n'ai trouvé aucune information pertinente dans les documents.",
                "sources": [],
            }

        # 3. Construire le contexte
        context_parts = []
        sources = []
        
        for i, hit in enumerate(results, 1):
            # hit est un dictionnaire qui contient 'id', 'score', et les champs du payload
            text = hit.get("text", "")
            doc_id = hit.get("document_id", "Inconnu")
            score = hit.get("score", 0.0)
            
            context_parts.append(f"--- Source {i} (Document: {doc_id}) ---\n{text}\n")
            sources.append({"document_id": doc_id, "score": score, "text_snippet": text[:100]})

        context_text = "\n".join(context_parts)

        # 4. Construire le Prompt selon le paradigme
        from control_tower.generation.paradigms import COGNITIVE_PARADIGMS
        if paradigm not in COGNITIVE_PARADIGMS:
            import logging
            logging.getLogger(__name__).warning(f"Paradigme '{paradigm}' inconnu. Utilisation de 'executive' par défaut.")
            paradigm = "executive"
            
        system_prompt = COGNITIVE_PARADIGMS[paradigm]

        user_prompt = f"CONTEXTE RÉCUPÉRÉ DES DOCUMENTS :\n{context_text}\n\nQUESTION DE L'UTILISATEUR :\n{question}\n\nRéponds en appliquant strictement ton paradigme."

        # 5. Appeler le LLM
        try:
            answer = self.llm.generate(prompt=user_prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.error(f"Erreur lors de la génération LLM: {e}")
            answer = f"Une erreur est survenue lors de la communication avec le modèle de langage : {e}"

        return {
            "answer": answer,
            "sources": sources,
        }
