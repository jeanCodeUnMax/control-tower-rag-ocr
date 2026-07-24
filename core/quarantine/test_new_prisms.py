#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DES NOUVEAUX PRISMES (55 TOTAL)

Nouveaux modes:
- writer, wiifm, machine_vision, ai_vision
- architect, security, economist, lawyer, psychologist
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
    """Démonstration des nouveaux prismes"""
    
    print("\n🎯"*25)
    print("   JIMINY CRICKET - 55 MODES DE RÉFLEXION")
    print("🎯"*25)
    
    context = {
        "situation": "Lancement nouveau produit SaaS",
        "product": "Plateforme IA pour développeurs",
        "market": "B2B tech",
        "budget": "500K€",
        "timeline": "6 mois"
    }
    
    print(f"\nScénario: {context['situation']}")
    print(f"Produit: {context['product']}")
    
    # ============ CRÉATIVITÉ & VISION ============
    print("\n" + "✨"*35)
    print("   CRÉATIVITÉ & VISION")
    print("✨"*35)
    
    vision_prisms = [
        ("writer", "✍️", "Écrivain/Structure"),
        ("wiifm", "🎁", "What's In It For Me"),
        ("machine_vision", "📷", "Vision Machine"),
        ("ai_vision", "🤖", "Vision IA"),
    ]
    
    for mode, emoji, name in vision_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.3)
    
    # ============ PROFESSIONNELS SPÉCIALISÉS ============
    print("\n" + "🎩"*35)
    print("   PROFESSIONNELS SPÉCIALISÉS")
    print("🎩"*35)
    
    pro_prisms = [
        ("architect", "🏗️", "Architecte Système"),
        ("security", "🔒", "Expert Sécurité"),
        ("economist", "📊", "Économiste"),
        ("lawyer", "⚖️", "Avocat/Juridique"),
        ("psychologist", "🧠", "Psychologue"),
    ]
    
    for mode, emoji, name in pro_prisms:
        await test_prism(mode, emoji, name, context)
        await asyncio.sleep(0.3)
    
    # ============ SYNTHÈSE FINALE ============
    print("\n" + "="*70)
    print("📊 RÉCAPITULATIF - 55 PRISMES TOTAL")
    print("="*70)
    print("""
✅ ORIGINAUX (12)
✅ PROFESSIONNELS (5)
✅ ÉTHIQUES (4)
✅ ÉSOTÉRIQUES (5)
✅ ANCESTRAUX (5)
✅ ORIENTAUX (2)
✅ ENSEIGNEMENT (6)
✅ NASA (1)
✅ DÉVELOPPEUR (5)
✅ PRODUCTIVITÉ (8)

✅ NOUVEAUX (8):
   ✨ CRÉATIVITÉ (4): writer, wiifm, machine_vision, ai_vision
   🎩 PROFESSIONNELS (5): architect, security, economist, lawyer, psychologist
""")
    
    print("="*70)
    print("🦗 JIMINY CRICKET - 55 MODES DE RÉFLEXION !")
    print("="*70)
    print("\nLe système peut penser comme:")
    print("  ✍️ Un écrivain (structure narrative)")
    print("  🎁 Un utilisateur egoïste (bénéfice perso)")
    print("  📷 Un ordinateur (vision machine)")
    print("  🤖 Une IA (patterns ML)")
    print("  🏗️ Un architecte (vue système)")
    print("  🔒 Un hacker éthique (sécurité)")
    print("  📊 Un économiste (ROI/marché)")
    print("  ⚖️ Un avocat (juridique)")
    print("  🧠 Un psychologue (comportement)")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
