#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSCIENCE DAEMON - Système de conscience autonome

Ce daemon tourne en arrière-plan et:
1. Se réveille automatiquement toutes les 5 minutes
2. Analyse l'état du système
3. Compare avec les demandes utilisateur
4. Priorise les tâches
5. Exécute les actions nécessaires
6. Auto-debug si problème

Usage:
    python conscience_daemon.py           # Démarrer
    python conscience_daemon.py --stop    # Arrêter
    python conscience_daemon.py --status  # Voir état
"""

import os
import sys
import json
import time
import signal
import asyncio
import threading
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional

# Configuration des chemins par rapport à la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / ".agent" / "rag"))

try:
    from conscience_manifest import ConscienceManifest
except ImportError as e:
    print(f"ERREUR: Impossible d'importer ConscienceManifest: {e}")
    print("Vérifiez que .agent/rag/conscience_manifest.py existe")
    sys.exit(1)

# Fichiers de lock et log (toujours à la racine pour être visibles)
PID_FILE = PROJECT_ROOT / ".agent/conscience_daemon.pid"
LOG_FILE = PROJECT_ROOT / ".agent/conscience_daemon.log"

def log(msg: str):
    """Log avec timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

class ConscienceDaemon:
    """
    Daemon de conscience - tourne en arrière-plan
    """
    
    def __init__(self):
        self.running = False
        self.conscience = None
        self.wake_interval = 5 * 60  # 5 minutes
        self.last_wake = None
        
    def start(self):
        """Démarrer le daemon"""
        if PID_FILE.exists():
            log("⚠️ Daemon déjà en cours (voir .agent/conscience_daemon.pid)")
            return False
        
        # Créer fichier PID
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        
        log("=" * 60)
        log("🧠 CONSCIENCE DAEMON DÉMARRÉ")
        log("=" * 60)
        log(f"PID: {os.getpid()}")
        log(f"Réveil toutes les {self.wake_interval//60} minutes")
        log("=" * 60)
        
        self.running = True
        
        # Lancer la boucle
        try:
            asyncio.run(self._main_loop())
        except KeyboardInterrupt:
            log("\n🛑 Arrêt demandé (Ctrl+C)")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Arrêter le daemon"""
        self.running = False
        if PID_FILE.exists():
            PID_FILE.unlink()
        log("🛑 Daemon arrêté")
    
    async def _main_loop(self):
        """Boucle principale"""
        # Initialiser la conscience
        try:
            # Architecture V3: mémoire locale dans current_workspace
            memory_local = os.environ.get("MEMORY_LOCAL", "C:/DATA-WEBMAN/memory/current_workspace")
            db_path = f"{memory_local}/conscience.db"
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.conscience = ConscienceManifest(
                manifest_path=PROJECT_ROOT / ".agent" / "consciousness_manifest.json",
                wake_interval_minutes=5,
                db_path=db_path
            )
            log("✅ Conscience initialisée sur mémoire unifiée")
        except Exception as e:
            log(f"❌ ERREUR initialisation conscience: {e}")
            # Auto-debug: créer la base si manquante
            await self._auto_fix_init_error(e)
            return
        
        # Boucle infinie de réveil
        while self.running:
            try:
                await self._wake_cycle()
            except Exception as e:
                log(f"❌ ERREUR réveil: {e}")
                # Auto-debug
                await self._auto_fix_wake_error(e)
            
            # Attendre prochain réveil
            log(f"😴 Prochain réveil dans {self.wake_interval//60} min...")
            await asyncio.sleep(self.wake_interval)
    
    async def _wake_cycle(self):
        """Un cycle de réveil avec réflexion multidimensionnelle"""
        log("\n" + "=" * 60)
        log("🌅 RÉVEIL DE LA CONSCIENCE")
        log("=" * 60)
        
        # Sélection du prisme de réflexion
        prismes = {
            "reasoning": "Comment l'action actuelle se lie-t-elle à la cause racine ?",
            "deep": "Quelle intention profonde guide mon évolution actuelle ?",
            "scientific": "Quelle preuve de succès avons-nous pour ce cycle ?",
            "dev": "Comment rendre cette infrastructure plus résiliente et portable ?",
            "philo": "Quelle est la limite éthique de mon autonomie ?"
        }
        ref_type = list(prismes.keys())[self.conscience.manifest.get('wake_up_count', 0) % len(prismes)]
        question = prismes[ref_type]
        
        log(f"🧠 MODE RÉFLEXION: {ref_type.upper()}")
        log(f"❓ QUESTION: {question}")
        
        # 1. Analyse d'état
        state = await self._analyze_state()
        log(f"📊 État système: {state['status']}")
        
        # Enregistrer l'intention de réveil avec son prisme
        self.conscience._add_event(
            "intent", 
            f"Début du cycle de réveil via le prisme {ref_type.upper()}",
            reflection_type=ref_type,
            question=question
        )
        
        # 2. Analyse des demandes utilisateur
        user_needs = self._analyze_user_needs()
        if user_needs:
            log(f"📋 Demandes utilisateur: {len(user_needs)}")
            for need in user_needs[:3]:
                log(f"   • {need}")
        
        # 3. Priorisation
        priorities = self._prioritize_tasks(state, user_needs)
        if priorities:
            log(f"🎯 Priorités identifiées: {len(priorities)}")
        
        # 4. Exécuter un réveil
        try:
            await self.conscience._wake_up()
            log("✅ Réveil effectué")
        except Exception as e:
            log(f"⚠️ Erreur réveil: {e}")
            raise
        
        # 5. Analyse post-réveil
        await self._post_wake_analysis()
        
        log("=" * 60)
    
    async def _analyze_state(self) -> Dict:
        """Analyser l'état actuel du système"""
        state = {
            "status": "unknown",
            "problems": [],
            "metrics": {}
        }
        
        try:
            # Lire manifeste
            manifest = self.conscience.manifest
            
            state["status"] = manifest.get("current_state", "unknown")
            state["metrics"]["wake_count"] = manifest.get("wake_up_count", 0)
            state["metrics"]["last_wake"] = manifest.get("last_wake_up", "never")
            
            # Compter problèmes
            dev_book = manifest.get("dev_book", {})
            blocked = len(dev_book.get("blocked", []))
            if blocked > 0:
                state["problems"].append(f"{blocked} tâches bloquées")
            
            # Vérifier composants
            for comp, healthy in manifest.get("component_health", {}).items():
                if not healthy:
                    state["problems"].append(f"{comp} down")
            
        except Exception as e:
            state["problems"].append(f"Erreur analyse: {e}")
        
        return state
    
    def _analyze_user_needs(self) -> List[str]:
        """Analyser les demandes de l'utilisateur"""
        needs = []
        
        try:
            manifest = self.conscience.manifest
            
            # Tâches TODO
            dev_book = manifest.get("dev_book", {})
            for task in dev_book.get("todo", []):
                needs.append(f"TODO: {task.get('task', 'Inconnu')}")
            
            # Tâches bloquées
            for task in dev_book.get("blocked", []):
                needs.append(f"BLOCKED: {task.get('task', 'Inconnu')}")
            
            # Actions pending
            for action in manifest.get("actions_pending", []):
                needs.append(f"ACTION: {action.get('description', 'Inconnu')}")
            
        except Exception as e:
            needs.append(f"Erreur lecture besoins: {e}")
        
        return needs
    
    def _prioritize_tasks(self, state: Dict, needs: List[str]) -> List[Dict]:
        """Prioriser les tâches"""
        priorities = []
        
        # Priorité 1: Problèmes système
        if state["problems"]:
            priorities.append({
                "level": "CRITICAL",
                "task": "Résoudre problèmes système",
                "reason": state["problems"]
            })
        
        # Priorité 2: Tâches bloquées
        blocked = [n for n in needs if n.startswith("BLOCKED:")]
        if blocked:
            priorities.append({
                "level": "HIGH",
                "task": "Débloquer tâches",
                "count": len(blocked)
            })
        
        # Priorité 3: TODOs
        todos = [n for n in needs if n.startswith("TODO:")]
        if todos:
            priorities.append({
                "level": "MEDIUM",
                "task": "Traiter TODOs",
                "count": len(todos)
            })
        
        return priorities
    
    async def _post_wake_analysis(self):
        """Analyse après réveil"""
        try:
            manifest = self.conscience.manifest
            wake_count = manifest.get("wake_up_count", 0)
            
            # Vérifier si réveil a compté
            if wake_count == getattr(self, '_last_wake_count', 0):
                log("⚠️ Réveil n'a pas incrémenté le compteur!")
            self._last_wake_count = wake_count
            
            log(f"📈 Réveil #{wake_count} enregistré")
            
        except Exception as e:
            log(f"⚠️ Erreur post-réveil: {e}")
    
    async def _auto_fix_init_error(self, error):
        """Auto-correction erreur initialisation"""
        log("🔧 AUTO-FIX: Initialisation...")
        
        if "db" in str(error).lower() or "sqlite" in str(error).lower():
            # Créer base SQLite
            try:
                import sqlite3
                db_path = Path(".agent/conscience.db")
                db_path.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(str(db_path))
                conn.close()
                log(f"✅ Base SQLite créée: {db_path}")
            except Exception as e:
                log(f"❌ Impossible créer base: {e}")
    
    async def _auto_fix_wake_error(self, error):
        """Auto-correction erreur réveil via Arbre de Causes"""
        log("🔧 [AWARENESS] Analyse causale de l'erreur...")
        error_msg = str(error)
        
        # 1. Consulter l'Arbre de Causes via le Manifeste
        analysis = self.conscience.analyze_problem_with_tree(error_msg)
        causality = analysis.get("causality", [])
        reco = analysis.get("recommandation", {})
        
        if causality:
            log(f"🌳 ARBRE DE CAUSES ({len(causality)} étages):")
            for i, event in enumerate(causality):
                log(f"   [{i+1}] {event.get('timestamp')} - {event.get('description')}")
        
        log(f"💡 RACINE IDENTIFIÉE: {reco.get('root_cause')}")
        log(f"🎯 ACTION RECOMMANDÉE: {reco.get('action').upper()}")
        
        # 2. Tenter l'action de correction automatique
        action = reco.get("action")
        if action == "fix_signature":
            log("🛠️ Tentative de correction de signature (déjà effectuée manuellement, validation...)")
            # Ici on pourrait ajouter de la logique de rewrite de code auto si besoin
        elif action == "reset_db_connection":
            log("🛠️ Réinitialisation de la connexion DB...")
            # Logique de reconnexion
            
        # 3. Marquer l'événement de correction
        self.conscience._add_event(
            "resolution",
            f"Tentative de résolution de: {error_msg[:50]}...",
            context={"analysis": reco},
            reflection_type="reasoning",
            causal_link=error_msg
        )


