from __future__ import annotations

from control_tower.domain.models import AtomicChunk


class KantGloveAnalyzer:
    def enrich(self, chunk: AtomicChunk) -> AtomicChunk:
        lower = chunk.text.lower()
        tensions: list[str] = list(chunk.tensions)
        tensions.append("facts_vs_interpretations")
        if "pour" in lower or "afin" in lower:
            tensions.append("means_vs_ends")
        if "donc" in lower or "parce" in lower:
            tensions.append("causation_vs_correlation")
        if "chaque" in lower or "toujours" in lower:
            tensions.append("universalization")
        return chunk.model_copy(update={"tensions": sorted(set(tensions))})
