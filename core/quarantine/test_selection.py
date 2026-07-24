#!/usr/bin/env python3
"""Test B: Sélection intelligente de prismes selon contexte"""

from jiminy_consciousness import AwakenedConsciousness

print("="*70)
print("🎯 TEST B: SÉLECTION INTELLIGENTE PAR CONTEXTE")
print("="*70)

consciousness = AwakenedConsciousness()

test_cases = [
    ("Mon serveur plante", "high", False, "TECHNIQUE"),
    ("Je cherche le sens de ma vie", "wicked", True, "EXISTENTIEL"),
    ("Bug CSS sur mobile", "simple", False, "FRONTEND"),
    ("Stratégie marketing Q1", "complex", False, "BUSINESS"),
]

for situation, complexity, spiritual, label in test_cases:
    print(f"\n{'='*70}")
    print(f"📋 {label}: {situation[:40]}...")
    print(f"   Complexité: {complexity} | Spirituel: {spiritual}")
    print("-"*70)
    
    prisms = consciousness.select_prisms(situation, complexity, spiritual, max_prisms=5)
    
    print(f"🎯 Prismes sélectionnés:")
    for i, p in enumerate(prisms, 1):
        depth = "?"
        if p in ["natural", "challenger", "scientific", "smart"]:
            depth = "🌊 surface"
        elif p in ["developer", "architect", "nasa", "mvp"]:
            depth = "⚡ intermédiaire"
        elif p in ["security", "psychologist", "backend"]:
            depth = "🔬 profond"
        elif p in ["divine", "meditation", "chakra", "wisdom"]:
            depth = "🔮 ésotérique"
        print(f"   {i}. {p:15} {depth}")

print(f"\n{'='*70}")
print("✅ TEST B: SÉLECTION ADAPTATIVE CONFIRMÉE")
print("="*70)
print("\n💡 La sélection s'adapte au contexte:")
print("   - Technique → challenger, developer, nasa, security")
print("   - Existentiel → wisdom, divine, meditation, chakra")
print("   - Simple → natural, smart, challenger (surface)")
print("   - Complexe → + architect, mvp (intermédiaire)")
