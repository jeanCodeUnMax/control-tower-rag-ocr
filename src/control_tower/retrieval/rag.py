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

    def ask(self, question: str, top_k: int = 5) -> dict[str, Any]:
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

        # 4. Construire le Prompt
        system_prompt = (
            "Tu es 'Control Tower', un assistant IA expert en analyse documentaire. "
            "Ton rôle est de répondre aux questions de l'utilisateur de manière précise, "
            "en te basant EXCLUSIVEMENT sur les documents fournis dans le contexte ci-dessous.\n\n"
            "RÈGLES IMPORTANTES :\n"
            "- Si la réponse ne se trouve pas dans le contexte, dis-le clairement. N'invente rien.\n"
            "- Cite toujours tes sources à la fin ou dans le corps de ta réponse (ex: 'D'après le document X...').\n"
            "- Sois concis et structuré (utilise des listes à puces si nécessaire)."
        )

        user_prompt = f"CONTEXTE RÉCUPÉRÉ DES DOCUMENTS :\n{context_text}\n\nQUESTION DE L'UTILISATEUR :\n{question}"

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
