#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JIMINY AWAKENING - Réveil et Exécution de la Conscience

Architecture:
1. SÉMANTIQUE → Analyse vectorielle pour choisir les prismes
2. RÉFLEXION → Le LLM réfléchit avec les outils sélectionnés  
3. EXÉCUTION → Script concret qui agit
4. APPRENTISSAGE → Zvec mémorise pour affiner les futures sélections

Usage:
    # Analyse (conscience)
    prisms = semantic_selector.select("mon serveur plante")
    
    # Réflexion (LLM)
    insights = await consciousness.reflect(prisms, context)
    
    # Exécution (script)
    action = await executor.run(insights)
    
    # Apprentissage (Zvec)
    await memory.learn(context, prisms, insights, action.success)
"""

import asyncio
import json
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import aiohttp


# ═══════════════════════════════════════════════════════════════════
# 1. SÉMANTIQUE - Sélection par recherche vectorielle
# ═══════════════════════════════════════════════════════════════════

class SemanticPrismSelector:
    """
    Sélectionne les prismes via recherche sémantique dans Zvec.
    
    Au lieu de règles codées en dur, on utilise la similarité vectorielle
    pour trouver les modes les plus pertinents pour une situation donnée.
    """
    
    def __init__(self, zvec_collection: str = "jiminy_prisms"):
        self.collection = zvec_collection
        self.cache = {}  # Cache des recherches récentes
        
    async def select(
        self,
        situation: str,
        depth: str = "adaptive",  # surface, intermediate, deep, esoteric, adaptive
        max_prisms: int = 5,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Sélectionne les prismes via recherche sémantique.
        
        Args:
            situation: Description de la situation
            depth: Profondeur souhaitée ou 'adaptive' pour auto-détect
            max_prisms: Nombre max de prismes à retourner
            
        Returns:
            Liste de prismes avec score de pertinence
        """
        # Check cache
        cache_key = f"{situation}:{depth}:{max_prisms}"
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Recherche vectorielle via Zvec
        # results = await mcp4_semantic_search(
        #     collection=self.collection,
        #     query=situation,
        #     limit=max_prisms * 2  # Chercher plus pour filtrer
        # )
        
        # Pour l'instant, simulation avec scoring simple
        # Dans la vraie implémentation, Zvec retourne les prismes les plus
        # proches vectoriellement de la requête
        results = self._semantic_search_simulation(situation, max_prisms * 2)
        
        # Filtrer par profondeur si spécifiée
        if depth != "adaptive":
            results = [r for r in results if r.get("depth") == depth]
        
        # Trier par score de pertinence
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Retourner les meilleurs
        selected = results[:max_prisms]
        
        # Mettre en cache
        if use_cache:
            self.cache[cache_key] = selected
        
        return selected
    
    def _semantic_search_simulation(
        self,
        situation: str,
        limit: int
    ) -> List[Dict]:
        """
        Simulation de recherche sémantique.
        À remplacer par vrai appel Zvec.
        """
        situation_lower = situation.lower()
        
        # Base de prismes avec métadonnées (simplifiée)
        prism_db = [
            {"mode": "challenger", "depth": "surface", "score": 0.0,
             "keywords": ["bug", "erreur", "problème", "test"]},
            {"mode": "scientific", "depth": "surface", "score": 0.0,
             "keywords": ["analyse", "cause", "preuve", "test"]},
            {"mode": "developer", "depth": "intermediate", "score": 0.0,
             "keywords": ["code", "développement", "programmation", "bug"]},
            {"mode": "architect", "depth": "intermediate", "score": 0.0,
             "keywords": ["système", "structure", "design", "architecture"]},
            {"mode": "nasa", "depth": "deep", "score": 0.0,
             "keywords": ["critique", "sécurité", "mission", "risque"]},
            {"mode": "security", "depth": "deep", "score": 0.0,
             "keywords": ["sécurité", "vulnérabilité", "protection", "attaque"]},
            {"mode": "divine", "depth": "esoteric", "score": 0.0,
             "keywords": ["sens", "vie", "vocation", "transformation"]},
            {"mode": "meditation", "depth": "esoteric", "score": 0.0,
             "keywords": ["calme", "présence", "intuition", "clarté"]},
        ]
        
        # Scoring simple par mots-clés
        for prism in prism_db:
            score = 0
            for keyword in prism["keywords"]:
                if keyword in situation_lower:
                    score += 1
            prism["score"] = score
        
        # Trier et filtrer
        prism_db.sort(key=lambda x: x["score"], reverse=True)
        return [p for p in prism_db if p["score"] > 0][:limit]


