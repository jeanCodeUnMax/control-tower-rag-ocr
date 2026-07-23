from __future__ import annotations

from control_tower.domain.models import AtomicChunk


class MaieuticAnalyzer:
    def enrich(self, chunk: AtomicChunk) -> AtomicChunk:
        questions = list(chunk.questions)
        questions.extend(
            [
                "Quelle hypothèse implicite soutient ce fragment ?",
                "Quelle information manque pour le vérifier ?",
            ]
        )
        if "doit" in chunk.text.lower() or "toujours" in chunk.text.lower():
            questions.append("Dans quelles conditions cette règle pourrait-elle ne pas s'appliquer ?")
        return chunk.model_copy(update={"questions": list(dict.fromkeys(questions))})
