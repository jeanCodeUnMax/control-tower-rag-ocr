#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DES PRISMES NASA, DÉVELOPPEUR ET PRODUCTIVITÉ

Nouveaux modes:
- nasa, frontend, backend, devops, agile, singleton
- 5s, pareto, eisenhower, 5whys, pomodoro, todo, kanban
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
    """Démonstration des prismes NASA, dev et productivité"""
    
    print("\n🚀"*25)
    print("   JIMINY CRICKET - NASA, DÉVELOPPEUR & MÉTHODES")
    print("🚀"*25)
    
    context = {
        "situation": "Développement nouvelle fonctionnalité critique",
        "feature": "Système de paiement en ligne",
        "deadline": "2 semaines",
        "team_size": "4 développeurs"
    }
    
    print(f"\nScénario: {context['situation']}")
    print(f"Feature: {context['feature']}")
    
    # ============ NASA & RIGUEUR ============
    print("\n" + "🛰️"*35)
    print("   RÈGLES DE VIE NASA")
    print("🛰️"*35)
    
    await test_prism("nasa", "🛰️", "Rigueur spatiale NASA", context)
    
    # ============ PARADIGMES DÉVELOPPEUR ============
    print("\n" + "💻"*35)
    print("   PARADIGMES DÉVELOPPEUR")
    print("💻"*35)
    
    dev_prisms = [
        ("frontend", "🎨", "Frontend/UX"),
        ("backend", "⚙️", "Backend/Scalabilité"),
        ("devops", "🔄", "DevOps/Automatisation"),
        ("agile", "📊", "Agile/Itération"),
        ("singleton", "🏗️", "Design Patterns"),
    ]
    
    for mode, emoji, name in dev_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.3)
    
    # ============ MÉTHODES DE PRODUCTIVITÉ ============
    print("\n" + "⚡"*35)
    print("   MÉTHODES DE PRODUCTIVITÉ")
    print("⚡"*35)
    
    productivity_prisms = [
        ("5s", "🧹", "5S Japonais"),
        ("pareto", "📈", "80/20 Pareto"),
        ("eisenhower", "🎯", "Matrice Eisenhower"),
        ("5whys", "❓", "5 Pourquoi"),
        ("pomodoro", "🍅", "Pomodoro"),
        ("todo", "✅", "TODO List"),
        ("kanban", "📋", "Kanban Board"),
    ]
    
    for mode, emoji, name in productivity_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.3)
    
    # ============ SYNTHÈSE ============
    print("\n" + "="*70)
    print("📊 RÉCAPITULATIF - 47 PRISMES TOTAL")
    print("="*70)
    print("""
✅ ORIGINAUX (12): natural, challenger, scientific...
✅ PROFESSIONNELS (5): alignment, investor, creator...
✅ ÉTHIQUES (4): ethical, just, moral, arbitrary
✅ ÉSOTÉRIQUES (5): cabal, wise, divine, magic...
✅ ANCESTRAUX (5): ancestral, celtic, olympus...
✅ ORIENTAUX (2): shiva, durga
✅ ENSEIGNEMENT (6): assistant, professor, student...

✅ NOUVEAUX:
   🛰️ NASA (1): nasa
   💻 DÉVELOPPEUR (5): frontend, backend, devops, agile, singleton
   ⚡ PRODUCTIVITÉ (8): 5s, pareto, eisenhower, 5whys, pomodoro, todo, kanban
""")
    
    print("="*70)
    print("🦗 TOTAL: 47 MODES DE RÉFLEXION !")
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
