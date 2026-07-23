from __future__ import annotations

from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from control_tower.config import OCRConfig
from control_tower.ocr.image import ImageOCRProvider
from control_tower.ocr.models import ExtractionMethod
from control_tower.ocr.pdf import PDFOCRProvider
from control_tower.ocr.router import DocumentExtractor
from control_tower.ocr.text import TextOCRProvider
from control_tower.service import ControlTowerService


class FakeOCREngine:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls = 0

    def image_to_string(self, image: Image.Image, *, lang: str, config: str) -> str:
        assert image.width > 0
        assert lang
        assert "--psm" in config
        self.calls += 1
        return self.text


def make_native_pdf(path: Path) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Architecture documentaire isolée avec extraction PDF native.")
    document.save(path)
    document.close()


def make_scanned_pdf(path: Path) -> None:
    image = Image.new("RGB", (900, 300), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 100), "Texte image pour OCR", fill="black")
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    document = fitz.open()
    page = document.new_page(width=900, height=300)
    page.insert_image(page.rect, stream=buffer.getvalue())
    document.save(path)
    document.close()


def test_native_pdf_is_extracted_without_tesseract(tmp_path: Path) -> None:
    source = tmp_path / "native.pdf"
    make_native_pdf(source)

    result = PDFOCRProvider(engine=FakeOCREngine("ne doit pas servir")).extract(
        source, OCRConfig(mode="auto", min_native_chars_per_page=20)
    )

    assert result.pages[0].method == ExtractionMethod.NATIVE_PDF
    assert "Architecture documentaire" in result.text


def test_scanned_pdf_uses_injected_ocr_engine(tmp_path: Path) -> None:
    source = tmp_path / "scan.pdf"
    make_scanned_pdf(source)
    engine = FakeOCREngine("Résultat OCR déterministe")

    result = PDFOCRProvider(engine=engine).extract(source, OCRConfig(mode="auto"))

    assert engine.calls == 1
    assert result.pages[0].method == ExtractionMethod.TESSERACT_PDF
    assert result.text == "Résultat OCR déterministe"


def test_image_provider_uses_ocr_and_reports_dimensions(tmp_path: Path) -> None:
    source = tmp_path / "image.png"
    Image.new("RGB", (640, 240), "white").save(source)
    engine = FakeOCREngine("Texte depuis image")

    result = ImageOCRProvider(engine=engine).extract(source, OCRConfig())

    assert result.pages[0].method == ExtractionMethod.TESSERACT_IMAGE
    assert result.pages[0].width == 640
    assert result.text == "Texte depuis image"


def test_pdf_pipeline_writes_artifacts_and_source_page(tmp_path: Path) -> None:
    source = tmp_path / "native.pdf"
    make_native_pdf(source)
    extractor = DocumentExtractor(
        providers=[TextOCRProvider(), PDFOCRProvider(engine=FakeOCREngine("fallback"))]
    )
    service = ControlTowerService(tmp_path / "projects", extractor=extractor)
    service.init_project("demo")

    response = service.ingest("demo", source)
    document_id = response["data"]["document_id"]
    inspection = service.inspect_document("demo", document_id)

    assert response["status"] == "ok"
    assert Path(response["data"]["artifacts"]["extraction_json"]).exists()
    assert inspection["extraction"]["summary"]["methods"] == ["native_pdf"]
    assert inspection["chunks"][0]["source_pages"] == [1]
    assert inspection["chunks"][0]["extraction_method"] == "native_pdf"
