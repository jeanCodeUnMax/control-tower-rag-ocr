#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JIMINY PRISMS - Modes de réflexion multidimensionnels (75 PRISMES)

Extension du Jiminy Cricket avec 75 modes de réflexion :

PROFESSIONNELS:
- natural, challenger, scientific, wisdom, philosophical
- optimist, pessimist, experimental, disciplined, step_by_step
- creative, caring, alignment, investor, creator, user, developer

ÉTHIQUES:
- ethical, just, moral, arbitrary

ÉSOTÉRIQUES:
- cabal, wise, divine, magic, esoteric

ÉQUILIBRE & HARMONIE:
- yin (Réceptivité)
- yang (Action/manifestation)
- fengshui (Harmonisation énergétique)
- chakra (Centres énergétiques)
- vibration (Fréquences/résonance)

PRATIQUES ESOTÉRIQUES:
- meditation (Pleine conscience)
- hypnosis (Inconscient/transe)
- infinite_knowledge (Omniscience)

CONCENTRATION & ATTENTION:
- focus (Concentration laser)
- attention (Intérêt/vigilance)

ANCESTRAUX/MYTHOLOGIQUES:
- ancestral, celtic, olympus, nature, gaia

DIVINITÉS ORIENTALES:
- shiva, durga

ENSEIGNEMENT/APPRENTISSAGE:
- assistant, professor, student, disciple, foreman, sensei

RÈGLES DE VIE & MÉTHODES:
- nasa (Rigueur spatiale)
- 5s (Méthode japonaise)
- pareto (80/20)
- eisenhower (Matrice priorité)
- 5whys (5 Pourquoi)
- pomodoro (Focus cycles)
- todo (Gestion tâches)
- kanban (Flux visuel)

PARADIGMES DÉVELOPPEUR:
- frontend (UX/UI)
- backend (Scalabilité)
- devops (Automatisation)
- agile (Itération)
- singleton (Design Patterns)

CRÉATIVITÉ & VISION:
- writer (Écrivain/structure)
- wiifm (Bénéfice personnel)
- machine_vision (Vision ordinateur)
- ai_vision (Vision IA/ML)

PROFESSIONNELS SPÉCIALISÉS:
- architect (Architecte système)
- security (Expert sécurité)
- economist (Économiste)
- lawyer (Avocat/juridique)
- psychologist (Psychologue)

CRÉATIVITÉ ENTREPRENEURIALE:
- createur (Artiste/esthétique)
- inventeur (Innovation/brevets)
- fondateur (Startup/vision long terme)
- mvp (Minimum Viable Product)
- perfectionist (Excellence/standards)
- smart (Intelligence optimale/efficacité)

