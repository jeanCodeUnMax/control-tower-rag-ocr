from pathlib import Path

from control_tower.service import ControlTowerService

service = ControlTowerService(Path(".control_tower/projects"))
service.init_project("demo-code", "Démonstration depuis Python")
service.set_config("demo-code", "atomizer.max_chars", "350")
service.set_config("demo-code", "features.maieutic", "true")

result = service.ingest("demo-code", Path("examples/sample.txt"))
print("INGESTION:", result)

answer_context = service.query("demo-code", "projet isolé")
print("RECHERCHE:", answer_context)

print("INSPECTION:", service.inspect_project("demo-code"))
