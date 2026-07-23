from __future__ import annotations

import json
from pathlib import Path

import typer

from control_tower.service import ControlTowerService

app = typer.Typer(help="Control Tower RAG — CLI V0.5")


def output(data: dict) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2, default=str))


@app.command("init-project")
def init_project(project_id: str, name: str | None = None) -> None:
    """Crée un workspace isolé et son config.yaml."""
    output(ControlTowerService().init_project(project_id, name))


@app.command()
def ingest(project: str = typer.Option(..., "--project", "-p"), source: Path = typer.Argument(...)) -> None:
    """Ingère TXT, Markdown, PDF ou image avec la configuration du projet."""
    output(ControlTowerService().ingest(project, source))


@app.command()
def query(
    project: str = typer.Option(..., "--project", "-p"),
    text: str = typer.Option(..., "--text", "-t"),
    top_k: int | None = typer.Option(None, "--top-k"),
) -> None:
    """Recherche et hydrate le contexte utile."""
    output(ControlTowerService().query(project, text, top_k))


@app.command("config-show")
def config_show(project: str = typer.Option(..., "--project", "-p")) -> None:
    """Montre la configuration réellement active du projet."""
    output(ControlTowerService().show_config(project))


@app.command("config-set")
def config_set(
    key: str = typer.Argument(..., help="Clé pointée, ex: atomizer.max_chars"),
    value: str = typer.Argument(..., help="Valeur YAML, ex: 350, true, '[.exe,.zip]'"),
    project: str = typer.Option(..., "--project", "-p"),
) -> None:
    """Modifie et valide un réglage du projet."""
    output(ControlTowerService().set_config(project, key, value))


@app.command("profile-set")
def profile_set(
    profile: str = typer.Argument(..., help="local_fast, balanced, cloud_turbo ou night_deep"),
    project: str = typer.Option(..., "--project", "-p"),
) -> None:
    """Sélectionne un profil d'ingestion sans éditer le YAML à la main."""
    if profile not in {"local_fast", "balanced", "cloud_turbo", "night_deep"}:
        raise typer.BadParameter("Profil inconnu.")
    service = ControlTowerService()
    service.set_config(project, "vision.profile", profile)
    service.set_config(project, "vision.provider", "router")
    output(service.show_config(project))


@app.command("plan-document")
def plan_document(
    source: Path = typer.Argument(...),
    project: str = typer.Option(..., "--project", "-p"),
) -> None:
    """Prévoit routes, lots et coût sans lancer d'appel cloud."""
    output(ControlTowerService().plan_document(project, source))


@app.command("benchmark-vision")
def benchmark_vision(
    source: Path = typer.Argument(...),
    project: str = typer.Option(..., "--project", "-p"),
    max_pages: int = typer.Option(12, "--max-pages"),
) -> None:
    """Teste la vitesse et les fallbacks sur un échantillon avant ingestion massive."""
    output(ControlTowerService().benchmark_vision(project, source, max_pages))


@app.command("enrich-document")
def enrich_document(
    document_id: str = typer.Option(..., "--document-id", "-d"),
    project: str = typer.Option(..., "--project", "-p"),
    profile: str = typer.Option("cloud_turbo", "--profile"),
) -> None:
    """Reprend uniquement les pages différées et remplace l'index du document."""
    output(ControlTowerService().enrich_document(project, document_id, profile))


@app.command("inspect-project")
def inspect_project(project: str = typer.Option(..., "--project", "-p")) -> None:
    """Prouve ce qui est configuré, câblé et stocké pour le projet."""
    output(ControlTowerService().inspect_project(project))


@app.command("inspect-document")
def inspect_document(
    project: str = typer.Option(..., "--project", "-p"),
    document_id: str = typer.Option(..., "--document-id", "-d"),
) -> None:
    """Montre l'extraction page par page et les chunks d'un document."""
    output(ControlTowerService().inspect_document(project, document_id))


@app.command("vectorize")
def vectorize(
    project: str = typer.Option(..., "--project", "-p"),
) -> None:
    """Génère les embeddings pour les chunks non vectorisés et les insère dans le Vector Store."""
    output(ControlTowerService().vectorize_project(project))


if __name__ == "__main__":
    app()
