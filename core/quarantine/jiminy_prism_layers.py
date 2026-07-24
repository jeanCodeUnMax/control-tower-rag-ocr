#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JIMINY PRISM LAYERS - Architecture en couches de profondeur

Organise les 83+ modes en niveaux de profondeur:
- SURFACE: Modes macro, universels, accessibles
- PROFONDEUR: Modes micro, spécialisés, ésotériques
- Le sélecteur choisit selon le contexte sans noyer le modèle
"""

from typing import List, Dict, Optional
from enum import Enum


class PrismDepth(Enum):
    """Niveaux de profondeur des prismes"""
    SURFACE = "surface"      # Macro, universel, accessible à tous
    INTERMEDIATE = "intermediate"  # Spécialisé mais concret
    DEEP = "deep"           # Micro, technique, complexe
    ESOTERIC = "esoteric"   # Profond, ésotérique, spirituel


class PrismGranularity(Enum):
    """Granularité des prismes"""
    MACRO = "macro"         # Vue d'ensemble, généraliste
    MESO = "meso"           # Niveau intermédiaire
    MICRO = "micro"         # Détail, spécialisé


# ARCHITECTURE EN COUCHES - 83 modes organisés
PRISM_LAYERS = {
    # ═══════════════════════════════════════════════════════════
    # COUCHE SURFACE - MACRO (Universel, accessible)
    # ═══════════════════════════════════════════════════════════
    (PrismDepth.SURFACE, PrismGranularity.MACRO): {
        "cognitive": ["natural", "challenger", "scientific", "wisdom"],
        "émotionnel": ["optimist", "pessimist", "creative", "caring"],
        "action": ["disciplined", "step_by_step", "smart", "experimental"],
        "social": ["alignment", "user", "ethical", "marketeur"],
    },
    
    # ═══════════════════════════════════════════════════════════
    # COUCHE INTERMÉDIAIRE - MESO (Spécialisé mais concret)
    # ═══════════════════════════════════════════════════════════
    (PrismDepth.INTERMEDIATE, PrismGranularity.MESO): {
        "business": ["investor", "creator", "fondateur", "mvp"],
        "technique": ["developer", "architect", "agile", "singleton"],
        "méthodes": ["pareto", "eisenhower", "5whys", "pomodoro", "kanban"],
        "excellence": ["perfectionist", "5s", "todo", "ikigai"],
        "validation": ["objective_critic", "auditor", "manifesto", "certifier"],
    },
    
    # ═══════════════════════════════════════════════════════════
    # COUCHE PROFONDE - MICRO (Technique, spécialisé)
    # ═══════════════════════════════════════════════════════════
    (PrismDepth.DEEP, PrismGranularity.MICRO): {
        "spécialistes": ["security", "economist", "lawyer", "psychologist"],
        "paradigmes": ["frontend", "backend", "devops", "nasa"],
        "enseignement": ["assistant", "professor", "student", "disciple", "foreman", "sensei"],
        "vision": ["writer", "wiifm", "machine_vision", "ai_vision"],
    },
    
    # ═══════════════════════════════════════════════════════════
    # COUCHE ÉSOTÉRIQUE - MICRO-PROFOND (Spirituel, ésotérique)
    # ═══════════════════════════════════════════════════════════
    (PrismDepth.ESOTERIC, PrismGranularity.MICRO): {
        "sagesse": ["cabal", "wise", "divine", "magic", "esoteric"],
        "équilibre": ["yin", "yang", "fengshui", "chakra", "vibration"],
        "pratiques": ["meditation", "hypnosis", "infinite_knowledge"],
        "concentration": ["focus", "attention"],
        "traditions": ["ancestral", "celtic", "olympus", "nature", "gaia"],
        "divinités": ["shiva", "durga"],
        "artistique": ["createur", "inventeur"],  # Redondance créative ésotérique
    },
}


class LayeredPrismSelector:
    """
    Sélecteur de prismes basé sur les couches de profondeur.
    """
    
    # Profils de requête → couches à activer
    DEPTH_PROFILES = {
        "rapide": {
            "description": "Réponse immédiate, surface uniquement",
            "depths": [PrismDepth.SURFACE],
            "granularities": [PrismGranularity.MACRO],
            "max_prisms": 3,
        },
        "standard": {
            "description": "Analyse équilibrée surface + intermédiaire",
            "depths": [PrismDepth.SURFACE, PrismDepth.INTERMEDIATE],
            "granularities": [PrismGranularity.MACRO, PrismGranularity.MESO],
            "max_prisms": 5,
        },
        "profond": {
            "description": "Analyse complète avec spécialistes",
            "depths": [PrismDepth.SURFACE, PrismDepth.INTERMEDIATE, PrismDepth.DEEP],
            "granularities": [PrismGranularity.MACRO, PrismGranularity.MESO, PrismGranularity.MICRO],
            "max_prisms": 8,
        },
        "ésotérique": {
            "description": "Vision spirituelle et transformationnelle",
            "depths": [PrismDepth.SURFACE, PrismDepth.ESOTERIC],
            "granularities": [PrismGranularity.MACRO, PrismGranularity.MICRO],
            "max_prisms": 6,
        },
        "complet": {
            "description": "Toutes couches, tous niveaux",
            "depths": [PrismDepth.SURFACE, PrismDepth.INTERMEDIATE, PrismDepth.DEEP, PrismDepth.ESOTERIC],
            "granularities": [PrismGranularity.MACRO, PrismGranularity.MESO, PrismGranularity.MICRO],
            "max_prisms": 12,
        },
    }
    
    # Contextes spécifiques → modes prioritaires par couche
    CONTEXT_LAYERS = {
        "bug_technique": {
            "surface": ["challenger", "smart"],
            "intermediate": ["developer", "agile"],
            "deep": ["backend", "security"],
        },
        "stratégie_business": {
            "surface": ["alignment", "investor"],
            "intermediate": ["fondateur", "marketeur"],
            "deep": ["economist", "architect"],
        },
        "créativité": {
            "surface": ["creative", "optimist"],
            "intermediate": ["creator", "writer"],
            "deep": ["ai_vision", "createur"],
            "ésotérique": ["divine", "magic"],
        },
        "développement_personnel": {
            "surface": ["wisdom", "caring"],
            "intermediate": ["ikigai", "perfectionist"],
            "deep": ["psychologist", "professor"],
            "ésotérique": ["meditation", "infinite_knowledge", "chakra"],
        },
        "crise": {
            "surface": ["challenger", "scientific"],
            "intermediate": ["auditor", "objective_critic"],
            "deep": ["security", "nasa"],
            "ésotérique": ["shiva", "durga"],
        },
    }
    
    @classmethod
    def select_by_profile(
        cls,
        profile_name: str = "standard",
        context_type: Optional[str] = None,
        force_include: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Sélectionne les prismes selon le profil de profondeur.
        
        Args:
            profile_name: rapide, standard, profond, ésotérique, complet
            context_type: Type de contexte spécifique
            force_include: Modes à inclure obligatoirement
            
        Returns:
            Dict organisé par couche de profondeur
        """
        profile = cls.DEPTH_PROFILES.get(profile_name, cls.DEPTH_PROFILES["standard"])
        
        result = {
            "surface": [],
            "intermediate": [],
            "deep": [],
            "esoteric": [],
            "forced": force_include or [],
        }
        
        # Collecter les prismes des couches activées
        for (depth, granularity), categories in PRISM_LAYERS.items():
            if depth not in profile["depths"]:
                continue
            if granularity not in profile["granularities"]:
                continue
            
            layer_name = depth.value
            for modes in categories.values():
                result[layer_name].extend(modes)
        
        # Deduplicate
        for key in result:
            result[key] = list(dict.fromkeys(result[key]))
        
        # Appliquer contexte spécifique si fourni
        if context_type and context_type in cls.CONTEXT_LAYERS:
            context_priority = cls.CONTEXT_LAYERS[context_type]
            for layer, priority_modes in context_priority.items():
                # Réorganiser pour mettre les priorités en premier
                current = result.get(layer, [])
                reordered = [m for m in priority_modes if m in current]
                reordered += [m for m in current if m not in priority_modes]
                result[layer] = reordered
        
        # Limiter au max
        total = 0
        for key in ["surface", "intermediate", "deep", "esoteric"]:
            if total >= profile["max_prisms"]:
                result[key] = []
            else:
                allowed = profile["max_prisms"] - total
                result[key] = result[key][:allowed]
                total += len(result[key])
        
        return result
    
    @classmethod
    def get_flat_selection(
        cls,
        profile_name: str = "standard",
        context_type: Optional[str] = None,
        priority_layer: Optional[str] = None
    ) -> List[str]:
        """
        Retourne une liste plate de prismes sélectionnés.
        
        Args:
            priority_layer: Couche prioritaire ("surface", "esoteric", etc.)
        """
        layered = cls.select_by_profile(profile_name, context_type)
        
        # Ordre de priorité
        if priority_layer == "esoteric":
            order = ["esoteric", "deep", "intermediate", "surface"]
        elif priority_layer == "deep":
            order = ["deep", "intermediate", "surface", "esoteric"]
        else:  # default surface-first
            order = ["surface", "intermediate", "deep", "esoteric"]
        
        flat = []
        for layer in order:
            flat.extend(layered.get(layer, []))
        
        # Ajouter forced si présent
        if layered.get("forced"):
            flat = list(dict.fromkeys(layered["forced"] + flat))
        
        # Limiter
        profile = cls.DEPTH_PROFILES.get(profile_name, cls.DEPTH_PROFILES["standard"])
        return flat[:profile["max_prisms"]]
    
    @classmethod
    def explain_selection(
        cls,
        profile_name: str,
        selected: Dict[str, List[str]]
    ) -> str:
        """Génère une explication de la sélection."""
        profile = cls.DEPTH_PROFILES.get(profile_name, cls.DEPTH_PROFILES["standard"])
        
        lines = [
            f"📊 PROFIL: {profile_name.upper()}",
            f"   {profile['description']}",
            f"",
        ]
        
        layers = [
            ("surface", "🌊 SURFACE (Macro/Universel)"),
            ("intermediate", "⚡ INTERMÉDIAIRE (Meso/Spécialisé)"),
            ("deep", "🔬 PROFONDEUR (Micro/Technique)"),
            ("esoteric", "🔮 ÉSOTÉRIQUE (Spirituel/Profond)"),
        ]
        
        for key, label in layers:
            modes = selected.get(key, [])
            if modes:
                lines.append(f"{label}: {len(modes)} modes")
                for mode in modes[:5]:  # Max 5 affichés
                    lines.append(f"   • {mode}")
                if len(modes) > 5:
                    lines.append(f"   ... et {len(modes)-5} autres")
                lines.append("")
        
        if selected.get("forced"):
            lines.append(f"⚙️ FORCÉS: {', '.join(selected['forced'])}")
        
        total = sum(len(selected.get(k, [])) for k in ["surface", "intermediate", "deep", "esoteric"])
        lines.append(f"\n📈 TOTAL: {total} prismes sélectionnés")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════

