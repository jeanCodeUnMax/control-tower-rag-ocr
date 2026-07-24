#!/usr/bin/env python3
"""Test de readiness - Modes + Ollama"""

import asyncio
import aiohttp
from jiminy_prisms import PrismReflection

print("="*60)
print("🦗 TEST A: VÉRIFICATION JIMINY")
print("="*60)

modes = PrismReflection.AVAILABLE_PRISMS
print(f"✅ {len(modes)} modes chargés")
print(f"📊 Surface: {len([m for m in modes if m in ['natural', 'challenger', 'scientific', 'wisdom']])}+")
print(f"📊 Intermédiaire: {len([m for m in modes if m in ['investor', 'fondateur', 'mvp']])}+")
print(f"📊 Profond: {len([m for m in modes if m in ['nasa', 'security', 'architect']])}+")
print(f"📊 Ésotérique: {len([m for m in modes if m in ['divine', 'meditation', 'chakra']])}+")

async def warmup():
    print("\n" + "="*60)
    print("🔥 PRÉCHAUFFAGE OLLAMA")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:11434/api/tags', timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m['name'] for m in data.get('models', [])]
                    print(f"✅ Ollama connecté")
                    print(f"📦 Modèles: {models[:3]}")
                else:
                    print(f"❌ Erreur {resp.status}")
                    return
        except Exception as e:
            print(f"❌ Ollama down: {e}")
            print("💡 Démarrez: ollama serve")
            return
        
        print(f"\n⏳ Chargement qwen2.5:7b (keep_alive: 30m)...")
        try:
            payload = {
                'model': 'qwen2.5:7b',
                'prompt': 'Say ready',
                'stream': False,
                'keep_alive': '30m'
            }
            async with session.post(
                'http://localhost:11434/api/generate',
                json=payload,
                timeout=60
            ) as resp:
                if resp.status == 200:
                    print("✅ Modèle CHARGÉ - GPU actif 30min")
                else:
                    print(f"⚠️ Status {resp.status}")
        except Exception as e:
            print(f"⚠️ Timeout ou erreur: {e}")

asyncio.run(warmup())

print("\n" + "="*60)
print("✅ TEST COMPLET TERMINÉ")
print("="*60)