# ═══════════════════════════════════════════════════════════════════
# 2. RÉFLEXION - Conscience avec prismes sélectionnés
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ReflectionResult:
    """Résultat d'une réflexion prismatique"""
    mode: str
    insight: str
    confidence: float
    recommendations: List[str]
    metadata: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ConsciousnessMirror:
    """
    La conscience qui réfléchit avec les prismes sélectionnés.
    
    C'est le 'cerveau' qui utilise les outils choisis par la sémantique
    pour analyser la situation en profondeur.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.ollama_url = ollama_url
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def reflect(
        self,
        prisms: List[Dict],
        context: Dict[str, Any],
        timeout: int = 30
    ) -> List[ReflectionResult]:
        """
        Réfléchit avec les prismes sélectionnés.
        
        Pour chaque prisme, charge son prompt et interroge Ollama.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        reflections = []
        
        for prism_info in prisms:
            mode = prism_info["mode"]
            
            # Charger le prompt du prisme
            prompt = self._load_prism_prompt(mode, context)
            
            # Interroger Ollama
            try:
                result = await self._query_ollama(prompt, timeout)
                
                if result:
                    reflections.append(ReflectionResult(
                        mode=mode,
                        insight=result.get("insight", ""),
                        confidence=result.get("confidence", 0.5),
                        recommendations=result.get("recommendations", []),
                        metadata={"raw": result, "prism_info": prism_info}
                    ))
                    
            except Exception as e:
                print(f"⚠️ Erreur réflexion {mode}: {e}")
                continue
        
        return reflections
    
    def _load_prism_prompt(self, mode: str, context: Dict) -> str:
        """Charge et prépare le prompt d'un prisme"""
        # Charger depuis fichier
        prompt_path = f"prompts/mode_{mode}.txt"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            # Prompt minimal par défaut
            template = f"Tu es Jiminy Cricket en mode {mode.upper()}. Analyse et réponds en JSON avec insight, confidence, recommendations.\n\nCONTEXTE\n{{context}}"
        
        # Injecter le contexte
        context_str = json.dumps(context, indent=2, ensure_ascii=False)
        return template.replace("{{context}}", context_str)
    
    async def _query_ollama(self, prompt: str, timeout: int) -> Optional[Dict]:
        """Interroge Ollama et parse la réponse JSON"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7}
        }
        
        try:
            async with self.session.post(url, json=payload, timeout=timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response_text = data.get("response", "")
                    
                    # Extraire JSON
                    start = response_text.find('{')
                    end = response_text.rfind('}')
                    if start >= 0 and end > start:
                        return json.loads(response_text[start:end+1])
                        
        except Exception as e:
            print(f"⚠️ Erreur Ollama: {e}")
            
        return None
    
    def synthesize(self, reflections: List[ReflectionResult]) -> Dict:
        """
        Synthétise les réflexions multiples en une vision unifiée.
        """
        if not reflections:
            return {"error": "Aucune réflexion disponible"}
        
        # Agréger les insights
        all_insights = [r.insight for r in reflections if r.insight]
        
        # Moyenne de confiance
        avg_confidence = sum(r.confidence for r in reflections) / len(reflections)
        
        # Toutes recommandations
        all_recommendations = []
        for r in reflections:
            all_recommendations.extend(r.recommendations)
        
        # Déterminer la cohérence (accord entre prismes)
        coherence = self._calculate_coherence(reflections)
        
        return {
            "synthesis": {
                "key_insights": all_insights[:3],
                "average_confidence": round(avg_confidence, 2),
                "coherence": coherence,
                "actionable_recommendations": list(set(all_recommendations))[:5],
                "modes_consulted": [r.mode for r in reflections],
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _calculate_coherence(self, reflections: List[ReflectionResult]) -> str:
        """Calcule le niveau d'accord entre les prismes"""
        if len(reflections) < 2:
            return "single"
        
        # Analyse simple de similarité des recommendations
        all_recs = set()
        overlaps = 0
        
        for r in reflections:
            recs = set(r.recommendations)
            if all_recs:
                overlaps += len(all_recs & recs)
            all_recs.update(recs)
        
        if overlaps >= len(reflections):
            return "high"  # Accord fort
        elif overlaps > 0:
            return "moderate"  # Accord partiel
        else:
            return "divergent"  # Perspectives divergentes


