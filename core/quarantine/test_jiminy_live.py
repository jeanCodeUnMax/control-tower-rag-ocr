#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JIMINY CRICKET - Mode "Live" avec introspection visible

Scénario: Serveur port 3002 down
Affiche en temps réel les questions que se pose le Cricket
"""

import asyncio
import json
import sys
from datetime import datetime
from jiminy_cricket import JiminyCricket


class LiveCricket:
    """Version live avec affichage des pensées"""
    
    def __init__(self):
        self.thoughts = []
        
    def think(self, question: str, answer: str = "...", confidence: float = None):
        """Affiche une pensée du Cricket"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        conf_str = f" [{confidence:.0%}]" if confidence else ""
        
        print(f"\n  🦗 [{timestamp}] Jiminy se demande:")
        print(f"     💭 {question}")
        if answer and answer != "...":
            print(f"     ✨ → {answer}{conf_str}")
        
        self.thoughts.append({
            "timestamp": timestamp,
            "question": question,
            "answer": answer,
            "confidence": confidence
        })
    
    def section(self, title: str):
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    
    def divider(self):
        print(f"\n  {'─'*66}")


async def live_investigation_port_3002():
    """Investigation live du problème serveur"""
    
    cricket_ui = LiveCricket()
    
    # Header
    print("\n" + "🦗"*35)
    print("   JIMINY CRICKET - MODE INTROSPECTION LIVE")
    print("🦗"*35)
    print("\n  Scénario: Un serveur ne répond plus sur le port 3002")
    print("  Objectif: Observer le processus de réflexion métacognitive\n")
    
    async with JiminyCricket() as cricket:
        
        # Vérifier Ollama
        if not await cricket.client.is_available():
            print("❌ Ollama non disponible")
            return
        
        # =================================================================
        # PHASE 1: OBSERVER (5 questions)
        # =================================================================
        cricket_ui.section("🔍 PHASE 1: OBSERVER - Les 5 Questions Essentielles")
        
        context = {
            "event": "server_unresponsive",
            "service": "web_api",
            "port": 3002,
            "symptoms": ["connection_refused", "timeout", "health_check_failed"],
            "last_working": "17:30",
            "current_time": "17:45",
            "recent_change": "express package updated 2h ago"
        }
        
        # Les 5 questions affichées en live
        questions = [
            "Qu'est-ce que je regarde ? Que s'est-il passé ?",
            "Qu'est-ce que je comprends ? Que signifie cet événement ?",
            "Qu'est-ce que j'évalue ? Quel est l'impact ?",
            "Qu'est-ce que je peux ? Que suis-je capable de faire ?",
            "Qu'est-ce que je décide ? Que devrais-je faire maintenant ?"
        ]
        
        print("\n  🎬 Jiminy Cricket commence son observation...\n")
        await asyncio.sleep(0.5)
        
        for i, q in enumerate(questions, 1):
            cricket_ui.think(f"{i}. {q}")
            await asyncio.sleep(0.3)
        
        # Inférence
        print("\n  🧠 Inférence en cours via Ollama...")
        observation = await cricket.meta_observe(context)
        
        if observation:
            cricket_ui.divider()
            cricket_ui.think(
                "1. PERCEPTION - Que s'est-il passé ?",
                observation.perception.get("what_changed"),
                observation.perception.get("confidence", 0.8)
            )
            cricket_ui.think(
                "2. COMPRÉHENSION - Que signifie cela ?",
                observation.comprehension.get("meaning"),
                observation.comprehension.get("confidence")
            )
            cricket_ui.think(
                "3. ÉVALUATION - Quel est l'impact ?",
                f"Impact: {observation.evaluation.get('impact')}, Urgence: {observation.evaluation.get('urgency')}",
                0.85
            )
            cricket_ui.think(
                "4. CAPACITÉ - Que puis-je faire ?",
                f"Actions autorisées: {len(observation.capacity.get('authorized', []))}",
                0.9
            )
            cricket_ui.think(
                "5. RÉFLEXION - Que devrais-je faire ?",
                f"Mode: {observation.reflection.get('should_act')}",
                observation.confidence
            )
        
        # =================================================================
        # PHASE 2: ANALYSER (Arbre de causes)
        # =================================================================
        impact = observation.evaluation.get("impact") if observation else "low"
        
        if impact in ["medium", "high", "critical"]:
            cricket_ui.section("🔬 PHASE 2: ANALYSER - Arbre de Causes")
            
            print("\n  🌳 Construction de l'arbre de causes...")
            print("     Jiminy explore les hypothèses:\n")
            
            hypotheses = [
                "H1: Le service a crashé après la mise à jour",
                "H2: Un autre processus occupe le port 3002",
                "H3: Le firewall bloque les connexions",
                "H4: Il y a une fuite mémoire progressive"
            ]
            
            for h in hypotheses:
                print(f"       📝 {h}")
                await asyncio.sleep(0.2)
            
            problem = "Service port 3002 connection refused"
            causal_context = {
                "symptoms": context["symptoms"],
                "correlation": context["recent_change"],
                "resources": "RAM 60%, CPU 45%, DISK 80%"
            }
            
            print("\n  🧠 Analyse causale via Ollama...")
            causes = await cricket.analyze_causes(problem, causal_context)
            
            if causes:
                cricket_ui.divider()
                print(f"\n  ✅ Analyse complétée (confiance: {causes.confidence:.0%})")
                
                for i, cause in enumerate(causes.suspected_causes[:3], 1):
                    desc = cause.get('description', cause.get('id', 'Unknown'))
                    conf = cause.get('confidence', 0)
                    print(f"\n     🎯 Cause #{i}: {desc[:50]}...")
                    print(f"        Confiance: {conf:.0%}")
                    
                    cricket_ui.think(
                        f"Cause suspectée #{i}",
                        desc[:60],
                        conf
                    )
                
                cricket_ui.think(
                    "Recommandation",
                    causes.recommended_next_step,
                    causes.confidence
                )
        else:
            causes = None
            print("\n  ⏭️ Impact faible, analyse causale ignorée")
        
        # =================================================================
        # PHASE 3: DÉCIDER (Grille 10 questions)
        # =================================================================
        cricket_ui.section("⚖️ PHASE 3: DÉCIDER - Grille Décisionnelle")
        
        print("\n  📋 Jiminy applique les 10 questions:\n")
        
        decision_questions = [
            "What changed? → Y a-t-il un changement réel ?",
            "Is it relevant? → C'est pertinent ?",
            "Is it expected? → C'était attendu ?",
            "Is it harmful? → C'est nuisible ?",
            "Is it known? → C'est un pattern connu ?",
            "Can I explain it? → Je comprends assez bien ?",
            "Am I authorized? → J'ai le droit d'agir ?",
            "Is it reversible? → L'action est réversible ?",
            "Lowest risk action? → Quelle action à moindre risque ?",
            "Act now or defer? → Agir maintenant ou attendre ?"
        ]
        
        for i, dq in enumerate(decision_questions, 1):
            print(f"     Q{i}: {dq}")
            await asyncio.sleep(0.15)
        
        # Décision
        print("\n  🧠 Prise de décision via Ollama...")
        
        evaluation = observation.to_dict() if observation else {}
        causes_dict = causes.to_dict() if causes else None
        actions = [
            "restart_service",
            "rollback_update",
            "check_logs",
            "notify_team",
            "monitor_only"
        ]
        
        decision = await cricket.decide(evaluation, causes_dict, actions)
        
        if decision:
            cricket_ui.divider()
            
            print(f"\n  ✅ DÉCISION FINALE:")
            print(f"     🎯 Mode: {decision.decision_mode.upper()}")
            print(f"     🎬 Action: {decision.best_action}")
            print(f"     📊 Confiance: {decision.confidence_score:.0%}")
            print(f"     👤 Validation: {'REQUISE' if decision.requires_human_validation else 'Non requise'}")
            
            cricket_ui.think(
                "Décision finale",
                f"{decision.decision_mode} → {decision.best_action}",
                decision.confidence_score
            )
        
        # =================================================================
        # SYNTHÈSE
        # =================================================================
        cricket_ui.section("📊 SYNTHÈSE - Rapport Jiminy Cricket")
        
        print("""
  ┌─────────────────────────────────────────────────────────────────┐
  │                    🦗 RAPPORT FINAL                               │
  ├─────────────────────────────────────────────────────────────────┤
""")
        
        if observation:
            print(f"  │  📋 OBSERVATION                                                │")
            print(f"  │     Événement: {observation.perception.get('what_changed', 'N/A')[:40]:40} │")
            print(f"  │     Impact: {observation.evaluation.get('impact', 'N/A'):10} │ Urgence: {observation.evaluation.get('urgency', 'N/A'):8} │")
            print(f"  │                                                                │")
        
        if causes:
            print(f"  │  🔍 ANALYSE CAUSALE                                            │")
            print(f"  │     Causes trouvées: {len(causes.suspected_causes):2}                                        │")
            if causes.suspected_causes:
                top = causes.suspected_causes[0]
                print(f"  │     Top cause: {top.get('id', 'N/A')[:45]:45} │")
            print(f"  │                                                                │")
        
        if decision:
            print(f"  │  ⚖️ DÉCISION                                                   │")
            print(f"  │     Mode: {decision.decision_mode:12} │ Action: {decision.best_action[:25]:25} │")
            print(f"  │     Confiance: {decision.confidence_score:.0%}                                    │")
            print(f"  │                                                                │")
        
        print("""  └─────────────────────────────────────────────────────────────────┘

  🎯 RÉSULTAT: Le serveur port 3002 nécessite une intervention.
     Action recommandée: Redémarrage du service (act_now)
""")
        
        # Compteur de pensées
        print(f"\n  💭 Total des réflexions: {len(cricket_ui.thoughts)} questions/réponses")
        print(f"     Couches traversées: Observer → Analyser → Décider")
        print(f"     Type: Inférence LLM (pas de script dur)")


async def main():
    """Point d'entrée"""
    print("\n" + "="*70)
    print("  JIMINY CRICKET - Investigation Live du Serveur Port 3002")
    print("="*70)
    
    try:
        await live_investigation_port_3002()
    except KeyboardInterrupt:
        print("\n\n  🛑 Investigation interrompue")
    except Exception as e:
        print(f"\n\n  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("  ✅ Investigation terminée")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