def select_prisms_for_context(
    situation: str,
    complexity: str = "moderate",
    spiritual_depth: bool = False,
    max_prisms: int = 5
) -> List[str]:
    """
    Point d'entrée simple pour sélectionner des prismes.
    
    Usage:
        prisms = select_prisms_for_context(
            situation="Bug production",
            complexity="high",
            spiritual_depth=False
        )
    """
    # Déterminer le profil
    if complexity == "simple" and not spiritual_depth:
        profile = "rapide"
    elif spiritual_depth:
        profile = "ésotérique"
    elif complexity in ["complex", "wicked"]:
        profile = "profond"
    else:
        profile = "standard"
    
    # Déterminer le contexte
    situation_lower = situation.lower()
    if any(w in situation_lower for w in ["bug", "erreur", "crash", "code"]):
        context = "bug_technique"
    elif any(w in situation_lower for w in ["business", "stratégie", "revenu", "client"]):
        context = "stratégie_business"
    elif any(w in situation_lower for w in ["créer", "design", "innovation", "idée"]):
        context = "créativité"
    elif any(w in situation_lower for w in ["perso", "croissance", "épanouissement", "vie"]):
        context = "développement_personnel"
    elif any(w in situation_lower for w in ["crise", "urgence", "problème", "danger"]):
        context = "crise"
    else:
        context = None
    
    selector = LayeredPrismSelector()
    selected = selector.get_flat_selection(profile, context)
    
    return selected[:max_prisms]


if __name__ == "__main__":
    # Démonstration
    selector = LayeredPrismSelector()
    
    print("="*70)
    print("DÉMONSTRATION ARCHITECTURE EN COUCHES")
    print("="*70)
    
    tests = [
        ("rapide", None, "Bug simple"),
        ("standard", "bug_technique", "Architecture microservices"),
        ("profond", "stratégie_business", "Pivot business"),
        ("ésotérique", "développement_personnel", "Recherche de sens"),
        ("complet", "crise", "Crise majeure"),
    ]
    
    for profile, context, desc in tests:
        print(f"\n{'='*70}")
        print(f"📝 {desc}")
        print(f"   Profil: {profile} | Contexte: {context or 'général'}")
        print("="*70)
        
        selected = selector.select_by_profile(profile, context)
        print(selector.explain_selection(profile, selected))
        
        flat = selector.get_flat_selection(profile, context)
        print(f"\n🎯 Liste finale: {flat}")
