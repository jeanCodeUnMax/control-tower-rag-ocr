from __future__ import annotations

import re

from control_tower.domain.models import AtomicChunk


class PseudocodeAnalyzer:
    """Extrait des lignes procédurales sans inventer un algorithme complet."""

    _procedural = re.compile(
        r"(^|\b)(étape|step|si|sinon|pour chaque|tant que|retourner|vérifier|calculer|"
        r"charger|enregistrer|extraire|analyser|indexer|then|else|for each|while|return)\b",
        re.IGNORECASE,
    )

    def analyze_text(self, text: str) -> list[str]:
        candidates: list[str] = []
        for raw in re.split(r"\n+|(?<=[.!?])\s+", text):
            line = raw.strip(" \t-*•")
            if not line:
                continue
            if self._procedural.search(line) or "->" in line or "→" in line:
                candidates.append(line[:500])
        return candidates[:12]

    def enrich(self, chunk: AtomicChunk) -> AtomicChunk:
        return chunk.model_copy(update={"pseudocode": self.analyze_text(chunk.text)})
