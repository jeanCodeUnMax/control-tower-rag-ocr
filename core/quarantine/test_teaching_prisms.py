#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DES PRISMES ENSEIGNEMENT/APPRENTISSAGE

Nouveaux modes:
- assistant, professor, student, disciple, foreman, sensei
"""

import asyncio
from jiminy_prisms import PrismReflection


async def test_prism(mode: str, emoji: str, name: str, context: dict):
    """Teste un prisme spécifique"""
    print(f"\n{'='*70}")
    print(f"{emoji} {name.upper()} ({mode})")
    print(f"{'='*70}")
    
    try:
        async with PrismReflection(mode) as prism:
            result = await prism.reflect(context)
            
            if result:
                print(f"\n💡 Insight: {result.insight[:100]}...")
                print(f"📊 Confiance: {result.confidence:.0%}")
                if result.recommendations:
                    print(f"🎯 Recommandation: {result.recommendations[0][:80]}...")
                return result
            else:
                print("⚠️ Pas de résultat")
                return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


async def main():
    """Démonstration des prismes enseignement"""
    
    print("\n🎓"*25)
    print("   JIMINY CRICKET - MODES ENSEIGNEMENT/APPRENTISSAGE")
    print("🎓"*25)
    
    context = {
        "situation": "Apprendre un nouveau framework de développement",
        "subject": "Architecture microservices",
        "level": "intermediate",
        "goal": "maîtrise professionnelle"
    }
    
    print(f"\nScénario: {context['situation']}")
    print(f"Sujet: {context['subject']}")
    
    teaching_prisms = [
        ("assistant", "🤝", "Assistant/Support"),
        ("professor", "👨‍🏫", "Professeur"),
        ("student", "🙋", "Élève/Apprenant"),
        ("disciple", "🧘", "Disciple/Dévoué"),
        ("foreman", "👷", "Contre-maître/Terrain"),
        ("sensei", "🥋", "Sensei/Maître"),
    ]
    
    results = {}
    for mode, emoji, name in teaching_prisms:
        result = await test_prism(mode, emoji, name, context)
        if result:
            results[mode] = result
        await asyncio.sleep(0.5)
    
    # Synthèse
    print("\n" + "="*70)
    print("📊 SYNTHÈSE DES 6 MODES ENSEIGNEMENT")
    print("="*70)
    
    if results:
        avg_conf = sum(r.confidence for r in results.values()) / len(results)
        print(f"\nModes actifs: {len(results)}/{len(teaching_prisms)}")
        print(f"Confiance moyenne: {avg_conf:.0%}")
        
        print("\nPerspectives complémentaires:")
        for mode, result in results.items():
            print(f"  • {mode}: {result.insight[:50]}...")
    
    print("\n" + "="*70)
    print("🦗 TOTAL: 33 MODES DE RÉFLEXION !")
    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
