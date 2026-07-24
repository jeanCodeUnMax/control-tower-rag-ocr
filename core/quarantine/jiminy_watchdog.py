#!/usr/bin/env python3
"""
JIMINY WATCHDOG - Supervision et contrôle des processus

Fonctionnalités:
- Surveillance des flux stdin/stdout/stderr
- Redirection des logs
- Détection de processus bloqués (PID)
- Kill des processus zombies
- Watchdog sur fichiers (taille, modification)
- Heartbeat monitoring
"""

import os
import sys
import time
import signal
import psutil
import asyncio
import subprocess
from datetime import datetime
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class ProcessInfo:
    """Information sur un processus surveillé"""
    pid: int
    name: str
    cmdline: List[str]
    start_time: float
    last_activity: float
    stdout_size: int = 0
    stderr_size: int = 0
    stdin_active: bool = False
    status: str = "running"


class ProcessWatchdog:
    """
    Watchdog pour surveiller et contrôler les processus.
    """
    
    def __init__(self, timeout_seconds: int = 60):
        self.timeout = timeout_seconds
        self.monitored_processes: Dict[int, ProcessInfo] = {}
        self.log_buffer: List[str] = []
        self.running = False
        self._shutdown_event = asyncio.Event()
        
    async def monitor_process(
        self,
        process: subprocess.Popen,
        name: str,
        on_stall: Optional[Callable] = None,
        on_output: Optional[Callable[[str], None]] = None
    ) -> ProcessInfo:
        """
        Surveille un processus avec ses flux.
        
        Args:
            process: Processus Popen à surveiller
            name: Nom identifiant
            on_stall: Callback si blocage détecté
            on_output: Callback pour chaque ligne de sortie
        """
        pid = process.pid
        info = ProcessInfo(
            pid=pid,
            name=name,
            cmdline=process.args if isinstance(process.args, list) else [process.args],
            start_time=time.time(),
            last_activity=time.time()
        )
        self.monitored_processes[pid] = info
        
        # Surveillance des flux
        async def watch_stream(stream, stream_name):
            """Surveille un flux (stdout/stderr)"""
            while self.running and process.poll() is None:
                try:
                    # Lecture non-bloquante
                    if stream:
                        line = await asyncio.wait_for(
                            asyncio.get_event_loop().run_in_executor(
                                None, stream.readline
                            ),
                            timeout=1.0
                        )
                        if line:
                            decoded = line.decode('utf-8', errors='replace').rstrip()
                            info.last_activity = time.time()
                            
                            if stream_name == 'stdout':
                                info.stdout_size += len(decoded)
                            else:
                                info.stderr_size += len(decoded)
                            
                            # Log et callback
                            log_line = f"[{name}:{stream_name}] {decoded}"
                            self.log_buffer.append(log_line)
                            
                            if on_output:
                                on_output(decoded)
                            
                            # Trunc buffer si trop grand
                            if len(self.log_buffer) > 1000:
                                self.log_buffer = self.log_buffer[-500:]
                except asyncio.TimeoutError:
                    # Pas de sortie, c'est OK
                    pass
                except Exception as e:
                    self.log_buffer.append(f"[{name}:ERROR] {e}")
                    break
        
        # Lancer les watchers
        if process.stdout:
            asyncio.create_task(watch_stream(process.stdout, 'stdout'))
        if process.stderr:
            asyncio.create_task(watch_stream(process.stderr, 'stderr'))
        
        # Heartbeat checker
        asyncio.create_task(self._heartbeat_checker(pid, on_stall))
        
        return info
    
    async def _heartbeat_checker(
        self,
        pid: int,
        on_stall: Optional[Callable] = None
    ):
        """Vérifie régulièrement que le processus répond"""
        while self.running and pid in self.monitored_processes:
            await asyncio.sleep(5)  # Check toutes les 5s
            
            if pid not in self.monitored_processes:
                break
            
            info = self.monitored_processes[pid]
            inactive_time = time.time() - info.last_activity
            
            if inactive_time > self.timeout:
                # Processus inactif depuis trop longtemps
                warning = f"⚠️ Processus {info.name} (PID {pid}) inactif depuis {inactive_time:.0f}s"
                self.log_buffer.append(warning)
                print(warning, file=sys.stderr)
                
                if on_stall:
                    try:
                        on_stall(info)
                    except Exception as e:
                        self.log_buffer.append(f"[ERROR] on_stall callback failed: {e}")
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """
        Tue un processus surveillé.
        
        Args:
            pid: ID du processus
            force: Si True, envoie SIGKILL, sinon SIGTERM
        """
        try:
            if pid in self.monitored_processes:
                info = self.monitored_processes[pid]
                
                try:
                    proc = psutil.Process(pid)
                    
                    if force:
                        proc.kill()  # SIGKILL
                        self.log_buffer.append(f"[KILL] Processus {pid} tué (SIGKILL)")
                    else:
                        proc.terminate()  # SIGTERM
                        self.log_buffer.append(f"[TERM] Processus {pid} terminé (SIGTERM)")
                    
                    info.status = "killed" if force else "terminated"
                    return True
                    
                except psutil.NoSuchProcess:
                    self.log_buffer.append(f"[INFO] Processus {pid} déjà terminé")
                    return True
                    
        except Exception as e:
            self.log_buffer.append(f"[ERROR] Échec kill PID {pid}: {e}")
            return False
    
    def kill_zombies(self) -> List[int]:
        """
        Tue tous les processus zombies (inactifs depuis > timeout).
        
        Returns:
            Liste des PID tués
        """
        killed = []
        now = time.time()
        
        for pid, info in list(self.monitored_processes.items()):
            inactive = now - info.last_activity
            
            if inactive > self.timeout * 2:  # 2x timeout = zombie
                if self.kill_process(pid, force=True):
                    killed.append(pid)
                del self.monitored_processes[pid]
        
        return killed
    
    def get_logs(self, lines: int = 100) -> List[str]:
        """Retourne les dernières lignes de log"""
        return self.log_buffer[-lines:]
    
    def save_logs(self, filepath: str):
        """Sauvegarde les logs dans un fichier"""
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"Logs du {datetime.now().isoformat()}\n")
            f.write(f"{'='*70}\n")
            for line in self.log_buffer:
                f.write(line + '\n')
    
    async def start(self):
        """Démarre le watchdog"""
        self.running = True
        self._shutdown_event.clear()
        print("🐕 Watchdog démarré")
    
    async def stop(self):
        """Arrête le watchdog proprement"""
        self.running = False
        self._shutdown_event.set()
        
        # Tuer tous les processus restants
        for pid in list(self.monitored_processes.keys()):
            self.kill_process(pid, force=False)
        
        print("🐕 Watchdog arrêté")


