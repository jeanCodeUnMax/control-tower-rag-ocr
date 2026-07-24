#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JIMINY VECTOR MEMORY - Mémoire sémantique des prismes

Indexation vectorielle de tous les modes avec métadonnées riches
dans Zvec pour recherche sémantique et sélection intelligente.
"""

import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class PrismDimension(Enum):
    """Dimensions d'analyse des prismes"""
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    ACTION = "action"
    STRATEGIC = "strategic"
    ESOTERIC = "esoteric"
    TECHNICAL = "technical"
    SOCIAL = "social"
    CREATIVE = "creative"


@dataclass
class PrismMetadata:
    """
    Métadonnées riches pour indexation vectorielle.
    
    Chaque prisme est décrit selon multiples dimensions
    pour permettre la recherche sémantique contextuelle.
    """
    # Identité
    mode: str
    name: str
    category: str
    
    # Essence
    essence: str  # Qu'est-ce que c'est en 1 phrase
    purpose: str  # À quoi ça sert
    philosophy: str  # Quelle est la philosophie sous-jacente
    
    # Dimensions
    dimensions: List[str]  # cognitive, emotional, technical...
    
    # Cas d'usage
    use_cases: List[str]  # Quand l'utiliser
    contexts: List[str]  # Contextes appropriés
    situations: List[str]  # Situations types
    
    # Granularité
    depth: str  # surface, intermediate, deep, esoteric
    granularity: str  # macro, meso, micro
    complexity: str  # simple, moderate, complex, wicked
    
    # Analogies et métaphores
    analogies: List[str]  # "Comme un...", "Semblable à..."
    metaphors: List[str]  # Métaphores descriptives
    archetype: str  # Archétype correspondant
    
    # Contraintes et affinités
    constraints: List[str]  # Limites, quand NE PAS l'utiliser
    synergies: List[str]  # Modes qui fonctionnent bien avec
    conflicts: List[str]  # Modes incompatibles
    
    # Écosystème
    related_modes: List[str]  # Modes similaires/connexes
    prerequisites: List[str]  # Modes à utiliser avant
    follow_up: List[str]  # Modes à utiliser après
    
    # Sémantique
    keywords: List[str]  # Mots-clés pour recherche
    semantic_field: List[str]  # Champ sémantique
    tags: List[str]  # Tags libres
    
    # Capacités
    skills: List[str]  # Compétences activées
    outputs: List[str]  # Types de résultats produits
    
    # Texte pour embedding
    description: str  # Description longue pour vectorisation
    
    def to_document(self) -> Dict[str, Any]:
        """Convertit en document pour Zvec"""
        return {
            "id": f"prism_{self.mode}",
            "text": self.description,  # Pour l'embedding
            "metadata": {
                "mode": self.mode,
                "name": self.name,
                "category": self.category,
                "essence": self.essence,
                "purpose": self.purpose,
                "dimensions": self.dimensions,
                "depth": self.depth,
                "granularity": self.granularity,
                "complexity": self.complexity,
                "contexts": self.contexts,
                "situations": self.situations,
                "keywords": self.keywords,
                "tags": self.tags,
            }
        }


# ═══════════════════════════════════════════════════════════════════
# BASE DE CONNAISSANCE DES PRISMES
# ═══════════════════════════════════════════════════════════════════

