#!/usr/bin/env python3
"""
CONSCIENCE UTIL - Scripts de lecture/écriture/modification robustes

Usage:
    python conscience_util.py read              # Lire manifeste
    python conscience_util.py add-task "Indexer BDD" high
    python conscience_util.py wake              # Réveil manuel
    python conscience_util.py status            # Statut complet
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration des chemins par rapport à la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / ".agent/consciousness_manifest.json"


def read_manifest():
    """Lire le manifeste de conscience"""
    try:
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erreur lecture: {e}")
        return None


def write_manifest(data):
    """Écrire le manifeste"""
    try:
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erreur écriture: {e}")
        return False


def show_status():
    """Afficher statut complet"""
    m = read_manifest()
    if not m:
        return
    
    print("=" * 60)
    print("  🧠 SYSTÈME DE CONSCIENCE")
    print("=" * 60)
    print(f"\n📊 Réveils: {m.get('wake_up_count', 0)}")
    print(f"📈 État: {m.get('current_state', 'inconnu').upper()}")
    print(f"🎯 Stratégie: {m.get('active_strategy', 'inconnu')}")
    print(f"🕐 Dernier: {m.get('last_wake_up', 'jamais')[:19]}")
    
    dev_book = m.get('dev_book', {})
    print(f"\n📋 DEV BOOK:")
    print(f"   À faire: {len(dev_book.get('todo', []))}")
    print(f"   En cours: {len(dev_book.get('in_progress', []))}")
    print(f"   Bloqués: {len(dev_book.get('blocked', []))}")
    print(f"   Faits: {len(dev_book.get('done_today', []))}")
    
    pending = m.get('actions_pending', [])
    if pending:
        print(f"\n⚡ Actions en attente: {len(pending)}")
        for a in pending[:3]:
            print(f"   • {a.get('description', 'Inconnu')[:40]}")
    
    print("\n" + "=" * 60)


def add_task(task_desc: str, priority: str = "medium"):
    """Ajouter une tâche au Dev Book"""
    m = read_manifest()
    if not m:
        return
    
    dev_book = m.setdefault('dev_book', {'todo': [], 'in_progress': [], 'blocked': [], 'done': []})
    
    task = {
        "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "task": task_desc,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "source": "manual"
    }
    
    dev_book['todo'].append(task)
    
    if write_manifest(m):
        print(f"✅ Tâche ajoutée: [{priority}] {task_desc}")
    

def list_tasks():
    """Lister toutes les tâches"""
    m = read_manifest()
    if not m:
        return
    
    dev_book = m.get('dev_book', {})
    
    print("\n📋 TÂCHES À FAIRE:")
    for t in dev_book.get('todo', []):
        print(f"   [{t.get('priority', '?')}] {t.get('task', 'Inconnu')}")
    
    if dev_book.get('blocked'):
        print("\n🚧 BLOQUÉES:")
        for t in dev_book['blocked']:
            print(f"   {t.get('task', 'Inconnu')}")


def wake_manual():
    """Réveil manuel simple"""
    m = read_manifest()
    if not m:
        return
    
    # Incrémenter compteur
    m['wake_up_count'] = m.get('wake_up_count', 0) + 1
    m['last_wake_up'] = datetime.now().isoformat()
    
    # Ajouter événement simple (sans appeler _add_event)
    timeline = m.setdefault('timeline', [])
    timeline.append({
        "timestamp": datetime.now().isoformat(),
        "event_type": "manual_wake",
        "description": "Réveil manuel utilisateur",
        "context": {"wake_num": m['wake_up_count']}
    })
    
    if write_manifest(m):
        print(f"🌅 Réveil #{m['wake_up_count']} effectué")
    

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "read" or cmd == "status":
        show_status()
    elif cmd == "add-task":
        if len(sys.argv) < 3:
            print("Usage: conscience_util.py add-task 'description' [priority]")
            return
        desc = sys.argv[2]
        prio = sys.argv[3] if len(sys.argv) > 3 else "medium"
        add_task(desc, prio)
    elif cmd == "list-tasks":
        list_tasks()
    elif cmd == "wake":
        wake_manual()
    else:
        print(f"Commande inconnue: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
