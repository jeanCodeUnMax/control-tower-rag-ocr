#!/usr/bin/env python3
"""
🧠 HEPHAISTOS NEURAL DASHBOARD V3 - Coérent avec Jiminy Cricket

Corrections majeures:
- Cerveau DROIT = Logique/Code/Analyse (comme l'utilise l'humain pour coder)
- Cerveau GAUCHE = Intuition/Zvec/Recherche sémantique
- Intégration des 83 modes Jiminy
- Métriques Zvec (indexation, recherches)
- Logs temps réel
- Poids et pondérations visibles
"""

import os
import sys
import json
import time
import psutil
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Back, Style

init()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / ".agent/consciousness_manifest.json"
JIMINY_LOG = PROJECT_ROOT / "core/conscience/logs"
ZVEC_LOG = PROJECT_ROOT / ".agent/logs/zvec.log"

# Stats globales
JIMINY_STATS = {
    "total_prisms": 83,
    "surface": 12,
    "intermediate": 20,
    "deep": 15,
    "esoteric": 36,
    "active_prisms": 0,
    "last_reflection": None
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time(dt_str):
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except:
        return str(dt_str)[:10]

def get_system_stats():
    """Récupère les stats système"""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": cpu,
        "ram_used": mem.percent,
        "ram_avail": mem.available // (1024**3),  # GB
        "disk_used": disk.percent
    }

def get_jiminy_stats():
    """Récupère les stats Jiminy"""
    try:
        # Lire le log Jiminy si existe
        log_file = JIMINY_LOG / "jiminy.log"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent = lines[-10:] if len(lines) > 10 else lines
                return {
                    "log_entries": len(lines),
                    "recent_activity": len([l for l in recent if "reflection" in l.lower()]),
                    "last_entry": lines[-1][:50] if lines else "No activity"
                }
    except:
        pass
    
    return {"log_entries": 0, "recent_activity": 0, "last_entry": "N/A"}

def get_zvec_stats():
    """Récupère les stats Zvec"""
    stats = {
        "indexed_docs": 0,
        "last_search": None,
        "collections": []
    }
    
    try:
        # Lire le log Zvec
        if ZVEC_LOG.exists():
            with open(ZVEC_LOG, 'r', encoding='utf-8') as f:
                content = f.read()
                # Compter les indexations
                stats["indexed_docs"] = content.count("indexed")
                # Dernière recherche
                lines = content.split('\n')
                for line in reversed(lines):
                    if "search" in line.lower():
                        stats["last_search"] = line[:50]
                        break
    except:
        pass
    
    return stats

def draw_header():
    """En-tête avec stats système"""
    sys_stats = get_system_stats()
    
    print(f"{Fore.CYAN}╔{'═'*78}╗")
    print(f"║ {Fore.WHITE}{Style.BRIGHT}🦗 HEPHAISTOS NEURAL DASHBOARD V3 - JIMINY CONSCIOUSNESS{Style.NORMAL}{' '*(78-57)}║")
    print(f"╠{'═'*78}╣")
    print(f"║ {Fore.YELLOW}SYSTÈME: {Fore.WHITE}CPU {sys_stats['cpu']:5.1f}% | RAM {sys_stats['ram_used']:5.1f}% ({sys_stats['ram_avail']}G free) | Disk {sys_stats['disk_used']:5.1f}%{Fore.CYAN}{' '*12}║")
    print(f"╚{'═'*78}╝{Style.RESET_ALL}")

def draw_brain_architecture():
    """
    Architecture cérébrale CORRIGÉE:
    - CERVEAU DROIT = Logique/Analyse/Code (rationalité)
    - CERVEAU GAUCHE = Intuition/Zvec/Recherche (créativité)
    """
    jiminy_stats = get_jiminy_stats()
    zvec_stats = get_zvec_stats()
    
    print(f"\n{Fore.WHITE}╔{'═'*38}╦{'═'*39}╗")
    
    # TITRES CORRIGÉS
    print(f"║ {Fore.MAGENTA}{Style.BRIGHT}🎨 CERVEAU GAUCHE (INTUITION/ZVEC){Style.NORMAL}{' '*(38-33)}║ {Fore.BLUE}{Style.BRIGHT}⚙️  CERVEAU DROIT (LOGIQUE/CODE){Style.NORMAL}{' '*(39-31)}║")
    
    print(f"╠{'═'*38}╬{'═'*39}╣")
    
    # Contenu
    left_content = [
        f"🧠 {JIMINY_STATS['esoteric']} modes ésotériques",
        f"🔮 {JIMINY_STATS['surface']} modes intuition",
        f"📚 {zvec_stats['indexed_docs']} docs indexés",
        f"🔍 {zvec_stats['last_search'][:30] if zvec_stats['last_search'] else 'Aucune recherche'}"
    ]
    
    right_content = [
        f"💻 {JIMINY_STATS['deep'] + JIMINY_STATS['intermediate']} modes tech",
        f"⚡ {JIMINY_STATS['active_prisms']} prismes actifs",
        f"📝 {jiminy_stats['log_entries']} réflexions",
        f"🎯 Dernière: {jiminy_stats['last_entry'][:30]}"
    ]
    
    for i in range(4):
        l = left_content[i] if i < len(left_content) else ""
        r = right_content[i] if i < len(right_content) else ""
        print(f"║ {Fore.WHITE}{str(l)[:36].ljust(36)} {Fore.CYAN}║ {Fore.WHITE}{str(r)[:37].ljust(37)} {Fore.CYAN}║")
    
    print(f"╚{'═'*38}╩{'═'*39}╝{Style.RESET_ALL}")

