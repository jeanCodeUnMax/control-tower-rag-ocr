#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DÉMONSTRATION MÉTACOGNITION COMPLÈTE

Scénario: Serveur sur port 3002 qui ne répond pas
Objectif: Montrer toutes les couches de réflexion Jiminy Cricket

Usage:
    python test_metacognition_demo.py
"""

import asyncio
import json
import time
from datetime import datetime
from jiminy_cricket import JiminyCricket, CricketConfig


class MetacognitionLogger:
    """Logger visuel pour les étapes de métacognition"""
    
    @staticmethod
    def section(title: str, icon: str = "🔹"):
        print(f"\n{icon}" + "="*70)
        print(f"{icon} {title}")
        print(f"{icon}" + "="*70)
    
    @staticmethod
    def step(level: int, title: str, detail: str = ""):
        indent = "  " * level
        print(f"{indent}▶️ {title}")
        if detail:
            print(f"{indent}   {detail}")
    
    @staticmethod
    def result(level: int, label: str, value: str, confidence: float = None):
        indent = "  " * level
        conf_str = f" (conf: {confidence:.0%})" if confidence else ""
        print(f"{indent}📌 {label}: {value}{conf_str}")
    
    @staticmethod
    def thinking(question: str, answer: str, confidence: float = None):
        conf_str = f" [{confidence:.0%}]" if confidence else ""
        print(f"    🤔 {question}")
        print(f"       → {answer}{conf_str}")


async def demo_server_port_3002_issue():
    """
    Scénario complet: Serveur port 3002 inaccessible
    Montre toutes les couches de métacognition
    """
    logger = MetacognitionLogger()
    
    logger.section("🎬 SCÉNARIO: Serveur port 3002 défaillant", "🎭")
    print("""
Contexte:
  - Un service web tourne sur le port 3002
  - Les requêtes timeout
  - Logs montrent 'connection refused'
  - Dernière modification: mise à jour du package 'express' il y a 2h
