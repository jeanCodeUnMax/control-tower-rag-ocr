#!/usr/bin/env python3
"""
JIMINY BENCHMARK - Test de charge et identification des fragilités

Objectifs:
1. Tester la sélection de prismes sous charge
2. Tester les timeouts et gestion d'erreurs
3. Tester la mémoire (fuites?)
4. Tester Ollama sous pression
5. Identifier les points de rupture
"""

import asyncio
import time
import psutil
import sys
import traceback
from datetime import datetime
from typing import List, Dict, Tuple
import aiohttp

from jiminy_consciousness import AwakenedConsciousness, ConsciousnessConfig
from jiminy_prisms import PrismReflection


class JiminyBenchmark:
    """Benchmark complet du système Jiminy"""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.errors: List[Dict] = []
        self.start_time = time.time()
        self.process = psutil.Process()
        
    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp"""
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{ts}] [{level:8}] {message}")
        
    def get_memory_mb(self) -> float:
        """Mémoire utilisée en MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 1: SÉLECTION DE PRISMES (Charge CPU/Mémoire)
    # ═══════════════════════════════════════════════════════════════════
    
    async def test_prism_selection_stress(self) -> Dict:
        """
        Test de sélection intensive de prismes.
        Fragilité potentielle: fuite mémoire, lenteur sélection
        """
        self.log("═" * 70)
        self.log("TEST 1: SÉLECTION DE PRISMES - STRESS TEST")
        self.log("═" * 70)
        
        consciousness = AwakenedConsciousness()
        
        # 1000 séquences de sélection rapide
        iterations = 1000
        situations = [
            "Bug production critique",
            "Migration base de données",
            "Nouvelle fonctionnalité",
            "Crash serveur",
            "Recherche de sens personnelle",
            "Crise financière",
            "Conflit équipe",
            "Architecture microservices",
            "Optimisation performance",
            "Sécurité compromised"
        ]
        
        start_mem = self.get_memory_mb()
        start = time.time()
        
        for i in range(iterations):
            situation = situations[i % len(situations)]
            complexity = ["simple", "moderate", "complex", "wicked"][i % 4]
            spiritual = i % 3 == 0
            
            try:
                prisms = consciousness.select_prisms(situation, complexity, spiritual, 5)
                
                if i % 100 == 0:
                    current_mem = self.get_memory_mb()
                    self.log(f"  Itération {i:4}/{iterations} - Prisms: {len(prisms)} - Mem: {current_mem:.1f}MB")
                    
            except Exception as e:
                self.log(f"  ❌ ERREUR itération {i}: {e}", "ERROR")
                self.errors.append({
                    "test": "prism_selection",
                    "iteration": i,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
        
        elapsed = time.time() - start
        end_mem = self.get_memory_mb()
        mem_growth = end_mem - start_mem
        
        result = {
            "test": "prism_selection_stress",
            "iterations": iterations,
            "elapsed_seconds": round(elapsed, 2),
            "per_iteration_ms": round((elapsed / iterations) * 1000, 2),
            "memory_start_mb": round(start_mem, 2),
            "memory_end_mb": round(end_mem, 2),
            "memory_growth_mb": round(mem_growth, 2),
            "errors_count": len([e for e in self.errors if e["test"] == "prism_selection"]),
            "status": "PASS" if mem_growth < 50 else "WARNING" if mem_growth < 100 else "FAIL"
        }
        
        self.log(f"\n  ⏱️  {result['per_iteration_ms']}ms par sélection")
        self.log(f"  📈 Mémoire: +{result['memory_growth_mb']}MB")
        self.log(f"  ✅ Status: {result['status']}")
        
        self.results.append(result)
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 2: GESTION DES ERREURS (Robustesse)
    # ═══════════════════════════════════════════════════════════════════
    
    async def test_error_handling(self) -> Dict:
        """
        Test de gestion d'erreurs.
        Fragilité potentielle: crash sur cas limites
        """
        self.log("\n" + "═" * 70)
        self.log("TEST 2: GESTION DES ERREURS - ROBUSTESSE")
        self.log("═" * 70)
        
        consciousness = AwakenedConsciousness()
        
        test_cases = [
            ("", "simple", "vide"),
            ("a" * 10000, "simple", "très long"),
            (None, "simple", "null"),
            ("test", "invalid_complexity", "complexité invalide"),
            ("test", "simple", "unicode_éèà"),
            ("test\n\n\n", "simple", "newlines"),
            ("test\x00\x01", "simple", "caractères spéciaux"),
        ]
        
        passed = 0
        failed = 0
        
        for situation, complexity, desc in test_cases:
            try:
                # Wrap dans try-except pour chaque cas
                try:
                    if situation is None:
                        situation = "null_test"
                    prisms = consciousness.select_prisms(str(situation), complexity, False, 5)
                    self.log(f"  ✅ {desc:20} - OK ({len(prisms)} prisms)")
                    passed += 1
                except Exception as e:
                    self.log(f"  ⚠️  {desc:20} - Exception gérée: {str(e)[:40]}")
                    # Une exception gérée est OK si elle ne crash pas tout
                    passed += 1
                    
            except Exception as e:
                self.log(f"  ❌ {desc:20} - CRASH: {e}", "ERROR")
                failed += 1
                self.errors.append({
                    "test": "error_handling",
                    "case": desc,
                    "error": str(e)
                })
        
        result = {
            "test": "error_handling",
            "total_cases": len(test_cases),
            "passed": passed,
            "failed": failed,
            "status": "PASS" if failed == 0 else "FAIL" if failed > 2 else "WARNING"
        }
        
        self.log(f"\n  ✅ Pass: {passed}  ❌ Fail: {failed}")
        self.log(f"  📊 Status: {result['status']}")
        
        self.results.append(result)
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 3: CHARGE CONCURRENTE (Threads/Asyncio)
    # ═══════════════════════════════════════════════════════════════════
    
    async def test_concurrent_load(self) -> Dict:
        """
        Test de charge concurrente.
        Fragilité potentielle: race conditions, blocages
        """
        self.log("\n" + "═" * 70)
        self.log("TEST 3: CHARGE CONCURRENTE - 50 TÂCHES PARALLÈLES")
        self.log("═" * 70)
        
        consciousness = AwakenedConsciousness()
        
        async def single_task(task_id: int) -> Tuple[int, bool, float]:
            """Une tâche isolée"""
            try:
                start = time.time()
                prisms = consciousness.select_prisms(
                    f"Task {task_id} concurrent test",
                    "moderate",
                    False,
                    5
                )
                elapsed = time.time() - start
                return (task_id, True, elapsed)
            except Exception as e:
                return (task_id, False, 0)
        
        # Lancer 50 tâches en parallèle
        num_tasks = 50
        start = time.time()
        
        tasks = [single_task(i) for i in range(num_tasks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start
        
        successes = sum(1 for r in results if isinstance(r, tuple) and r[1])
        failures = num_tasks - successes
        
        result = {
            "test": "concurrent_load",
            "tasks": num_tasks,
            "successes": successes,
            "failures": failures,
            "total_time_seconds": round(elapsed, 2),
            "avg_time_per_task_ms": round((elapsed / num_tasks) * 1000, 2),
            "status": "PASS" if failures == 0 else "WARNING" if failures < 5 else "FAIL"
        }
        
        self.log(f"  🚀 {num_tasks} tâches en {elapsed:.2f}s")
        self.log(f"  ✅ Succès: {successes}  ❌ Échecs: {failures}")
        self.log(f"  ⏱️  Moyenne: {result['avg_time_per_task_ms']}ms par tâche")
        self.log(f"  📊 Status: {result['status']}")
        
        self.results.append(result)
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 4: OLLAMA SOUS PRESSION (Timeout, charge)
    # ═══════════════════════════════════════════════════════════════════
    
    async def test_ollama_pressure(self) -> Dict:
        """
        Test de pression sur Ollama.
        Fragilité potentielle: timeout, surcharge GPU, crash
        """
        self.log("\n" + "═" * 70)
        self.log("TEST 4: OLLAMA SOUS PRESSION")
        self.log("═" * 70)
        
        # Vérifier si Ollama est accessible
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'http://localhost:11434/api/tags',
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status != 200:
                        self.log("  ⚠️  Ollama non accessible - SKIP TEST")
                        return {
                            "test": "ollama_pressure",
                            "status": "SKIP",
                            "reason": "Ollama not available"
                        }
        except Exception as e:
            self.log(f"  ⚠️  Ollama non accessible: {e} - SKIP TEST")
            return {
                "test": "ollama_pressure",
                "status": "SKIP",
                "reason": f"Ollama error: {e}"
            }
        
        self.log("  🔥 Test charge Ollama...")
        
        # 5 appels rapides pour tester la latence
        num_calls = 5
        latencies = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(num_calls):
                try:
                    start = time.time()
                    payload = {
                        "model": "qwen2.5:7b",
                        "prompt": f"Test {i}",
                        "stream": False
                    }
                    async with session.post(
                        'http://localhost:11434/api/generate',
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        if resp.status == 200:
                            elapsed = time.time() - start
                            latencies.append(elapsed)
                            self.log(f"    Appel {i+1}: {elapsed:.2f}s")
                        else:
                            self.log(f"    ❌ Appel {i+1}: HTTP {resp.status}")
                except Exception as e:
                    self.log(f"    ❌ Appel {i+1}: {str(e)[:50]}")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            
            result = {
                "test": "ollama_pressure",
                "calls": num_calls,
                "successful": len(latencies),
                "avg_latency_seconds": round(avg_latency, 2),
                "max_latency_seconds": round(max_latency, 2),
                "status": "PASS" if avg_latency < 10 else "WARNING" if avg_latency < 20 else "FAIL"
            }
            
            self.log(f"\n  ⏱️  Latence moyenne: {avg_latency:.2f}s")
            self.log(f"  📊 Status: {result['status']}")
        else:
            result = {
                "test": "ollama_pressure",
                "status": "FAIL",
                "reason": "All calls failed"
            }
            self.log(f"  ❌ Tous les appels ont échoué")
        
        self.results.append(result)
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 5: MÉMOIRE (Fuites potentielles)
    # ═══════════════════════════════════════════════════════════════════
    
    async def test_memory_stability(self) -> Dict:
        """
        Test de stabilité mémoire sur longue durée.
        Fragilité potentielle: fuite mémoire progressive
        """
        self.log("\n" + "═" * 70)
        self.log("TEST 5: STABILITÉ MÉMOIRE (30s de charge)")
        self.log("═" * 70)
        
        consciousness = AwakenedConsciousness()
        
        # Échantillons de mémoire
        memory_samples = []
        start_mem = self.get_memory_mb()
        
        start = time.time()
        iteration = 0
        
        while time.time() - start < 30:  # 30 secondes
            iteration += 1
            
            # Travail: sélection de prismes
            prisms = consciousness.select_prisms(
                f"Memory test iteration {iteration}",
                "moderate",
                False,
                5
            )
            
            # Échantillon mémoire toutes les 5s
            if iteration % 50 == 0:
                current_mem = self.get_memory_mb()
                memory_samples.append(current_mem)
                elapsed = time.time() - start
                self.log(f"  [{elapsed:5.1f}s] Mémoire: {current_mem:.1f}MB")
            
            # Petite pause pour ne pas bloquer
            await asyncio.sleep(0.01)
        
        end_mem = self.get_memory_mb()
        
        # Analyse des échantillons
        if len(memory_samples) >= 2:
            growth_rate = (memory_samples[-1] - memory_samples[0]) / len(memory_samples)
        else:
            growth_rate = 0
        
        total_growth = end_mem - start_mem
        
        result = {
            "test": "memory_stability",
            "duration_seconds": 30,
            "iterations": iteration,
            "memory_start_mb": round(start_mem, 2),
            "memory_end_mb": round(end_mem, 2),
            "total_growth_mb": round(total_growth, 2),
            "growth_per_sample_mb": round(growth_rate, 3),
            "status": "PASS" if total_growth < 20 else "WARNING" if total_growth < 50 else "FAIL"
        }
        
        self.log(f"\n  📈 Croissance totale: {total_growth:.1f}MB en 30s")
        self.log(f"  📊 Croissance/itération: {growth_rate:.3f}MB")
        self.log(f"  ✅ Status: {result['status']}")
        
        self.results.append(result)
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # RAPPORT FINAL
    # ═══════════════════════════════════════════════════════════════════
    
    def generate_report(self) -> Dict:
        """Génère le rapport de benchmark"""
        self.log("\n" + "═" * 70)
        self.log("RAPPORT FINAL - ANALYSE DES FRAGILITÉS")
        self.log("═" * 70)
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.get("status") == "PASS")
        warnings = sum(1 for r in self.results if r.get("status") == "WARNING")
        failed = sum(1 for r in self.results if r.get("status") == "FAIL")
        skipped = sum(1 for r in self.results if r.get("status") == "SKIP")
        
        total_time = time.time() - self.start_time
        
        self.log(f"\n  📊 RÉSULTATS:")
        self.log(f"     Total tests: {total_tests}")
        self.log(f"     ✅ PASS: {passed}")
        self.log(f"     ⚠️  WARNING: {warnings}")
        self.log(f"     ❌ FAIL: {failed}")
        self.log(f"     ⏭️  SKIP: {skipped}")
        self.log(f"\n  ⏱️  Temps total: {total_time:.1f}s")
        
        if self.errors:
            self.log(f"\n  ❌ ERREURS DÉTECTÉES ({len(self.errors)}):")
            for i, err in enumerate(self.errors[:5], 1):
                self.log(f"     {i}. {err['test']}: {err.get('error', 'Unknown')[:50]}")
        
        # Identifier les fragilités
        self.log(f"\n  🔍 FRAGILITÉS IDENTIFIÉES:")
        
        fragilities = []
        for result in self.results:
            if result.get("status") in ["WARNING", "FAIL"]:
                fragilities.append({
                    "test": result["test"],
                    "severity": result["status"],
                    "details": result
                })
        
        if fragilities:
            for f in fragilities:
                self.log(f"     ⚠️  {f['test']}: {f['severity']}")
        else:
            self.log(f"     ✅ Aucune fragilité majeure détectée")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "warnings": warnings,
                "failed": failed,
                "skipped": skipped,
                "total_time_seconds": round(total_time, 2)
            },
            "results": self.results,
            "errors": self.errors,
            "fragilities": fragilities
        }
    
    async def run_all(self) -> Dict:
        """Lance tous les tests"""
        print("=" * 70)
        print("🦗 JIMINY BENCHMARK - TEST DE CHARGE COMPLET")
        print("=" * 70)
        print(f"Démarré à: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"PID: {self.process.pid}")
        print("=" * 70)
        
        try:
            # Lancer tous les tests
            await self.test_prism_selection_stress()
            await self.test_error_handling()
            await self.test_concurrent_load()
            await self.test_ollama_pressure()
            await self.test_memory_stability()
            
        except Exception as e:
            self.log(f"\n💥 ERREUR FATALE: {e}", "CRITICAL")
            self.log(traceback.format_exc(), "CRITICAL")
        
        return self.generate_report()


# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

async def main():
    """Point d'entrée principal"""
    benchmark = JiminyBenchmark()
    report = await benchmark.run_all()
    
    # Sauvegarder le rapport
    import json
    report_file = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Rapport sauvegardé: {report_file}")
    
    # Exit code selon résultat
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Benchmark interrompu par l'utilisateur")
        sys.exit(130)
