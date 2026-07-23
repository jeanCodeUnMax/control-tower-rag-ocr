"""Preuve locale reproductible de l'OCR image et PDF scanné.

Exécution depuis la racine du dépôt :
    python scripts/prove_ocr.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from control_tower.service import ControlTowerService  # noqa: E402


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/Library/Fonts/Arial Bold.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def build_sources(directory: Path) -> tuple[Path, Path]:
    image_path = directory / "preuve_ocr.png"
    image = Image.new("RGB", (1500, 420), "white")
    draw = ImageDraw.Draw(image)
    font = find_font(44)
    draw.text((60, 80), "CONTROLE TOUR OCR", font=font, fill="black")
    draw.text((60, 170), "Projet isole et tracable", font=font, fill="black")
    draw.text((60, 260), "Hydratation ciblee", font=font, fill="black")
    image.save(image_path)

    pdf_path = directory / "preuve_scan.pdf"
    document = fitz.open()
    page = document.new_page(width=1500, height=420)
    page.insert_image(page.rect, filename=str(image_path))
    document.save(pdf_path)
    document.close()
    return image_path, pdf_path


def main() -> int:
    runtime = ROOT / ".proof_ocr"
    if runtime.exists():
        shutil.rmtree(runtime)
    runtime.mkdir(parents=True)
    image_path, pdf_path = build_sources(runtime)

    service = ControlTowerService(runtime / "projects")
    service.init_project("preuve-ocr", "Preuve OCR réelle")

    summary = []
    for source in (image_path, pdf_path):
        result = service.ingest("preuve-ocr", source)
        item = {
            "source": source.name,
            "status": result["status"],
            "errors": result["errors"],
        }
        if result["status"] == "ok":
            document_id = result["data"]["document_id"]
            extracted_path = Path(result["data"]["artifacts"]["extracted_text"])
            inspection = service.inspect_document("preuve-ocr", document_id)
            item.update(
                {
                    "document_id": document_id,
                    "methods": result["data"]["extraction"]["methods"],
                    "extracted_text": extracted_path.read_text(encoding="utf-8"),
                    "chunks": len(inspection["chunks"]),
                    "first_chunk_source": {
                        "pages": inspection["chunks"][0]["source_pages"],
                        "method": inspection["chunks"][0]["extraction_method"],
                    },
                }
            )
        summary.append(item)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    success = all(item["status"] == "ok" for item in summary)
    print("\nPREUVE OCR:", "RÉUSSIE" if success else "ÉCHOUÉE")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
