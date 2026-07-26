import os
import sys
import logging
from pathlib import Path
from rich.console import Console

# Ajouter src au PYTHONPATH
sys.path.insert(0, str(Path("src").resolve()))

from control_tower.project.workspace import WorkspaceManager
from control_tower.generation.llm import get_llm_provider

# Baisser le niveau de log de httpx pour ne pas polluer l'affichage
logging.getLogger("httpx").setLevel(logging.WARNING)

console = Console()

def test_ping_pong():
    # 1. Charger le .env manuellement
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip("\"").strip("'")
                
    console.print("\n[bold cyan]=== TEST DES PROVIDERS LLM (PING PONG) ===[/bold cyan]\n")
    
    # 2. Charger la conf
    workspace = WorkspaceManager()
    try:
        config = workspace.load_config("demo")
    except Exception:
        console.print("[red]Projet demo introuvable. Création...[/red]")
        workspace.create("demo")
        config = workspace.load_config("demo")
        
    llm_config = config.llm
    
    # Tester les providers un par un
    console.print("[bold yellow]--- TEST INDIVIDUEL DES PROVIDERS ---[/bold yellow]")
    for p in llm_config.providers:
        if not p.enabled:
            continue
        try:
            console.print(f"[dim]Test de {p.name} ({p.kind})...[/dim]")
            provider = get_llm_provider(p.kind, model_name=p.model, api_key_env=p.api_key_env)
            response = provider.generate("Dis exactement et uniquement les mots: Ping Pong.", "Tu es un bot de test. Ne dis rien d'autre.")
            console.print(f"[green]✅ {p.name} OK:[/green] {response}")
        except Exception as e:
            console.print(f"[red]❌ {p.name} ERREUR:[/red] {e}")
            
    # Tester le routeur complet
    console.print("\n[bold yellow]--- TEST DU ROUTEUR (Ordre de repli) ---[/bold yellow]")
    try:
        router = get_llm_provider("router", config_obj=llm_config)
        console.print(f"[dim]Envoi via le routeur (va essayer l'ordre configuré: {', '.join(llm_config.provider_order)})...[/dim]")
        response = router.generate("Si tu m'entends, réponds juste: Routeur OK.", "Tu es un bot.")
        console.print(f"[bold green]✅ ROUTEUR OK:[/bold green] {response}")
    except Exception as e:
        console.print(f"[bold red]❌ ROUTEUR ERREUR TOTALE:[/bold red] {e}")
        
    console.print("\n[bold cyan]=== FIN DU TEST ===[/bold cyan]\n")

if __name__ == "__main__":
    test_ping_pong()
