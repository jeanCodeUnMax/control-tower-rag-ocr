from __future__ import annotations

from pathlib import Path
from typing import Protocol

from PIL import Image, ImageOps

from control_tower.config import OCRConfig


class ImageToTextEngine(Protocol):
    def image_to_string(self, image: Image.Image, *, lang: str, config: str) -> str: ...


class TesseractEngine:
    def __init__(self, executable: str | None = None) -> None:
        self.executable = executable

    def image_to_string(self, image: Image.Image, *, lang: str, config: str) -> str:
        try:
            import pytesseract
        except ImportError as exc:  # pragma: no cover - dépend de l'installation
            raise RuntimeError(
                "pytesseract n'est pas installé. Exécute: pip install -e '.[ocr]'"
            ) from exc

        if self.executable:
            pytesseract.pytesseract.tesseract_cmd = self.executable
        try:
            return pytesseract.image_to_string(image, lang=lang, config=config)
        except pytesseract.TesseractNotFoundError as exc:
            raise RuntimeError(
                "Tesseract n'est pas installé ou introuvable. Configure ocr.tesseract_cmd."
            ) from exc
        except pytesseract.TesseractError as exc:
            raise RuntimeError(f"Échec Tesseract: {exc}") from exc


def prepare_image(image: Image.Image, config: OCRConfig) -> Image.Image:
    prepared = image.convert("RGB")
    if config.grayscale:
        prepared = ImageOps.grayscale(prepared)
    if config.autocontrast:
        prepared = ImageOps.autocontrast(prepared)
    return prepared


def tesseract_config(config: OCRConfig) -> str:
    return f"--oem {config.oem} --psm {config.psm}"


def resolve_tesseract_executable(config: OCRConfig) -> str | None:
    value = config.tesseract_cmd
    return str(Path(value).expanduser()) if value else None
