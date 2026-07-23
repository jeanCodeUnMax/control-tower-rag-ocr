from __future__ import annotations

import json
import shutil
import tempfile
import time
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from control_tower.service import ControlTowerService


def build_repeated_diagram(path: Path) -> None:
    image = Image.new("RGB", (360, 180), "white")
    draw = ImageDraw.Draw(image)
    draw.line((30, 145, 330, 35), fill="black", width=5)
    draw.line((315, 35, 330, 35), fill="black", width=5)
    draw.line((330, 35, 325, 50), fill="black", width=5)
    draw.text((35, 20), "Signal de contrôle", fill="black")
    image.save(path)


def build_pdf(path: Path, page_count: int = 800) -> None:
    diagram = path.with_suffix(".png")
    build_repeated_diagram(diagram)
    document = fitz.open()
    templates = [
        "Vérifier le capteur puis enregistrer le résultat dans le registre.",
        "Arrêter la machine avant toute intervention de maintenance.",
        "Analyser le signal, comparer le seuil et déclencher une alerte si nécessaire.",
        "Chaque contrôle doit conserver une preuve, une date et une origine.",
        "Le système découpe le document sans exposer la totalité du contexte.",
        "Une connaissance répétée doit être reliée à un canonique unique.",
        "Le moteur hydrate uniquement les fragments utiles à la question.",
        "La politique bloque l'indexation lorsque des pages sont manquantes.",
    ]
    for index in range(page_count):
        page = document.new_page()
        text = templates[index % len(templates)]
        page.insert_textbox(
            fitz.Rect(50, 50, 545, 180),
            text + " " + text,
            fontsize=12,
        )
        if index % 100 == 0:
            page.insert_image(fitz.Rect(80, 230, 440, 410), filename=str(diagram))
            page.draw_rect(fitz.Rect(70, 220, 450, 420), width=1.5)
            page.draw_line(fitz.Point(90, 390), fitz.Point(420, 250), width=2)
    document.save(path, garbage=4, deflate=True)
    document.close()
    diagram.unlink(missing_ok=True)


def main() -> None:
    runtime = Path(tempfile.mkdtemp(prefix="control-tower-proof-800-"))
    try:
        source = runtime / "preuve_800_pages.pdf"
        build_pdf(source)
        service = ControlTowerService(runtime / "workspace")
        service.init_project("proof-800")
        service.set_config("proof-800", "vision.provider", "local")
        service.set_config("proof-800", "batching.max_pages", "5")
        service.set_config("proof-800", "batching.strict_completeness", "true")
        service.set_config("proof-800", "consolidation.semantic_embeddings", "false")

        started = time.perf_counter()
        result = service.ingest("proof-800", source)
        elapsed = time.perf_counter() - started
        data = result.get("data", {})
        ledger = data.get("ledger") or {}
        consolidation = data.get("consolidation") or {}
        proof = {
            "status": result.get("status"),
            "elapsed_seconds": round(elapsed, 3),
            "source_pages": 800,
            "ledger": ledger,
            "chunk_count": data.get("chunk_count"),
            "canonical_chunk_count": data.get("canonical_chunk_count"),
            "consolidation": consolidation,
            "artifacts": data.get("artifacts"),
        }
        print(json.dumps(proof, ensure_ascii=False, indent=2))
        assert result["status"] == "ok"
        assert ledger["complete"] is True
        assert ledger["completed_pages"] == 800
        assert ledger["failed_pages"] == []
        assert ledger["missing_pages"] == []
        assert data["chunk_count"] == 800
        assert data["canonical_chunk_count"] <= 16
    finally:
        shutil.rmtree(runtime, ignore_errors=True)


if __name__ == "__main__":
    main()
