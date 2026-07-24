#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DÉMONSTRATION COMPLÈTE - TOUS LES MODES DE RÉFLEXION

Ce script montre comment Jiminy Cricket peut s'adapter à toutes les situations
en utilisant différents "prismes" de réflexion.
"""

import asyncio
from jiminy_prisms import PrismReflection


async def demonstrate_prism(mode: str, name: str, emoji: str, context: dict):
    """Teste un prisme spécifique"""
    print(f"\n{'='*70}")
    print(f"{emoji} {name.upper()} ({mode})")
    print(f"{'='*70}")
    
    try:
        async with PrismReflection(mode) as prism:
            result = await prism.reflect(context)
            
            if result:
                print(f"\n💡 Insight: {result.insight}")
                print(f"📊 Confiance: {result.confidence:.0%}")
                if result.recommendations:
                    print(f"🎯 Recommandation: {result.recommendations[0]}")
                return result
            else:
                print("⚠️ Pas de résultat")
                return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


async def main():
    """Démonstration complète"""
    
    print("\n🌈"*25)
    print("   JIMINY CRICKET - MULTI-MODES DE RÉFLEXION")
    print("🌈"*25)
    
    # Scénario serveur port 3002
    context = {
        "situation": "Serveur port 3002 inaccessible",
        "symptoms": ["ECONNREFUSED", "timeout"],
        "recent_change": "express updated 2h ago"
    }
    
    print(f"\nScénario: {context['situation']}")
    print(f"Symptômes: {', '.join(context['symptoms'])}")
    print(f"Changement récent: {context['recent_change']}")
    
    # Tester les modes clés
    prisms_to_test = [
        ("natural", "Naturel/Intuitif", "🌿"),
        ("challenger", "Challenger/Critique", "⚔️"),
        ("scientific", "Scientifique/Rigoureux", "🔬"),
        ("wisdom", "Sagesse/Expérience", "📚"),
        ("philosophical", "Philosophique/Profond", "🤔"),
        ("optimist", "Optimiste/Constructif", "☀️"),
        ("pessimist", "Pessimiste/Prudent", "🛡️"),
        ("experimental", "Expérimental/Test", "🧪"),
        ("disciplined", "Discipliné/Procédure", "📋"),
        ("creative", "Créatif/Innovant", "🎨"),
    ]
    
    results = {}
    
    for mode, name, emoji in prisms_to_test:
        result = await demonstrate_prism(mode, name, emoji, context)
        if result:
            results[mode] = result
    
    # Synthèse
    print("\n" + "="*70)
    print("📊 SYNTHÈSE MULTI-DIMENSIONNELLE")
    print("="*70)
    
    if results:
        avg_conf = sum(r.confidence for r in results.values()) / len(results)
        print(f"\nModes actifs: {len(results)}/{len(prisms_to_test)}")
        print(f"Confiance moyenne: {avg_conf:.0%}")
        
        print("\nPerspectives complémentaires:")
        for mode, result in results.items():
            print(f"  • {mode}: {result.insight[:50]}...")
    
    print("\n" + "="*70)
    print("✅ Démonstration terminée")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
