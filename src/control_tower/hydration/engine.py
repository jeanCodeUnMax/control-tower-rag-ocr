from __future__ import annotations

from control_tower.domain.models import SearchHit


class HydrationEngine:
    def hydrate(self, hits: list[SearchHit], budget_chars: int = 3000) -> dict:
        items: list[dict] = []
        used = 0
        for hit in hits:
            text = hit.chunk.text
            if used + len(text) > budget_chars:
                break
            items.append(
                {
                    "chunk_id": hit.chunk.id,
                    "score": hit.score,
                    "text": text,
                    "questions": hit.chunk.questions,
                    "tensions": hit.chunk.tensions,
                }
            )
            used += len(text)
        return {"items": items, "used_chars": used, "budget_chars": budget_chars}
