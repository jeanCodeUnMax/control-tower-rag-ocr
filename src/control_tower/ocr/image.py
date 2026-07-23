from __future__ import annotations

from pathlib import Path

from PIL import Image

from control_tower.config import OCRConfig
from control_tower.ocr.models import ExtractedPage, ExtractionMethod, ExtractionResult
from control_tower.ocr.tesseract import (
    ImageToTextEngine,
    TesseractEngine,
    prepare_image,
    resolve_tesseract_executable,
    tesseract_config,
)


class ImageOCRProvider:
    accepted = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

    def __init__(self, engine: ImageToTextEngine | None = None) -> None:
        self.engine = engine

    def extract(self, source: Path, config: OCRConfig) -> ExtractionResult:
        if source.suffix.lower() not in self.accepted:
            raise ValueError(f"Extension image non supportée: {source.suffix}")

        with Image.open(source) as image:
            prepared = prepare_image(image, config)
            engine = self.engine or TesseractEngine(resolve_tesseract_executable(config))
            text = engine.image_to_string(
                prepared,
                lang=config.languages,
                config=tesseract_config(config),
            ).strip()
            warning = [] if text else ["Tesseract n'a détecté aucun texte dans l'image."]
            page = ExtractedPage(
                page_number=1,
                text=text,
                method=ExtractionMethod.TESSERACT_IMAGE,
                width=prepared.width,
                height=prepared.height,
                warnings=warning,
            )
        return ExtractionResult(
            source_path=str(source),
            source_type=source.suffix.lower().lstrip("."),
            pages=[page],
            warnings=warning,
        )
