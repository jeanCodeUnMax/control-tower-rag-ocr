from __future__ import annotations

import json
import logging
import os
import sys
import warnings
from pathlib import Path

# Ajouter src/ au PYTHONPATH pour permettre l'exécution directe
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Chargement du fichier .env local s'il existe (pour l'API Key)
_env_file = Path(".env")
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _key, _val = _line.split("=", 1)
            os.environ[_key.strip()] = _val.strip().strip("'\"")

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
def ingest(
    source: Path = typer.Argument(..., help="Fichier ou dossier à ingérer"),
    project: str = typer.Option(..., "--project", "-p"),
    workers: int = typer.Option(4, "--workers", "-w", help="Nombre de threads en parallèle"),
) -> None:
    """Ingère TXT, Markdown, PDF ou image. Accepte les dossiers pour un traitement multithread en parallèle."""
    service = ControlTowerService()
    
    if source.is_file():
        typer.echo(f"Ingestion d'un seul fichier: {source}")
        output(service.ingest(project, source))
        return
        
    if source.is_dir():
        valid_ext = {".pdf", ".txt", ".md", ".png", ".jpg", ".jpeg"}
        files = [f for f in source.rglob("*") if f.is_file() and f.suffix.lower() in valid_ext]
        
        if not files:
            typer.echo(f"Aucun fichier valide trouvé dans {source}", err=True)
            return
            
        typer.echo(f"Dossier détecté: {len(files)} fichiers à ingérer en parallèle ({workers} threads).")
        
        import concurrent.futures
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
        
        results = []
        errors = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Ingestion en cours...", total=len(files))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_file = {executor.submit(service.ingest, project, f): f for f in files}
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        res = future.result()
                        results.append(res)
                    except Exception as exc:
                        errors.append({"file": str(file_path), "error": str(exc)})
                    finally:
                        progress.advance(task)
                        
        typer.echo(f"\n[Terminé] {len(results)} succès, {len(errors)} erreurs.")
        if errors:
            typer.echo("Détail des erreurs :", err=True)
            for err in errors:
                typer.echo(f" - {err['file']}: {err['error']}", err=True)


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


@app.command("consolidate")
def consolidate(
    project: str = typer.Option(..., "--project", "-p"),
) -> None:
    """Déduplique globalement les chunks et les assets sur l'ensemble du projet."""
    output(ControlTowerService().consolidate_project(project))


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
    database: str = typer.Option(
        None,
        "--database",
        "-db",
        help="Base de données (zvec ou qdrant_local)",
    ),
) -> None:
    """Génère les embeddings pour les chunks non vectorisés et les insère dans le Vector Store."""
    if not database:
        import rich.prompt
        database = rich.prompt.Prompt.ask(
            "Dans quelle base de données voulez-vous injecter les vecteurs ?",
            choices=["zvec", "qdrant_local"],
            default="zvec"
        )
    output(ControlTowerService().vectorize_project(project, database=database))


@app.command("ask")
def ask(
    project: str = typer.Option(..., "--project", "-p"),
    question: str = typer.Argument(..., help="La question à poser à l'IA."),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Nombre de documents à récupérer."),
    database: str = typer.Option(
        None,
        "--database",
        "-db",
        help="Base de données (zvec ou qdrant_local)",
    ),
) -> None:
    """Pose une question au système (RAG) en s'appuyant sur les documents ingérés."""
    if not database:
        import rich.prompt
        database = rich.prompt.Prompt.ask(
            "Quelle base de données interroger ?",
            choices=["zvec", "qdrant_local"],
            default="zvec"
        )
    result = ControlTowerService().ask_project(project, question, top_k, database=database)
    
    if "answer" in result and "sources" in result:
        try:
            from rich.console import Console
            from rich.markdown import Markdown
            from rich.panel import Panel
            from rich.text import Text
            
            console = Console()
            
            # Affichage de la réponse en Markdown enrichi
            console.print(Panel(Markdown(result["answer"]), title="[bold green]🤖 Réponse de l'IA[/bold green]", border_style="green", padding=(1, 2)))
            
            # Affichage des sources
            if result["sources"]:
                console.print("\n[bold blue]📚 Sources utilisées :[/bold blue]")
                for i, src in enumerate(result["sources"], 1):
                    doc_id = src.get("document_id", "Inconnu")
                    score = src.get("score", 0.0)
                    text = src.get("text_snippet", "").replace('\n', ' ').strip()
                    
                    source_text = Text()
                    source_text.append(f" {i}. ", style="bold blue")
                    source_text.append(f"[Pertinence: {score:.2f}] ", style="yellow")
                    source_text.append(f"Document: {doc_id}\n    ", style="cyan")
                    source_text.append(f"\"{text}...\"", style="italic dim")
                    console.print(source_text)
            else:
                console.print("\n[yellow]⚠️ Aucune source pertinente trouvée pour cette question.[/yellow]")
                
        except ImportError:
            # Fallback si rich n'est pas installé (bien que typer l'inclut généralement)
            output(result)
    else:
        output(result)


