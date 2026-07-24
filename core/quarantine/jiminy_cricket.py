#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JIMINY CRICKET - Couche métacognitive par inférence locale

Système de "conscience" par micro-inférences Ollama :
- Meta-Observer : pose les 5 questions essentielles
- CausalAnalyzer : arbre de causes par inférence
- DecisionGate : grille des 10 questions décisionnelles

Usage:
    from jiminy_cricket import JiminyCricket
    cricket = JiminyCricket()
    insight = await cricket.reflect(state, context)
"""

import os
import json
import aiohttp
import asyncio
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CricketConfig:
    """Configuration Jiminy Cricket via .env"""
    enabled: bool = True
    host: str = "http://localhost:11434"
    model_cricket: str = "qwen2.5:7b"
    model_causal: str = "qwen2.5:7b"
    model_decision: str = "llama3.2:3b"
    context_window: int = 32768
    temperature: float = 0.3
    timeout: int = 30
    
    # Workers activation
    worker_meta_observer: bool = True
    worker_causal_analyzer: bool = True
    worker_decision_gate: bool = True
    
    # Inférence
    reflection_depth: int = 3
    
    @classmethod
    def from_env(cls) -> "CricketConfig":
        """Charge la configuration depuis les variables d'environnement"""
        return cls(
            enabled=os.getenv("OLLAMA_ENABLED", "true").lower() == "true",
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            model_cricket=os.getenv("OLLAMA_MODEL_CRICKET", "qwen2.5:7b"),
            model_causal=os.getenv("OLLAMA_MODEL_CAUSAL", "qwen2.5:7b"),
            model_decision=os.getenv("OLLAMA_MODEL_DECISION", "llama3.2:3b"),
            context_window=int(os.getenv("OLLAMA_CONTEXT_WINDOW", "32768")),
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.3")),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "30")),
            worker_meta_observer=os.getenv("CRICKET_WORKER_META_OBSERVER", "true").lower() == "true",
            worker_causal_analyzer=os.getenv("CRICKET_WORKER_CAUSAL_ANALYZER", "true").lower() == "true",
            worker_decision_gate=os.getenv("CRICKET_WORKER_DECISION_GATE", "true").lower() == "true",
            reflection_depth=int(os.getenv("CRICKET_REFLECTION_DEPTH", "3")),
        )


@dataclass
class MetaObservation:
    """Résultat de l'observation métacognitive"""
    perception: Dict[str, Any]
    comprehension: Dict[str, Any]
    evaluation: Dict[str, Any]
    capacity: Dict[str, Any]
    reflection: Dict[str, Any]
    confidence: float
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "perception": self.perception,
            "comprehension": self.comprehension,
            "evaluation": self.evaluation,
            "capacity": self.capacity,
            "reflection": self.reflection,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }


@dataclass
class CausalAnalysis:
    """Résultat de l'analyse causale"""
    is_problem: bool
    suspected_causes: List[Dict[str, Any]]
    confidence: float
    recommended_next_step: str
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "is_problem": self.is_problem,
            "suspected_causes": self.suspected_causes,
            "confidence": self.confidence,
            "recommended_next_step": self.recommended_next_step,
            "timestamp": self.timestamp,
        }


@dataclass
class Decision:
    """Résultat de la grille décisionnelle"""
    what_changed: bool
    relevant: bool
    expected: bool
    harmful: bool
    known_pattern: bool
    confidence_score: float
    authorized_to_act: bool
    reversible_action_available: bool
    best_action: str
    decision_mode: str  # act_now, defer, notify, memorize_only
    requires_human_validation: bool
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "what_changed": self.what_changed,
            "relevant": self.relevant,
            "expected": self.expected,
            "harmful": self.harmful,
            "known_pattern": self.known_pattern,
            "confidence_score": self.confidence_score,
            "authorized_to_act": self.authorized_to_act,
            "reversible_action_available": self.reversible_action_available,
            "best_action": self.best_action,
            "decision_mode": self.decision_mode,
            "requires_human_validation": self.requires_human_validation,
            "timestamp": self.timestamp,
        }