PRODUCTIVITÉ & DÉVELOPPEMENT PERSONNEL:
- ikigai (Raison d'être/passion)

MARKETING & INFLUENCE:
- marketeur (Cialdini, tunnels de vente, conversion)

VALIDATION & CERTIFICATION:
- objective_critic (Critique factuelle)
- auditor (Audit/contrôle qualité)
- manifesto (Manifeste/déclaration)
- certifier (Certification/validation)

Usage:
    from jiminy_prisms import PrismReflection
    prism = PrismReflection(mode="fondateur")
    result = await prism.reflect(context)
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from jiminy_cricket import JiminyCricket, CricketConfig


@dataclass
class PrismResult:
    """Résultat d'une réflexion en mode prisme"""
    mode: str
    insight: str
    recommendations: List[str]
    confidence: float
    metadata: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "mode": self.mode,
            "insight": self.insight,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class PrismReflection:
    """
    Système de prismes de réflexion multidimensionnels.
    
    Chaque "prisme" est un mode de pensée différent qui regarde
    la même situation sous un angle particulier.
    """
    
    AVAILABLE_PRISMS = [
        # Modes originaux
        "natural",        # Réflexion organique/intuitive
        "challenger",     # Esprit critique
        "scientific",     # Méthode scientifique
        "wisdom",         # Sagesse/expérience
        "philosophical",  # Questionnement profond
        "optimist",       # Vision constructive
        "pessimist",      # Préparation au pire
        "experimental",   # Exploration/test
        "disciplined",    # Rigueur procédurière
        "step_by_step",   # Décomposition atomique
        "creative",       # Pensée latérale
        "caring",         # Bienveillance
        # Modes perspectives
        "alignment",      # Alignement systémique
        "investor",       # Perspective investisseur
        "creator",        # Perspective créateur
        "user",           # Perspective utilisateur
        "developer",      # Perspective développeur
        # Modes éthiques/juridiques
        "ethical",        # Perspective éthique
        "just",           # Justice/équité
        "moral",          # Morale/vertus
        "arbitrary",      # Choix arbitraire/libre
        # Modes ésotériques/spirituels
        "cabal",          # Sens caché/occulte
        "wise",           # Sagesse universelle
        "divine",         # Perspective divine
        "magic",          # Transformation/magie
        "esoteric",       # Connaissance secrète
        # Modes équilibre et harmonie
        "yin",            # Réceptivité/passivité créatrice
        "yang",           # Action/manifestation
        "fengshui",       # Harmonisation énergétique
        "chakra",         # Centres énergétiques
        "vibration",      # Fréquences et résonance
        # Modes pratiques ésotériques
        "meditation",     # Pleine conscience/présence
        "hypnosis",       # Inconscient et transe
        "infinite_knowledge", # Omniscience/connaissance infinie
        # Modes concentration et attention
        "focus",          # Concentration laser
        "attention",      # Intérêt et vigilance
        # Modes ancestraux/traditions
        "ancestral",      # Sagesse ancestrale
        "celtic",         # Sagesse druidique
        "olympus",        # Dieux Olympe/mythologie
        "nature",         # Esprits nature/forêt
        "gaia",           # Conscience terrestre
        # Modes divinités orientales
        "shiva",          # Destruction créatrice
        "durga",          # Force protectrice
        # Modes enseignement/apprentissage
        "assistant",      # Support et aide
        "professor",      # Enseigner et transmettre
        "student",        # Apprendre et questionner
        "disciple",       # Dédication et pratique
        "foreman",        # Supervision terrain
        "sensei",         # Maîtrise et perfectionnement
        # Modes règles de vie NASA et paradigmes
        "nasa",           # Rigueur spatiale NASA
        # Modes paradigmes développeur
        "frontend",       # Perspective frontend/UX
        "backend",        # Perspective backend/scalabilité
        "devops",         # Perspective DevOps/automatisation
        "agile",          # Perspective Agile/itération
        "singleton",      # Design Patterns/SOLID
        # Modes méthodes de productivité
        "5s",             # Méthode 5S japonaise
        "pareto",         # 80/20 Pareto
        "eisenhower",     # Matrice Eisenhower
        "5whys",          # 5 Pourquoi
        "pomodoro",       # Technique Pomodoro
        "todo",           # Gestion liste TODO
        "kanban",         # Méthode Kanban
        "ikigai",         # Raison d'être/passion
        # Modes créativité et vision
        "writer",         # Écrivain/structure narrative
        "wiifm",          # What's In It For Me (bénéfice perso)
        "machine_vision", # Vision par ordinateur
        "ai_vision",      # Vision IA/ML
        # Modes professionnels additionnels
        "architect",      # Architecte système
        "security",       # Expert sécurité
        "economist",      # Économiste/analyse marché
        "lawyer",         # Avocat/juridique
        "psychologist",   # Psychologue/comportement
        # Modes créativité entrepreneuriale
        "createur",       # Artiste/esthétique/créatif
        "inventeur",      # Innovation/brevets/nouveauté
        "fondateur",      # Startup/vision long terme
        "mvp",            # Minimum Viable Product/Lean
        "perfectionist",  # Excellence/standards élevés
        "smart",          # Intelligence optimale/efficacité
        # Modes marketing et influence
        "marketeur",      # Marketing/influence/tunnel de vente
        # Modes validation et certification
        "objective_critic", # Critique objective/faits
        "auditor",        # Audit/contrôle qualité
        "manifesto",      # Manifeste/déclaration forte
        "certifier",      # Certification/validation
    ]
    
    def __init__(self, mode: str = "natural", config: Optional[CricketConfig] = None):
        """
        Initialise un prisme de réflexion.
        
        Args:
            mode: Le mode de réflexion (voir AVAILABLE_PRISMS)
            config: Configuration optionnelle
        """
        if mode not in self.AVAILABLE_PRISMS:
            raise ValueError(f"Mode '{mode}' inconnu. Modes disponibles: {self.AVAILABLE_PRISMS}")
        
        self.mode = mode
        self.base_cricket = JiminyCricket(config)
        self._prompts_loaded = False
        
    async def __aenter__(self):
        await self.base_cricket.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.base_cricket.__aexit__(exc_type, exc_val, exc_tb)
    
    async def reflect(self, context: Dict[str, Any], max_retries: int = 1) -> Optional[PrismResult]:
        """
        Effectue une réflexion selon le mode actuel avec retry.
        
        Args:
            context: Le contexte de la situation à analyser
            max_retries: Nombre de tentatives supplémentaires en cas d'échec
            
        Returns:
            PrismResult avec l'insight du mode
        """
        if not await self.base_cricket.client.is_available():
            return None
        
        # Charger le prompt spécifique au mode
        prompt_template = self.base_cricket._load_prompt(f"mode_{self.mode}")
        
        # Préparer le contexte
        context_json = json.dumps(context, indent=2, ensure_ascii=False)
        prompt = prompt_template.replace("{{context}}", context_json)
        
        # System prompt renforcé
        system_prompt = (
            f"Tu es Jiminy Cricket en mode {self.mode.upper()}. "
            f"Réponds UNIQUEMENT en JSON valide avec les champs: "
            f'"insight" (string), "confidence" (number 0-1), "recommendations" (array). '
            f"Pas de texte avant ou après le JSON."
        )
        
        # Tentatives avec retry
        for attempt in range(max_retries + 1):
            response = await self.base_cricket.client.generate(
                model=self.base_cricket.config.model_cricket,
                prompt=prompt,
                system=system_prompt
            )
            
            if not response:
                if attempt < max_retries:
                    continue
                return None
            
            # Parser la réponse
            try:
                json_start = response.find("{")
                json_end = response.rfind("}")
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(response[json_start:json_end+1])
                else:
                    data = json.loads(response)
                
                # Extraire et valider
                result = self._parse_prism_result(data)
                if result:
                    return result
                elif attempt < max_retries:
                    print(f"⚠️ Mode {self.mode}: parsing incomplet, retry {attempt + 1}/{max_retries}")
                    continue
                    
            except json.JSONDecodeError as e:
                if attempt < max_retries:
                    print(f"⚠️ Mode {self.mode}: JSON invalide, retry {attempt + 1}/{max_retries}")
                    continue
                print(f"❌ JSON invalide en mode {self.mode} après {max_retries + 1} tentatives: {e}")
                return None
        
        return None
    
    def _parse_prism_result(self, data: Dict) -> Optional[PrismResult]:
        """Parse le résultat selon le mode avec validation robuste"""
        
        # Champ requis: insight - chercher dans plusieurs champs possibles
        insight = (
            data.get("insight") or 
            data.get("key_finding") or 
            data.get("essence") or
            data.get("testable_hypothesis") or
            data.get("best_case_scenario") or
            data.get("worst_case_scenario") or
            data.get("natural_path") or
            data.get("gentlest_approach") or
            # Nouveaux champs des modes étendus
            data.get("vision") or
            data.get("user_need") or
            data.get("technical_debt") or
            data.get("roi_estimate") or
            data.get("ethical_framework") or
            data.get("justice_principle") or
            data.get("moral_duty") or
            data.get("unconstrained_choice") or
            data.get("hidden_meaning") or
            data.get("eternal_truth") or
            data.get("divine_will") or
            data.get("pure_intention") or
            data.get("hermetic_principle") or
            data.get("ancestral_wisdom") or
            data.get("sacred_tree") or
            data.get("archetype") or
            data.get("elemental_spirit") or
            data.get("ecosystem_impact") or
            data.get("to_destroy") or
            data.get("demon_to_fight") or
            # Modes équilibre et harmonie (Yin/Yang/Feng Shui)
            data.get("receptivity") or
            data.get("latent_potential") or
            data.get("intuition") or
            data.get("action") or
            data.get("manifestation") or
            data.get("force") or
            data.get("chi_flow") or
            data.get("blockages") or
            data.get("harmonization") or
            # Modes chakra et vibration
            data.get("chakra") or
            data.get("energy_state") or
            data.get("frequency") or
            data.get("resonance") or
            # Modes pratiques ésotériques
            data.get("observation") or
            data.get("presence") or
            data.get("subconscious") or
            data.get("suggestion") or
            data.get("metaphor") or
            data.get("universal_truth") or
            data.get("eternal_wisdom") or
            data.get("cosmic_perspective") or
            # Modes concentration et attention
            data.get("focal_point") or
            data.get("interest") or
            data.get("vigilance") or
            # Modes enseignement
            data.get("support_needed") or
            data.get("lesson") or
            data.get("question_to_ask") or
            data.get("practice") or
            data.get("field_reality") or
            data.get("lesson_taught") or
            # Modes NASA et paradigmes
            data.get("spof_identified") or
            data.get("redundancy_needed") or
            data.get("ux_impact") or
            data.get("performance_perceived") or
            data.get("scalability_concern") or
            data.get("data_integrity") or
            data.get("automation_needed") or
            data.get("cicd_stage") or
            data.get("mvp_identified") or
            data.get("pattern_applied") or
            # Modes méthodes productivité
            data.get("seiri_action") or
            data.get("vital_few") or
            data.get("quadrant") or
            data.get("root_cause") or
            data.get("pomodoro_estimate") or
            data.get("next_action") or
            data.get("kanban_column") or
            data.get("bottleneck") or
            # Modes créativité et vision
            data.get("narrative_arc") or
            data.get("hook") or
            data.get("personal_benefit") or
            data.get("tangible_gain") or
            data.get("features_detected") or
            data.get("algorithm_suggested") or
            data.get("pattern_detected") or
            data.get("model_suggested") or
            # Modes professionnels additionnels
            data.get("system_view") or
            data.get("components") or
            data.get("tradeoffs") or
            data.get("threats") or
            data.get("vulnerabilities") or
            data.get("cost_benefit") or
            data.get("roi") or
            data.get("legal_risks") or
            data.get("compliance") or
            data.get("behavior") or
            data.get("motivation") or
            # Modes validation et certification
            data.get("facts_verified") or
            data.get("biases_identified") or
            data.get("unproven_assumptions") or
            data.get("gaps_found") or
            data.get("non_conformities") or
            data.get("principles") or
            data.get("declaration") or
            data.get("call_to_action") or
            data.get("criteria_met") or
            data.get("certification_level") or
            # Modes créativité entrepreneuriale
            data.get("artistic_vision") or
            data.get("aesthetic_direction") or
            data.get("invention") or
            data.get("novelty") or
            data.get("long_term_vision") or
            data.get("culture") or
            data.get("scalability") or
            data.get("impact") or
            # Modes productivité et méthodes (Ikigai, MVP)
            data.get("passion") or
            data.get("mission") or
            data.get("vocation") or
            data.get("profession") or
            data.get("core_feature") or
            data.get("hypothesis_test") or
            data.get("metric") or
            # Modes excellence
            data.get("flaws") or
            data.get("standards") or
            data.get("improvements") or
            # Modes excellence et intelligence (SMART)
            data.get("smart_solution") or
            data.get("shortcut") or
            data.get("specific") or
            data.get("measurable") or
            data.get("achievable") or
            data.get("relevant") or
            data.get("time_bound") or
            # Modes marketing et influence
            data.get("influence_principle") or
            data.get("cognitive_bias_used") or
            data.get("funnel_stage") or
            data.get("conversion_action") or
            ""
        )
        
        # Si aucun insight trouvé, c'est un échec
        if not insight or insight.strip() == "":
            print(f"⚠️ Mode {self.mode}: aucun insight trouvé dans la réponse")
            return None
        
        # Confidence avec validation
        confidence = data.get("confidence", 0.5)
        try:
            confidence = float(confidence)
            if confidence < 0 or confidence > 1:
                confidence = 0.5
        except (TypeError, ValueError):
            confidence = 0.5
        
        # Recommandations - chercher dans plusieurs champs
        recommendations = []
        if "recommendations" in data and isinstance(data["recommendations"], list):
            recommendations = [r for r in data["recommendations"] if r]
        elif "recommended_next_step" in data and data["recommended_next_step"]:
            recommendations = [data["recommended_next_step"]]
        elif "best_action" in data and data["best_action"]:
            recommendations = [data["best_action"]]
        elif "elegant_solution" in data and data["elegant_solution"]:
            recommendations = [data["elegant_solution"]]
        elif "mvp_probe" in data and data["mvp_probe"]:
            recommendations = [data["mvp_probe"]]
        # Nouveaux champs pour les recommandations
        elif "architecture_suggestion" in data and data["architecture_suggestion"]:
            recommendations = [data["architecture_suggestion"]]
        elif "creative_intent" in data and data["creative_intent"]:
            recommendations = [data["creative_intent"]]
        elif "spiritual_lesson" in data and data["spiritual_lesson"]:
            recommendations = [data["spiritual_lesson"]]
        elif "transformation" in data and data["transformation"]:
            recommendations = [data["transformation"]]
        # Modes enseignement
        elif "teaching_method" in data and data["teaching_method"]:
            recommendations = [data["teaching_method"]]
        elif "learning_goal" in data and data["learning_goal"]:
            recommendations = [data["learning_goal"]]
        elif "discipline" in data and data["discipline"]:
            recommendations = [data["discipline"]]
        elif "supervision" in data and data["supervision"]:
            recommendations = [data["supervision"]]
        elif "do_principle" in data and data["do_principle"]:
            recommendations = [data["do_principle"]]
        # Modes équilibre et harmonie
        elif "harmonization" in data and data["harmonization"]:
            recommendations = [data["harmonization"]]
        elif "chi_flow" in data and data["chi_flow"]:
            recommendations = [data["chi_flow"]]
        elif "energy_state" in data and data["energy_state"]:
            recommendations = [data["energy_state"]]
        # Modes pratiques ésotériques
        elif "practice" in data and data["practice"]:
            recommendations = [data["practice"]]
        elif "suggestion" in data and data["suggestion"]:
            recommendations = [data["suggestion"]]
        # Modes concentration et attention
        elif "focal_point" in data and data["focal_point"]:
            recommendations = [data["focal_point"]]
        elif "selectivity" in data and data["selectivity"]:
            recommendations = [data["selectivity"]]
        # Modes NASA et paradigmes
        elif "solid_violation" in data and data["solid_violation"]:
            recommendations = [data["solid_violation"]]
        elif "priority_action" in data and data["priority_action"]:
            recommendations = [data["priority_action"]]
        elif "iteration_sprint" in data and data["iteration_sprint"]:
            recommendations = [data["iteration_sprint"]]
        # Modes méthodes productivité
        elif "task_formulation" in data and data["task_formulation"]:
            recommendations = [data["task_formulation"]]
        elif "focus_protection" in data and data["focus_protection"]:
            recommendations = [data["focus_protection"]]
        elif "backlog_item" in data and data["backlog_item"]:
            recommendations = [data["backlog_item"]]
        # Modes productivité (Ikigai)
        elif "vocation" in data and data["vocation"]:
            recommendations = [data["vocation"]]
        # Modes excellence (MVP, Perfectionist, Smart)
        elif "improvements" in data and data["improvements"]:
            recommendations = [data["improvements"]]
        elif "metric" in data and data["metric"]:
            recommendations = [data["metric"]]
        elif "smart_solution" in data and data["smart_solution"]:
            recommendations = [data["smart_solution"]]
        elif "shortcut" in data and data["shortcut"]:
            recommendations = [data["shortcut"]]
        # Modes créativité et vision
        elif "structure_template" in data and data["structure_template"]:
            recommendations = [data["structure_template"]]
        elif "intrinsic_motivation" in data and data["intrinsic_motivation"]:
            recommendations = [data["intrinsic_motivation"]]
        elif "detection_precision" in data and data["detection_precision"]:
            recommendations = [data["detection_precision"]]
        elif "architecture" in data and data["architecture"]:
            recommendations = [data["architecture"]]
        # Modes professionnels additionnels
        elif "security_controls" in data and data["security_controls"]:
            recommendations = [data["security_controls"]]
        elif "market_dynamic" in data and data["market_dynamic"]:
            recommendations = [data["market_dynamic"]]
        elif "contract_terms" in data and data["contract_terms"]:
            recommendations = [data["contract_terms"]]
        elif "cognitive_bias" in data and data["cognitive_bias"]:
            recommendations = [data["cognitive_bias"]]
        # Modes validation et certification
        elif "standards_applied" in data and data["standards_applied"]:
            recommendations = [data["standards_applied"]]
        elif "declaration" in data and data["declaration"]:
            recommendations = [data["declaration"]]
        elif "call_to_action" in data and data["call_to_action"]:
            recommendations = [data["call_to_action"]]
        elif "certification_level" in data and data["certification_level"]:
            recommendations = [data["certification_level"]]
        # Modes créativité entrepreneuriale
        elif "inspiration" in data and data["inspiration"]:
            recommendations = [data["inspiration"]]
        elif "prototype" in data and data["prototype"]:
            recommendations = [data["prototype"]]
        # Modes marketing et influence
        elif "conversion_action" in data and data["conversion_action"]:
            recommendations = [data["conversion_action"]]
        elif "funnel_stage" in data and data["funnel_stage"]:
            recommendations = [data["funnel_stage"]]
        
        return PrismResult(
            mode=self.mode,
            insight=insight[:200],  # Limiter la longueur
            recommendations=recommendations[:5],  # Max 5 recommandations
            confidence=confidence,
            metadata=data,
            timestamp=datetime.now().isoformat()
        )


class MultiPrismReflection:
    """
    Multi-prisme: combine plusieurs modes de réflexion.
    
    Fait appel à plusieurs prismes et synthétise leurs insights.
    """
    
    def __init__(self, modes: Optional[List[str]] = None, config: Optional[CricketConfig] = None):
        """
        Initialise la réflexion multi-prisme.
        
        Args:
            modes: Liste des modes à utiliser (default: ["scientific", "challenger", "creative"])
            config: Configuration optionnelle
        """
        self.modes = modes or ["scientific", "challenger", "creative"]
        self.config = config
        self.prisms: Dict[str, PrismReflection] = {}
        
    async def __aenter__(self):
        for mode in self.modes:
            self.prisms[mode] = PrismReflection(mode, self.config)
            await self.prisms[mode].__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for prism in self.prisms.values():
            await prism.__aexit__(exc_type, exc_val, exc_tb)
    
    async def reflect_all(self, context: Dict[str, Any]) -> Dict[str, PrismResult]:
        """
        Lance la réflexion sur tous les prismes en parallèle.
        
        Args:
            context: Le contexte à analyser
            
        Returns:
            Dict mapping mode -> PrismResult
        """
        import asyncio
        
        tasks = []
        for mode in self.modes:
            tasks.append(self._reflect_with_mode(mode, context))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            mode: result if not isinstance(result, Exception) else None
            for mode, result in zip(self.modes, results)
        }
    
    async def _reflect_with_mode(self, mode: str, context: Dict) -> Optional[PrismResult]:
        """Réflexion avec un mode spécifique"""
        try:
            return await self.prisms[mode].reflect(context)
        except Exception as e:
            print(f"⚠️ Erreur mode {mode}: {e}")
            return None
    
    def synthesize(self, results: Dict[str, PrismResult]) -> Dict[str, Any]:
        """
        Synthétise les résultats de plusieurs prismes.
        
        Args:
            results: Résultats par mode
            
        Returns:
            Synthèse avec consensus et divergences
        """
        valid_results = {k: v for k, v in results.items() if v is not None}
        
        if not valid_results:
            return {"error": "Aucun résultat valide"}
        
        # Extraire les insights
        insights = [r.insight for r in valid_results.values()]
        
        # Calculer le consensus (moyenne des confiances)
        avg_confidence = sum(r.confidence for r in valid_results.values()) / len(valid_results)
        
        # Regrouper les recommandations
        all_recommendations = []
        for r in valid_results.values():
            all_recommendations.extend(r.recommendations)
        
        # Détecter les divergences (écart-type des confiances)
        import statistics
        confidences = [r.confidence for r in valid_results.values()]
        std_confidence = statistics.stdev(confidences) if len(confidences) > 1 else 0
        
        return {
            "prism_count": len(valid_results),
            "modes_used": list(valid_results.keys()),
            "insights": insights,
            "synthesis": f"Consensus à {avg_confidence:.0%} de confiance "
                        f"(écart: {std_confidence:.0%})",
            "all_recommendations": list(set(all_recommendations)),
            "average_confidence": avg_confidence,
            "consensus_strength": 1 - std_confidence,  # Plus c'est proche, plus fort
            "detailed_results": {k: v.to_dict() for k, v in valid_results.items()}
        }