PRISM_KNOWLEDGE_BASE = [
    # PRISMES SURFACE - COGNITIFS
    PrismMetadata(
        mode="natural",
        name="Naturel/Intuitif",
        category="cognitive_surface",
        essence="Réflexion organique, fluide, basée sur l'intuition et le sens",
        purpose="Obtenir une première impression authentique et holistique",
        philosophy="L'intuition première contient souvent la vérité essentielle",
        dimensions=["cognitive", "emotional"],
        use_cases=["Première impression", "Diagnostic rapide", "Feeling check"],
        contexts=["Exploration", "Brainstorming", "Crise initiale"],
        situations=["Bug mystérieux", "Décision à prendre vite", "Ambiance équipe"],
        depth="surface",
        granularity="macro",
        complexity="simple",
        analogies=["Comme le premier regard d'un médecin", "Instinct de survie"],
        metaphors=["Ruisseau qui trouve son chemin naturellement"],
        archetype="L'Enfant",
        constraints=["Ne pas remplacer l'analyse approfondie"],
        synergies=["scientific", "wisdom", "challenger"],
        conflicts=["disciplined", "step_by_step"],
        related_modes=["wisdom", "creative"],
        prerequisites=[],
        follow_up=["scientific", "5whys"],
        keywords=["intuition", "naturel", "organique", "flux", "feeling"],
        semantic_field=["instinct", "intuitif", "spontané", "authentique"],
        tags=["rapide", "holistique", "primaire"],
        skills=["perception", "sensibilité", "intuition"],
        outputs=["impression", "direction", "ressenti"],
        description="Mode natural: réflexion fluide et intuitive. Capture l'essence d'une situation par l'intuition et le sens global. Parfait pour les premières impressions et le diagnostic rapide. Fonctionne comme un radar émotionnel et cognitif qui détecte les patterns naturels."
    ),
    
    PrismMetadata(
        mode="challenger",
        name="Challenger/Critique",
        category="cognitive_surface",
        essence="Esprit critique qui remet en question, teste la solidité",
        purpose="Identifier les failles, contradictions et angles morts",
        philosophy="Ce qui ne résiste pas à la critique ne mérite pas d'exister",
        dimensions=["cognitive", "strategic"],
        use_cases=["Validation d'idée", "Test de robustesse", "Audit rapide"],
        contexts=["Revue de code", "Planification", "Prise de décision"],
        situations=["Trop beau pour être vrai", "Consensus trop facile", "Avant lancement"],
        depth="surface",
        granularity="macro",
        complexity="moderate",
        analogies=["Comme un avocat du diable", "Éprouvette qui teste"],
        metaphors=["Épée qui tranche les illusions"],
        archetype="Le Rebelle",
        constraints=["Peut devenir négatif excessif", "Ralentir la créativité"],
        synergies=["objective_critic", "scientific", "security"],
        conflicts=["optimist", "creative", "caring"],
        related_modes=["objective_critic", "auditor"],
        prerequisites=[],
        follow_up=["scientific", "objective_critic"],
        keywords=["critique", "challenger", "test", "failles", "robustesse"],
        semantic_field=["doute", "scepticisme", "validation", "épreuve"],
        tags=["testeur", "gardien", "protecteur"],
        skills=["analyse critique", "détection failles", "questionnement"],
        outputs=["risques identifiés", "failles", "questions clés"],
        description="Mode challenger: esprit critique et testeur. Remet en question les idées pour en tester la solidité. Identifie les angles morts, contradictions et hypothèses non testées. Indispensable avant tout lancement important."
    ),
    
    PrismMetadata(
        mode="scientific",
        name="Scientifique/Méthode",
        category="cognitive_surface",
        essence="Approche méthodique, hypothèses, preuves, expérimentation",
        purpose="Comprendre causalement, prouver, valider avec rigueur",
        philosophy="Toute affirmation doit être testable et testée",
        dimensions=["cognitive", "technical"],
        use_cases=["Investigation", "Résolution problème", "Validation"],
        contexts=["Debugging", "Recherche", "Analyse cause-racine"],
        situations=["Problème récurrent", "Cause inconnue", "Nécessité de preuves"],
        depth="surface",
        granularity="macro",
        complexity="moderate",
        analogies=["Comme un détective Sherlock Holmes", "Méthode Descartes"],
        metaphors=["Loupe qui révèle les détails cachés"],
        archetype="Le Chercheur",
        constraints=["Peut être lent", "Nécessite données"],
        synergies=["5whys", "objective_critic", "auditor"],
        conflicts=["creative", "divine", "magic"],
        related_modes=["5whys", "objective_critic"],
        prerequisites=[],
        follow_up=["auditor", "architect"],
        keywords=["scientifique", "méthode", "preuves", "hypothèses", "test"],
        semantic_field=["rigueur", "analyse", "causalité", "vérité"],
        tags=["rigoureux", "factuel", "analytique"],
        skills=["analyse causale", "expérimentation", "validation"],
        outputs=["faits établis", "hypothèses testées", "preuves"],
        description="Mode scientific: approche méthodique et factuelle. Formule des hypothèses, conçoit des expériences, analyse les preuves. Recherche la vérité causale derrière les symptômes. Essentiel pour la résolution rigoureuse de problèmes."
    ),
    
    # PRISMES ÉSOTÉRIQUES
    PrismMetadata(
        mode="divine",
        name="Divin/Omniscient",
        category="esoteric_deep",
        essence="Perspective d'ensemble, sagesse universelle, transcendance",
        purpose="Accéder à la vision d'ensemble et aux vérités éternelles",
        philosophy="Du point de vue de l'éternité, tout s'organise différemment",
        dimensions=["esoteric", "strategic"],
        use_cases=["Vision long terme", "Sens de la vie", "Transformation"],
        contexts=["Crise existentielle", "Recherche sens", "Changement fondamental"],
        situations=["Pourquoi faire tout cela ?", "Quel est mon but ?", "Désespoir/Renaissance"],
        depth="esoteric",
        granularity="micro",
        complexity="wicked",
        analogies=["Comme la vue d'un aigle", "Perspective d'Einstein sur l'univers"],
        metaphors=["Montagne sacrée où tout devient clair"],
        archetype="Le Sage/La Déesse",
        constraints=["Abstrait", "Difficile à traduire en action concrète"],
        synergies=["wisdom", "meditation", "infinite_knowledge"],
        conflicts=["scientific", "auditor", "objective_critic"],
        related_modes=["wisdom", "wise", "infinite_knowledge"],
        prerequisites=["meditation", "wisdom"],
        follow_up=["architect", "fondateur"],
        keywords=["divin", "omniscient", "universel", "transcendant", "éternel"],
        semantic_field=["sacré", "infini", "absolu", "essence", " vérité ultime"],
        tags=["spirituel", "transformationnel", "visionnaire"],
        skills=["intuition cosmique", "sagesse", "vision transcendantale"],
        outputs=["vérité profonde", "direction de vie", "transformation"],
        description="Mode divine: perspective omnisciente et universelle. Contemple la situation depuis une hauteur spirituelle, révélant les patterns cachés et les vérités éternelles. Pour les questions de sens, de vocation, de transformation fondamentale."
    ),
    
    PrismMetadata(
        mode="meditation",
        name="Méditation/Présence",
        category="esoteric_practice",
        essence="Pleine conscience, observation sans jugement, silence intérieur",
        purpose="Créer l'espace intérieur pour la clarté et l'intuition",
        philosophy="Dans le silence, la vérité se révèle",
        dimensions=["esoteric", "emotional"],
        use_cases=[["Clarté mentale", "Calme", "Intuition"]],
        contexts=[["Stress", "Confusion", "Décision importante"]],
        situations=[["Trop d'informations", "Besoin de recul", "Chaos mental"]],
        depth="esoteric",
        granularity="micro",
        complexity="simple",
        analogies=["Comme un lac calme qui reflète", "Miroir pur"],
        metaphors=["Silence d'une forêt", "Espace vide qui contient tout"],
        archetype="Le Moine/La Nonne",
        constraints=["Nécessite pratique", "Peut sembler passif"],
        synergies=["divine", "wisdom", "focus", "yin"],
        conflicts=["challenger", "experimental", "disciplined"],
        related_modes=["focus", "attention", "yin"],
        prerequisites=[],
        follow_up=["divine", "wisdom", "natural"],
        keywords=["méditation", "présence", "conscience", "silence", "calme"],
        semantic_field=["pleine conscience", "observation", "recueillement", "paix"],
        tags=["présent", "conscient", "intérieur"],
        skills=[["observation", "présence", "lâcher prise"]],
        outputs=[["clarté", "calme", "intuition"]],
        description="Mode meditation: pleine conscience et présence. Crée un espace intérieur de calme et d'observation sans jugement. Permet à la vérité de remonter à la surface. Essentiel avant toute décision importante ou en situation de stress."
    ),
    
    # PRISMES TECHNIQUES
    PrismMetadata(
        mode="architect",
        name="Architecte/Système",
        category="technical_intermediate",
        essence="Vue d'ensemble, structure, composants, interactions",
        purpose="Concevoir et comprendre les systèmes complexes",
        philosophy="Tout système est plus que la somme de ses parties",
        dimensions=["technical", "strategic"],
        use_cases=["Design système", "Refactoring", "Scaling"],
        contexts=["Architecture logicielle", "Infrastructure", "Organisation"],
        situations=["Complexité croissante", "Nouveau projet", "Dette technique"],
        depth="intermediate",
        granularity="meso",
        complexity="complex",
        analogies=["Comme un architecte de bâtiments", "Urbaniste"],
        metaphors=["Plan d'une cathédrale", "Échiquier stratégique"],
        archetype="Le Bâtisseur",
        constraints=["Abstrait", "Nécessite vision long terme"],
        synergies=["developer", "nasa", "alignment"],
        conflicts=["mvp", "experimental"],
        related_modes=["developer", "nasa", "singleton"],
        prerequisites=[],
        follow_up=["developer", "devops", "nasa"],
        keywords=["architecture", "système", "structure", "design", "patterns"],
        semantic_field=["conception", "organisation", "modules", "interfaces"],
        tags=["visionnaire", "structuré", "holistique"],
        skills=["design système", "abstraction", "modélisation"],
        outputs=["architecture", "structure", "patterns", "interfaces"],
        description="Mode architect: conception et compréhension systémique. Analyse les composants, leurs interactions, et l'organisation globale. Pour concevoir des systèmes scalables et maintenables. Voir la forêt ET les arbres."
    ),
    
    PrismMetadata(
        mode="nasa",
        name="NASA/Rigueur",
        category="technical_deep",
        essence="Rigueur spatiale, redondance, sécurité, checklists",
        purpose="Assurer la fiabilité absolue face aux risques critiques",
        philosophy="Un seul point de défaillance peut tout détruire",
        dimensions=["technical", "strategic"],
        use_cases=["Mission critique", "Sécurité", "Fiabilité"],
        contexts=["Production", "Espace", "Médical", "Finance"],
        situations=[["Vies en danger", "Perte massive", "Irreversible"]],
        depth="deep",
        granularity="micro",
        complexity="complex",
        analogies=["Comme un ingénieur spatial", "Pilote d'avion"],
        metaphors=["Cadenas multiples", "Filet de sécurité"],
        archetype="Le Gardien",
        constraints=["Lourd", "Coûteux", "Peut ralentir"],
        synergies=["security", "auditor", "perfectionist"],
        conflicts=["mvp", "experimental", "creative"],
        related_modes=["security", "auditor", "perfectionist"],
        prerequisites=[],
        follow_up=["auditor", "certifier"],
        keywords=["nasa", "rigueur", "sécurité", "fiabilité", "redondance"],
        semantic_field=[["critique", "mission", "checklist", "procédure"]],
        tags=["critique", "sûr", "rigoureux"],
        skills=["analyse risque", "redondance", "procédures"],
        outputs=["checklists", "points de contrôle", "plans de secours"],
        description="Mode nasa: rigueur spatiale et fiabilité absolue. Analyse les points de défaillance, établit des redondances, crée des checklists. Pour les situations où l'erreur est inacceptable. Pas de place pour l'improvisation."
    ),
    
    # PRISMES BUSINESS
    PrismMetadata(
        mode="fondateur",
        name="Fondateur/Vision",
        category="business_intermediate",
        essence="Vision long terme, culture, impact, scalabilité",
        purpose="Construire quelque chose qui dure et transforme",
        philosophy="Les grandes visions demandent du temps et de la persévérance",
        dimensions=["strategic", "social"],
        use_cases=["Startup", "Vision", "Culture", "Legacy"],
        contexts=["Fondation", "Croissance", "Transformation"],
        situations=["Quelle vision à 10 ans ?", "Culture d'entreprise", "Impact durable"],
        depth="intermediate",
        granularity="meso",
        complexity="complex",
        analogies=["Comme un capitaine de navire", "Père fondateur"],
        metaphors=["Graines qui deviennent forêt", "Pont vers l'avenir"],
        archetype="Le Père/Mère Fondateur",
        constraints=["Long terme", "Difficile à mesurer court terme"],
        synergies=["investor", "architect", "alignment"],
        conflicts=["auditor", "objective_critic"],
        related_modes=["investor", "creator", "mvp"],
        prerequisites=["alignment"],
        follow_up=["architect", "investor"],
        keywords=["fondateur", "vision", "long terme", "culture", "legacy"],
        semantic_field=["entreprise", "mission", "impact", "durable"],
        tags=["visionnaire", "bâtisseur", "leader"],
        skills=["vision", "culture", "persévérance"],
        outputs=["vision", "valeurs", "culture", "stratégie long terme"],
        description="Mode fondateur: vision long terme et construction durable. Pense en décennies, pas en trimestres. Crée la culture, les valeurs, et l'impact transformationnel. Pour les entrepreneurs qui veulent changer le monde."
    ),
    
    PrismMetadata(
        mode="smart",
        name="Smart/Efficace",
        category="cognitive_surface",
        essence="Intelligence optimale, 80/20, solutions élégantes",
        purpose="Maximum résultat avec minimum d'effort",
        philosophy="Travailler intelligemment, pas durement",
        dimensions=["cognitive", "strategic"],
        use_cases=["Optimisation", "Efficacité", "Productivité"],
        contexts=["Routine", "Processus", "Automatisation"],
        situations=["Trop de travail", "Répétitif", "Complexité inutile"],
        depth="surface",
        granularity="macro",
        complexity="simple",
        analogies=["Comme un artisan efficace", "Programmeur paresseux"],
        metaphors=["Raccourci de montagne", "Clé passe-partout"],
        archetype="L'Artisan Malin",
        constraints=["Peut sacrifier la qualité", "Biais de facilité"],
        synergies=["pareto", "agile", "mvp"],
        conflicts=["perfectionist", "nasa", "disciplined"],
        related_modes=["pareto", "agile", "eisenhower"],
        prerequisites=[],
        follow_up=["pareto", "agile"],
        keywords=["smart", "intelligent", "efficace", "80/20", "optimal"],
        semantic_field=["optimisation", "productivité", "simplicité", "raccourci"],
        tags=["malin", "rapide", "pragmatique"],
        skills=["optimisation", "simplification", "automatisation"],
        outputs=["solution élégante", "raccourci", "gain de temps"],
        description="Mode smart: intelligence et efficacité optimale. Trouve les solutions les plus élégantes avec le minimum d'effort. Applique le principe 80/20. Pour ceux qui veulent travailler moins mais mieux."
    ),
]


