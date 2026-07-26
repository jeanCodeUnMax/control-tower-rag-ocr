from __future__ import annotations

import logging
from urllib.parse import urlparse

from control_tower.domain.models import AtomicChunk

logger = logging.getLogger(__name__)


class WebAnalyzer:
    """
    Agent Chercheur Web (La Douane).
    Effectue une recherche Internet et filtre strictement les domaines autorisés (Whitelisting).
    """

    def __init__(self) -> None:
        # La Douane (Domaines de confiance)
        self.trusted_domains = [
            "wikipedia.org",
            "gov",       # Tous les .gov
            "edu",       # Tous les .edu
            "arxiv.org",
            "ncbi.nlm.nih.gov", # PubMed
            "nature.com",
            "science.org",
            "ieee.org"
        ]

    def is_trusted(self, url: str) -> bool:
        """Vérifie si l'URL passe la Douane (Whitelisting)."""
        try:
            domain = urlparse(url).netloc.lower()
            for trusted in self.trusted_domains:
                if trusted in domain:
                    return True
            return False
        except Exception:
            return False

    def extract_keywords(self, text: str) -> str:
        """Méthode simpliste pour extraire des mots clés du texte."""
        # Dans une V2, on utiliserait un LLM pour extraire l'essence.
        # Pour le MVP, on prend les 100 premiers caractères.
        return text[:100].replace("\n", " ")

    def enrich(self, chunk: AtomicChunk) -> AtomicChunk:
        """Effectue la recherche web pour le chunk et l'enrichit si pertinent."""
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.warning("duckduckgo-search non installé. Pip install duckduckgo-search pour activer le web.")
            return chunk

        keywords = self.extract_keywords(chunk.text)
        if len(keywords.strip()) < 10:
            return chunk

        try:
            import time
            import random
            time.sleep(random.uniform(2.0, 3.5)) # Anti-RateLimit DDG
            with DDGS() as ddgs:
                # On cherche les 5 premiers résultats
                results = list(ddgs.text(keywords, max_results=5))
                
                valid_enrichments = []
                valid_sources = []

                for res in results:
                    url = res.get("href", "")
                    body = res.get("body", "")
                    
                    if self.is_trusted(url):
                        valid_enrichments.append(body)
                        valid_sources.append(url)
                        
                        # Limiter à 2 sources maximum par chunk pour éviter le bruit
                        if len(valid_sources) >= 2:
                            break

                if valid_enrichments:
                    # On met à jour le chunk avec les données du web (sécurisées par la douane)
                    return chunk.model_copy(update={
                        "web_enrichments": chunk.web_enrichments + valid_enrichments,
                        "web_sources": list(set(chunk.web_sources + valid_sources))
                    })
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche web: {e}")
            
        return chunk
