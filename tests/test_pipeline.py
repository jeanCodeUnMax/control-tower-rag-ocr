from pathlib import Path

from control_tower.domain.models import ResultStatus
from control_tower.service import ControlTowerService


def test_end_to_end_pipeline(tmp_path: Path) -> None:
    service = ControlTowerService(tmp_path / "projects")
    service.init_project("demo")
    source = tmp_path / "doc.txt"
    source.write_text("Un projet isolé protège les données. Le recalcul doit rester ciblé.", encoding="utf-8")
    result = service.ingest("demo", source)
    assert result["status"] == ResultStatus.OK
    response = service.query("demo", "projet isolé")
    assert response["hits"]
    assert response["hydrated"]["items"]
