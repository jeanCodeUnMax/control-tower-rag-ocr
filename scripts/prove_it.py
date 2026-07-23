"""Démonstration locale reproductible, sans API externe ni LLM."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC = ROOT_DIR / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from control_tower.service import ControlTowerService  # noqa: E402

ROOT = ROOT_DIR / ".proof_control_tower"
if ROOT.exists():
    shutil.rmtree(ROOT)

service = ControlTowerService(ROOT / "projects")
print("\n1) CRÉATION")
print(json.dumps(service.init_project("preuve"), ensure_ascii=False, indent=2, default=str))

print("\n2) RÉGLAGES RÉELLEMENT MODIFIÉS")
service.set_config("preuve", "atomizer.max_chars", "120")
service.set_config("preuve", "atomizer.overlap_chars", "30")
service.set_config("preuve", "features.maieutic", "false")
print(json.dumps(service.show_config("preuve"), ensure_ascii=False, indent=2, default=str))

print("\n3) INGESTION")
result = service.ingest("preuve", ROOT_DIR / "examples" / "sample.txt")
print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

print("\n4) RECHERCHE")
result = service.query("preuve", "projet documentaire")
print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

print("\n5) INSPECTION HONNÊTE")
inspection = service.inspect_project("preuve")
summary = {
    "config": inspection["active_config"],
    "store": inspection["store"],
    "capabilities": {item["name"]: item["status"] for item in inspection["capabilities"]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))

print("\nPreuve créée dans:", ROOT.resolve())
