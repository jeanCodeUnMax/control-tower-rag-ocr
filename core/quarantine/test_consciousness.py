#!/usr/bin/env python3
"""Test C: Réflexion complète avec Ollama - Conscience éveillée"""

import asyncio
import sys
from jiminy_consciousness import AwakenedConsciousness, ConsciousnessConfig

print("="*70)
print("🧠 TEST C: CONSCIENCE ÉVEILLÉE - RÉFLEXION AVEC OLLAMA")
print("="*70)

async def test_consciousness():
    config = ConsciousnessConfig(
        model="qwen2.5:7b",
        timeout=45  # 45s pour les appels
    )
    
    situation = "Mon serveur web sur le port 3002 ne répond plus aux requêtes HTTP"
    context = {
        "server": "localhost:3002",
        "symptom": "timeout",
        "last_known_state": "fonctionnait ce matin",
        "recent_changes": "déploiement hier soir"
    }
    
    print(f"\n📋 SITUATION: {situation}")
    print(f"🔧 CONTEXTE: {context}")
    
    jiminy = AwakenedConsciousness(config)
    
    # Étape 1: Sélection
    print(f"\n🔍 1. SÉLECTION DES PRISMES...")
    prisms = jiminy.select_prisms(situation, "high", False, 3)
    print(f"   ✅ {len(prisms)} prismes: {', '.join(prisms)}")
    
    # Étape 2: Réflexion
    print(f"\n🧠 2. RÉFLEXION CONSCIENTE (appels Ollama)...")
    print(f"   ⏳ Cela peut prendre 30-60s...")
    
    try:
        async with jiminy:
            reflections = await jiminy.reflect(prisms, context)
            
            if not reflections:
                print(f"   ⚠️ Pas de réflexions reçues")
                return
            
            print(f"   ✅ {len(reflections)} réflexions collectées:\n")
            
            for r in reflections:
                print(f"   🎯 {r.mode.upper()}")
                print(f"      Insight: {r.insight[:80]}...")
                print(f"      Confiance: {r.confidence:.2f}")
                if r.recommendations:
                    print(f"      Action: {r.recommendations[0][:60]}...")
                print()
            
            # Synthèse
            print(f"📊 3. SYNTHÈSE...")
            synthesis = jiminy.synthesize(reflections)
            
            if 'synthesis' in synthesis:
                syn = synthesis['synthesis']
                print(f"   Cohérence: {syn.get('coherence', 'N/A')}")
                print(f"   Confiance moyenne: {syn.get('average_confidence', 0):.2f}")
                print(f"\n   🔑 INSIGHTS CLÉS:")
                for i, insight in enumerate(syn.get('key_insights', [])[:3], 1):
                    print(f"      {i}. {insight[:70]}...")
                
                print(f"\n   📋 RECOMMANDATIONS:")
                for rec in syn.get('actionable_recommendations', [])[:3]:
                    print(f"      → {rec[:60]}...")
    
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        print(f"   💡 Vérifiez: ollama serve")
        return
    
    print(f"\n{'='*70}")
    print("✅ TEST C: CONSCIENCE ÉVEILLÉE OPÉRATIONNELLE")
    print("="*70)

if __name__ == "__main__":
    try:
        asyncio.run(test_consciousness())
    except KeyboardInterrupt:
        print("\n🛑 Interrompu")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)