""")
    
    # =========================================================================
    # ÉTAPE 0: ÉTAT INITIAL (Watchdog / Conscience existante)
    # =========================================================================
    logger.section("🔍 ÉTAPE 0: ÉTAT INITIAL (Watchdog)", "0️⃣")
    
    raw_state = {
        "timestamp": datetime.now().isoformat(),
        "system_status": "degraded",
        "services": {
            "web_server": {
                "port": 3002,
                "status": "unresponsive",
                "last_heartbeat": "2026-04-09T17:30:00Z",
                "error_rate": 0.95,
                "recent_errors": [
                    "ECONNREFUSED on port 3002",
                    "Request timeout after 30000ms",
                    "Cannot GET /health"
                ]
            }
        },
        "recent_changes": [
            {
                "file": "package.json",
                "change": "express updated 4.18.2 → 4.19.0",
                "timestamp": "2026-04-09T15:45:00Z",
                "author": "dev"
            }
        ],
        "logs": {
            "last_hour": [
                "17:45:23 ERROR: Connection refused on port 3002",
                "17:45:30 ERROR: Health check failed",
                "17:46:00 WARN: Retry attempt 3/3 failed"
            ]
        }
    }
    
    logger.step(0, "Watchdog détecte un signal anormal", "port 3002 - 95% erreurs")
    logger.result(1, "Signal brut", "ECONNREFUSED, timeouts, health check failures")
    logger.result(1, "Fréquence", "3 erreurs/minute - dégradation rapide")
    
    input("\n⏎ Appuyez sur Entrée pour lancer la métacognition...")
    
    # =========================================================================
    # ÉTAPE 1: META-OBSERVER (Les 5 questions essentielles)
    # =========================================================================
    logger.section("🧠 ÉTAPE 1: META-OBSERVER (5 Questions)", "1️⃣")
    
    async with JiminyCricket() as cricket:
        # Vérifier Ollama
        available = await cricket.client.is_available()
        if not available:
            print("❌ Ollama non disponible - démo en mode simulation")
            return
        
        print("\n🔄 Lancement Meta-Observer...")
        print("   Pose des 5 questions essentielles:\n")
        
        # Simuler les 5 questions avec le vrai worker
        context = {
            "event": "service_degradation",
            "service": "web_server",
            "port": 3002,
            "symptoms": ["ECONNREFUSED", "timeouts", "health_check_failure"],
            "timeline": "degradation over 2 hours",
            "recent_change": "express package updated 2h ago"
        }
        
        observation = await cricket.meta_observe(context)
        
        if observation:
            # Q1: Perception
            logger.thinking(
                "1. PERCEPTION - Que s'est-il passé ?",
                observation.perception.get("what_changed", "N/A"),
                observation.perception.get("relevance_confidence")
            )
            
            # Q2: Compréhension
            logger.thinking(
                "2. COMPRÉHENSION - Que signifie cela ?",
                observation.comprehension.get("meaning", "N/A"),
                observation.comprehension.get("confidence")
            )
            
            # Q3: Évaluation
            impact = observation.evaluation.get("impact", "unknown")
            urgency = observation.evaluation.get("urgency", "unknown")
            logger.thinking(
                "3. ÉVALUATION - Quel est l'impact ?",
                f"Impact: {impact}, Urgence: {urgency}"
            )
            
            # Q4: Capacité
            can_act = observation.capacity.get("can_act", False)
            authorized = observation.capacity.get("authorized", [])
            logger.thinking(
                "4. CAPACITÉ - Que puis-je faire ?",
                f"Peut agir: {can_act}, Actions autorisées: {len(authorized)}"
            )
            
            # Q5: Réflexion
            should_act = observation.reflection.get("should_act", "unknown")
            reason = observation.reflection.get("reason", "")
            logger.thinking(
                "5. RÉFLEXION - Que devrais-je faire ?",
                f"Mode: {should_act} - {reason}"
            )
            
            logger.result(0, "Confiance globale", "", observation.confidence)
        else:
            print("⚠️ Meta-Observer n'a pas retourné de résultat")
            return
        
        # Si l'observation indique un problème, continuer avec l'analyse causale
        if observation.evaluation.get("impact") in ["medium", "high", "critical"]:
            
            input("\n⏎ Appuyez sur Entrée pour l'analyse causale...")
            
            # =====================================================================
            # ÉTAPE 2: CAUSAL ANALYZER (Arbre de causes)
            # =====================================================================
            logger.section("🔬 ÉTAPE 2: CAUSAL ANALYZER (Arbre de Causes)", "2️⃣")
            
            print("\n🔄 Lancement Causal Analyzer...")
            print("   Construction de l'arbre de causes par inférence:\n")
            
            problem = f"Service port {raw_state['services']['web_server']['port']} unresponsive"
            causal_context = {
                "symptoms": raw_state["services"]["web_server"]["recent_errors"],
                "timeline": "degradation started 2h ago",
                "correlation": "express package update 2h ago",
                "error_pattern": "connection refused + timeout",
                "system_resources": "CPU 45%, RAM 60%, DISK 80%"
            }
            
            causes = await cricket.analyze_causes(problem, causal_context)
            
            if causes and causes.is_problem:
                print(f"   Problème confirmé (confiance: {causes.confidence:.0%})\n")
                
                print("   🔍 Causes suspectées identifiées:")
                for i, cause in enumerate(causes.suspected_causes[:3], 1):
                    conf = cause.get("confidence", 0)
                    desc = cause.get("description", "")
                    print(f"      {i}. {desc}")
                    print(f"         Confiance: {conf:.0%}")
                    print(f"         Preuves: {cause.get('evidence', [])}")
                    print()
                
                print(f"   📋 Recommandation: {causes.recommended_next_step}")
            else:
                print("⚠️ Analyse causale n'a pas identifié de problème")
            
            input("\n⏎ Appuyez sur Entrée pour la décision...")
            
            # =====================================================================
            # ÉTAPE 3: DECISION GATE (Grille 10 questions)
            # =====================================================================
            logger.section("⚖️ ÉTAPE 3: DECISION GATE (Grille Décisionnelle)", "3️⃣")
            
            print("\n🔄 Lancement Decision Gate...")
            print("   Application des 10 questions:\n")
            
            evaluation = observation.to_dict()
            causes_dict = causes.to_dict() if causes else None
            possible_actions = [
                "restart_service_port_3002",
                "rollback_express_package",
                "check_firewall_rules",
                "inspect_application_logs",
                "notify_dev_team",
                "escalate_to_sre"
            ]
            
            decision = await cricket.decide(evaluation, causes_dict, possible_actions)
            
            if decision:
                # Afficher les réponses aux 10 questions
                questions = [
                    ("What changed?", decision.what_changed, "Changement détecté"),
                    ("Is it relevant?", decision.relevant, "Pertinent"),
                    ("Is it expected?", decision.expected, "Attendu"),
                    ("Is it harmful?", decision.harmful, "Nuisible"),
                    ("Is it known pattern?", decision.known_pattern, "Pattern connu"),
                    ("Authorized to act?", decision.authorized_to_act, "Autorisé"),
                    ("Reversible action?", decision.reversible_action_available, "Réversible"),
                ]
                
                print("   Réponses aux questions décisionnelles:")
                for q, ans, label in questions:
                    status = "✅" if ans else "❌"
                    print(f"      {status} {q}: {ans}")
                
                print(f"\n   🎯 Décision finale:")
                print(f"      Mode: {decision.decision_mode.upper()}")
                print(f"      Action: {decision.best_action}")
                print(f"      Confiance: {decision.confidence_score:.0%}")
                print(f"      Validation humaine: {'OUI' if decision.requires_human_validation else 'NON'}")
            else:
                print("⚠️ Decision Gate n'a pas retourné de résultat")
        else:
            print("\n✅ Évaluation indique pas d'action nécessaire (impact faible)")
            decision = None
        
        # =====================================================================
        # ÉTAPE 4: SYNTHÈSE ET RAPPORT
        # =====================================================================
        input("\n⏎ Appuyez sur Entrée pour la synthèse finale...")
        
        logger.section("📊 ÉTAPE 4: SYNTHÈSE FINALE", "4️⃣")
        
        print("\n" + "="*70)
        print("🦗 RAPPORT JIMINY CRICKET")
        print("="*70)
        
        if observation:
            print(f"""
