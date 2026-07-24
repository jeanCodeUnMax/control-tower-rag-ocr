#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JIMINY DEPTH ANALYZER - Analyse progressive des prismes

Sélectionne dynamiquement les modes de réflexion appropriés
en fonction de la profondeur et complexité de la requête.
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DepthLevel(Enum):
    """Niveaux de profondeur d'analyse"""
    SURFACE = 1      # Réponse rapide, intuition
    ANALYSIS = 2     # Analyse structurée
    STRATEGY = 3     # Stratégie et planification
    DEEP = 4         # Réflexion profonde
    TRANSFORM = 5    # Transformation/paradigme


@dataclass
class DepthProfile:
    """Profil de profondeur d'une requête"""
    level: DepthLevel
    urgency: str  # low, medium, high, critical
    complexity: str  # simple, moderate, complex, wicked
    emotional_load: str  # neutral, light, heavy
    stakeholder_count: int
    time_horizon: str  # immediate, short, medium, long
    risk_level: str  # low, medium, high, existential


class ProgressivePrismSelector:
    """
    Sélecteur progressif de prismes selon la profondeur.
    """
    
    # Mapping profondeur → prismes recommandés
    DEPTH_PRISMS = {
        DepthLevel.SURFACE: {
            "primary": ["natural", "challenger", "smart"],
            "secondary": ["wiifm", "attention", "step_by_step"],
            "tertiary": ["optimist", "pessimist"]
        },
        DepthLevel.ANALYSIS: {
            "primary": ["scientific", "5whys", "objective_critic", "auditor"],
            "secondary": ["disciplined", "pareto", "eisenhower", "focus"],
            "tertiary": ["developer", "backend", "singleton"]
        },
        DepthLevel.STRATEGY: {
            "primary": ["architect", "investor", "nasa", "alignment"],
            "secondary": ["agile", "mvp", "kanban", "5s"],
            "tertiary": ["economist", "lawyer", "security"]
        },
        DepthLevel.DEEP: {
            "primary": ["wisdom", "philosophical", "ikigai", "meditation"],
            "secondary": ["psychologist", "yin", "yang", "fengshui"],
            "tertiary": ["ancestral", "wise", "esoteric"]
        },
        DepthLevel.TRANSFORM: {
            "primary": ["shiva", "durga", "divine", "magic"],
            "secondary": ["infinite_knowledge", "cabal", "chakra", "vibration"],
            "tertiary": ["manifesto", "fondateur", "inventeur", "createur"]
        }
    }
    
    # Modes spécifiques selon contexte
    CONTEXT_MODES = {
        "technical": ["developer", "architect", "security", "nasa", "singleton"],
        "business": ["investor", "economist", "marketeur", "mvp", "fondateur"],
        "creative": ["createur", "inventeur", "writer", "ai_vision", "creative"],
        "personal": ["ikigai", "psychologist", "wiifm", "meditation", "attention"],
        "crisis": ["shiva", "durga", "security", "auditor", "objective_critic"],
        "learning": ["student", "professor", "5whys", "scientific", "wisdom"],
        "decision": ["eisenhower", "pareto", "just", "ethical", "alignment"]
    }
    
    @staticmethod
    def analyze_depth(context: Dict) -> DepthProfile:
        """
        Analyse la profondeur nécessaire pour une requête.
        
        Args:
            context: Dictionnaire avec les informations de la situation
            
        Returns:
            Profil de profondeur déterminé
        """
        # Score de profondeur basé sur les indicateurs
        score = 0
        
        # Complexité
        complexity = context.get("complexity", "simple")
        complexity_scores = {"simple": 1, "moderate": 2, "complex": 3, "wicked": 4}
        score += complexity_scores.get(complexity, 1)
        
        # Horizon temporel
        horizon = context.get("time_horizon", "immediate")
        horizon_scores = {"immediate": 1, "short": 2, "medium": 3, "long": 4}
        score += horizon_scores.get(horizon, 1)
        
        # Nombre de parties prenantes
        stakeholders = context.get("stakeholders", 1)
        if stakeholders > 10:
            score += 3
        elif stakeholders > 3:
            score += 2
        else:
            score += 1
        
        # Risque
        risk = context.get("risk", "low")
        risk_scores = {"low": 1, "medium": 2, "high": 3, "existential": 4}
        score += risk_scores.get(risk, 1)
        
        # Charge émotionnelle
        emotional = context.get("emotional_load", "neutral")
        if emotional in ["heavy", "intense"]:
            score += 2
        elif emotional == "light":
            score += 1
        
        # Déterminer le niveau
        if score <= 4:
            level = DepthLevel.SURFACE
        elif score <= 8:
            level = DepthLevel.ANALYSIS
        elif score <= 12:
            level = DepthLevel.STRATEGY
        elif score <= 16:
            level = DepthLevel.DEEP
        else:
            level = DepthLevel.TRANSFORM
        
        return DepthProfile(
            level=level,
            urgency=context.get("urgency", "medium"),
            complexity=complexity,
            emotional_load=emotional,
            stakeholder_count=stakeholders,
            time_horizon=horizon,
            risk_level=risk
        )
    
    @classmethod
    def select_prisms(cls, context: Dict, max_prisms: int = 5) -> List[str]:
        """
        Sélectionne les prismes appropriés pour une requête.
        
        Args:
            context: Contexte de la situation
            max_prisms: Nombre maximum de prismes à retourner
            
        Returns:
            Liste des modes prismes recommandés
        """
        # Analyser la profondeur
        profile = cls.analyze_depth(context)
        
        # Obtenir les prismes du niveau
        level_prisms = cls.DEPTH_PRISMS.get(profile.level, cls.DEPTH_PRISMS[DepthLevel.ANALYSIS])
        
        selected = []
        
        # Ajouter les prismes primaires (toujours présents)
        selected.extend(level_prisms["primary"])
        
        # Ajouter contexte spécifique si applicable
        context_type = context.get("context_type", "")
        if context_type in cls.CONTEXT_MODES:
            context_prisms = cls.CONTEXT_MODES[context_type][:2]  # Max 2 spécifiques
            selected.extend(context_prisms)
        
        # Compléter avec secondaires si besoin
        if len(selected) < max_prisms:
            needed = max_prisms - len(selected)
            selected.extend(level_prisms["secondary"][:needed])
        
        # Ajouter tertiaires si toujours pas assez
        if len(selected) < max_prisms:
            needed = max_prisms - len(selected)
            selected.extend(level_prisms["tertiary"][:needed])
        
        return selected[:max_prisms]
    
    @classmethod
    def get_analysis_plan(cls, context: Dict) -> Dict:
        """
        Génère un plan d'analyse complet avec phases.
        
        Args:
            context: Contexte de la situation
            
        Returns:
            Plan avec phases et prismes recommandés
        """
        profile = cls.analyze_depth(context)
        
        # Plan progressif
        plan = {
            "depth_level": profile.level.name,
            "profile": {
                "urgency": profile.urgency,
                "complexity": profile.complexity,
                "risk": profile.risk_level,
                "emotional_load": profile.emotional_load
            },
            "phases": []
        }
        
        # Phase 1: Observation (toujours)
        phase1_prisms = ["natural", "challenger", "attention"]
        plan["phases"].append({
            "phase": 1,
            "name": "Observation & Première Impression",
            "prisms": phase1_prisms,
            "goal": "Capturer l'essence de la situation"
        })
        
        # Phase 2: Analyse (si niveau > SURFACE)
        if profile.level.value >= DepthLevel.ANALYSIS.value:
            phase2_prisms = cls.select_prisms(context, max_prisms=3)
            # Retirer les doublons avec phase 1
            phase2_prisms = [p for p in phase2_prisms if p not in phase1_prisms][:3]
            if phase2_prisms:
                plan["phases"].append({
                    "phase": 2,
                    "name": "Analyse Structurée",
                    "prisms": phase2_prisms,
                    "goal": "Comprendre en profondeur"
                })
        
        # Phase 3: Stratégie (si niveau > ANALYSIS)
        if profile.level.value >= DepthLevel.STRATEGY.value:
            strategy_prisms = ["architect", "investor", "alignment"]
            if profile.risk_level in ["high", "existential"]:
                strategy_prisms.insert(0, "nasa")
            if profile.emotional_load == "heavy":
                strategy_prisms.append("psychologist")
            
            plan["phases"].append({
                "phase": 3,
                "name": "Stratégie & Planification",
                "prisms": strategy_prisms[:3],
                "goal": "Définir l'approche optimale"
            })
        
        # Phase 4: Transformation (si niveau DEEP ou TRANSFORM)
        if profile.level.value >= DepthLevel.DEEP.value:
            transform_prisms = ["wisdom", "meditation"]
            if profile.level == DepthLevel.TRANSFORM:
                transform_prisms.extend(["shiva", "divine"])
            
            plan["phases"].append({
                "phase": 4,
                "name": "Vision Profonde & Transformation",
                "prisms": transform_prisms[:3],
                "goal": "Accéder à la sagesse profonde"
            })
        
        # Synthèse finale
        all_prisms = []
        for phase in plan["phases"]:
            all_prisms.extend(phase["prisms"])
        
        plan["recommended_prisms"] = list(dict.fromkeys(all_prisms))  # Sans doublons
        plan["estimated_time"] = len(plan["phases"]) * 30  # 30s par phase estimé
        
        return plan
    
    @staticmethod
    def explain_selection(prisms: List[str], profile: DepthProfile) -> str:
        """
        Génère une explication de la sélection des prismes.
        
        Args:
            prisms: Liste des prismes sélectionnés
            profile: Profil de profondeur
            
        Returns:
            Explication textuelle
        """
        lines = [
            f"📊 PROFONDEUR: {profile.level.name}",
            f"   Urgence: {profile.urgency} | Complexité: {profile.complexity} | Risque: {profile.risk_level}",
            f"",
            f"🎯 {len(prisms)} PRISMES SÉLECTIONNÉS:",
        ]
        
        for i, prism in enumerate(prisms, 1):
            lines.append(f"   {i}. {prism}")
        
        lines.append(f"")
        lines.append(f"💡 Pourquoi ce profil ?")
        
        if profile.level == DepthLevel.SURFACE:
            lines.append(f"   → Situation simple, réponse rapide nécessaire")
        elif profile.level == DepthLevel.ANALYSIS:
            lines.append(f"   → Analyse structurée requise pour clarifier")
        elif profile.level == DepthLevel.STRATEGY:
            lines.append(f"   → Planification stratégique nécessaire")
        elif profile.level == DepthLevel.DEEP:
            lines.append(f"   → Réflexion profonde sur implications multiples")
        elif profile.level == DepthLevel.TRANSFORM:
            lines.append(f"   → Transformation fondamentale nécessaire")
        
        return "\n".join(lines)


