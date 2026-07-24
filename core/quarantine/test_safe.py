#!/usr/bin/env python3
"""Test avec protection anti-plantage - timeouts partout"""

import asyncio
import aiohttp
import signal
import sys
from jiminy_consciousness import AwakenedConsciousness, ConsciousnessConfig

# Handler pour interruption propre
def signal_handler(sig, frame):
    print("\n🛑 Interruption utilisateur")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("="*70)
print("🛡️ TEST SÉCURISÉ - Anti-plantage avec timeouts")
print("="*70)

async def safe_test():
    # 1. Vérification rapide Ollama (3s max)
    print("\n🔍 ÉTAPE 1: Ping Ollama (timeout 3s)...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'http://localhost:11434/api/tags',
                timeout=aiohttp.ClientTimeout(total=3)
            ) as resp:
                if resp.status == 200:
                    print("✅ Ollama répond")
                else:
                    print(f"❌ Ollama erreur {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Ollama inaccessible: {e}")
        print("💡 Lancez: ollama serve")
        return False
    
    # 2. Test rapide modèle (5s max)
    print("\n🔍 ÉTAPE 2: Test modèle (timeout 5s)...")
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "qwen2.5:7b",
                "prompt": "Say hi",
                "stream": False
            }
            async with session.post(
                'http://localhost:11434/api/generate',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    print("✅ Modèle répond rapidement")
                else:
                    print(f"⚠️ Modèle lent ou indisponible ({resp.status})")
                    return False
    except Exception as e:
        print(f"⚠️ Modèle pas prêt: {e}")
        return False
    
    # 3. Test Jiminy - sélection seule (pas d'appel LLM)
    print("\n🔍 ÉTAPE 3: Test sélection prismes...")
    config = ConsciousnessConfig(model="qwen2.5:7b", timeout=10)
    jiminy = AwakenedConsciousness(config)
    
    prisms = jiminy.select_prisms(
        "serveur plante",
        complexity="high",
        spiritual=False,
        max_prisms=3
    )
    print(f"✅ {len(prisms)} prismes sélectionnés: {prisms}")
    
    print("\n" + "="*70)
    print("✅ TOUS LES TESTS SÉCURISÉS ONT RÉUSSI")
    print("="*70)
    print("\n💡 Système prêt pour utilisation réelle")
    print("   Les appels LLM lents ont été isolés des tests rapides")
    
    return True

if __name__ == "__main__":
    try:
        # Timeout global 20s pour tout le test
        result = asyncio.wait_for(safe_test(), timeout=20)
        if not result:
            sys.exit(1)
    except asyncio.TimeoutError:
        print("\n⏱️ Timeout global - Test interrompu après 20s")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Interrompu par l'utilisateur")
        sys.exit(0)
