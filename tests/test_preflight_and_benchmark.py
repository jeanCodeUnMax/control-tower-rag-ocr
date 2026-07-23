from pathlib import Path

import fitz

from control_tower.service import ControlTowerService


def make_pdf(path: Path) -> None:
    document = fitz.open()
    for number in range(1, 5):
        page = document.new_page()
        page.insert_text(
            (50, 80),
            f"Page {number}. Procédure de maintenance et contrôle de la tour de contrôle RAG OCR.",
        )
    document.save(path)
    document.close()


def test_preflight_and_local_benchmark_do_not_require_cloud(tmp_path: Path):
    source = tmp_path / "sample.pdf"
    make_pdf(source)
    service = ControlTowerService(tmp_path / "workspace")
    service.init_project("demo")

    plan = service.plan_document("demo", source)
    benchmark = service.benchmark_vision("demo", source, max_pages=3)

    assert plan["pdf_pages"] == 4
    assert plan["vision_plan"]["counts"]["cloud"] == 0
    assert benchmark["sampled_pages"] == [1, 3, 4]
    assert benchmark["provider_report"]["profile"] == "local_fast"
    assert Path(benchmark["artifact"]).exists()
