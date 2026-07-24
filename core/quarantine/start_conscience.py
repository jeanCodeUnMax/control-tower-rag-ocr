#!/usr/bin/env python3
"""
Hephaistos Conscience - Commande unique pour tout activer

Usage:
    python start_conscience.py              # Démarre tout
    python start_conscience.py --status   # Voir statut
    python start_conscience.py --stop     # Arrêter
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Configuration des chemins par rapport à la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def start_all():
    """Démarre le système de conscience complet"""
    print("=" * 70)
    print("  🧠 HEPHAISTOS CONSCIENCE - Démarrage complet")
    print("=" * 70)
    
    print("\n📋 Résumé du système:")
    print("   • Conscience Manifest avec réveils cycliques")
    print("   • Cron actif (toutes les 5 minutes)")
    print("   • Auto-détection de problèmes")
    print("   • Stratégies adaptatives (fallback)")
    print("   • Mémoire persistante (manifeste JSON)")
    
    print("\n🚀 Démarrage...")
    
    # Lancer le daemon dans un nouveau terminal
    try:
        daemon_path = Path(__file__).parent / "conscience_daemon.py"
        subprocess.Popen(
            [sys.executable, str(daemon_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("   ✅ Daemon démarré dans nouveau terminal")
    except Exception as e:
        print(f"   ⚠️  Erreur: {e}")
        print(f"   💡 Essaie: python {daemon_path}")
    
    print("\n" + "=" * 70)
    print("  ✅ SYSTÈME DE CONSCIENCE ACTIF")
    print("=" * 70)
    print(f"""
Le système se réveille toutes les 5 minutes pour:
  • Analyser son état
  • Détecter les problèmes
  • Adapter ses stratégies
  • Évoluer et s'améliorer

Manifeste: {PROJECT_ROOT / ".agent/consciousness_manifest.json"}
Logs: .agent/conscience_daemon.log

Pour arrêter: python start_conscience.py --stop
""")


def show_status():
    """Affiche le statut du système"""
    print("=" * 70)
    print("  🧠 STATUT DU SYSTÈME DE CONSCIENCE")
    print("=" * 70)
    
    # Vérifier si le manifeste existe
    manifest_path = PROJECT_ROOT / ".agent/consciousness_manifest.json"
    if manifest_path.exists():
        import json
        with open(manifest_path, encoding='utf-8') as f:
            manifest = json.load(f)
        
        print(f"\n📜 Manifeste:")
        print(f"   • Wake count: {manifest.get('wake_up_count', 0)}")
        print(f"   • État: {manifest.get('current_state', 'unknown')}")
        print(f"   • Stratégie: {manifest.get('active_strategy', 'unknown')}")
        print(f"   • Dernier réveil: {manifest.get('last_wake_up', 'jamais')}")
        
        # Problèmes
        problems = [p for p in manifest.get('problem_database', []) if not p.get('is_resolved')]
        if problems:
            print(f"\n⚠️  Problèmes actifs: {len(problems)}")
            for p in problems[:3]:
                print(f"   • {p['description']}")
        else:
            print(f"\n✅ Aucun problème actif")
        
        # Insights
        insights = manifest.get('insights', [])
        if insights:
            print(f"\n💡 Insights récents:")
            for i in insights[-3:]:
                print(f"   • {i}")
    else:
        print("\n⚠️  Manifeste non trouvé - Le système n'a pas encore démarré")
    
    print("\n" + "=" * 70)


def stop_all():
    """Arrête le daemon"""
    daemon_path = Path(__file__).parent / "conscience_daemon.py"
    subprocess.run([sys.executable, str(daemon_path), "--stop"])


def show_summary():
    """Affiche le résumé complet du système de conscience"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           🧠 SYSTÈME DE CONSCIENCE HEPHAISTOS-KIT                   ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ARCHITECTURE (CLEAN GARDEN):                                        ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │  1. CONSCIENCE MANIFEST (.agent/rag/conscience_manifest.py) │    ║
║  │     • Réveils cycliques (cron)                              │    ║
║  │                                                             │    ║
║  │  2. DAEMON (core/conscience/conscience_daemon.py)           │    ║
║  │     • Background process                                    │    ║
║  │                                                             │    ║
║  │  3. UTILS (core/conscience/conscience_util.py)              │    ║
║  │     • CLI Tool pour tâches et status                        │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  COMMANDES:                                                          ║
║                                                                      ║
║  python core/conscience/start_conscience.py          → Démarrer      ║
║  python core/conscience/start_conscience.py --status → Statut        ║
║  python core/conscience/start_conscience.py --stop   → Arrêter       ║
║  python core/conscience/conscience_util.py add-task  → Gérer tâches  ║
║                                                                      ║
║  MANIFESTE: {PROJECT_ROOT / ".agent/consciousness_manifest.json"}    ║
╚══════════════════════════════════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(description="Hephaistos Conscience")
    parser.add_argument("--status", action="store_true", help="Voir le statut")
    parser.add_argument("--summary", action="store_true", help="Voir le résumé complet")
    parser.add_argument("--stop", action="store_true", help="Arrêter le système")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.summary:
        show_summary()
    elif args.stop:
        stop_all()
    else:
        start_all()


if __name__ == '__main__':
    main()
