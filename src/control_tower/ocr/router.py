from __future__ import annotations

from pathlib import Path

from control_tower.config import OCRConfig
from control_tower.ocr.base import OCRProvider
from control_tower.ocr.image import ImageOCRProvider
from control_tower.ocr.models import ExtractionResult
from control_tower.ocr.pdf import PDFOCRProvider
from control_tower.ocr.text import TextOCRProvider


class DocumentExtractor:
    def __init__(self, providers: list[OCRProvider] | None = None) -> None:
        configured = providers or [TextOCRProvider(), PDFOCRProvider(), ImageOCRProvider()]
        self._providers: dict[str, OCRProvider] = {}
        for provider in configured:
            for extension in provider.accepted:
                self._providers[extension] = provider

    @property
    def accepted_extensions(self) -> set[str]:
        return set(self._providers)

    def provider_for(self, extension: str) -> OCRProvider:
        provider = self._providers.get(extension.lower())
        if provider is None:
            supported = ", ".join(sorted(self.accepted_extensions))
            raise ValueError(
                f"Extension non supportée: {extension or '<aucune>'}. Supportées: {supported}"
            )
        return provider

    def extract(self, source: Path, config: OCRConfig) -> ExtractionResult:
        return self.provider_for(source.suffix).extract(source, config)