class FileWatchdog:
    """
    Watchdog pour surveiller les fichiers (logs, outputs).
    Détecte si un fichier stagne (pas de modification).
    """
    
    def __init__(self, check_interval: int = 5):
        self.check_interval = check_interval
        self.watched_files: Dict[str, Dict] = {}
        self.running = False
    
    def watch_file(
        self,
        filepath: str,
        stall_timeout: int = 30,
        on_stall: Optional[Callable[[str], None]] = None,
        on_change: Optional[Callable[[str, int], None]] = None
    ):
        """
        Surveille un fichier.
        
        Args:
            filepath: Chemin du fichier
            stall_timeout: Secondes sans modification = stall
            on_stall: Callback si fichier ne change plus
            on_change: Callback si fichier change (path, new_size)
        """
        self.watched_files[filepath] = {
            'last_size': 0,
            'last_modified': 0,
            'stall_timeout': stall_timeout,
            'on_stall': on_stall,
            'on_change': on_change,
            'stall_detected': False
        }
    
    async def start(self):
        """Démarre la surveillance"""
        self.running = True
        
        while self.running:
            await asyncio.sleep(self.check_interval)
            
            for filepath, info in list(self.watched_files.items()):
                try:
                    if not os.path.exists(filepath):
                        continue
                    
                    # Stats actuelles
                    stat = os.stat(filepath)
                    current_size = stat.st_size
                    current_mtime = stat.st_mtime
                    
                    # Détection de changement
                    if current_size != info['last_size']:
                        # Fichier modifié !
                        info['last_modified'] = current_mtime
                        info['last_size'] = current_size
                        info['stall_detected'] = False
                        
                        if info['on_change']:
                            try:
                                info['on_change'](filepath, current_size)
                            except Exception as e:
                                print(f"[FileWatchdog] on_change error: {e}")
                    
                    # Détection de stall
                    else:
                        # Taille identique, vérifier le temps
                        inactive = time.time() - info['last_modified']
                        
                        if inactive > info['stall_timeout'] and not info['stall_detected']:
                            info['stall_detected'] = True
                            
                            warning = f"⚠️ Fichier {filepath} stagne ({inactive:.0f}s sans changement)"
                            print(warning, file=sys.stderr)
                            
                            if info['on_stall']:
                                try:
                                    info['on_stall'](filepath)
                                except Exception as e:
                                    print(f"[FileWatchdog] on_stall error: {e}")
                
                except Exception as e:
                    print(f"[FileWatchdog] Erreur surveillance {filepath}: {e}")
    
    def stop(self):
        """Arrête la surveillance"""
        self.running = False


