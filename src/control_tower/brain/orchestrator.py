from __future__ import annotations

from control_tower.domain.models import ExecutionPlan, ExecutionStep


class Brain:
    def plan_ingestion(self, project_id: str) -> ExecutionPlan:
        return ExecutionPlan(
            project_id=project_id,
            intent="ingest_document",
            steps=[
                ExecutionStep(module="policy", action="check_ingestion"),
                ExecutionStep(module="ocr", action="extract"),
                ExecutionStep(module="atomizer", action="split"),
                ExecutionStep(module="semantics", action="enrich", required=False),
                ExecutionStep(module="storage", action="persist"),
                ExecutionStep(module="state", action="refresh"),
            ],
        )
