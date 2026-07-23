from pathlib import Path

from control_tower.domain.models import PolicyEffect
from control_tower.policy.checker import PolicyChecker
from control_tower.project.workspace import WorkspaceManager


def test_policy_blocks_executable(tmp_path: Path) -> None:
    workspace = WorkspaceManager(tmp_path / "projects")
    workspace.create("demo")
    source = tmp_path / "payload.exe"
    source.write_bytes(b"x")
    decision = PolicyChecker(workspace).check_ingestion("demo", source)
    assert decision.effect == PolicyEffect.DENY
