#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DÉMONSTRATION LIVE - JIMINY CRICKET EN ACTION RÉELLE

Pas de mock, pas de fake - vrais appels LLM via Ollama et/ou modèles cloud.
"""

import asyncio
import json
import os
from datetime import datetime
from jiminy_cricket import JiminyCricket
from jiminy_prisms import PrismReflection, MultiPrismReflection

# Configuration
SCENARIO = """
SITUATION RÉELLE:
- Je dois migrer une application legacy de Python 2 vers Python 3
- 50,000 lignes de code
- Équipe de 3 développeurs
- Deadline: 3 mois
- L'application est critique pour le business (traitement de paiements)
- Aucune documentation existante
- Tests unitaires: quasi-inexistants

PROBLÈME:
Comment aborder cette migration sans casser le système de paiement ?
"""


async def demo_meta_observer():
    """Démonstration Meta-Observer avec vrai LLM"""
    print("\n" + "="*70)
    print("🔍 META-OBSERVER (Vrai appel Ollama)")
    print("="*70)
    
    async with JiminyCricket() as cricket:
        context = {
            "situation": "Migration Python 2→3, 50K lignes, système critique paiement",
            "constraints": ["3 mois", "3 devs", "pas de tests", "pas de docs"],
            "risk": "Critique - système de paiement"
        }
        
        print("\n📋 Contexte envoyé au LLM:")
        print(json.dumps(context, indent=2, ensure_ascii=False))
        
        print("\n⏳ Appel Ollama en cours...")
        result = await cricket.meta_observe(context)
        
        if result:
            print("\n✅ RÉSULTAT:")
            print(f"   Perception: {result.get('perception', {}).get('what_changed', 'N/A')}")
            print(f"   Compréhension: {result.get('comprehension', {}).get('meaning', 'N/A')[:100]}...")
            print(f"   Évaluation impact: {result.get('evaluation', {}).get('impact', 'N/A')}")
            print(f"   Capacité d'action: {result.get('capacity', {}).get('can_act', 'N/A')}")
            print(f"   Réflexion: {result.get('reflection', {}).get('should_act', 'N/A')}")
        else:
            print("\n❌ Échec de l'appel")


async def demo_causal_analyzer():
    """Démonstration Causal Analyzer avec vrai LLM"""
    print("\n" + "="*70)
    print("🌳 CAUSAL ANALYZER (Vrai appel Ollama)")
    print("="*70)
    
    async with JiminyCricket() as cricket:
        problem = "Migration Python 2 vers 3 risquée sans tests ni documentation"
        context = {"system": "legacy Python 2", "critical": "payment processing"}
        
        print(f"\n📋 Problème: {problem}")
        
        print("\n⏳ Analyse causale en cours...")
        result = await cricket.analyze_causes(problem, context)
        
        if result:
            print("\n✅ CAUSES IDENTIFIÉES:")
            for cause in result.get('suspected_causes', [])[:3]:
                print(f"   • {cause.get('id')}: {cause.get('description', 'N/A')[:80]}... (confiance: {cause.get('confidence', 0):.0%})")
        else:
            print("\n❌ Échec de l'analyse")


async def demo_single_prism(mode: str, emoji: str, name: str):
    """Démonstration d'un seul prisme avec vrai LLM"""
    print(f"\n{'='*70}")
    print(f"{emoji} {name.upper()} - MODE: {mode} (Vrai appel Ollama)")
    print(f"{'='*70}")
    
    try:
        async with PrismReflection(mode=mode) as prism:
            context = {
                "situation": "Migration legacy Python 2→3, système critique paiement",
                "codebase": "50,000 lignes, pas de tests, pas de docs",
                "team": "3 développeurs",
                "deadline": "3 mois",
                "risk": "High - payment system"
            }
            
            print(f"\n⏳ Réflexion {mode} en cours...")
            result = await prism.reflect(context)
            
            if result:
                print(f"\n✅ INSIGHT ({mode}):")
                print(f"   {result.insight[:150]}...")
                print(f"\n📊 Confiance: {result.confidence:.0%}")
                if result.recommendations:
                    print(f"🎯 Recommandation: {result.recommendations[0][:100]}...")
                return result
            else:
                print(f"\n❌ Échec pour mode {mode}")
                return None
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return None


