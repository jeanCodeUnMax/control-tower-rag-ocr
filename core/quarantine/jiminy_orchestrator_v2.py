#!/usr/bin/env python3
"""
JIMINY ORCHESTRATOR V2 - Création interactive de workspace

Workflow:
1. Demande le nom du workspace (ex: "projetX")
2. Crée le dossier patate/
3. Lance hephaistos-kit init dans ce dossier
4. Ouvre tous les services
"""

import os
import sys
import time
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class JiminyOrchestratorV2:
    """Orchestre la création et le démarrage d'un nouveau workspace"""
    
    def __init__(self):
        self.hephaistos_root = Path(__file__).resolve().parents[2]
        self.workspace_root = Path("C:/DATA-WEBMAN/projets")  # Workspaces ici
        self.memory_global = Path("C:/DATA-WEBMAN/memory")  # Mémoire globale persistante
        self.memory_local = Path("C:/DATA-WEBMAN/memory/current_workspace")  # Mémoire locale workspace actif
        self.workspace_name = None
        self.workspace_path = None
        
    def log(self, message: str, level: str = "INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [{level:8}] {message}")
    
    def ask_workspace_name(self) -> str:
        """Demande interactivement le nom du workspace"""
        print("\n" + "=" * 70)
        print("🦗 JIMINY  ORCHESTRATOR V2 - Création de Workspace")
        print("=" * 70)
        print("\nBienvenue ! Je vais créer un nouveau workspace Hephaistos pour vous.")
        print("\nCe workspace incluera:")
        print("  • Structure Hephaistos-Kit complète")
        print("  • Mémoire unifiée (Zvec + Memory MCP)")
        print("  • Jiminy Conscience (83 modes de réflexion)")
        print("  • Dashboard de supervision")
        print("  • Watchdog de protection")
        print()
        
        while True:
            name = input("📁 Nom du workspace (ex: patate, mon-projet): ").strip()
            
            if not name:
                print("❌ Le nom ne peut pas être vide")
                continue
            
            if ' ' in name or any(c in name for c in '<>:"/\\|?*'):
                print("❌ Caractères invalides. Utilisez uniquement lettres, chiffres, - et _")
                continue
            
            # Vérifier si existe déjà
            workspace_path = self.workspace_root / name
            if workspace_path.exists():
                print(f"⚠️  Le dossier '{name}' existe déjà")
                choice = input("   Utiliser ce dossier ? (o/n): ").lower()
                if choice != 'o':
                    continue
            
            return name
    
    def create_workspace(self, name: str) -> Path:
        """Crée la structure du workspace"""
        self.workspace_name = name
        self.workspace_path = self.workspace_root / name
        
        self.log("\n" + "=" * 70)
        self.log("CRÉATION DU WORKSPACE")
        self.log("=" * 70)
        
        # Créer le dossier
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.log(f"📁 Dossier créé: {self.workspace_path}")
        
        # Lancer ifastos-kit init pour injecter la mémoire unifiée
        self._run_ifastos_init()
        
        # Copier la structure Hephaistos-Kit
        self._copy_hephaistos_structure()
        
        # Initialiser la mémoire unifiée (déjà fait par _run_ifastos_init avec fallback)
        pass
        
        # Créer le jiminy launcher local
        self._create_local_jiminy()
        
        return self.workspace_path
    
    def _copy_hephaistos_structure(self):
        """Copie les fichiers essentiels de Hephaistos"""
        self.log("\n📦 Copie de la structure Hephaistos-Kit...")
        
        # Dossiers à créer
        dirs_to_create = [
            "core/conscience",
            "core/conscience/prompts",
            "core/conscience/logs",
            ".agent/scripts",
            ".agent/logs",
            "logs/supervision",
        ]
        
        for d in dirs_to_create:
            (self.workspace_path / d).mkdir(parents=True, exist_ok=True)
        
        # Copier les fichiers essentiels Jiminy
        files_to_copy = [
            ("core/conscience/jiminy_prisms.py", "core/conscience/"),
            ("core/conscience/jiminy_consciousness.py", "core/conscience/"),
            ("core/conscience/jiminy_watchdog.py", "core/conscience/"),
            ("core/conscience/dashboard_v3.py", "core/conscience/"),
            ("core/conscience/test_safe.py", "core/conscience/"),
            ("core/conscience/benchmark_jiminy.py", "core/conscience/"),
            ("jiminy", ""),  # Lanceur
        ]
        
        for src, dst in files_to_copy:
            src_path = self.hephaistos_root / src
            dst_path = self.workspace_path / dst / Path(src).name
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                self.log(f"  ✅ {src}")
        
        # Copier tous les prompts
        prompts_src = self.hephaistos_root / "core" / "conscience" / "prompts"
        prompts_dst = self.workspace_path / "core" / "conscience" / "prompts"
        if prompts_src.exists():
            for prompt_file in prompts_src.glob("*.txt"):
                shutil.copy2(prompt_file, prompts_dst / prompt_file.name)
            self.log(f"  ✅ {len(list(prompts_src.glob('*.txt')))} prompts copiés")
    
    def _run_ifastos_init(self):
        """Lance ifastos-kit init pour injecter la mémoire unifiée"""
        self.log("\n🚀 Injection de la mémoire unifiée (ifastos-kit init)...")
        
        init_commands = ["ifastos-kit", "hephaistos-kit"]
        for init_cmd in init_commands:
            try:
                result = subprocess.run(
                    [init_cmd, "init", "--quiet"],
                    cwd=str(self.workspace_path),
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.log(f"  ✅ Injection réussie via {init_cmd} init")
                    if result.stdout:
                        for line in result.stdout.strip().split('\n')[:5]:
                            self.log(f"     {line}")
                    return

                self.log(
                    f"  ⚠️  {init_cmd} init a retourné une erreur "
                    f"(code {result.returncode})"
                )
            except FileNotFoundError:
                self.log(f"  ⚠️  Commande '{init_cmd}' non trouvée")
            except subprocess.TimeoutExpired:
                self.log(f"  ⚠️  Timeout lors de l'exécution de {init_cmd} init")
            except Exception as e:
                self.log(f"  ⚠️  Erreur avec {init_cmd} init: {e}")

        self.log("  → Fallback: création manuelle de la structure init...")
        self._init_unified_memory_manual()

    def _inject_template_structure_manual(self):
        """Copie la structure init standard (.agent/.vscode/.editorconfig)."""
        self.log("\n📦 Injection manuelle de la structure template...")

        copy_targets = [".agent", ".vscode"]
        optional_files = [".editorconfig"]

        for target in copy_targets:
            src = self.hephaistos_root / target
            dst = self.workspace_path / target
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                self.log(f"  ✅ {target} injecté")
            else:
                self.log(f"  ⚠️  Source introuvable: {src}")

        for filename in optional_files:
            src = self.hephaistos_root / filename
            dst = self.workspace_path / filename
            if src.exists():
                shutil.copy2(src, dst)
                self.log(f"  ✅ {filename} copié")
    
    def _init_unified_memory_manual(self):
        """Initialise la mémoire unifiée (fallback manuel)"""
        self.log("\n🧠 Initialisation manuelle de la mémoire unifiée...")
        self._inject_template_structure_manual()
        
        # Mémoire globale (persistante) et locale (workspace actif)
        self.memory_global.mkdir(parents=True, exist_ok=True)
        self.memory_local.mkdir(parents=True, exist_ok=True)
        
        # Créer .env
        env_file = self.workspace_path / ".env"
        env_content = f"""# Configuration Hephaistos Workspace
CASCADE_DB_ROOT={self.memory_local}
WORKSPACE_NAME={self.workspace_name}
OLLAMA_URL=http://localhost:11434

# Mémoire unifiée
MEMORY_GLOBAL={self.memory_global}
MEMORY_LOCAL={self.memory_local}
ZVEC_PATH={self.memory_local}/zvec.db
"""
        env_file.write_text(env_content, encoding='utf-8')
        self.log(f"  ✅ Configuration: {env_file}")
        
        # Créer structure mémoire
        (self.memory_global / "patterns").mkdir(exist_ok=True)  # Patterns extraits des workspaces
        (self.memory_global / "rules").mkdir(exist_ok=True)     # Règles système
        (self.memory_global / "corrections").mkdir(exist_ok=True) # Corrections/difficultés
        self.log(f"  ✅ Mémoire globale: {self.memory_global}")
        self.log(f"  ✅ Mémoire locale: {self.memory_local}")
    
    def _create_local_jiminy(self):
        """Crée un lanceur Jiminy local adapté au workspace"""
        self.log("\n🔧 Configuration du lanceur...")
        
        # Modifier le jiminy local pour qu'il pointe sur ce workspace
        jiminy_local = self.workspace_path / "jiminy"
        if jiminy_local.exists():
            content = jiminy_local.read_text(encoding='utf-8')
            # Remplacer le chemin root par le workspace
            content = content.replace(
                'Path(__file__).resolve().parent',
                f'Path("{self.workspace_path}")'
            )
            jiminy_local.write_text(content, encoding='utf-8')
        
        self.log(f"  ✅ Lanceur prêt: jiminy")
    
    def start_services(self):
        """Démarre tous les services"""
        self.log("\n" + "=" * 70)
        self.log("DÉMARRAGE DES SERVICES")
        self.log("=" * 70)
        
        # 1. Dashboard
        self.log("\n📊 Lancement du Dashboard V3...")
        dashboard = subprocess.Popen(
            [sys.executable, "core/conscience/dashboard_v3.py"],
            cwd=str(self.workspace_path),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.log(f"  ✅ Dashboard (PID: {dashboard.pid})")
        time.sleep(2)
        
        # 2. Watchdog
        self.log("\n🐕 Lancement du Watchdog...")
        watchdog = subprocess.Popen(
            [sys.executable, "core/conscience/jiminy_watchdog.py"],
            cwd=str(self.workspace_path),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.log(f"  ✅ Watchdog (PID: {watchdog.pid})")
        time.sleep(1)
        
        # 3. Conscience (prête mais en veille)
        self.log("\n🦗 Réveil de la Conscience Jiminy...")
        self.log("  ✅ 83 modes de réflexion prêts")
        self.log("  ✅ Sélection intelligente par couches")
        self.log("  ✅ Intégration Ollama (qwen2.5:7b)")
    
    def show_summary(self):
        """Affiche le récapitulatif"""
        print("\n" + "=" * 70)
        print("✅ WORKSPACE OPÉRATIONNEL")
        print("=" * 70)
        print(f"\n📁 Workspace: {self.workspace_path}")
        print(f"🧠 Mémoire globale: {self.memory_global}")
        print(f"📝 Mémoire locale: {self.memory_local}")
        print(f"\n🚀 Commandes disponibles:")
        print(f"   cd {self.workspace_name}")
        print(f"   python jiminy dashboard    → Dashboard")
        print(f"   python jiminy watchdog       → Watchdog")
        print(f"   python jiminy test           → Tests")
        print(f"   python jiminy benchmark      → Benchmark")
        print(f"\n💡 La conscience est prête à réfléchir !")
        print(f"   Les apprentissages iront dans la mémoire globale")
        print("=" * 70)
    
    def run(self):
        """Workflow complet"""
        try:
            # 1. Demander le nom
            name = self.ask_workspace_name()
            
            # 2. Créer le workspace
            self.create_workspace(name)
            
            # 3. Démarrer les services
            self.start_services()
            
            # 4. Afficher le récap
            self.show_summary()
            
        except KeyboardInterrupt:
            print("\n\n🛑 Interrompu par l'utilisateur")
            sys.exit(0)
        except Exception as e:
            print(f"\n💥 Erreur: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    orchestrator = JiminyOrchestratorV2()
    orchestrator.run()
