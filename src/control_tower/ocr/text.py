from __future__ import annotations

from pathlib import Path

from control_tower.config import OCRConfig
from control_tower.ocr.models import ExtractionResult


class TextOCRProvider:
    accepted = {".txt", ".md"}

    def extract(self, source: Path, config: OCRConfig) -> ExtractionResult:
        del config
        if source.suffix.lower() not in self.accepted:
            raise ValueError(f"Extension texte non supportée: {source.suffix}")
        try:
            text = source.read_text(encoding="utf-8-sig").strip()
        except UnicodeDecodeError as exc:
            raise ValueError(
                "Le fichier texte n'est pas encodé en UTF-8. Convertis-le avant ingestion."
            ) from exc
        return ExtractionResult.for_text(source, text)
