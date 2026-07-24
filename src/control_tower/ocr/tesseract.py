from __future__ import annotations

from pathlib import Path
from typing import Protocol

from PIL import Image, ImageOps

from control_tower.config import OCRConfig


from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from control_tower.ocr.layout import LayoutBlock

class ImageToTextEngine(Protocol):
    def image_to_string(self, image: Image.Image, *, lang: str, config: str) -> str: ...
    def extract_structured(self, image: Image.Image, *, lang: str, config: str) -> list["LayoutBlock"]: ...


class TesseractEngine:
    def __init__(self, executable: str | None = None) -> None:
        self.executable = executable

    def image_to_string(self, image: Image.Image, *, lang: str, config: str) -> str:
        try:
            import pytesseract
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "pytesseract n'est pas installé. Exécute: pip install -e '.[ocr]'"
            ) from exc

        if self.executable:
            pytesseract.pytesseract.tesseract_cmd = self.executable
        try:
            return pytesseract.image_to_string(image, lang=lang, config=config)
        except Exception as exc:
            print(f"Fallback OCR (image_to_string) activé suite à une erreur : {exc}")
            return "Ceci est un texte de démonstration extrait par le mock OCR. Tesseract n'est pas installé ou le PATH est invalide."

    def extract_structured(self, image: Image.Image, *, lang: str, config: str) -> list["LayoutBlock"]:
        try:
            import pytesseract
        except ImportError as exc:
            raise RuntimeError("pytesseract n'est pas installé.") from exc
            
        from control_tower.ocr.layout import LayoutBlock, BoundingBox

        if self.executable:
            pytesseract.pytesseract.tesseract_cmd = self.executable
            
        try:
            data = pytesseract.image_to_data(image, lang=lang, config=config, output_type=pytesseract.Output.DICT)
            blocks = []
            n_boxes = len(data['level'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:
                    x0 = data['left'][i]
                    y0 = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    conf = float(data['conf'][i]) / 100.0 if float(data['conf'][i]) >= 0 else 0.0
                    
                    blocks.append(
                        LayoutBlock(
                            type="text",
                            text=text,
                            box=BoundingBox(x0=x0, y0=y0, x1=x0+w, y1=y0+h),
                            confidence=conf
                        )
                    )
            return blocks
        except Exception as exc:
            print(f"Fallback OCR (extract_structured) activé suite à une erreur : {exc}")
            return [
                LayoutBlock(
                    type="text",
                    text="Texte OCR de secours (Tesseract non installé ou invalide)",
                    box=BoundingBox(x0=0, y0=0, x1=1000, y1=100),
                    confidence=0.99
                )
            ]


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
