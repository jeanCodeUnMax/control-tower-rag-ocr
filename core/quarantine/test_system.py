#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SYSTÈME - Vérification que tout fonctionne
"""

import os
import sys

print("\n" + "="*70)
print("🔍 VÉRIFICATION SYSTÈME JIMINY CRICKET")
print("="*70)

# Test 1: Imports
print("\n1️⃣  TEST IMPORTS...")
try:
    from jiminy_cricket import JiminyCricket, CricketConfig
    from jiminy_prisms import PrismReflection, MultiPrismReflection
    AVAILABLE_PRISMS = PrismReflection.AVAILABLE_PRISMS
    print("   ✅ Imports OK")
except Exception as e:
    print(f"   ❌ Erreur import: {e}")
    sys.exit(1)

# Test 2: Nombre de prismes
print("\n2️⃣  TEST NOMBRE DE PRISMES...")
expected = 59
actual = len(AVAILABLE_PRISMS)
if actual == expected:
    print(f"   ✅ {actual}/{expected} prismes présents")
else:
    print(f"   ⚠️  {actual}/{expected} prismes (attendu: {expected})")

# Test 3: Vérification fichiers prompts
print("\n3️⃣  TEST FICHIERS PROMPTS...")
base_path = os.path.dirname(os.path.abspath(__file__))
prompts_dir = os.path.join(base_path, "prompts")

missing = []
for mode in AVAILABLE_PRISMS:
    prompt_file = os.path.join(prompts_dir, f"mode_{mode}.txt")
    if not os.path.exists(prompt_file):
        missing.append(mode)

if missing:
    print(f"   ⚠️  {len(missing)} prompts manquants:")
    for m in missing[:5]:
        print(f"      - mode_{m}.txt")
else:
    print(f"   ✅ Tous les prompts ({len(AVAILABLE_PRISMS)}) présents")

# Test 4: Structure classes
print("\n4️⃣  TEST STRUCTURE CLASSES...")
try:
    # Test PrismReflection
    prism = PrismReflection(mode="natural")
    assert prism.mode == "natural"
    print("   ✅ PrismReflection OK")
    
    # Test MultiPrismReflection
    multi = MultiPrismReflection(modes=["natural", "challenger"])
    assert len(multi.modes) == 2
    print("   ✅ MultiPrismReflection OK")
    
    # Test JiminyCricket
    cricket = JiminyCricket()
    assert cricket.config is not None
    print("   ✅ JiminyCricket OK")
    
except Exception as e:
    print(f"   ❌ Erreur structure: {e}")

# Test 5: Liste des prismes par catégorie
print("\n5️⃣  RÉPARTITION DES PRISMES...")
categories = {
    "Originaux": ["natural", "challenger", "scientific", "wisdom", "philosophical", 
                  "optimist", "pessimist", "experimental", "disciplined", 
                  "step_by_step", "creative", "caring"],
    "Perspectives": ["alignment", "investor", "creator", "user", "developer"],
    "Éthiques": ["ethical", "just", "moral", "arbitrary"],
    "Ésotériques": ["cabal", "wise", "divine", "magic", "esoteric"],
    "Ancestraux": ["ancestral", "celtic", "olympus", "nature", "gaia"],
    "Orientaux": ["shiva", "durga"],
    "Enseignement": ["assistant", "professor", "student", "disciple", "foreman", "sensei"],
    "NASA": ["nasa"],
    "Développeur": ["frontend", "backend", "devops", "agile", "singleton"],
    "Productivité": ["5s", "pareto", "eisenhower", "5whys", "pomodoro", "todo", "kanban"],
    "Créativité": ["writer", "wiifm", "machine_vision", "ai_vision"],
    "Pro Spécialisés": ["architect", "security", "economist", "lawyer", "psychologist"],
    "Validation": ["objective_critic", "auditor", "manifesto", "certifier"]
}

for cat, modes in categories.items():
    present = sum(1 for m in modes if m in AVAILABLE_PRISMS)
    total = len(modes)
    status = "✅" if present == total else "⚠️"
    print(f"   {status} {cat}: {present}/{total}")

# Test 6: Ollama disponible
print("\n6️⃣  TEST CONNEXION OLLAMA...")
try:
    import aiohttp
    import asyncio
    
    async def check_ollama():
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m.get('name', 'unknown') for m in data.get('models', [])]
                    return True, models
                return False, []
    
    available, models = asyncio.run(check_ollama())
    if available:
        print(f"   ✅ Ollama connecté")
        print(f"   📦 Modèles: {', '.join(models[:3])}")
    else:
        print(f"   ⚠️  Ollama ne répond pas")
        print(f"   💡 Démarrez: ollama serve")
except Exception as e:
    print(f"   ⚠️  Impossible de tester Ollama: {e}")

# Résumé
print("\n" + "="*70)
print("📊 RÉSUMÉ")
print("="*70)
print(f"""
✅ SYSTÈME CONFIGURÉ: {len(AVAILABLE_PRISMS)} MODES

Jiminy Cricket peut penser comme:
• 🧠 Un philosophe, scientifique, créatif
• 💼 Un investisseur, développeur, architecte
• ⚖️ Un juge, moraliste, éthique
• 🔮 Un ésotérique, mage, druide
• 🌳 Un ancien, une divinité
• 🎓 Un professeur, sensei, disciple
• 🛰️ Un ingénieur NASA
• 💻 Un dev frontend/backend/DevOps
• ⚡ Un expert 5S, Pareto, Pomodoro
• ✍️ Un écrivain, économiste, avocat
• ✅ Un auditeur, certifieur, critique

Pour tester:
   python demo_live.py
""")

print("="*70)