# Fonction utilitaire simple
def analyze_with_progressive_depth(context: Dict) -> Dict:
    """
    Point d'entrée principal pour l'analyse progressive.
    
    Usage:
        result = analyze_with_progressive_depth({
            "situation": "Migration base de données",
            "complexity": "complex",
            "risk": "high",
            "stakeholders": 5,
            "context_type": "technical"
        })
    """
    selector = ProgressivePrismSelector()
    plan = selector.get_analysis_plan(context)
    
    return {
        "plan": plan,
        "prisms": plan["recommended_prisms"],
        "phases_count": len(plan["phases"]),
        "depth": plan["depth_level"]
    }


if __name__ == "__main__":
    # Exemple d'utilisation
    test_contexts = [
        {
            "situation": "Bug simple à corriger",
            "complexity": "simple",
            "risk": "low",
            "urgency": "medium"
        },
        {
            "situation": "Architecture microservices",
            "complexity": "complex",
            "risk": "high",
            "stakeholders": 8,
            "context_type": "technical"
        },
        {
            "situation": "Changement de carrière",
            "complexity": "wicked",
            "risk": "medium",
            "emotional_load": "heavy",
            "time_horizon": "long",
            "context_type": "personal"
        }
    ]
    
    print("="*70)
    print("DÉMONSTRATION ANALYSE PROGRESSIVE")
    print("="*70)
    
    for ctx in test_contexts:
        print(f"\n📋 SITUATION: {ctx['situation']}")
        result = analyze_with_progressive_depth(ctx)
        
        profile = ProgressivePrismSelector.analyze_depth(ctx)
        print(ProgressivePrismSelector.explain_selection(result["prisms"], profile))
        print(f"\n⏱️  Temps estimé: {result['plan']['estimated_time']}s")