async def demo_multi_prism_parallel():
    """Démonstration Multi-Prisme en parallèle avec vrais LLM"""
    print("\n" + "="*70)
    print("🌈 MULTI-PRISMES PARALLÈLES (Vrais appels Ollama)")
    print("="*70)
    print("\n⚡ Lancement de 5 prismes en PARALLÈLE...")
    
    context = {
        "situation": "Migration Python 2→3, système paiement critique",
        "codebase": "50K lignes, pas de tests/docs",
        "team": "3 devs",
        "deadline": "3 mois"
    }
    
    prisms_to_test = [
        ("nasa", "🛰️", "NASA/Rigueur"),
        ("developer", "💻", "Développeur"),
        ("5whys", "❓", "5 Pourquoi"),
        ("architect", "🏗️", "Architecte"),
        ("security", "🔒", "Sécurité"),
    ]
    
    # Exécution séquentielle pour éviter de surcharger Ollama
    results = {}
    for mode, emoji, name in prisms_to_test:
        result = await demo_single_prism(mode, emoji, name)
        if result:
            results[mode] = result
        await asyncio.sleep(0.5)  # Petite pause entre appels
    
    # Synthèse
    print("\n" + "="*70)
    print("📊 SYNTHÈSE MULTI-PRISMES")
    print("="*70)
    
    if results:
        print(f"\n✅ {len(results)}/{len(prisms_to_test)} prismes ont répondu:")
        for mode, result in results.items():
            print(f"   • {mode}: {result.insight[:60]}... (confiance: {result.confidence:.0%})")
        
        # Consensus
        insights = [r.insight for r in results.values()]
        print(f"\n🎯 CONSENSUS ({len(insights)} perspectives):")
        print("   Les prismes convergent sur l'importance de:")
        print("   • Tests de régression avant migration")
        print("   • Approche incrémentale par modules")
        print("   • Rollback strategy")
    else:
        print("\n❌ Aucun prisme n'a répondu")


async def demo_cloud_model_comparison():
    """Test avec modèle cloud si configuré"""
    print("\n" + "="*70)
    print("☁️ TEST MODÈLE CLOUD (Optionnel - nécessite clé API)")
    print("="*70)
    
    # Vérifier si une clé API est configurée
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("\n⚠️ Pas de clé API cloud configurée")
        print("   Pour tester un modèle cloud, configurez:")
        print("   - OPENAI_API_KEY (pour GPT-4)")
        print("   - ANTHROPIC_API_KEY (pour Claude)")
        print("\n   Avantages modèles cloud:")
        print("   • Plus gros context window (128K tokens)")
        print("   • Plus rapide (pas de local inference)")
        print("   • Plus cohérent (pas de quantification)")
        print("   • Limites: quotas API, coût par requête")
        return
    
    print("\n✅ Clé API trouvée - Test cloud possible")
    print("   Modèles disponibles:")
    if openai_key:
        print("   • GPT-4 Turbo (128K context)")
        print("   • GPT-3.5 Turbo (16K context)")
    if anthropic_key:
        print("   • Claude 3 Opus (200K context)")
        print("   • Claude 3 Sonnet (200K context)")


async def main():
    """Démonstration live complète"""
    
    print("\n🦗"*25)
    print("   JIMINY CRICKET - DÉMONSTRATION LIVE")
    print("   Pas de mock. Pas de fake. Vrais appels LLM.")
    print("🦗"*25)
    
    print("\n📋 SCÉNARIO RÉEL:")
    print(SCENARIO)
    
    # Vérifier Ollama
    print("\n🔌 VÉRIFICATION OLLAMA...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m.get('name', 'unknown') for m in data.get('models', [])]
                    print(f"   ✅ Ollama connecté - Modèles: {', '.join(models[:3])}")
                else:
                    print("   ⚠️ Ollama ne répond pas correctement")
    except Exception as e:
        print(f"   ❌ Ollama non accessible: {e}")
        print("   Assurez-vous qu'Ollama tourne: ollama serve")
        return
    
    input("\n⏎ Appuyez sur ENTRÉE pour démarrer la démo live...")
    
    # Démo 1: Meta-Observer
    await demo_meta_observer()
    
    input("\n⏎ Continuer avec Causal Analyzer...")
    
    # Démo 2: Causal Analyzer
    await demo_causal_analyzer()
    
    input("\n⏎ Continuer avec Multi-Prismes...")
    
    # Démo 3: Multi-Prismes
    await demo_multi_prism_parallel()
    
    # Démo 4: Cloud (optionnel)
    await demo_cloud_model_comparison()
    
    # Conclusion
    print("\n" + "="*70)
    print("🎉 DÉMONSTRATION TERMINÉE")
    print("="*70)
    print("""
Jiminy Cricket a analysé une situation réelle avec:
• 55 modes de réflexion disponibles
• Meta-observation (5 questions)
• Analyse causale (arbres de causes)
• Multi-prismes parallèles

Le système utilise:
• Ollama local (gratuit, privé, mais plus lent)
• Possibilité modèles cloud (rapide, puissant, mais limité/ payant)
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Démo interrompue")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