📋 OBSERVATION:
   Signal détecté: Port 3002 unresponsive
   Impact: {observation.evaluation.get('impact', 'unknown').upper()}
   Urgence: {observation.evaluation.get('urgency', 'unknown').upper()}

🔍 ANALYSE CAUSALE:
   Problème: {'CONFIRMÉ' if (causes and causes.is_problem) else 'NON CONFIRMÉ'}
   Causes identifiées: {len(causes.suspected_causes) if causes else 0}
""")
        
        if decision:
            print(f"""\
⚖️ DÉCISION:
   Mode: {decision.decision_mode.upper()}
   Action recommandée: {decision.best_action}
   Validation requise: {'OUI' if decision.requires_human_validation else 'NON'}

📈 CONFIANCE GLOBALE: {decision.confidence_score:.0%}
""")
            
            # Plan d'action
            print("🎯 PLAN D'ACTION:")
            if decision.decision_mode == "act_now":
                print(f"   1. {decision.best_action}")
                print("   2. Vérifier le résultat (health check)")
                print("   3. Mettre à jour la mémoire unifiée")
            elif decision.decision_mode == "defer":
                print("   1. Surveillance renforcée (intervalle 1 min)")
                print("   2. Collecter plus de données")
                print("   3. Réévaluer dans 5 minutes")
            elif decision.decision_mode == "notify":
                print("   1. Notifier l'équipe dev/SRE")
                print("   2. Fournir le rapport d'analyse")
                print("   3. Attendre validation humaine")
            else:
                print("   1. Mémoriser l'événement")
                print("   2. Monitoring standard")
        
        print("\n" + "="*70)
        print("✅ CYCLE DE MÉTACOGNITION TERMINÉ")
        print("="*70)


async def demo_all_layers():
    """Démonstration de toutes les couches en séquence"""
    print("\n" + "🦗"*35)
    print("  DÉMONSTRATION COMPLÈTE: MÉTACOGNITION MULTI-COUCHES")
    print("🦗"*35)
    
    await demo_server_port_3002_issue()
    
    # Résumé final
    print("\n" + "="*70)
    print("📚 RÉSUMÉ DES COUCHES IMPLÉMENTÉES:")
    print("="*70)
    print("""
✅ Couche 0: Watchdog (état initial)
   → Détection brute du problème

✅ Couche 1: Meta-Observer (5 questions)
   → Perception / Compréhension / Évaluation / Capacité / Réflexion

✅ Couche 2: Causal Analyzer (arbre de causes)
   → Inférence des causes probables avec confiance

✅ Couche 3: Decision Gate (10 questions)
   → Grille décisionnelle → act_now/defer/notify/memorize

✅ Couche 4: Synthèse
   → Rapport final avec plan d'action
""")
    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(demo_all_layers())
    except KeyboardInterrupt:
        print("\n\n🛑 Démo interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
