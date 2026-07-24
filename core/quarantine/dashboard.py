#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 HEPHAISTOS NEURO-DASHBOARD - Version Bio-Inspirée V2.0
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialiser colorama
init()

# Configurer les chemins
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / ".agent/consciousness_manifest.json"
LOG_FILE = PROJECT_ROOT / ".agent/conscience_daemon.log"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_timestamp(ts):
    if not ts: return "N/A"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except:
        return ts[:10] if ts else "N/A"

def draw_header(manifest):
    state = str(manifest.get('current_state', 'healthy')).upper()
    wake_count = manifest.get('wake_up_count', 0)
    last_wake = format_timestamp(manifest.get('last_wake_up'))
    strategy = manifest.get('active_strategy', 'standard')
    
    color = Fore.GREEN if state == 'HEALTHY' else Fore.YELLOW if state == 'DEGRADED' else Fore.RED
    
    print(f"{Fore.CYAN}╔{'═'*78}╗")
    print(f"║ {Fore.WHITE}{Style.BRIGHT}🧠 HEPHAISTOS NEURO-DASHBOARD V2.0 (BIO-INSPIRED){Style.NORMAL}{' '*(77-49)}║")
    print(f"╠{'═'*20}╦{'═'*57}╣")
    print(f"║ {Fore.WHITE}ÉTAT COGNITIF:    ║ {color}{state.ljust(55)}{Fore.CYAN} ║")
    print(f"║ {Fore.WHITE}CYCLES (RÉVEILS): ║ {Fore.WHITE}{str(wake_count).ljust(55)}{Fore.CYAN} ║")
    print(f"║ {Fore.WHITE}MÉMOIRE COURT T.: ║ {Fore.WHITE}{last_wake.ljust(55)}{Fore.CYAN} ║")
    print(f"║ {Fore.WHITE}FOCUS ACTUEL:     ║ {Fore.WHITE}{strategy.ljust(55)}{Fore.CYAN} ║")
    print(f"╚{'═'*20}╩{'═'*57}╝{Style.RESET_ALL}")

def draw_brain_hemispheres(manifest):
    brain = manifest.get('brain_architecture', {})
    left = brain.get('left_hemisphere', {})
    right = brain.get('right_hemisphere', {})
    
    print(f"\n{Fore.WHITE}╔{'═'*38}╦{'═'*39}╗")
    print(f"║ {Fore.BLUE}{Style.BRIGHT}CERVEAU GAUCHE (LOGIQUE/CODE){Style.NORMAL}{' '*(38-29)}║ {Fore.MAGENTA}{Style.BRIGHT}CERVEAU DROIT (INTUITION/ZVEC){Style.NORMAL}{' '*(39-30)}║")
    print(f"╠{'═'*38}╬{'═'*39}╣")
    
    # Extraire les faits et intuitions
    facts = left.get('facts', [])[-3:] if left.get('facts') else ["(En attente de faits)"]
    intuitions = right.get('associations', [])[-3:] if right.get('associations') else ["(En attente d'intuitions)"]
    
    for i in range(3):
        f = facts[i] if i < len(facts) else ""
        it = intuitions[i] if i < len(intuitions) else ""
        print(f"║ {Fore.WHITE}{str(f)[:36].ljust(36)} {Fore.CYAN}║ {Fore.WHITE}{str(it)[:37].ljust(37)} {Fore.CYAN}║")
        
    print(f"╚{'═'*38}╩{'═'*39}╝{Style.RESET_ALL}")

def draw_consciousness_layers(manifest):
    brain = manifest.get('brain_architecture', {})
    conscious = brain.get('conscious_layer', {})
    subconscious = brain.get('subconscious_layer', {})
    
    print(f"\n{Fore.YELLOW}🔦 COUCHE CONSCIENTE (FOCUS ACTUEL){Style.RESET_ALL}")
    thought = conscious.get('active_thought', 'Veille cognitive')
    intent = conscious.get('current_intent', 'Stabilisation')
    print(f" {Fore.WHITE}→ PENSÉE: {Fore.CYAN}{thought}")
    print(f" {Fore.WHITE}→ INTENTION: {Fore.GREEN}{intent}")
    
    print(f"\n{Fore.BLUE}🌊 COUCHE SUBCONSCIENTE (PROCESSUS){Style.RESET_ALL}")
    processes = ", ".join(subconscious.get('background_processes', []))
    print(f" {Fore.WHITE}→ ACTIVITÉS: {Fore.BLUE}{processes}")

def draw_timeline(manifest):
    timeline = manifest.get('timeline', [])
    print(f"\n{Fore.WHITE}🕐 MÉMOIRE COURT TERME (ÉVÉNEMENTS RECENT){Style.RESET_ALL}")
    print(f"{Fore.WHITE}────────────────────────────────────────────────────────────────────────────────")
    
    for evt in timeline[-5:]:
        ts = format_timestamp(evt.get('timestamp'))
        desc = evt.get('description', 'Inconnu')
        refl = evt.get('reflection_type', 'standard')
        
        color = Fore.CYAN if refl == 'deep' else Fore.GREEN if refl == 'scientific' else Fore.WHITE
        if 'error' in desc.lower(): color = Fore.RED
        
        print(f" {Style.DIM}{ts}{Style.NORMAL} {color}{desc[:70].ljust(70)}")

def draw_dev_book(manifest):
    dev_book = manifest.get('dev_book', {})
    todos = dev_book.get('todo', [])
    print(f"\n{Fore.MAGENTA}📋 DEV BOOK (TÂCHES EN ATTENTE){Style.RESET_ALL}")
    print(f"{Fore.WHITE}────────────────────────────────────────────────────────────────────────────────")
    if not todos:
        print(f" {Style.DIM}Aucune tâche en attente.{Style.RESET_ALL}")
    else:
        for t in todos[-4:]:  # Afficher les 4 dernières
             task_desc = str(t.get('task', 'Inconnu'))
             prio = str(t.get('priority', 'medium'))
             color = Fore.RED if 'high' in prio.lower() else Fore.YELLOW if 'medium' in prio.lower() else Fore.WHITE
             print(f" {color}[{prio.upper()[:4]}] {Fore.WHITE}{task_desc[:70].ljust(70)}")

def main():
    try:
        while True:
            if MANIFEST_PATH.exists():
                try:
                    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    
                    clear_screen()
                    draw_header(manifest)
                    draw_brain_hemispheres(manifest)
                    draw_consciousness_layers(manifest)
                    draw_timeline(manifest)
                    draw_dev_book(manifest)
                    
                    print(f"\n{Style.DIM}Rafraîchissement toutes les 5s... (Ctrl+C pour quitter){Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Erreur Dashboard: {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Manifeste non trouvé à {MANIFEST_PATH}{Style.RESET_ALL}")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Arrêt du Neuro-Dashboard.{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    main()