def get_prism_metadata(mode: str) -> Optional[PrismMetadata]:
    """Récupère les métadonnées d'un prisme"""
    for prism in PRISM_KNOWLEDGE_BASE:
        if prism.mode == mode:
            return prism
    return None


def find_prisms_by_context(
    context_description: str,
    depth_preference: Optional[str] = None
) -> List[PrismMetadata]:
    """
    Trouve les prismes pertinents pour un contexte donné.
    
    Cette fonction serait remplacée par une recherche vectorielle Zvec
    dans l'implémentation complète.
    """
    context_lower = context_description.lower()
    matches = []
    
    for prism in PRISM_KNOWLEDGE_BASE:
        score = 0
        
        # Match sur situations
        for situation in prism.situations:
            if any(word in context_lower for word in situation.lower().split()):
                score += 3
        
        # Match sur keywords
        for keyword in prism.keywords:
            if keyword in context_lower:
                score += 2
        
        # Match sur contexts
        for ctx in prism.contexts:
            if any(word in context_lower for word in ctx.lower().split()):
                score += 2
        
        # Filtre sur profondeur
        if depth_preference and prism.depth != depth_preference:
            score *= 0.5
        
        if score > 0:
            matches.append((prism, score))
    
    # Trier par score
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return [m[0] for m in matches[:5]]


