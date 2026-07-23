from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from control_tower.config import (
    ProjectConfig,
    default_project_config,
    load_project_config,
    set_nested_value,
    settings,
    write_project_config,
)
from control_tower.domain.models import Project

PROJECT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")


class WorkspaceError(ValueError):
    pass


class WorkspaceManager:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or settings.workspace_root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def validate_project_id(self, project_id: str) -> None:
        if not PROJECT_RE.fullmatch(project_id):
            raise WorkspaceError("Identifiant projet invalide: utiliser 2-64 caractères [a-z0-9_-].")

    def path_for(self, project_id: str) -> Path:
        self.validate_project_id(project_id)
        path = (self.root / project_id).resolve()
        if self.root not in path.parents:
            raise WorkspaceError("Sortie de workspace détectée.")
        return path

    def config_path(self, project_id: str) -> Path:
        return self.path_for(project_id) / "config.yaml"

    def create(self, project_id: str, name: str | None = None) -> Project:
        path = self.path_for(project_id)
        path.mkdir(parents=True, exist_ok=True)
        for directory in ("documents", "artifacts", "logs", "state"):
            (path / directory).mkdir(exist_ok=True)
        project = Project(id=project_id, name=name or project_id)
        meta = path / "project.json"
        if not meta.exists():
            meta.write_text(project.model_dump_json(indent=2), encoding="utf-8")
        else:
            project = Project.model_validate_json(meta.read_text(encoding="utf-8"))
        config_path = self.config_path(project_id)
        if not config_path.exists():
            write_project_config(config_path, default_project_config())
        return project

    def require(self, project_id: str) -> Project:
        path = self.path_for(project_id)
        meta = path / "project.json"
        if not meta.exists():
            raise WorkspaceError(f"Projet inconnu: {project_id}")
        config_path = self.config_path(project_id)
        if not config_path.exists():
            write_project_config(config_path, default_project_config())
        return Project.model_validate_json(meta.read_text(encoding="utf-8"))

    def load_config(self, project_id: str) -> ProjectConfig:
        self.require(project_id)
        return load_project_config(self.config_path(project_id))

    def update_config(self, project_id: str, dotted_key: str, value: Any) -> ProjectConfig:
        current = self.load_config(project_id).model_dump(mode="python")
        updated = set_nested_value(current, dotted_key, value)
        validated = ProjectConfig.model_validate(updated)
        write_project_config(self.config_path(project_id), validated)
        self.append_event(
            project_id,
            {
                "type": "config.updated",
                "key": dotted_key,
                "value": value,
                "schema_version": validated.schema_version,
            },
        )
        return validated

    def event_log(self, project_id: str) -> Path:
        return self.path_for(project_id) / "logs" / "events.jsonl"

    def append_event(self, project_id: str, event: dict) -> None:
        target = self.event_log(project_id)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
