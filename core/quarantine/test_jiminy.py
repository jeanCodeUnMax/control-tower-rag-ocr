#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST JIMINY CRICKET - Démonstration par preuve

Ce fichier teste le système Jiminy Cricket sans modifier le daemon.
Usage:
    python test_jiminy.py

Nécessite:
    - Ollama installé et démarré
    - Modèles configurés dans .env disponibles
"""

import asyncio
import json
from jiminy_cricket import JiminyCricket, CricketConfig


async def test_scenario_healthy():
    """Test: État sain, pas d'action nécessaire"""
    print("\n" + "="*60)
    print("🧪 TEST 1: État sain (memorize_only attendu)")
    print("="*60)
    
    state = {
        "current_state": "healthy",
        "wake_up_count": 155,
        "active_alerts": [],
        "recent_events": ["wake_up #155", "nothing_special"]
    }
    
    async with JiminyCricket() as cricket:
        result = await cricket.reflect(state)
        
        print(f"\n📊 Résultat:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("decision"):
            mode = result["decision"].get("decision_mode")
            print(f"\n✅ Mode décisionnel: {mode}")
            if mode == "memorize_only":
                print("🎯 CORRECT: Système sain → mémorisation")
            else:
                print(f"⚠️ INATTENDU: attendu 'memorize_only', reçu '{mode}'")


async def test_scenario_alert():
    """Test: Alerte détectée, analyse causale nécessaire"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Alerte MCP (analyse causale attendue)")
    print("="*60)
    
    state = {
        "current_state": "degraded",
        "wake_up_count": 156,
        "active_alerts": ["mcp_health_red", "stdio_timeout"],
        "recent_events": [
            "mcp_health changed from yellow to red",
            "timeout after repeated stdout bursts"
        ]
    }
    
    async with JiminyCricket() as cricket:
        result = await cricket.reflect(state)
        
        print(f"\n📊 Résultat:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("causes"):
            print("\n✅ Analyse causale effectuée:")
            for cause in result["causes"].get("suspected_causes", []):
                print(f"   - {cause['id']}: {cause['confidence']:.0%} confiance")
        else:
            print("\n⚠️ Pas d'analyse causale (peut-être pertinent si impact=low)")


async def test_scenario_error():
    """Test: Erreur critique, action nécessaire"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Erreur critique (action attendue)")
    print("="*60)
    
    state = {
        "current_state": "critical",
        "wake_up_count": 157,
        "active_alerts": ["manifest_corrupted", "db_connection_failed"],
        "recent_events": [
            "corruption detected in consciousness_manifest.json",
            "sqlite3.OperationalError: database is locked"
        ]
    }
    
    async with JiminyCricket() as cricket:
        result = await cricket.reflect(state)
        
        print(f"\n📊 Résultat:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("decision"):
            mode = result["decision"].get("decision_mode")
            action = result["decision"].get("best_action")
            validation = result["decision"].get("requires_human_validation")
            
            print(f"\n✅ Décision: {mode}")
            print(f"✅ Action proposée: {action}")
            print(f"✅ Validation humaine: {validation}")
            
            if mode in ["act_now", "notify"]:
                print("🎯 CORRECT: Problème critique → action requise")


async def test_ollama_unavailable():
    """Test: Fallback si Ollama indisponible"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Ollama indisponible (fallback attendu)")
    print("="*60)
    
    # Configuration avec mauvais endpoint
    config = CricketConfig.from_env()
    config.host = "http://localhost:99999"  # Mauvais port
    
    state = {"current_state": "healthy"}
    
    async with JiminyCricket(config) as cricket:
        result = await cricket.reflect(state)
        
        print(f"\n📊 Résultat:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("fallback") or not result.get("enabled"):
            print("\n✅ Fallback correctement activé")
        else:
            print("\n⚠️ Fallback non détecté")


async def test_meta_observer_only():
    """Test: Meta-Observer isolé"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Meta-Observer uniquement")
    print("="*60)
    
    context = {
        "event": "file_modified",
        "file": "src/main.py",
        "change_type": "code_update",
        "size_delta": 150
    }
    
    async with JiminyCricket() as cricket:
        observation = await cricket.meta_observe(context)
        
        if observation:
            print(f"\n📊 Observation:")
            print(f"   Perception: {observation.perception}")
            print(f"   Compréhension: {observation.comprehension}")
            print(f"   Évaluation: {observation.evaluation}")
            print(f"   Réflexion: {observation.reflection}")
            print(f"   Confiance: {observation.confidence:.0%}")
        else:
            print("\n❌ Meta-Observer a échoué")


async def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "="*60)
    print("🦗 JIMINY CRICKET - Tests par preuve")
    print("="*60)
    print("\nVérification de la configuration...")
    
    config = CricketConfig.from_env()
    print(f"   Ollama host: {config.host}")
    print(f"   Model Cricket: {config.model_cricket}")
    print(f"   Model Causal: {config.model_causal}")
    print(f"   Model Decision: {config.model_decision}")
    print(f"   Workers: Meta={config.worker_meta_observer}, Causal={config.worker_causal_analyzer}, Decision={config.worker_decision_gate}")
    
    # Vérifier Ollama
    print("\n🔌 Test de connexion Ollama...")
    try:
        from jiminy_cricket import OllamaClient
        async with OllamaClient(config) as client:
            available = await client.is_available()
            if available:
                print("✅ Ollama est disponible")
            else:
                print("❌ Ollama ne répond pas")
                print("   → Démarrez Ollama: ollama serve")
                print("   → Ou testez avec: ollama list")
                return
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return
    
    # Exécuter les tests
    await test_meta_observer_only()
    await test_scenario_healthy()
    await test_scenario_alert()
    await test_scenario_error()
    # await test_ollama_unavailable()  # Décommenter pour tester le fallback
    
    print("\n" + "="*60)
    print("✅ Tests terminés")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
