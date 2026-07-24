#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DES PRISMES ÉSOTÉRIQUES ET SPIRITUELS

Démonstration des nouveaux modes:
- alignment, investor, creator, user, developer
- ethical, just, moral, arbitrary
- cabal, wise, divine, magic, esoteric
- ancestral, celtic, olympus, nature, gaia, shiva, durga
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
    """Démonstration complète des prismes étendus"""
    
    print("\n✨"*25)
    print("   JIMINY CRICKET - PRISMES ÉSOTÉRIQUES ET MULTI-PERSPECTIVES")
    print("✨"*25)
    
    context = {
        "situation": "Décision architecturale critique",
        "problem": "Migration vers nouvelle stack technologique",
        "impact": "toute l'organisation",
        "urgency": "medium",
        "resources": "limités"
    }
    
    print(f"\nScénario: {context['situation']}")
    print(f"Problème: {context['problem']}")
    
    # ============ PERSPECTIVES PROFESSIONNELLES ============
    print("\n" + "🎯"*35)
    print("   PERSPECTIVES PROFESSIONNELLES")
    print("🎯"*35)
    
    professional_prisms = [
        ("alignment", "🎯", "Alignement systémique"),
        ("investor", "💰", "Perspective investisseur"),
        ("creator", "🎨", "Perspective créateur"),
        ("user", "👤", "Perspective utilisateur"),
        ("developer", "💻", "Perspective développeur"),
    ]
    
    for mode, emoji, name in professional_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.5)
    
    # ============ PERSPECTIVES ÉTHIQUES ============
    print("\n" + "⚖️"*35)
    print("   PERSPECTIVES ÉTHIQUES ET MORALES")
    print("⚖️"*35)
    
    ethical_prisms = [
        ("ethical", "⚖️", "Perspective éthique"),
        ("just", "🏛️", "Justice/Équité"),
        ("moral", "🕊️", "Morale/Vertus"),
        ("arbitrary", "🎲", "Arbitraire/Libre"),
    ]
    
    for mode, emoji, name in ethical_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.5)
    
    # ============ PERSPECTIVES ÉSOTÉRIQUES ============
    print("\n" + "🔮"*35)
    print("   PERSPECTIVES ÉSOTÉRIQUES ET SPIRITUELLES")
    print("🔮"*35)
    
    esoteric_prisms = [
        ("cabal", "🔮", "Sens caché/Cabale"),
        ("wise", "📜", "Sage universelle"),
        ("divine", "⭐", "Perspective divine"),
        ("magic", "✨", "Magie/Transformation"),
        ("esoteric", "🗝️", "Connaissance secrète"),
    ]
    
    for mode, emoji, name in esoteric_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.5)
    
    # ============ PERSPECTIVES ANCESTRALES ============
    print("\n" + "🌳"*35)
    print("   PERSPECTIVES ANCESTRALES ET MYTHOLOGIQUES")
    print("🌳"*35)
    
    ancestral_prisms = [
        ("ancestral", "👴", "Sagesse ancestrale"),
        ("celtic", "🌲", "Sagesse druidique"),
        ("olympus", "⚡", "Dieux de l'Olympe"),
        ("nature", "🍃", "Esprits de la nature"),
        ("gaia", "🌍", "Conscience de Gaia"),
    ]
    
    for mode, emoji, name in ancestral_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.5)
    
    # ============ PERSPECTIVES ORIENTALES ============
    print("\n" + "🕉️"*35)
    print("   PERSPECTIVES DIVINITÉS ORIENTALES")
    print("🕉️"*35)
    
    oriental_prisms = [
        ("shiva", "🔥", "Shiva/Destruction créatrice"),
        ("durga", "🦁", "Durga/Force protectrice"),
    ]
    
    for mode, emoji, name in oriental_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.5)
    
    # ============ SYNTHÈSE ============
    print("\n" + "="*70)
    print("📊 SYNTHÈSE DES 27 PRISMES")
    print("="*70)
    print("""
✅ PERSPECTIVES PROFESSIONNELLES (5):
   alignment, investor, creator, user, developer

✅ PERSPECTIVES ÉTHIQUES (4):
   ethical, just, moral, arbitrary

✅ PERSPECTIVES ÉSOTÉRIQUES (5):
   cabal, wise, divine, magic, esoteric

✅ PERSPECTIVES ANCESTRALES (5):
   ancestral, celtic, olympus, nature, gaia

✅ PERSPECTIVES ORIENTALES (2):
   shiva, durga

✅ PERSPECTIVES ORIGINALES (12):
   natural, challenger, scientific, wisdom, philosophical,
   optimist, pessimist, experimental, disciplined, step_by_step,
   creative, caring

📈 TOTAL: 27 MODES DE RÉFLEXION
""")
    
    print("="*70)
    print("🦗 JIMINY CRICKET peut maintenant penser sous 27 perspectives!")
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
