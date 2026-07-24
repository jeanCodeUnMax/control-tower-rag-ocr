#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DÉMONSTRATION CLOUD - Modèles premium pour Jiminy Cricket

Avantages:
- Plus gros context window (128K-200K tokens vs 4-8K local)
- Plus puissant (meilleure compréhension, JSON plus fiable)
- Plus rapide (pas d'inference locale)
- Limites: quotas API, coût par requête, rate limiting
"""

import asyncio
import json
import os
from datetime import datetime


class CloudJiminyCricket:
    """Version cloud de Jiminy Cricket avec modèles premium"""
    
    def __init__(self, provider="openai", model="gpt-4-turbo-preview"):
        self.provider = provider
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY") if provider == "openai" else os.getenv("ANTHROPIC_API_KEY")
        
    async def generate(self, prompt: str, system: str = None) -> str:
        """Génère avec modèle cloud"""
        if not self.api_key:
            raise ValueError(f"Clé API manquante pour {self.provider}")
        
        if self.provider == "openai":
            return await self._openai_generate(prompt, system)
        elif self.provider == "anthropic":
            return await self._anthropic_generate(prompt, system)
    
    async def _openai_generate(self, prompt: str, system: str = None) -> str:
        """Appel OpenAI API"""
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}  # Force JSON
        }
        
        print(f"   ☁️ Appel OpenAI {self.model}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
                else:
                    error = await resp.text()
                    raise Exception(f"OpenAI Error {resp.status}: {error}")
    
    async def _anthropic_generate(self, prompt: str, system: str = None) -> str:
        """Appel Anthropic API"""
        import aiohttp
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 2000,
            "temperature": 0.7,
            "system": system or "Tu es un assistant qui répond en JSON valide.",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        print(f"   ☁️ Appel Anthropic {self.model}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['content'][0]['text']
                else:
                    error = await resp.text()
                    raise Exception(f"Anthropic Error {resp.status}: {error}")


async def compare_models():
    """Compare Ollama local vs Cloud sur la même tâche"""
    
    print("\n" + "="*70)
    print("☁️ COMPARAISON OLLAMA LOCAL vs MODÈLES CLOUD")
    print("="*70)
    
    # Même prompt pour tous
    prompt = """
Analyse cette situation complexe et réponds UNIQUEMENT en JSON:

SITUATION:
Nous devons refactoriser une architecture monolithique legacy en microservices.
- 200K lignes de code
- 50 tables de base de données
- 10 ans d'historique
- Équipe de 8 développeurs
- Système critique (100K users/jour)

Réponds en JSON strict:
{
  "analysis": "analyse de la situation",
  "risks": ["risque 1", "risque 2"],
  "approach": "approche recommandée",
  "priority": "priorité immédiate",
  "confidence": 0.85
}
"""
    
    results = {}
    
    # Test 1: Ollama local
    print("\n🖥️  TEST 1: OLLAMA LOCAL (llama2/mistral)")
    print("   Caractéristiques: Gratuit, privé, mais 4-8K context")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "mistral",
                "prompt": prompt,
                "system": "Tu réponds uniquement en JSON valide.",
                "stream": False,
                "options": {"temperature": 0.7}
            }
            
            start = datetime.now()
            async with session.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    elapsed = (datetime.now() - start).total_seconds()
                    
                    response = data.get('response', '')
                    # Essayer de parser le JSON
                    try:
                        json_data = json.loads(response)
                        results['ollama'] = {
                            'success': True,
                            'time': elapsed,
                            'confidence': json_data.get('confidence', 'N/A'),
                            'approach': json_data.get('approach', 'N/A')[:50]
                        }
                        print(f"   ✅ Succès en {elapsed:.1f}s")
                        print(f"   📊 Confiance: {json_data.get('confidence', 'N/A')}")
                    except:
                        results['ollama'] = {'success': False, 'time': elapsed, 'error': 'JSON invalide'}
                        print(f"   ⚠️ JSON invalide après {elapsed:.1f}s")
                else:
                    results['ollama'] = {'success': False, 'error': f'HTTP {resp.status}'}
                    print(f"   ❌ Erreur HTTP {resp.status}")
    except Exception as e:
        results['ollama'] = {'success': False, 'error': str(e)}
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: OpenAI GPT-4 (si clé dispo)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("\n☁️  TEST 2: OPENAI GPT-4 TURBO")
        print("   Caractéristiques: 128K context, rapide, mais payant")
        try:
            cloud = CloudJiminyCricket(provider="openai", model="gpt-4-turbo-preview")
            
            start = datetime.now()
            response = await cloud.generate(
                prompt=prompt,
                system="Tu es un expert architecture qui répond en JSON strict."
            )
            elapsed = (datetime.now() - start).total_seconds()
            
            try:
                json_data = json.loads(response)
                results['openai'] = {
                    'success': True,
                    'time': elapsed,
                    'confidence': json_data.get('confidence', 'N/A'),
                    'approach': json_data.get('approach', 'N/A')[:50]
                }
                print(f"   ✅ Succès en {elapsed:.1f}s")
                print(f"   📊 Confiance: {json_data.get('confidence', 'N/A')}")
                print(f"   🎯 Approche: {json_data.get('approach', 'N/A')[:60]}...")
            except:
                results['openai'] = {'success': False, 'time': elapsed, 'error': 'JSON invalide'}
                print(f"   ⚠️ JSON invalide après {elapsed:.1f}s")
        except Exception as e:
            results['openai'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Erreur: {e}")
    else:
        print("\n☁️  TEST 2: OPENAI (clé manquante - saute)")
    
    # Test 3: Anthropic Claude (si clé dispo)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print("\n☁️  TEST 3: ANTHROPIC CLAUDE 3")
        print("   Caractéristiques: 200K context, très cohérent")
        try:
            cloud = CloudJiminyCricket(provider="anthropic", model="claude-3-sonnet-20240229")
            
            start = datetime.now()
            response = await cloud.generate(
                prompt=prompt,
                system="Tu es un expert architecture. Réponds UNIQUEMENT en JSON valide."
            )
            elapsed = (datetime.now() - start).total_seconds()
            
            try:
                # Claude peut wrapper le JSON dans du texte
                # Extraire le JSON
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0]
                elif '```' in response:
                    json_str = response.split('```')[1].split('```')[0]
                else:
                    json_str = response
                
                json_data = json.loads(json_str)
                results['anthropic'] = {
                    'success': True,
                    'time': elapsed,
                    'confidence': json_data.get('confidence', 'N/A'),
                    'approach': json_data.get('approach', 'N/A')[:50]
                }
                print(f"   ✅ Succès en {elapsed:.1f}s")
                print(f"   📊 Confiance: {json_data.get('confidence', 'N/A')}")
            except Exception as e:
                results['anthropic'] = {'success': False, 'time': elapsed, 'error': str(e)}
                print(f"   ⚠️ Erreur parsing après {elapsed:.1f}s: {e}")
        except Exception as e:
            results['anthropic'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Erreur: {e}")
    else:
        print("\n☁️  TEST 3: ANTHROPIC (clé manquante - saute)")
    
    # Résumé comparatif
    print("\n" + "="*70)
    print("📊 TABLEAU COMPARATIF")
    print("="*70)
    print(f"\n{'Modèle':<20} {'Succès':<10} {'Temps':<10} {'Confiance':<15}")
    print("-" * 70)
    
    for model, result in results.items():
        success = "✅" if result.get('success') else "❌"
        time = f"{result.get('time', 'N/A'):.1f}s" if 'time' in result else "N/A"
        conf = result.get('confidence', 'N/A')
        print(f"{model:<20} {success:<10} {time:<10} {conf}")
    
    print("\n" + "="*70)
    print("💡 RECOMMANDATION")
    print("="*70)
    
    cloud_available = 'openai' in results or 'anthropic' in results
    
    if cloud_available:
        print("""
✅ MODÈLES CLOUD DISPONIBLES

Pour Jiminy Cricket en production:
• Utilisez Ollama local pour: 
  - Développement quotidien
  - Tests fréquents
  - Analyses simples
  - Vie privée des données

• Utilisez Cloud (GPT-4/Claude) pour:
  - Analyses complexes critiques
  - Décisions importantes
  - JSON fiable requis
  - Grand contexte (200K tokens)
  - 
Limites Cloud à respecter:
• Rate limiting (RPM/tokens par minute)
• Coût par token (surveiller la facturation)
• Pas d'inférence illimitée
• Dépendance réseau
""")
    else:
        print("""
🖥️  UNIQUEMENT OLLAMA LOCAL

Avantages:
• Gratuit et illimité
• 100% offline/privé
• Pas de rate limiting

Inconvénients:
• Context limité (4-8K tokens)
• Moins cohérent sur JSON
• Plus lent (inference locale)
• Nécessite GPU pour vitesse

Pour utiliser les modèles cloud:
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
""")


async def demo_cloud_prism():
    """Démonstration d'un prisme avec modèle cloud"""
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("\n⚠️ Pas de clé OpenAI - démo cloud prism impossible")
        return
    
    print("\n" + "="*70)
    print("🌈 PRISME CLOUD - Mode 'architect'")
    print("="*70)
    
    cloud = CloudJiminyCricket(provider="openai", model="gpt-4-turbo-preview")
    
    context = {
        "situation": "Migration monolithique vers microservices",
        "codebase": "200K lignes, 50 tables, 10 ans d'historique",
        "scale": "100K users/jour",
        "team": "8 développeurs"
    }
    
    prompt = f"""
Tu es Jiminy Cricket en mode ARCHITECTE système.

CONTEXTE:
{json.dumps(context, indent=2, ensure_ascii=False)}

Analyse cette situation et réponds UNIQUEMENT en JSON:
{{
  "insight": "vue d'ensemble architecture",
  "confidence": 0.9,
  "system_view": "description vue système",
  "components": ["composant 1", "composant 2"],
  "tradeoffs": "principaux trade-offs",
  "recommendations": ["recommandation 1", "recommandation 2"]
}}
"""
    
    print("\n⏳ Analyse architecture avec GPT-4...")
    
    try:
        response = await cloud.generate(
            prompt=prompt,
            system="Tu es un architecte système senior. Réponds en JSON strict."
        )
        
        data = json.loads(response)
        
        print("\n✅ RÉSULTAT ARCHITECTE (Cloud):")
        print(f"   💡 Insight: {data.get('insight', 'N/A')[:80]}...")
        print(f"   📊 Confiance: {data.get('confidence', 'N/A')}")
        print(f"   🏗️  Vue système: {data.get('system_view', 'N/A')[:60]}...")
        print(f"   ⚖️  Trade-offs: {data.get('tradeoffs', 'N/A')[:60]}...")
        
        if data.get('recommendations'):
            print("\n   🎯 Recommandations:")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                print(f"      {i}. {rec[:70]}...")
        
        print("\n✨ Notez la qualité et cohérence du JSON (force du modèle cloud)")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")


async def main():
    """Démonstration cloud complète"""
    
    print("\n☁️"*25)
    print("   JIMINY CRICKET - DÉMONSTRATION CLOUD")
    print("   Comparaison Ollama local vs Modèles premium")
    print("☁️"*25)
    
    # Vérifier clés API
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("\n🔑 CLÉS API:")
    print(f"   OpenAI: {'✅ Configurée' if openai_key else '❌ Manquante'}")
    print(f"   Anthropic: {'✅ Configurée' if anthropic_key else '❌ Manquante'}")
    
    if not openai_key and not anthropic_key:
        print("\n⚠️  Aucune clé API cloud configurée")
        print("   Seul Ollama local sera testé")
        print("\n   Pour configurer:")
        print("   $env:OPENAI_API_KEY='sk-...'")
        print("   $env:ANTHROPIC_API_KEY='sk-ant-...'")
    
    input("\n⏎ Appuyez sur ENTRÉE pour lancer la comparaison...")
    
    # Comparaison
    await compare_models()
    
    # Demo prism cloud (si dispo)
    if openai_key:
        input("\n⏎ Démonstration prisme cloud...")
        await demo_cloud_prism()
    
    print("\n" + "="*70)
    print("🎉 DÉMONSTRATION CLOUD TERMINÉE")
    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Démo interrompue")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