def main():
    """Point d'entrée"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Conscience Daemon")
    parser.add_argument("--stop", action="store_true", help="Arrêter le daemon")
    parser.add_argument("--status", action="store_true", help="Voir le statut")
    parser.add_argument("--wake-now", action="store_true", help="Réveil immédiat")
    
    args = parser.parse_args()
    
    if args.status:
        if PID_FILE.exists():
            with open(PID_FILE) as f:
                pid = f.read().strip()
            print(f"🟢 Daemon actif (PID: {pid})")
            print(f"   Log: {LOG_FILE}")
            if LOG_FILE.exists():
                lines = LOG_FILE.read_text(encoding='utf-8').split("\n")[-10:]
                print("\n   10 derniers événements:")
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
        else:
            print("🔴 Daemon inactif")
            print(f"   Démarrer avec: python conscience_daemon.py")
        return
    
    if args.stop:
        if PID_FILE.exists():
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"🛑 Signal d'arrêt envoyé au PID {pid}")
            except ProcessLookupError:
                print("⚠️ Processus déjà mort, nettoyage...")
                PID_FILE.unlink()
            except Exception as e:
                print(f"❌ Erreur arrêt: {e}")
        else:
            print("🔴 Daemon déjà arrêté")
        return
    
    if args.wake_now:
        # Réveil unique sans daemon
        print("🌅 Réveil immédiat...")
        try:
            # Architecture V3: mémoire locale dans current_workspace
            memory_local = os.environ.get("MEMORY_LOCAL", "C:/DATA-WEBMAN/memory/current_workspace")
            db_path = f"{memory_local}/conscience.db"
            conscience = ConscienceManifest(
                manifest_path=PROJECT_ROOT / ".agent/consciousness_manifest.json",
                db_path=db_path
            )
            asyncio.run(conscience._wake_up())
            print("✅ Réveil effectué")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        return
    
    # Démarrer le daemon
    daemon = ConscienceDaemon()
    daemon.start()


if __name__ == "__main__":
    main()