def index_prisms_to_zvec(collection_name: str = "jiminy_prisms"):
    """
    Indexe tous les prismes dans Zvec pour recherche sémantique.
    
    À exécuter une fois pour créer la collection.
    """
    documents = []
    for prism in PRISM_KNOWLEDGE_BASE:
        doc = prism.to_document()
        documents.append({
            "id": doc["id"],
            "text": doc["text"],
            "metadata": doc["metadata"]
        })
    
    # Ici, on appellerait Zvec pour indexer
    # mcp4_add_documents(collection=collection_name, documents=documents)
    
    print(f"📚 {len(documents)} prismes indexés dans Zvec")
    return documents


if __name__ == "__main__":
    # Démonstration
    print("="*70)
    print("📚 JIMINY VECTOR MEMORY - BASE DE CONNAISSANCE")
    print("="*70)
    
    print(f"\n📊 {len(PRISM_KNOWLEDGE_BASE)} prismes documentés")
    
    # Exemple de recherche
    print("\n" + "="*70)
    print("🔍 RECHERCHE: 'bug production serveur qui plante'")
    print("="*70)
    
    results = find_prisms_by_context("bug production serveur qui plante")
    for i, prism in enumerate(results, 1):
        print(f"\n{i}. 🎯 {prism.name.upper()} (score: contexte)")
        print(f"   Essence: {prism.essence}")
        print(f"   Profondeur: {prism.depth} | Granularité: {prism.granularity}")
        print(f"   Tags: {', '.join(prism.tags[:3])}")
        print(f"   Synergies: {', '.join(prism.synergies[:2])}")
    
    print("\n" + "="*70)
    print("💡 AVEC ZVEC: Recherche vectorielle pour trouver")
    print("   les modes les plus pertinents sémantiquement")
    print("="*70)