class JiminySupervisor:
    """
    Superviseur global qui combine ProcessWatchdog + FileWatchdog.
    Gère l'ensemble du système Jiminy.
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.process_watchdog = ProcessWatchdog(timeout_seconds=60)
        self.file_watchdog = FileWatchdog(check_interval=5)
        
        self.supervision_log = self.log_dir / "supervision.log"
        self.running = False
    
    async def start(self):
        """Démarre toute la supervision"""
        self.running = True
        
        # Démarrer les watchdogs
        await self.process_watchdog.start()
        
        # Lancer le file watchdog en tâche de fond
        asyncio.create_task(self.file_watchdog.start())
        
        # Surveiller le fichier de supervision lui-même
        self.file_watchdog.watch_file(
            str(self.supervision_log),
            stall_timeout=60,
            on_stall=lambda f: print(f"[Supervisor] Log stall detected: {f}")
        )
        
        print(f"🛡️ Superviseur Jiminy démarré")
        print(f"   Logs: {self.supervision_log}")
    
    async def run_jiminy_process(
        self,
        command: List[str],
        name: str = "jiminy",
        env: Optional[Dict[str, str]] = None
    ) -> subprocess.Popen:
        """
        Lance un processus Jiminy sous surveillance.
        
        Args:
            command: Commande à exécuter (ex: ["python", "jiminy.py"])
            name: Nom identifiant
            env: Variables d'environnement additionnelles
        """
        # Préparer l'environnement
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        
        # Lancer le processus
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            env=process_env,
            bufsize=1  # Ligne par ligne
        )
        
        # Surveiller
        await self.process_watchdog.monitor_process(
            process,
            name=name,
            on_stall=self._on_process_stall,
            on_output=self._on_process_output
        )
        
        return process
    
    def _on_process_stall(self, info: ProcessInfo):
        """Callback quand un processus stagne"""
        warning = f"⚠️ Processus {info.name} (PID {info.pid}) inactif - intervention"
        print(warning, file=sys.stderr)
        
        # Sauvegarder l'état
        self._log_event("STALL", info)
        
        # Tuer le processus
        self.process_watchdog.kill_process(info.pid, force=True)
    
    def _on_process_output(self, line: str):
        """Callback pour chaque ligne de sortie"""
        # Écrire dans le log de supervision
        with open(self.supervision_log, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | {line}\n")
    
    def _log_event(self, event_type: str, info: ProcessInfo):
        """Log un événement de supervision"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "pid": info.pid,
            "name": info.name,
            "inactive_since": time.time() - info.last_activity
        }
        
        with open(self.supervision_log, 'a', encoding='utf-8') as f:
            f.write(f"EVENT: {json.dumps(event)}\n")
    
    def get_status(self) -> Dict:
        """Retourne le statut de supervision"""
        return {
            "running": self.running,
            "monitored_processes": len(self.process_watchdog.monitored_processes),
            "watched_files": len(self.file_watchdog.watched_files),
            "recent_logs": self.process_watchdog.get_logs(20)
        }
    
    async def emergency_stop(self):
        """Arrêt d'urgence - tue tout"""
        print("🚨 ARRÊT D'URGENCE - Tous les processus tués")
        
        # Tuer tous les processus
        killed = self.process_watchdog.kill_zombies()
        
        # Arrêter les watchdogs
        await self.process_watchdog.stop()
        self.file_watchdog.stop()
        
        self.running = False
        
        return {"killed_processes": killed}
    
    async def stop(self):
        """Arrêt normal"""
        print("🛑 Arrêt normal du superviseur")
        
        await self.process_watchdog.stop()
        self.file_watchdog.stop()
        self.running = False