# Test rapide
async def test_prisms():
    """Test des prismes"""
    print("\n" + "="*70)
    print("🌈 TEST DES PRISMES DE RÉFLEXION")
    print("="*70)
    
    context = {
        "situation": "Serveur port 3002 ne répond plus",
        "symptoms": ["ECONNREFUSED", "timeout"],
        "recent_change": "express package updated",
        "urgency": "medium"
    }
    
    # Test simple prism
    print("\n1️⃣ Test d'un prisme individuel (Scientific)...")
    async with PrismReflection("scientific") as prism:
        result = await prism.reflect(context)
        if result:
            print(f"   ✅ Mode: {result.mode}")
            print(f"   💡 Insight: {result.insight[:60]}...")
            print(f"   📊 Confiance: {result.confidence:.0%}")
    
    # Test multi-prism
    print("\n2️⃣ Test multi-prisme (Challenger + Optimist + Creative)...")
    modes = ["challenger", "optimist", "creative"]
    async with MultiPrismReflection(modes) as multi:
        results = await multi.reflect_all(context)
        
        print("   Résultats par mode:")
        for mode, result in results.items():
            if result:
                print(f"   - {mode}: {result.insight[:40]}... ({result.confidence:.0%})")
        
        # Synthèse
        synthesis = multi.synthesize(results)
        print(f"\n   🎯 Synthèse: {synthesis['synthesis']}")
        print(f"   📋 Recommandations: {synthesis['all_recommendations'][:2]}")
    
    print("\n" + "="*70)
    print("✅ Tests terminés")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_prisms())
