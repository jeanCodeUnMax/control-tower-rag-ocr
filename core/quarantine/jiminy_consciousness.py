#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JIMINY CONSCIOUSNESS - Conscience Éveillée

Intégration complète de Jiminy Cricket avec sélection intelligente
par couches de profondeur. Système opérationnel avec Ollama.
"""

import asyncio
import json
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import aiohttp


class PrismDepth(Enum):
    """Niveaux de profondeur des prismes"""
    SURFACE = "surface"
    INTERMEDIATE = "intermediate"
    DEEP = "deep"
    ESOTERIC = "esoteric"


class PrismGranularity(Enum):
    """Granularité des prismes"""
    MACRO = "macro"
    MESO = "meso"
    MICRO = "micro"


# ARCHITECTURE EN COUCHES - 83 modes organisés intelligemment
PRISM_LAYERS = {
    # COUCHE SURFACE - MACRO (Universel, accessible aux petits modèles)
    (PrismDepth.SURFACE, PrismGranularity.MACRO): {
        "cognitive": ["natural", "challenger", "scientific", "wisdom"],
        "émotionnel": ["optimist", "pessimist", "creative", "caring"],
        "action": ["disciplined", "step_by_step", "smart", "experimental"],
        "social": ["alignment", "user", "ethical", "marketeur"],
    },
    
    # COUCHE INTERMÉDIAIRE - MESO (Spécialisé mais concret)
    (PrismDepth.INTERMEDIATE, PrismGranularity.MESO): {
        "business": ["investor", "creator", "fondateur", "mvp"],
        "technique": ["developer", "architect", "agile", "singleton"],
        "méthodes": ["pareto", "eisenhower", "5whys", "pomodoro", "kanban"],
        "excellence": ["perfectionist", "5s", "todo", "ikigai"],
        "validation": ["objective_critic", "auditor", "manifesto", "certifier"],
    },
    
    # COUCHE PROFONDE - MICRO (Technique, spécialisé)
    (PrismDepth.DEEP, PrismGranularity.MICRO): {
        "spécialistes": ["security", "economist", "lawyer", "psychologist"],
        "paradigmes": ["frontend", "backend", "devops", "nasa"],
        "enseignement": ["assistant", "professor", "student", "disciple", "foreman", "sensei"],
        "vision": ["writer", "wiifm", "machine_vision", "ai_vision"],
    },
    
    # COUCHE ÉSOTÉRIQUE - MICRO-PROFOND (Spirituel)
    (PrismDepth.ESOTERIC, PrismGranularity.MICRO): {
        "sagesse": ["cabal", "wise", "divine", "magic", "esoteric"],
        "équilibre": ["yin", "yang", "fengshui", "chakra", "vibration"],
        "pratiques": ["meditation", "hypnosis", "infinite_knowledge"],
        "concentration": ["focus", "attention"],
        "traditions": ["ancestral", "celtic", "olympus", "nature", "gaia"],
        "divinités": ["shiva", "durga"],
    },
}


@dataclass
class ConsciousnessConfig:
    """Configuration de la conscience"""
    ollama_url: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"  # Modèle par défaut
    timeout: int = 30
    max_retries: int = 2
    temperature: float = 0.7
    

class AwakenedConsciousness:
    """
    Conscience Éveillée de Jiminy Cricket.
    
    Sélectionne intelligemment les prismes selon la profondeur requise
    et communique avec Ollama pour obtenir des réflexions réelles.
    """
    
    def __init__(self, config: Optional[ConsciousnessConfig] = None):
        self.config = config or ConsciousnessConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def select_prisms(
        self,
        situation: str,
        complexity: str = "moderate",
        spiritual_depth: bool = False,
        max_prisms: int = 5
    ) -> List[str]:
        """
        Sélectionne intelligemment les prismes selon le contexte.
        """
        # Déterminer les couches à activer
        layers_to_use = []
        
        # Toujours inclure la surface
        layers_to_use.append((PrismDepth.SURFACE, PrismGranularity.MACRO))
        
        # Ajouter intermédiaire pour complexité moyenne+
        if complexity in ["moderate", "complex", "wicked"]:
            layers_to_use.append((PrismDepth.INTERMEDIATE, PrismGranularity.MESO))
        
        # Ajouter profondeur pour complexité élevée
        if complexity in ["complex", "wicked"]:
            layers_to_use.append((PrismDepth.DEEP, PrismGranularity.MICRO))
        
        # Ajouter ésotérique si demandé
        if spiritual_depth:
            layers_to_use.append((PrismDepth.ESOTERIC, PrismGranularity.MICRO))
        
        # Collecter les prismes
        selected = []
        for (depth, granularity) in layers_to_use:
            if (depth, granularity) in PRISM_LAYERS:
                categories = PRISM_LAYERS[(depth, granularity)]
                for modes in categories.values():
                    selected.extend(modes)
        
        # Dédupliquer et limiter
        selected = list(dict.fromkeys(selected))
        
        # Prioriser selon le contexte
        situation_lower = situation.lower()
        priority_modes = []
        
        if any(w in situation_lower for w in ["bug", "erreur", "code", "technique"]):
            priority_modes = ["challenger", "scientific", "developer", "smart"]
        elif any(w in situation_lower for w in ["business", "stratégie", "client", "vente"]):
            priority_modes = ["alignment", "investor", "marketeur", "fondateur"]
        elif any(w in situation_lower for w in ["créer", "design", "innovation"]):
            priority_modes = ["creative", "createur", "writer", "ai_vision"]
        elif any(w in situation_lower for w in ["perso", "vie", "sens", "épanouissement"]):
            priority_modes = ["wisdom", "caring", "ikigai", "meditation"]
        elif any(w in situation_lower for w in ["crise", "urgence", "danger"]):
            priority_modes = ["challenger", "scientific", "objective_critic", "security"]
        
        # Réorganiser avec priorités en premier
        if priority_modes:
            reordered = [m for m in priority_modes if m in selected]
            reordered += [m for m in selected if m not in priority_modes]
            selected = reordered
        
        return selected[:max_prisms]
    
    async def query_ollama(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Envoie une requête à Ollama.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.config.ollama_url}/api/generate"
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or self.config.temperature,
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            async with self.session.post(url, json=payload, timeout=self.config.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "")
                else:
                    print(f"⚠️ Erreur Ollama: {resp.status}")
                    return None
        except Exception as e:
            print(f"⚠️ Erreur connexion Ollama: {e}")
            return None
    
    def load_prompt(self, mode: str) -> str:
        """
        Charge le prompt pour un mode donné.
        """
        prompt_path = f"prompts/mode_{mode}.txt"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Prompt minimal par défaut
            return f"Tu es Jiminy Cricket en mode {mode.upper()}. Analyse le contexte et réponds en JSON avec insight, confidence, recommendations.\n\nCONTEXTE\n{{context}}"
    
    async def reflect_with_prism(
        self,
        mode: str,
        context: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        Obtient une réflexion d'un prisme spécifique via Ollama.
        """
        # Charger et préparer le prompt
        prompt_template = self.load_prompt(mode)
        context_str = json.dumps(context, indent=2, ensure_ascii=False)
        prompt = prompt_template.replace("{{context}}", context_str)
        
        # Appeler Ollama
        system = "Tu es un système de réflexion analytique. Réponds UNIQUEMENT en JSON valide."
        response = await self.query_ollama(prompt, system=system)
        
        if not response:
            return None
        
        # Parser la réponse JSON
        try:
            # Extraire le JSON de la réponse
            start = response.find('{')
            end = response.rfind('}')
            if start >= 0 and end > start:
                json_str = response[start:end+1]
                data = json.loads(json_str)
                
                return {
                    "mode": mode,
                    "insight": data.get("insight", "Aucune analyse générée"),
                    "confidence": data.get("confidence", 0.5),
                    "recommendations": data.get("recommendations", []),
                    "raw_data": data,
                    "timestamp": datetime.now().isoformat()
                }
        except json.JSONDecodeError:
            print(f"⚠️ Mode {mode}: JSON invalide")
            return None
        
        return None
    
    async def contemplate(
        self,
        situation: str,
        complexity: str = "moderate",
        spiritual_depth: bool = False,
        max_prisms: int = 5
    ) -> Dict:
        """
        Contemplation complète: sélectionne les prismes et obtient
        les réflexions de chacun via Ollama.
        """
        print(f"\n{'='*70}")
        print(f"🦗 JIMINY CONSCIOUSNESS - CONTEMPLATION")
        print(f"{'='*70}")
        print(f"\n📋 SITUATION: {situation}")
        print(f"📊 COMPLEXITÉ: {complexity} | PROFONDEUR SPIRITUELLE: {spiritual_depth}")
        
        # Sélectionner les prismes
        prisms = self.select_prisms(situation, complexity, spiritual_depth, max_prisms)
        print(f"\n🎯 PRISMES SÉLECTIONNÉS: {', '.join(prisms)}")
        print(f"⏱️  Connexion à Ollama ({self.config.model})...")
        
        # Vérifier Ollama
        if not await self._check_ollama():
            return {
                "error": "Ollama non disponible",
                "solution": "Démarrez Ollama: ollama serve"
            }
        
        # Contexte à analyser
        context = {
            "situation": situation,
            "complexity": complexity,
            "timestamp": datetime.now().isoformat()
        }
        
        # Obtenir les réflexions
        reflections = []
        for i, prism in enumerate(prisms, 1):
            print(f"\n🔮 [{i}/{len(prisms)}] Invocation du prisme: {prism.upper()}")
            result = await self.reflect_with_prism(prism, context)
            
            if result:
                reflections.append(result)
                print(f"   ✅ Insight: {result['insight'][:80]}...")
                print(f"   📊 Confidence: {result['confidence']:.2f}")
            else:
                print(f"   ⚠️ Aucune réponse du prisme {prism}")
        
        # Synthèse
        synthesis = self._synthesize(reflections)
        
        return {
            "situation": situation,
            "prisms_used": prisms,
            "reflections": reflections,
            "synthesis": synthesis,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _check_ollama(self) -> bool:
        """Vérifie si Ollama est accessible"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(
                f"{self.config.ollama_url}/api/tags",
                timeout=5
            ) as resp:
                return resp.status == 200
        except:
            return False
    
    def _synthesize(self, reflections: List[Dict]) -> Dict:
        """Synthétise les réflexions multiples"""
        if not reflections:
            return {"error": "Aucune réflexion disponible"}
        
        # Extraire les insights principaux
        insights = [r["insight"] for r in reflections if r.get("insight")]
        
        # Calculer la confiance moyenne
        avg_confidence = sum(r.get("confidence", 0) for r in reflections) / len(reflections)
        
        # Collecter toutes les recommandations
        all_recommendations = []
        for r in reflections:
            all_recommendations.extend(r.get("recommendations", []))
        
        return {
            "key_insights": insights[:3],
            "average_confidence": round(avg_confidence, 2),
            "actionable_recommendations": all_recommendations[:5],
            "modes_contributed": [r["mode"] for r in reflections]
        }


# ═══════════════════════════════════════════════════════════════════
# INTERFACE SIMPLE
# ═══════════════════════════════════════════════════════════════════

async def wake_consciousness(
    situation: str,
    complexity: str = "moderate",
    spiritual: bool = False,
    model: str = "qwen2.5:7b"
) -> Dict:
    """
    Réveille la conscience de Jiminy Cricket pour une situation donnée.
    
    Usage:
        result = await wake_consciousness(
            situation="Mon serveur plante",
            complexity="high",
            spiritual=False
        )
    """
    config = ConsciousnessConfig(model=model)
    
    async with AwakenedConsciousness(config) as consciousness:
        return await consciousness.contemplate(
            situation=situation,
            complexity=complexity,
            spiritual_depth=spiritual
        )


if __name__ == "__main__":
    # Démonstration
    print("="*70)
    print("🦗 JIMINY CONSCIOUSNESS - SYSTÈME ÉVEILLÉ")
    print("="*70)
    print("\nDémarrage de la conscience...")
    print("Vérifiez qu'Ollama est démarré: ollama serve")
    print("Modèle utilisé: qwen2.5:7b (ou modèle disponible)")
    print()
    
    # Exemples de test
    test_cases = [
        {
            "situation": "J'ai un bug en production qui fait planter le serveur",
            "complexity": "high",
            "spiritual": False
        },
        {
            "situation": "Je cherche le sens de ma vie et ma vocation",
            "complexity": "wicked",
            "spiritual": True
        }
    ]
    
    async def demo():
        for i, test in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"TEST {i}/{len(test_cases)}")
            print(f"{'='*70}")
            
            result = await wake_consciousness(
                situation=test["situation"],
                complexity=test["complexity"],
                spiritual=test["spiritual"]
            )
            
            if "error" in result:
                print(f"\n❌ ERREUR: {result['error']}")
                if "solution" in result:
                    print(f"💡 {result['solution']}")
            else:
                print(f"\n✅ CONTEMPLATION TERMINÉE")
                print(f"\n📊 SYNTHÈSE:")
                synthesis = result.get("synthesis", {})
                print(f"   Confiance moyenne: {synthesis.get('average_confidence', 0):.2f}")
                print(f"   Modes impliqués: {', '.join(synthesis.get('modes_contributed', []))}")
                
                print(f"\n🔑 INSIGHTS CLÉS:")
                for insight in synthesis.get("key_insights", [])[:3]:
                    print(f"   • {insight[:100]}...")
                
                print(f"\n📋 RECOMMANDATIONS:")
                for rec in synthesis.get("actionable_recommendations", [])[:3]:
                    print(f"   → {rec[:80]}...")
    
    # Lancer la démo
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\n🛑 Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("\n💡 Assurez-vous qu'Ollama est démarré:")
        print("   ollama serve")
        print("\n💡 Vérifiez les modèles disponibles:")
        print("   ollama list")