# ═══════════════════════════════════════════════════════════════════
# UTILISATION
# ═══════════════════════════════════════════════════════════════════

async def demo():
    """Démonstration du superviseur"""
    supervisor = JiminySupervisor(log_dir="logs/supervision")
    
    await supervisor.start()
    
    # Lancer un processus de test (simulation)
    print("\n🔍 Lancement processus test...")
    
    # Simuler avec un simple ping
    if sys.platform == "win32":
        cmd = ["ping", "-n", "10", "localhost"]
    else:
        cmd = ["ping", "-c", "10", "localhost"]
    
    process = await supervisor.run_jiminy_process(cmd, name="test_ping")
    
    # Attendre et surveiller
    for i in range(12):
        await asyncio.sleep(1)
        status = supervisor.get_status()
        print(f"  [{i+1}s] Processus: {status['monitored_processes']}")
    
    # Arrêt
    await supervisor.stop()
    
    print("\n✅ Démonstration terminée")
    print(f"   Logs disponibles dans: logs/supervision/")


async def run_watch_mode():
    """Mode surveillance continue - affiche les processus toutes les 10s"""
    print("="*70)
    print("🛡️ JIMINY WATCHDOG - Mode surveillance active")
    print("="*70)
    print("  Ctrl+C pour arrêter\n")
    
    watchdog = ProcessWatchdog(timeout_seconds=120)
    iteration = 0
    
    while True:
        iteration += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Scanner les processus python actifs
        python_procs = [p for p in psutil.process_iter(['pid', 'name', 'cmdline', 'status'])
                        if p.info['name'] and 'python' in p.info['name'].lower()]
        
        print(f"\n[{now}] 🐕 Cycle #{iteration} - {len(python_procs)} processus Python actifs")
        for p in python_procs[:5]:
            cmdline = ' '.join(p.info['cmdline'] or [])[:60]
            print(f"  PID {p.info['pid']:>6} [{p.info['status']:>8}] {cmdline}")
        
        # Mémoire système
        mem = psutil.virtual_memory()
        print(f"  💾 RAM: {mem.percent:.1f}% utilisée ({mem.available // 1024 // 1024} MB libres)")
        
        await asyncio.sleep(10)


if __name__ == "__main__":
    print("="*70)
    print("🛡️ JIMINY WATCHDOG - Système de supervision")
    print("="*70)
    print("\nFonctionnalités:")
    print("  🐕 Surveillance processus (PID, flux, heartbeat)")
    print("  📁 Watchdog fichiers (taille, modification)")
    print("  ⚡ Kill des zombies (timeout configurable)")
    print("  📝 Redirection logs centralisée")
    print("  🚨 Arrêt d'urgence")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(demo())
    elif len(sys.argv) > 1 and sys.argv[1] == "--watch":
        try:
            asyncio.run(run_watch_mode())
        except KeyboardInterrupt:
            print("\n🛑 Watchdog arrêté.")
    else:
        print("\n💡 Usage:")
        print("   python jiminy_watchdog.py --watch   → Surveillance continue")
        print("   python jiminy_watchdog.py --demo    → Démonstration")
