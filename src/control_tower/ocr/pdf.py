from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image

from control_tower.config import BatchConfig, OCRConfig
from control_tower.ocr.models import ExtractedPage, ExtractionMethod, ExtractionResult
from control_tower.ocr.tesseract import (
    ImageToTextEngine,
    TesseractEngine,
    prepare_image,
    resolve_tesseract_executable,
    tesseract_config,
)
from control_tower.processing.models import PageProfile


class PDFOCRProvider:
    accepted = {".pdf"}

    def __init__(self, engine: ImageToTextEngine | None = None) -> None:
        self.engine = engine

    def page_count(self, source: Path) -> int:
        with fitz.open(source) as document:
            return document.page_count

    def profile(
        self,
        source: Path,
        ocr_config: OCRConfig,
        batch_config: BatchConfig,
    ) -> list[PageProfile]:
        if source.suffix.lower() not in self.accepted:
            raise ValueError(f"Extension PDF attendue, reçu: {source.suffix}")
        profiles: list[PageProfile] = []
        with fitz.open(source) as document:
            self._validate_page_count(document.page_count, ocr_config)
            for index, page in enumerate(document):
                native_text = page.get_text("text", sort=True).strip()
                compact_chars = len("".join(native_text.split()))
                image_count = len(page.get_images(full=True))
                drawings = page.get_drawings()
                drawing_count = len(drawings)
                text_dict = page.get_text("dict")
                text_block_count = sum(
                    1 for block in text_dict.get("blocks", []) if block.get("type") == 0
                )
                estimated_text_units = max(1, len(native_text) // 4)
                estimated_units = (
                    estimated_text_units
                    + image_count * batch_config.image_context_units
                    + drawing_count * batch_config.drawing_context_units
                )
                requires_ocr = not self._use_native_text(native_text, ocr_config)
                profiles.append(
                    PageProfile(
                        page_number=index + 1,
                        native_characters=compact_chars,
                        image_count=image_count,
                        drawing_count=drawing_count,
                        text_block_count=text_block_count,
                        estimated_context_units=estimated_units,
                        requires_ocr=requires_ocr,
                        requires_visual_analysis=bool(image_count or drawing_count),
                    )
                )
        return profiles

    def extract_pages(
        self,
        source: Path,
        config: OCRConfig,
        page_numbers: list[int],
    ) -> ExtractionResult:
        if source.suffix.lower() not in self.accepted:
            raise ValueError(f"Extension PDF attendue, reçu: {source.suffix}")
        requested = sorted(set(page_numbers))
        if not requested:
            return ExtractionResult(source_path=str(source), source_type="pdf", pages=[])

        pages: list[ExtractedPage] = []
        warnings: list[str] = []
        with fitz.open(source) as document:
            self._validate_page_count(document.page_count, config)
            invalid = [number for number in requested if number < 1 or number > document.page_count]
            if invalid:
                raise ValueError(f"Pages PDF invalides: {invalid}")
            for page_number in requested:
                page = document.load_page(page_number - 1)
                native_text = page.get_text("text", sort=True).strip()
                use_native = self._use_native_text(native_text, config)
                if use_native:
                    pages.append(
                        ExtractedPage(
                            page_number=page_number,
                            text=native_text,
                            method=ExtractionMethod.NATIVE_PDF,
                        )
                    )
                    continue

                if config.mode == "text_only":
                    message = f"Page {page_number}: aucun texte natif exploitable."
                    warnings.append(message)
                    pages.append(
                        ExtractedPage(
                            page_number=page_number,
                            text=native_text,
                            method=ExtractionMethod.NATIVE_PDF,
                            warnings=[message],
                        )
                    )
                    continue

                ocr_text, width, height = self._ocr_page(page, config)
                page_warnings: list[str] = []
                if not ocr_text:
                    message = f"Page {page_number}: Tesseract n'a détecté aucun texte."
                    warnings.append(message)
                    page_warnings.append(message)
                pages.append(
                    ExtractedPage(
                        page_number=page_number,
                        text=ocr_text,
                        method=ExtractionMethod.TESSERACT_PDF,
                        width=width,
                        height=height,
                        warnings=page_warnings,
                    )
                )
            return ExtractionResult(
                source_path=str(source),
                source_type="pdf",
                pages=pages,
                warnings=warnings,
                metadata={"pdf_page_count": document.page_count, "requested_pages": requested},
            )

    def extract(self, source: Path, config: OCRConfig) -> ExtractionResult:
        count = self.page_count(source)
        self._validate_page_count(count, config)
        result = self.extract_pages(source, config, list(range(1, count + 1)))
        if not result.text.strip():
            raise ValueError("Aucun texte exploitable n'a été extrait du PDF.")
        return result

    @staticmethod
    def _validate_page_count(page_count: int, config: OCRConfig) -> None:
        if page_count > config.max_pages:
            raise ValueError(
                f"PDF trop long: {page_count} pages, limite configurée {config.max_pages}."
            )

    @staticmethod
    def _use_native_text(native_text: str, config: OCRConfig) -> bool:
        if config.mode == "force_ocr":
            return False
        if config.mode == "text_only":
            return True
        compact = "".join(native_text.split())
        return len(compact) >= config.min_native_chars_per_page

    def _ocr_page(self, page: fitz.Page, config: OCRConfig) -> tuple[str, int, int]:
        zoom = config.dpi / 72
        pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        prepared = prepare_image(image, config)
        engine = self.engine or TesseractEngine(resolve_tesseract_executable(config))
        text = engine.image_to_string(
            prepared,
            lang=config.languages,
            config=tesseract_config(config),
        ).strip()
        return text, prepared.width, prepared.height