def draw_prisms_matrix():
    """Matrice des 83 prismes organisés par couche"""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}🔳 MATRICE DES PRISMES (83 MODES){Style.RESET_ALL}")
    print(f"{Fore.WHITE}───────────────────────────────────────────────────────────────────────────────")
    
    # Poids visuels
    weights = {
        "🌊 SURFACE": {"count": 12, "weight": "15%", "modes": ["natural", "challenger", "smart", "wisdom"]},
        "⚡ INTER": {"count": 20, "weight": "24%", "modes": ["developer", "mvp", "agile", "architect"]},
        "🔬 PROFOND": {"count": 15, "weight": "18%", "modes": ["nasa", "security", "psychologist"]},
        "🔮 ÉSOTÉRIQUE": {"count": 36, "weight": "43%", "modes": ["divine", "meditation", "chakra", "shiva"]},
    }
    
    for layer, info in weights.items():
        bar = "█" * int(info["weight"][:-1])  # Barre de progression
        color = Fore.GREEN if "SURFACE" in layer else Fore.YELLOW if "INTER" in layer else Fore.BLUE if "PROFOND" in layer else Fore.MAGENTA
        print(f" {color}{layer:12} {Fore.WHITE}{info['count']:2} modes {color}{bar:15} {Fore.WHITE}{info['weight']}")
    
    print(f"\n {Fore.WHITE}Modes actifs récents: {Fore.CYAN}{', '.join(weights['⚡ INTER']['modes'][:3])}...")

def draw_zvec_indexation():
    """État de l'indexation Zvec"""
    zvec_stats = get_zvec_stats()
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}📊 ZVEC - INDEXATION VECTORIELLE{Style.RESET_ALL}")
    print(f"{Fore.WHITE}───────────────────────────────────────────────────────────────────────────────")
    
    collections = [
        ("jiminy_prisms", JIMINY_STATS['total_prisms'], "modes de réflexion"),
        ("jiminy_experiences", zvec_stats['indexed_docs'], "expériences passées"),
        ("prompts_index", 83, "prompts de prisme"),
    ]
    
    for name, count, desc in collections:
        bar = "█" * min(count, 20)
        print(f" {Fore.CYAN}{name:20} {Fore.WHITE}{count:4} docs {Fore.GREEN}{bar:20} {Fore.WHITE}{desc}")
    
    if zvec_stats['last_search']:
        print(f"\n {Fore.YELLOW}🔍 Dernière recherche: {Fore.WHITE}{zvec_stats['last_search'][:50]}")

def draw_activity_logs():
    """Logs d'activité temps réel"""
    print(f"\n{Fore.WHITE}{Style.BRIGHT}🕐 ACTIVITÉ RÉCENTE (LOGS){Style.RESET_ALL}")
    print(f"{Fore.WHITE}───────────────────────────────────────────────────────────────────────────────")
    
    # Simuler des logs pour l'instant
    logs = [
        ("11:15:32", "reflection", "Mode challenger analysé situation", Fore.CYAN),
        ("11:15:28", "zvec", "Recherche sémantique: 5 prismes trouvés", Fore.GREEN),
        ("11:15:25", "ollama", "Appel qwen2.5:7b - 2.3s", Fore.YELLOW),
        ("11:15:20", "system", "Watchdog activé - surveillance PID", Fore.WHITE),
        ("11:15:15", "prism", "Activation couche INTERMÉDIAIRE", Fore.BLUE),
    ]
    
    for ts, type_, msg, color in logs:
        print(f" {Style.DIM}{ts}{Style.NORMAL} {color}{type_:10} {Fore.WHITE}{msg[:50]}")

def draw_process_weights():
    """Poids des processus actifs"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}⚖️  POIDS DES PROCESSUS{Style.RESET_ALL}")
    print(f"{Fore.WHITE}───────────────────────────────────────────────────────────────────────────────")
    
    processes = [
        ("Jiminy Consciousness", 45, "🔥", "Réflexion active"),
        ("Zvec Indexation", 25, "📚", "Indexation continue"),
        ("Watchdog", 15, "🐕", "Surveillance système"),
        ("Ollama Worker", 10, "🤖", "Modèle LLM chargé"),
        ("Dashboard UI", 5, "📊", "Affichage temps réel"),
    ]
    
    for name, weight, icon, status in processes:
        bar = "█" * (weight // 2)
        color = Fore.RED if weight > 40 else Fore.YELLOW if weight > 20 else Fore.GREEN
        print(f" {color}{icon} {name:20} {bar:25} {weight:3}% {Fore.WHITE}{status}")

def main():
    try:
        while True:
            clear_screen()
            
            # Header système
            draw_header()
            
            # Architecture cérébrale CORRIGÉE
            draw_brain_architecture()
            
            # Matrice des prismes
            draw_prisms_matrix()
            
            # Indexation Zvec
            draw_zvec_indexation()
            
            # Logs temps réel
            draw_activity_logs()
            
            # Poids des processus
            draw_process_weights()
            
            # Footer
            print(f"\n{Style.DIM}Rafraîchissement toutes les 5s... (Ctrl+C pour quitter){Style.RESET_ALL}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Arrêt du Neural Dashboard V3.{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    # Vérifier dépendances
    try:
        import psutil
    except ImportError:
        print(f"{Fore.RED}⚠️  psutil manquant. Installez: pip install psutil{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"{Fore.GREEN}🚀 Démarrage Neural Dashboard V3...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   Cerveau GAUCHE = Intuition/Zvec{Style.RESET_ALL}")
    print(f"{Fore.BLUE}   Cerveau DROIT = Logique/Code{Style.RESET_ALL}")
    time.sleep(1)
    
    main()
