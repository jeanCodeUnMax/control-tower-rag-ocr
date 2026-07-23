from __future__ import annotations

import hashlib
import re
from uuid import uuid4

from control_tower.domain.models import AtomicChunk


def _sentences(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"(?<=[.!?])\s+|\n+", text) if item.strip()]


def _tail_on_word_boundary(text: str, max_chars: int) -> str:
    """Retourne une fin de texte sans commencer au milieu d'un mot."""
    if max_chars <= 0 or len(text) <= max_chars:
        return text if max_chars > 0 else ""
    tail = text[-max_chars:]
    first_space = tail.find(" ")
    return tail[first_space + 1 :].strip() if first_space >= 0 else ""


class AtomicChunker:
    def __init__(self, max_chars: int | None = None, overlap_chars: int | None = None) -> None:
        self.max_chars = max_chars or 700
        self.overlap_chars = overlap_chars if overlap_chars is not None else 80

    def split(
        self,
        project_id: str,
        document_id: str,
        text: str,
        *,
        start_ordinal: int = 0,
        source_pages: list[int] | None = None,
        extraction_method: str | None = None,
    ) -> list[AtomicChunk]:
        if not text.strip():
            return []
        groups: list[str] = []
        current = ""
        for sentence in _sentences(text):
            candidate = f"{current} {sentence}".strip()
            if current and len(candidate) > self.max_chars:
                groups.append(current)
                overlap = _tail_on_word_boundary(current, self.overlap_chars)
                current = f"{overlap} {sentence}".strip()
            else:
                current = candidate
        if current:
            groups.append(current)

        chunks: list[AtomicChunk] = []
        for ordinal, group in enumerate(groups, start=start_ordinal):
            digest = hashlib.sha256(group.encode("utf-8")).hexdigest()
            chunks.append(
                AtomicChunk(
                    id=str(uuid4()),
                    project_id=project_id,
                    document_id=document_id,
                    ordinal=ordinal,
                    text=group,
                    content_hash=digest,
                    source_pages=source_pages or [],
                    extraction_method=extraction_method,
                )
            )
        return chunks
