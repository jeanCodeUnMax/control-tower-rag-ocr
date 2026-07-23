from __future__ import annotations

from pathlib import Path

from control_tower.config import ProjectConfig
from control_tower.domain.models import PolicyDecision, PolicyEffect
from control_tower.project.workspace import WorkspaceManager


class PolicyChecker:
    def __init__(self, workspace: WorkspaceManager) -> None:
        self.workspace = workspace

    def check_ingestion(
        self, project_id: str, source: Path, config: ProjectConfig | None = None
    ) -> PolicyDecision:
        try:
            self.workspace.require(project_id)
            active = config or self.workspace.load_config(project_id)
        except ValueError as exc:
            return PolicyDecision(effect=PolicyEffect.DENY, rule_id="project.exists", reason=str(exc))

        extension = source.suffix.lower()
        blocked_extensions = {item.lower() for item in active.policy.blocked_extensions}
        allowed_extensions = {item.lower() for item in active.policy.allowed_extensions}
        if extension in blocked_extensions:
            return PolicyDecision(
                effect=PolicyEffect.DENY,
                rule_id="ingestion.block_extension",
                reason=f"Extension interdite par la configuration du projet: {source.suffix}",
            )
        if extension not in allowed_extensions:
            return PolicyDecision(
                effect=PolicyEffect.DENY,
                rule_id="ingestion.unsupported_extension",
                reason=(
                    f"Extension non autorisée: {extension or '<aucune>'}. "
                    f"Extensions permises: {', '.join(sorted(allowed_extensions))}"
                ),
            )
        if not source.exists() or not source.is_file():
            return PolicyDecision(
                effect=PolicyEffect.DENY,
                rule_id="source.exists",
                reason="La source n'existe pas ou n'est pas un fichier.",
            )
        if source.stat().st_size > active.policy.max_ingest_bytes:
            return PolicyDecision(
                effect=PolicyEffect.REVIEW,
                rule_id="ingestion.large_file",
                reason="Le fichier dépasse la limite automatique configurée pour le projet.",
                obligations=["human_approval"],
            )
        return PolicyDecision(
            effect=PolicyEffect.ALLOW,
            rule_id="ingestion.default_allow",
            reason="Source documentaire autorisée.",
        )