@app.command("compare")
def compare(
    project: str = typer.Option(..., "--project", "-p"),
    question: str = typer.Argument(..., help="La question à poser aux LLMs."),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Nombre de documents à récupérer."),
) -> None:
    """Compare les réponses de tous les LLMs configurés en parallèle."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.columns import Columns
        from rich.markdown import Markdown
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        console = Console()
        service = ControlTowerService()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            progress.add_task("[cyan]Recherche RAG et génération parallèle sur tous les LLMs...", total=None)
            result = service.compare_llms(project, question, top_k)
            
        comparisons = result.get("comparisons", [])
        if not comparisons:
            console.print("[red]Aucun résultat de comparaison.[/red]")
            return
            
        panels = []
        for comp in comparisons:
            name = comp.get("name", "Inconnu")
            model = comp.get("model", "")
            time_sec = comp.get("time", 0.0)
            error = comp.get("error")
            answer = comp.get("answer")
            
            title = f"[bold]{name}[/bold] ({model})\n[dim]{time_sec:.1f}s[/dim]"
            
            if error:
                content = f"[red]Erreur:[/red]\n{error}"
                border_style = "red"
            else:
                content = Markdown(answer) if answer else "[italic]Réponse vide[/italic]"
                border_style = "green"
                
            panels.append(Panel(content, title=title, border_style=border_style, padding=(1, 2)))
            
        console.print(f"\n[bold magenta]📊 Comparaison des LLMs pour la question :[/bold magenta] [white]{question}[/white]\n")
        console.print(Columns(panels, expand=True))
        
        # Affichage des sources
        sources = result.get("sources", [])
        if sources:
            console.print("\n[bold blue]📚 Sources RAG utilisées pour le contexte commun :[/bold blue]")
            for i, src in enumerate(sources, 1):
                doc_id = src.get("document_id", "Inconnu")
                score = src.get("score", 0.0)
                text = src.get("text_snippet", "").replace('\n', ' ').strip()
                console.print(f" [bold blue]{i}.[/bold blue] [yellow][Pertinence: {score:.2f}][/yellow] [cyan]Document: {doc_id}[/cyan]\n    [italic dim]\"{text}...\"[/italic dim]")
        
    except ImportError:
        typer.echo("Veuillez installer 'rich' pour un affichage optimal de la comparaison.")
        result = ControlTowerService().compare_llms(project, question, top_k)
        output(result)


@app.command("synthesize")
def synthesize(
    project: str = typer.Option(..., "--project", "-p"),
    question: str = typer.Argument(..., help="La question à poser."),
    output_file: str = typer.Option("synthese-ai-grouped.md", "--out", "-o", help="Fichier de sortie Markdown."),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Nombre de documents à récupérer."),
    web: bool = typer.Option(False, "--web", "-w", help="Enrichir avec une recherche web (DuckDuckGo)."),
    paradigm: str = typer.Option("executive", "--paradigm", "-t", help="Mode cognitif: executive, analogy, discovery, socratic, json_schema, pseudocode")
) -> None:
    """Compare tous les LLMs puis synthétise leurs réponses via Mistral dans un fichier Markdown."""
    try:
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn
        from rich.panel import Panel
        
        console = Console()
        service = ControlTowerService()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task1 = progress.add_task("[cyan]Phase 1 : Génération parallèle sur tous les LLMs...", total=None)
            
            progress_desc = "[cyan]Phase 1 & 2 : Génération parallèle puis Méga-Synthèse (Mistral Large)..."
            if web:
                progress_desc = "[cyan]Phase 1, 2 & 3 : Génération, Recherche Web en cours, puis Synthèse finale..."
                
            progress.update(task1, description=progress_desc)
            
            result = service.synthesize_llms(project, question, output_file, top_k, use_web_search=web, paradigm=paradigm)
            
        web_info = ""
        if web:
            web_info = f"🌐 [bold]Sources Web :[/bold] {result.get('web_sources', 0)} sites consultés\n"
            
        console.print(Panel(
            f"[bold green]Synthèse réussie ! 🎉[/bold green]\n\n"
            f"🧠 [bold]Modèle maître :[/bold] {result['synthesizer']}\n"
            f"🎭 [bold]Paradigme actif :[/bold] {paradigm.upper()}\n"
            f"🤖 [bold]Brouillons fusionnés :[/bold] {result['sources_used']} IA différentes\n"
            f"{web_info}"
            f"💾 [bold]Fichier généré :[/bold] [cyan]{result['output_file']}[/cyan]",
            title="Consensus LLM",
            border_style="green"
        ))
        
        # Affichage des sources issues de la base vectorielle
        sources = result.get("rag_sources", [])
        if sources:
            console.print("\n[bold blue]📚 VECTEURS EXTRAITS DE LA BASE (Qdrant/Zvec) :[/bold blue]")
            for i, src in enumerate(sources, 1):
                doc_id = src.get("document_id", "Inconnu")
                score = src.get("score", 0.0)
                text = src.get("text_snippet", "").replace('\n', ' ').strip()
                console.print(f" [bold blue]{i}.[/bold blue] [yellow][Pertinence: {score:.2f}][/yellow] [cyan]Document: {doc_id}[/cyan]\n    [italic dim]\"{text}...\"[/italic dim]")
        elif not web:
            console.print("\n[yellow]⚠️ La base de données vectorielle n'a retourné aucun fragment pertinent pour cette question.[/yellow]")
        
    except ImportError:
        result = ControlTowerService().synthesize_llms(project, question, output_file, top_k, use_web_search=web, paradigm=paradigm)
        output(result)
        typer.echo(f"Synthèse terminée. Fichier généré: {result['output_file']}")
    except Exception as e:
        typer.echo(f"Erreur lors de la synthèse : {e}")

if __name__ == "__main__":
    app()
