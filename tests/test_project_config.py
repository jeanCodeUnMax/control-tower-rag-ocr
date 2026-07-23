from pathlib import Path

from control_tower.service import ControlTowerService
from control_tower.storage.sqlite import SQLiteStore


def test_project_config_really_changes_chunking_and_features(tmp_path: Path) -> None:
    service = ControlTowerService(tmp_path / "projects")
    service.init_project("demo")
    service.set_config("demo", "atomizer.max_chars", "55")
    service.set_config("demo", "atomizer.overlap_chars", "0")
    service.set_config("demo", "features.maieutic", "false")
    service.set_config("demo", "features.kant_glove", "false")

    source = tmp_path / "doc.txt"
    source.write_text(
        "Première phrase volontairement longue. Deuxième phrase également détaillée. "
        "Troisième phrase pour forcer plusieurs fragments.",
        encoding="utf-8",
    )
    result = service.ingest("demo", source)

    assert result["data"]["chunk_count"] >= 2
    assert result["data"]["active_config"]["atomizer"]["max_chars"] == 55
    assert result["data"]["active_config"]["features"]["maieutic"] is False

    store = SQLiteStore(tmp_path / "projects" / "demo" / "state" / "knowledge.db")
    chunks = store.all_chunks()
    assert all(chunk.questions == [] for chunk in chunks)
    assert all(chunk.tensions == [] for chunk in chunks)


def test_inspection_exposes_truthful_capability_statuses(tmp_path: Path) -> None:
    service = ControlTowerService(tmp_path / "projects")
    service.init_project("demo")
    inspection = service.inspect_project("demo")
    statuses = {item["name"]: item["status"] for item in inspection["capabilities"]}
    assert statuses["atomizer"] == "wired"
    assert statuses["consensusless"] == "available"
    assert statuses["pdf_image_ocr"] == "wired"


def test_config_set_supports_provider_list_indexes(tmp_path: Path):
    service = ControlTowerService(tmp_path / "workspace")
    service.init_project("demo")

    result = service.set_config("demo", "vision.providers.1.enabled", "true")

    assert result["config"]["vision"]["providers"][1]["enabled"] is True