# ═══════════════════════════════════════════════════════════════════
# 3. EXÉCUTION - Action concrète
# ═══════════════════════════════════════════════════════════════════

class ActionExecutor:
    """
    Exécuteur d'actions concrètes basé sur les réflexions.
    
    Transforme les insights en actions opérationnelles :
    - Commandes système
    - Appels API
    - Notifications
    - Logs
    """
    
    def __init__(self):
        self.actions_log = []
        self.handlers: Dict[str, Callable] = {}
        
    def register_handler(self, action_type: str, handler: Callable):
        """Enregistre un gestionnaire d'action"""
        self.handlers[action_type] = handler
    
    async def execute(
        self,
        synthesis: Dict,
        context: Dict,
        dry_run: bool = False
    ) -> Dict:
        """
        Exécute les recommandations issues de la réflexion.
        
        Args:
            synthesis: Synthèse des réflexions
            context: Contexte de la situation
            dry_run: Si True, simule sans exécuter
            
        Returns:
            Résultat de l'exécution
        """
        recommendations = synthesis.get("actionable_recommendations", [])
        
        executed = []
        failed = []
        
        for rec in recommendations:
            # Déterminer le type d'action
            action_type = self._classify_action(rec)
            
            if dry_run:
                executed.append({
                    "action": rec,
                    "type": action_type,
                    "status": "simulated",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                # Exécuter via le handler approprié
                handler = self.handlers.get(action_type)
                if handler:
                    try:
                        result = await handler(rec, context)
                        executed.append({
                            "action": rec,
                            "type": action_type,
                            "status": "success",
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as e:
                        failed.append({
                            "action": rec,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })
                else:
                    # Action par défaut: log
                    executed.append({
                        "action": rec,
                        "type": "log",
                        "status": "logged",
                        "note": "Aucun handler spécifique",
                        "timestamp": datetime.now().isoformat()
                    })
        
        result = {
            "executed": executed,
            "failed": failed,
            "success_rate": len(executed) / (len(executed) + len(failed)) if (executed or failed) else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        self.actions_log.append(result)
        return result
    
    def _classify_action(self, recommendation: str) -> str:
        """Classifie le type d'action recommandée"""
        rec_lower = recommendation.lower()
        
        if any(w in rec_lower for w in ["vérifier", "check", "tester", "ping"]):
            return "check"
        elif any(w in rec_lower for w in ["redémarrer", "restart", "reboot", "relancer"]):
            return "restart"
        elif any(w in rec_lower for w in ["alerter", "notifier", "envoyer", "mail"]):
            return "notify"
        elif any(w in rec_lower for w in ["corriger", "fix", "réparer", "modifier"]):
            return "fix"
        elif any(w in rec_lower for w in ["analyser", "investiguer", "creuser"]):
            return "analyze"
        else:
            return "log"


# ═══════════════════════════════════════════════════════════════════
# 4. APPRENTISSAGE - Mémoire évolutive
# ═══════════════════════════════════════════════════════════════════

class EvolvingMemory:
    """
    Mémoire qui apprend et évolue avec chaque interaction.
    
    Stocke dans Zvec les associations:
    - Situation → Prismes sélectionnés
    - Prismes → Qualité des insights
    - Action → Succès/Échec
    
    Permet d'affiner progressivement la sélection des prismes.
    """
    
    def __init__(self, zvec_collection: str = "jiminy_experiences"):
        self.collection = zvec_collection
        self.local_buffer = []  # Buffer avant indexation
        
    async def learn(
        self,
        situation: str,
        prisms_used: List[str],
        reflections: List[ReflectionResult],
        action_result: Dict,
        feedback: Optional[str] = None
    ):
        """
        Apprend d'une session de réflexion/action.
        
        Stocke l'expérience pour affiner les futures sélections.
        """
        # Calculer la qualité de la session
        success_rate = action_result.get("success_rate", 0)
        avg_confidence = sum(r.confidence for r in reflections) / len(reflections) if reflections else 0
        
        # Créer l'entrée d'apprentissage
        experience = {
            "id": f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "text": f"Situation: {situation}. Prismes: {', '.join(prisms_used)}. "
                    f"Résultat: {success_rate:.2f} succès. Feedback: {feedback or 'N/A'}",
            "metadata": {
                "situation": situation,
                "prisms_used": prisms_used,
                "success_rate": success_rate,
                "avg_confidence": avg_confidence,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat(),
                "effective": success_rate > 0.7 and avg_confidence > 0.6
            }
        }
        
        # Bufferiser
        self.local_buffer.append(experience)
        
        # Indexer par batch
        if len(self.local_buffer) >= 10:
            await self._flush_buffer()
    
    async def _flush_buffer(self):
        """Indexe le buffer dans Zvec"""
        if not self.local_buffer:
            return
        
        # Ici: appel Zvec pour indexer
        # await mcp4_add_documents(
        #     collection=self.collection,
        #     documents=self.local_buffer
        # )
        
        print(f"📚 {len(self.local_buffer)} expériences indexées dans Zvec")
        self.local_buffer = []
    
    async def find_similar_experiences(
        self,
        situation: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Trouve des expériences passées similaires.
        
        Permet de réutiliser les prismes qui ont bien fonctionné
        dans des situations similaires.
        """
        # Recherche vectorielle dans les expériences
        # results = await mcp4_semantic_search(
        #     collection=self.collection,
        #     query=situation,
        #     filter={"effective": True},  # Que les expériences positives
        #     limit=limit
        # )
        
        # Simulation pour l'instant
        return []


# ═══════════════════════════════════════════════════════════════════
# ORCHESTRATION COMPLÈTE
# ═══════════════════════════════════════════════════════════════════

class AwakenedJiminy:
    """
    Jiminy Cricket complètement éveillé.
    
    Orchestrateur qui coordonne:
    1. Sélection sémantique
    2. Réflexion consciente
    3. Exécution d'action
    4. Apprentissage mémoriel
    """
    
    def __init__(self):
        self.selector = SemanticPrismSelector()
        self.consciousness = ConsciousnessMirror()
        self.executor = ActionExecutor()
        self.memory = EvolvingMemory()
        
    async def contemplate_and_act(
        self,
        situation: str,
        context: Optional[Dict] = None,
        execute: bool = True
    ) -> Dict:
        """
        Flux complet: réflexion → action → apprentissage.
        
        Args:
            situation: Description de la situation
            context: Contexte additionnel
            execute: Si True, exécute les actions recommandées
            
        Returns:
            Résultat complet de la session
        """
        context = context or {}
        
        print(f"\n{'='*70}")
        print(f"🦗 JIMINY S'ÉVEILLE...")
        print(f"{'='*70}")
        print(f"\n📋 SITUATION: {situation}")
        
        # Étape 1: Sélection sémantique
        print(f"\n🔍 1. SÉLECTION SÉMANTIQUE...")
        prisms = await self.selector.select(situation, max_prisms=5)
        print(f"   {len(prisms)} prismes choisis: {', '.join(p['mode'] for p in prisms)}")
        
        # Étape 2: Réflexion consciente
        print(f"\n🧠 2. RÉFLEXION CONSCIENTE...")
        async with self.consciousness:
            reflections = await self.consciousness.reflect(prisms, context)
            synthesis = self.consciousness.synthesize(reflections)
        
        print(f"   {len(reflections)} réflexions collectées")
        print(f"   Confiance moyenne: {synthesis['synthesis']['average_confidence']:.2f}")
        print(f"   Cohérence: {synthesis['synthesis']['coherence']}")
        
        # Étape 3: Exécution (si demandée)
        action_result = {"executed": [], "failed": [], "success_rate": 0}
        if execute:
            print(f"\n⚡ 3. EXÉCUTION...")
            action_result = await self.executor.execute(
                synthesis["synthesis"],
                context,
                dry_run=False
            )
            print(f"   {len(action_result['executed'])} actions exécutées")
            print(f"   {len(action_result['failed'])} échecs")
            print(f"   Taux de succès: {action_result['success_rate']:.0%}")
        
        # Étape 4: Apprentissage
        print(f"\n📚 4. APPRENTISSAGE...")
        await self.memory.learn(
            situation=situation,
            prisms_used=[p["mode"] for p in prisms],
            reflections=reflections,
            action_result=action_result
        )
        print(f"   Expérience mémorisée")
        
        # Résultat complet
        return {
            "situation": situation,
            "prisms_selected": prisms,
            "reflections": [{
                "mode": r.mode,
                "insight": r.insight[:100] + "..." if len(r.insight) > 100 else r.insight,
                "confidence": r.confidence
            } for r in reflections],
            "synthesis": synthesis["synthesis"],
            "action_result": action_result,
            "timestamp": datetime.now().isoformat()
        }


# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT POUR CRON
# ═══════════════════════════════════════════════════════════════════

async def awakening_script():
    """
    Script de réveil exécutable par cron.
    
    Usage cron (toutes les 5 minutes):
        */5 * * * * cd /path && python -c "import asyncio; from jiminy_awakening import awakening_script; asyncio.run(awakening_script())"
    """
    jiminy = AwakenedJiminy()
    
    # Exemple: vérifier si un serveur répond
    # Dans la vraie vie, cette info viendrait d'une source externe
    situation = "Le serveur sur le port 3002 ne répond plus aux requêtes"
    context = {
        "server": "localhost:3002",
        "last_check": datetime.now().isoformat(),
        "severity": "high"
    }
    
    result = await jiminy.contemplate_and_act(situation, context, execute=True)
    
    # Log le résultat
    print(f"\n{'='*70}")
    print(f"📊 RÉSULTAT FINAL")
    print(f"{'='*70}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


if __name__ == "__main__":
    # Test standalone
    print("="*70)
    print("🦗 JIMINY AWAKENING - SYSTÈME DE RÉVEIL")
    print("="*70)
    print("\nArchitecture:")
    print("  1. SÉMANTIQUE → Sélection vectorielle")
    print("  2. RÉFLEXION  → Conscience avec prismes")
    print("  3. EXÉCUTION  → Action concrète")
    print("  4. APPRENTISSAGE → Mémoire évolutive")
    print("\nPour lancer via cron:")
    print('  */5 * * * * python jiminy_awakening.py')
    
    # Demo
    asyncio.run(awakening_script())
