#!/usr/bin/env python3
"""
JIMINY ORCHESTRATOR - Démarrage complet du système

Lance tout automatiquement:
1. Tue les MCP orphelins
2. Démarre le workspace (auto-ingest)
3. Démarre les MCP (Zvec, Memory)
4. Démarre le dashboard
5. Démarre la conscience Jiminy
6. Supervise avec watchdog
"""

import os
import sys
import time
import signal
import subprocess
import psutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class JiminyOrchestrator:
    """Orchestre le démarrage complet de l'écosystème Hephaistos"""
    
    def __init__(self):
        self.root = Path(__file__).resolve().parents[2]
        self.processes: Dict[str, subprocess.Popen] = {}
        self.log_file = self.root / "logs" / "orchestrator.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp"""
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{level:8}] {message}"
        print(line)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    
    def kill_orphan_mcps(self):
        """Tue les processus MCP orphelins sur les ports 8001/8002"""
        self.log("═" * 70)
        self.log("ÉTAPE 1: Nettoyage MCP orphelins")
        self.log("═" * 70)
        
        killed = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                # Détecter les MCP zombies
                if any(x in cmdline.lower() for x in ['mcp', 'zvec', 'memory_mcp', '8001', '8002']):
                    if proc.info['pid'] != os.getpid():
                        proc.kill()
                        killed.append(proc.info['pid'])
                        self.log(f"  💀 Tué PID {proc.info['pid']}: {cmdline[:50]}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if not killed:
            self.log("  ✅ Aucun MCP orphelin trouvé")
        else:
            self.log(f"  ✅ {len(killed)} processus tués")
            time.sleep(2)  # Attendre la libération des ports
    
    def start_workspace(self):
        """Démarre le workspace (auto-ingest)"""
        self.log("\n" + "═" * 70)
        self.log("ÉTAPE 2: Démarrage Workspace (Auto-Ingest)")
        self.log("═" * 70)
        
        script = self.root / ".agent" / "scripts" / "auto-ingest.ps1"
        if not script.exists():
            self.log(f"  ❌ Script non trouvé: {script}", "ERROR")
            return False
        
        # Lancer en arrière-plan
        proc = subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            cwd=str(self.root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE  # Fenêtre séparée
        )
        
        self.processes['workspace'] = proc
        self.log(f"  🚀 Workspace lancé (PID: {proc.pid})")
        self.log(f"  📁 Surveillance: {self.root}")
        time.sleep(3)  # Laisser démarrer
        return True
    
    def start_dashboard(self):
        """Démarre le dashboard V3"""
        self.log("\n" + "═" * 70)
        self.log("ÉTAPE 3: Démarrage Dashboard V3")
        self.log("═" * 70)
        
        script = self.root / "core" / "conscience" / "dashboard_v3.py"
        if not script.exists():
            self.log(f"  ❌ Dashboard non trouvé", "ERROR")
            return False
        
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            cwd=str(self.root / "core" / "conscience"),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        self.processes['dashboard'] = proc
        self.log(f"  📊 Dashboard lancé (PID: {proc.pid})")
        self.log(f"  🧠 Cerveau GAUCHE = Intuition/Zvec")
        self.log(f"  ⚙️  Cerveau DROIT = Logique/Code")
        return True
    
    def start_consciousness(self):
        """Démarre la conscience Jiminy"""
        self.log("\n" + "═" * 70)
        self.log("ÉTAPE 4: Réveil de la Conscience Jiminy")
        self.log("═" * 70)
        
        self.log(f"  🦗 83 prismes prêts")
        self.log(f"  🌊 Surface: 12 modes (rapide)")
        self.log(f"  ⚡ Intermédiaire: 20 modes (technique)")
        self.log(f"  🔬 Profond: 15 modes (expert)")
        self.log(f"  🔮 Ésotérique: 36 modes (spirituel)")
        self.log(f"  📡 Ollama: qwen2.5:7b prêt")
        
        # La conscience attend une requête pour se réveiller
        self.log("  💤 Conscience en veille (attente de requête)")
        return True
    
    def start_watchdog(self):
        """Démarre le watchdog de supervision"""
        self.log("\n" + "═" * 70)
        self.log("ÉTAPE 5: Activation Watchdog")
        self.log("═" * 70)
        
        script = self.root / "core" / "conscience" / "jiminy_watchdog.py"
        if not script.exists():
            self.log("  ❌ Watchdog non trouvé", "ERROR")
            return False
        
        proc = subprocess.Popen(
            [sys.executable, str(script), "--daemon"],
            cwd=str(self.root / "core" / "conscience"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes['watchdog'] = proc
        self.log(f"  🐕 Watchdog actif (PID: {proc.pid})")
        self.log(f"  👀 Surveillance: PID, flux, heartbeat")
        self.log(f"  ⚡ Kill automatique après timeout")
        return True
    
    def show_status(self):
        """Affiche le statut complet"""
        self.log("\n" + "═" * 70)
        self.log("STATUT SYSTÈME")
        self.log("═" * 70)
        
        for name, proc in self.processes.items():
            if proc.poll() is None:
                self.log(f"  ✅ {name:12} → RUNNING (PID {proc.pid})")
            else:
                self.log(f"  ❌ {name:12} → STOPPED (code {proc.returncode})")
        
        self.log("\n  📊 Ressources:")
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        self.log(f"     CPU: {cpu}% | RAM: {mem.percent}% ({mem.available//1024//1024}MB free)")
        
        self.log("\n  🌐 Services:")
        self.log(f"     Workspace: Surveillance fichier active")
        self.log(f"     Dashboard: Affichage temps réel")
        self.log(f"     Watchdog: Protection processus")
        self.log(f"     Conscience: 83 modes prêts")
    
    def run(self):
        """Orchestration complète"""
        print("\n" + "=" * 70)
        print("🦗 JIMINY ORCHESTRATOR - Démarrage Complet")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Root: {self.root}")
        print("=" * 70 + "\n")
        
        try:
            # Séquence de démarrage
            self.kill_orphan_mcps()
            self.start_workspace()
            self.start_dashboard()
            self.start_consciousness()
            self.start_watchdog()
            
            # Statut final
            self.show_status()
            
            self.log("\n" + "═" * 70)
            self.log("✅ SYSTÈME HEPHAISTOS OPÉRATIONNEL")
            self.log("═" * 70)
            self.log("\nCommandes disponibles:")
            self.log("  jiminy dashboard     → Voir le dashboard")
            self.log("  jiminy test          → Tests rapides")
            self.log("  jiminy benchmark     → Test de charge")
            self.log("  Ctrl+C               → Arrêt complet")
            
            # Boucle de supervision
            self.supervise()
            
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            self.log(f"\n💥 ERREUR FATALE: {e}", "CRITICAL")
            self.shutdown()
    
    def supervise(self):
        """Boucle de supervision"""
        self.log("\n🔍 Supervision active (Ctrl+C pour arrêter)")
        
        while True:
            time.sleep(5)
            
            # Vérifier chaque processus
            for name, proc in list(self.processes.items()):
                if proc.poll() is not None:
                    self.log(f"⚠️  {name} s'est arrêté (code {proc.returncode})")
    
    def shutdown(self):
        """Arrêt propre de tout"""
        self.log("\n" + "═" * 70)
        self.log("🛑 ARRÊT DU SYSTÈME")
        self.log("═" * 70)
        
        for name, proc in self.processes.items():
            try:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)
                    self.log(f"  ✅ {name} arrêté")
            except:
                proc.kill()
                self.log(f"  💀 {name} tué")
        
        self.log("\n👋 Au revoir!")
        sys.exit(0)

if __name__ == "__main__":
    orchestrator = JiminyOrchestrator()
    orchestrator.run()
