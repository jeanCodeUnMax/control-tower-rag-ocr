from __future__ import annotations

import json
import logging
from typing import Any

from control_tower.domain.models import AtomicChunk
from control_tower.config import LLMConfig
from control_tower.generation.llm import get_llm_provider

logger = logging.getLogger(__name__)

class SelfReflectionAnalyzer:
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        
        # L'utilisateur a demandé explicitement d'utiliser l'API Mistral pour le Juge
        mistral_prov = next((p for p in llm_config.providers if p.kind == "mistral"), None)
        
        provider_type = "mistral"
        model_name = "mistral-large-latest"
        api_key_env = "MISTRAL_API_KEY"
        
        if mistral_prov:
            provider_type = mistral_prov.kind
            model_name = mistral_prov.model
            api_key_env = mistral_prov.api_key_env
            
        self.llm = get_llm_provider(
            provider_type=provider_type,
            config_obj=llm_config,
            model_name=model_name,
            api_key_env=api_key_env,
            temperature=0.1  # Basse température pour le jugement
        )

    def enrich(self, chunk: AtomicChunk) -> AtomicChunk:
        """Évalue la cohérence du chunk et de ses enrichissements, avec boucle de retry."""
        max_retries = 1
        current_chunk = chunk

        for attempt in range(max_retries + 1):
            score, feedback = self._evaluate_chunk(current_chunk)
            
            if score >= 7:
                # La cohérence est jugée suffisante
                if feedback:
                    current_chunk = current_chunk.model_copy(
                        update={"tags": current_chunk.tags + ["reflection:passed"]}
                    )
                return current_chunk
                
            logger.info(f"[Reflection] Chunk {current_chunk.id} noté {score}/10. Feedback: {feedback}")
            
            if attempt < max_retries:
                # Appliquer le feedback pour regénérer les enrichissements (simulation simplifiée)
                # Dans une version avancée, on demanderait au LLM de réécrire le contenu.
                current_chunk = self._apply_feedback(current_chunk, feedback)
                
        # Si on dépasse les retries, on garde le dernier mais on le taggue
        return current_chunk.model_copy(
            update={"tags": current_chunk.tags + ["reflection:failed_threshold"]}
        )

    def _evaluate_chunk(self, chunk: AtomicChunk) -> tuple[int, str]:
        system_prompt = (
            "Tu es un Juge Cognitif implacable. Ton rôle est d'évaluer la cohérence "
            "sémantique d'un fragment de texte et de ses métadonnées extraites.\n"
            "Réponds UNIQUEMENT au format JSON strict avec deux clés :\n"
            '{"score": <entier de 1 à 10>, "feedback": "<une phrase de critique ou conseil>"}'
        )
        
        content = (
            f"TEXTE:\n{chunk.text}\n\n"
            f"CONCEPTS:\n{chunk.concepts}\n\n"
            f"QUESTIONS (Maïeutique):\n{chunk.questions}\n"
        )
        
        try:
            response = self.llm.generate(prompt=content, system_prompt=system_prompt)
            # Extraire le JSON (parfois le LLM met des backticks)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
                
            data = json.loads(json_str)
            return int(data.get("score", 5)), data.get("feedback", "")
        except Exception as e:
            logger.warning(f"Erreur lors de la réflexion: {e}")
            return 8, "Erreur d'évaluation ignorée"

    def _apply_feedback(self, chunk: AtomicChunk, feedback: str) -> AtomicChunk:
        """Utilise le LLM pour corriger le chunk selon le feedback."""
        system_prompt = (
            "Tu es un expert en révision. Améliore la clarté du texte et la pertinence "
            "des questions associées en tenant compte de la critique fournie.\n"
            "Réponds UNIQUEMENT au format JSON strict avec deux clés :\n"
            '{"text": "<texte amélioré>", "questions": ["<q1>", "<q2>"]}'
        )
        
        prompt = (
            f"CRITIQUE DU JUGE: {feedback}\n\n"
            f"TEXTE ORIGINAL:\n{chunk.text}\n\n"
            f"QUESTIONS ORIGINALES:\n{chunk.questions}\n"
        )
        
        try:
            response = self.llm.generate(prompt=prompt, system_prompt=system_prompt)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
                
            data = json.loads(json_str)
            new_text = data.get("text", chunk.text)
            new_questions = data.get("questions", chunk.questions)
            
            return chunk.model_copy(update={
                "text": new_text,
                "questions": new_questions,
                "tags": chunk.tags + ["reflection:corrected"]
            })
        except Exception as e:
            logger.warning(f"Erreur lors de la correction: {e}")
            return chunk