class OllamaClient:
    """Client HTTP pour Ollama avec retry et timeout"""
    
    def __init__(self, config: CricketConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def generate(self, model: str, prompt: str, system: Optional[str] = None) -> Optional[str]:
        """Génère une réponse via Ollama avec retry"""
        if not self.session:
            raise RuntimeError("Client not connected, use async with")
            
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_ctx": self.config.context_window,
            }
        }
        
        if system:
            payload["system"] = system
            
        # Retry avec backoff
        for attempt in range(3):
            try:
                async with self.session.post(
                    f"{self.config.host}/api/generate",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        text = await response.text()
                        print(f"⚠️ Ollama HTTP {response.status}: {text}")
                        
            except asyncio.TimeoutError:
                print(f"⏱️ Timeout Ollama (tentative {attempt + 1}/3)")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    
            except Exception as e:
                print(f"❌ Erreur Ollama: {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    
        return None
        
    async def is_available(self) -> bool:
        """Vérifie si Ollama est accessible"""
        if not self.session:
            return False
            
        try:
            async with self.session.get(f"{self.config.host}/api/tags") as response:
                return response.status == 200
        except:
            return False


class JiminyCricket:
    """
    Jiminy Cricket - Couche métacognitive par inférence locale
    
    Implémente le pipeline d'inférence du PRD :
    1. Meta-Observer : les 5 questions essentielles
    2. Causal Analyzer : arbre de causes (si problème)
    3. Decision Gate : grille des 10 questions
    """
    
    def __init__(self, config: Optional[CricketConfig] = None):
        self.config = config or CricketConfig.from_env()
        self.client: Optional[OllamaClient] = None
        self._prompts_dir = Path(__file__).parent / "prompts"
        
        # Cache des prompts
        self._prompts: Dict[str, str] = {}
        
    async def __aenter__(self):
        self.client = OllamaClient(self.config)
        await self.client.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
            
    def _load_prompt(self, name: str) -> str:
        """Charge un prompt depuis le fichier .txt"""
        if name not in self._prompts:
            prompt_path = self._prompts_dir / f"{name}.txt"
            if prompt_path.exists():
                self._prompts[name] = prompt_path.read_text(encoding="utf-8")
            else:
                # Fallback: prompt par défaut
                self._prompts[name] = self._default_prompt(name)
        return self._prompts[name]
    
    def _inject_context(self, prompt_template: str, context_json: str) -> str:
        """Injecte le contexte JSON dans le template sans conflit d'accolades"""
        # Utiliser replace() au lieu de format() pour éviter le conflit avec les {} du JSON
        return prompt_template.replace("{{context}}", context_json)
        
    def _default_prompt(self, name: str) -> str:
        """Prompts par défaut si fichier manquant"""
        prompts = {
            "meta_observer": """Tu es Meta-Observer, un système d'observation métacognitive.
Analyse la situation et réponds aux 5 questions essentielles.

SITUATION:
{{context}}

Réponds UNIQUEMENT en JSON valide:
{{
  "perception": {{"what_changed": "...", "relevant": true/false}},
  "comprehension": {{"meaning": "...", "confidence": 0.0-1.0}},
  "evaluation": {{"impact": "low|medium|high", "urgency": "none|low|medium|high"}},
  "capacity": {{"can_act": true/false, "authorized": ["action1", "action2"]}},
  "reflection": {{"should_act": "act_now|defer|notify|memorize", "reason": "..."}}
}}""",
            "causal_analyzer": """Tu es CausalAnalyzer. Analyse les causes probables.

PROBLÈME: {{problem}}
CONTEXTE: {{context}}

Réponds UNIQUEMENT en JSON:
{{
  "is_problem": true/false,
  "suspected_causes": [
    {{"id": "cause1", "description": "...", "confidence": 0.0-1.0}}
  ],
  "recommended_next_step": "...",
  "confidence": 0.0-1.0
}}""",
            "decision_gate": """Tu es DecisionGate. Applique la grille des 10 questions.

ÉVALUATION: {{evaluation}}
CAUSES: {{causes}}
ACTIONS POSSIBLES: {{actions}}

Réponds UNIQUEMENT en JSON:
{{
  "what_changed": true/false,
  "relevant": true/false,
  "expected": true/false,
  "harmful": true/false,
  "known_pattern": true/false,
  "confidence_score": 0.0-1.0,
  "authorized_to_act": true/false,
  "reversible_action_available": true/false,
  "best_action": "...",
  "decision_mode": "act_now|defer|notify|memorize_only",
  "requires_human_validation": true/false
}}""",
        }
        return prompts.get(name, "")
        
    async def meta_observe(self, context: Dict[str, Any]) -> Optional[MetaObservation]:
        """
        Worker 1: Meta-Observer
        Pose les 5 questions essentielles du PRD section 2
        """
        if not self.config.worker_meta_observer:
            return None
            
        prompt_template = self._load_prompt("meta_observer")
        context_json = json.dumps(context, indent=2, ensure_ascii=False)
        prompt = self._inject_context(prompt_template, context_json)
        
        response = await self.client.generate(
            model=self.config.model_cricket,
            prompt=prompt,
            system="Tu es un système d'observation métacognitive. Réponds UNIQUEMENT en JSON valide."
        )
        
        if not response:
            return None
            
        try:
            # Extraction JSON
            json_start = response.find("{")
            json_end = response.rfind("}")
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end+1])
            else:
                data = json.loads(response)
                
            return MetaObservation(
                perception=data.get("perception", {}),
                comprehension=data.get("comprehension", {}),
                evaluation=data.get("evaluation", {}),
                capacity=data.get("capacity", {}),
                reflection=data.get("reflection", {}),
                confidence=data.get("comprehension", {}).get("confidence", 0.5),
                timestamp=datetime.now().isoformat(),
            )
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide Meta-Observer: {e}")
            print(f"   Réponse: {response[:200]}...")
            return None
            
    async def analyze_causes(self, problem: str, context: Dict[str, Any]) -> Optional[CausalAnalysis]:
        """
        Worker 2: Causal Analyzer
        Arbre de causes par inférence (PRD section 6)
        """
        if not self.config.worker_causal_analyzer:
            return None
            
        prompt_template = self._load_prompt("causal_analyzer")
        context_json = json.dumps(context, indent=2, ensure_ascii=False)
        prompt = prompt_template.replace("{{problem}}", problem).replace("{{context}}", context_json)
        
        response = await self.client.generate(
            model=self.config.model_causal,
            prompt=prompt,
            system="Tu es un analyseur causal. Réponds UNIQUEMENT en JSON valide."
        )
        
        if not response:
            return None
            
        try:
            json_start = response.find("{")
            json_end = response.rfind("}")
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end+1])
            else:
                data = json.loads(response)
                
            return CausalAnalysis(
                is_problem=data.get("is_problem", False),
                suspected_causes=data.get("suspected_causes", []),
                confidence=data.get("confidence", 0.5),
                recommended_next_step=data.get("recommended_next_step", "none"),
                timestamp=datetime.now().isoformat(),
            )
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide CausalAnalyzer: {e}")
            return None
            
    async def decide(self, evaluation: Dict, causes: Optional[Dict], actions: List[str]) -> Optional[Decision]:
        """
        Worker 3: Decision Gate
        Grille des 10 questions décisionnelles (PRD section 8)
        """
        if not self.config.worker_decision_gate:
            return None
            
        prompt_template = self._load_prompt("decision_gate")
        evaluation_json = json.dumps(evaluation, indent=2, ensure_ascii=False)
        causes_json = json.dumps(causes or {}, indent=2, ensure_ascii=False)
        actions_json = json.dumps(actions, indent=2, ensure_ascii=False)
        prompt = prompt_template.replace("{{evaluation}}", evaluation_json).replace("{{causes}}", causes_json).replace("{{actions}}", actions_json)
        
        response = await self.client.generate(
            model=self.config.model_decision,
            prompt=prompt,
            system="Tu es une grille décisionnelle. Réponds UNIQUEMENT en JSON valide."
        )
        
        if not response:
            return None
            
        try:
            json_start = response.find("{")
            json_end = response.rfind("}")
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end+1])
            else:
                data = json.loads(response)
                
            return Decision(
                what_changed=data.get("what_changed", False),
                relevant=data.get("relevant", False),
                expected=data.get("expected", True),
                harmful=data.get("harmful", False),
                known_pattern=data.get("known_pattern", False),
                confidence_score=data.get("confidence_score", 0.5),
                authorized_to_act=data.get("authorized_to_act", False),
                reversible_action_available=data.get("reversible_action_available", False),
                best_action=data.get("best_action", "memorize_only"),
                decision_mode=data.get("decision_mode", "defer"),
                requires_human_validation=data.get("requires_human_validation", True),
                timestamp=datetime.now().isoformat(),
            )
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide DecisionGate: {e}")
            return None
            
    async def reflect(self, state: Dict[str, Any], prism_result: Optional[Dict] = None, depth: int = 3) -> Dict[str, Any]:
        """
        Pipeline complet de réflexion Jiminy Cricket
        
        Args:
            state: État du système (manifest, logs, etc.)
            prism_result: Résultat des prismes existants
            depth: Profondeur de réflexion (1-3)
            
        Returns:
            Dict avec l'insight complet du Cricket
        """
        if not self.config.enabled:
            return {"enabled": False, "reason": "Jiminy Cricket désactivé"}
            
        # Vérifier Ollama
        if not await self.client.is_available():
            return {"enabled": False, "reason": "Ollama non disponible", "fallback": True}
            
        context = {
            "state": state,
            "prism_result": prism_result,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Étape 1: Meta-Observer (toujours)
        observation = await self.meta_observe(context)
        if not observation:
            return {"enabled": True, "error": "Meta-Observer failed", "stage": 1}
            
        # Si pas pertinent, arrêt rapide
        if not observation.perception.get("relevant", True):
            return {
                "enabled": True,
                "stage": 1,
                "observation": observation.to_dict(),
                "decision": {"decision_mode": "memorize_only", "reason": "not_relevant"},
                "summary": "Événement non pertinent, mémorisation uniquement"
            }
            
        # Étape 2: Causal Analyzer (si problème ou anomalie)
        causes = None
        if observation.evaluation.get("impact") in ["medium", "high"] or observation.comprehension.get("is_problem"):
            problem = observation.perception.get("what_changed", "unknown")
            causes = await self.analyze_causes(problem, context)
            
        # Étape 3: Decision Gate (toujours)
        actions = observation.capacity.get("authorized", [])
        decision = await self.decide(observation.to_dict(), causes.to_dict() if causes else None, actions)
        
        if not decision:
            return {
                "enabled": True,
                "stage": 2,
                "observation": observation.to_dict(),
                "causes": causes.to_dict() if causes else None,
                "error": "DecisionGate failed"
            }
            
        # Synthèse
        summary = self._synthesize(observation, causes, decision)
        
        return {
            "enabled": True,
            "stage": 3,
            "observation": observation.to_dict(),
            "causes": causes.to_dict() if causes else None,
            "decision": decision.to_dict(),
            "summary": summary,
            "confidence": decision.confidence_score,
        }
        
    def _synthesize(self, observation: MetaObservation, causes: Optional[CausalAnalysis], decision: Decision) -> str:
        """Synthétise les résultats en un résumé lisible"""
        parts = []
        
        # Perception
        what = observation.perception.get("what_changed", "unknown")
        parts.append(f"👁️ Obs: {what}")
        
        # Évaluation
        impact = observation.evaluation.get("impact", "unknown")
        urgency = observation.evaluation.get("urgency", "unknown")
        parts.append(f"📊 Impact: {impact}, Urgence: {urgency}")
        
        # Causes (si présent)
        if causes and causes.is_problem:
            top_cause = causes.suspected_causes[0] if causes.suspected_causes else None
            if top_cause:
                parts.append(f"🔍 Cause: {top_cause.get('id')} ({top_cause.get('confidence', 0):.0%})")
                
        # Décision
        mode = decision.decision_mode
        action = decision.best_action
        parts.append(f"🎯 Action: {action} ({mode})")
        
        return " | ".join(parts)


# Test standalone
if __name__ == "__main__":
    async def test():
        print("🦗 Test Jiminy Cricket")
        print("=" * 50)
        
        async with JiminyCricket() as cricket:
            # Vérifier Ollama
            available = await cricket.client.is_available()
            print(f"Ollama disponible: {available}")
            
            if available:
                # Test simple
                state = {
                    "current_state": "healthy",
                    "wake_up_count": 155,
                    "active_alerts": []
                }
                
                result = await cricket.reflect(state)
                print(f"\nRésultat: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
    asyncio.run(test())
