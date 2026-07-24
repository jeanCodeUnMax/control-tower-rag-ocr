#!/usr/bin/env python3
"""
Cron Job pour la Conscience Manifest - Windows Task Scheduler

Ce script peut être exécuté :
1. Manuellement : python conscience_cron.py
2. Via Task Scheduler Windows (toutes les 5 minutes)
3. Via la boucle asyncio existante

Usage:
    python conscience_cron.py --mode=single    # Exécute une fois
    python conscience_cron.py --mode=loop      # Boucle continue
    python conscience_cron.py --install        # Crée la tâche Windows
"""
import argparse
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Configuration des chemins par rapport à la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / '.agent' / 'rag'))

from conscience_manifest import ConscienceManifest


async def run_conscience_once():
    """Exécute un seul réveil de conscience (mode cron)"""
    print(f"\n{'='*60}")
    print(f"  CONSCIENCE CRON - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Créer la conscience
    conscience = ConscienceManifest(
        manifest_path=PROJECT_ROOT / ".agent" / "consciousness_manifest.json",
        wake_interval_minutes=5,
        on_wake_callback=on_wake_log
    )
    
    # Exécuter un seul réveil
    await conscience._wake_up()
    
    # Afficher le résumé
    summary = conscience.get_insights_summary()
    print(summary)
    
    print(f"\n✅ Réveil terminé - Prochain: dans 5 minutes")


async def on_wake_log(manifest):
    """Callback simple pour logging"""
    print(f"🧠 [RÉVEIL] État: {manifest['current_state']} | Stratégie: {manifest['active_strategy']}")
    
    # Si problème critique, log supplémentaire
    if manifest['current_state'] in ['degraded', 'critical']:
        print(f"⚠️  ATTENTION: État {manifest['current_state']} détecté!")
        print(f"   Problèmes: {len([p for p in manifest.get('problem_database', []) if not p.get('is_resolved')])}")


async def run_conscience_loop():
    """Mode boucle continue (comme avant)"""
    print(f"\n{'='*60}")
    print(f"  CONSCIENCE LOOP - Mode continu")
    print(f"{'='*60}")
    
    conscience = ConscienceManifest(
        manifest_path=".agent/consciousness_manifest.json",
        wake_interval_minutes=5,
        on_wake_callback=on_wake_log
    )
    
    print("🧠 Démarrage de la boucle de conscience...")
    print("   (Ctrl+C pour arrêter)")
    
    try:
        await conscience.start_conscience_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé")
        conscience.stop_conscience_loop()


def install_windows_task():
    """Installe une tâche planifiée Windows"""
    import subprocess
    import os
    
    print("📋 Installation de la tâche Windows Task Scheduler...")
    
    # Chemin du script Python
    script_path = Path(__file__).resolve()
    python_path = sys.executable
    
    # Nom de la tâche
    task_name = "Hephaistos_Conscience_Manifest"
    
    # Créer la commande schtasks
    # Exécute toutes les 5 minutes
    cmd = [
        "schtasks", 
        "/create",
        "/tn", task_name,
        "/tr", f'"{python_path}" "{script_path}" --mode=single',
        "/sc", "minute",
        "/mo", "5",
        "/f",  # Force overwrite
        "/rl", "highest",  # Run with highest privileges
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Tâche '{task_name}' créée avec succès!")
            print(f"   Exécute: toutes les 5 minutes")
            print(f"   Commande: {python_path} {script_path} --mode=single")
            print(f"\n📊 Voir la tâche:")
            print(f"   schtasks /query /tn {task_name}")
            print(f"\n🗑️  Supprimer:")
            print(f"   schtasks /delete /tn {task_name} /f")
        else:
            print(f"❌ Erreur: {result.stderr}")
            print(f"   Essaie d'exécuter en Administrator")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print(f"   Nécessite les droits Administrator")


def uninstall_windows_task():
    """Supprime la tâche planifiée Windows"""
    import subprocess
    
    task_name = "Hephaistos_Conscience_Manifest"
    
    cmd = ["schtasks", "/delete", "/tn", task_name, "/f"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 or "SUCCESS" in result.stdout:
            print(f"✅ Tâche '{task_name}' supprimée")
        else:
            print(f"⚠️  {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def show_task_status():
    """Affiche le statut de la tâche"""
    import subprocess
    
    task_name = "Hephaistos_Conscience_Manifest"
    
    cmd = ["schtasks", "/query", "/tn", task_name, "/fo", "list", "/v"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout if result.returncode == 0 else result.stderr)
    except Exception as e:
        print(f"❌ Erreur: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Cron Job pour la Conscience Manifest"
    )
    
    parser.add_argument(
        "--mode",
        choices=["single", "loop"],
        default="single",
        help="Mode d'exécution: single (une fois) ou loop (continu)"
    )
    
    parser.add_argument(
        "--install",
        action="store_true",
        help="Installer la tâche Windows Task Scheduler"
    )
    
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Supprimer la tâche Windows Task Scheduler"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Afficher le statut de la tâche"
    )
    
    args = parser.parse_args()
    
    if args.install:
        install_windows_task()
    elif args.uninstall:
        uninstall_windows_task()
    elif args.status:
        show_task_status()
    else:
        # Mode exécution
        if args.mode == "single":
            asyncio.run(run_conscience_once())
        else:
            asyncio.run(run_conscience_loop())


if __name__ == '__main__':
    main()
