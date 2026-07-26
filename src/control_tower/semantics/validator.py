from __future__ import annotations

import json
import logging
from control_tower.domain.models import AtomicChunk
from control_tower.config import LLMConfig
from control_tower.generation.llm import get_llm_provider

logger = logging.getLogger(__name__)

class EpistemicValidator:
    """
    Agent Juge (Epistemic Validator) - Mode Réel (Balles Réelles).
    Filtre par un vrai modèle de langage (LLM) pour évaluer la cohérence et l'absence d'hallucination.
    """
    
    def __init__(self, llm_config: LLMConfig) -> None:
        self.llm = get_llm_provider(
            provider_type=llm_config.provider,
            config_obj=llm_config,
            model_name=llm_config.model,
            api_key_env=llm_config.api_key_env,
            temperature=0.0  # Juge implacable, pas de créativité
        )
        self.system_prompt = (
            "Tu es l'Agent Juge (Epistemic Validator). Ta mission est de lire un extrait de texte "
            "et de déterminer s'il est valide (ancré dans le réel, objectif, factuel) ou invalide "
            "(hallucination, refus de répondre type 'En tant qu'IA', mention de concepts absurdes comme un "
            "moteur anti-gravité, délires non pertinents).\n"
            "Si le texte contient des données issues du web (généralement sourcées), tu agis comme un Arbitre "
            "de Pertinence : vérifie que cet ajout a un vrai rapport avec le sujet initial, qu'il ne contredit pas "
            "de façon violente l'essence du texte, et rejette-le s'il est hors-sujet.\n"
            "Tu dois répondre EXACTEMENT par un JSON valide avec le format suivant, SANS AUCUN autre texte:\n"
            '{"status": "validated" ou "rejected", "reason": "courte explication"}'
        )

    def evaluate_chunk(self, chunk: AtomicChunk) -> AtomicChunk:
        """Évalue un chunk et met à jour son statut épistémique et de validation via LLM."""
        
        web_context = ""
        if chunk.web_enrichments:
            web_context = f"\n\n=== ENRICHISSEMENT WEB ===\n{chr(10).join(chunk.web_enrichments)}"
            
        user_prompt = f"Évalue ce texte et ses enrichissements éventuels :\n\n{chunk.text}{web_context}"
        
        try:
            # Appel LLM réel
            response = self.llm.generate(prompt=user_prompt, system_prompt=self.system_prompt)
            
            # Parsing de la réponse json
            try:
                # Nettoyage si le LLM met des backticks (ex: ```json ... ```)
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                    
                data = json.loads(cleaned_response.strip(), strict=False)
                status = data.get("status", "rejected")
                reason = data.get("reason", "Pas de raison fournie.")
                
                if status == "validated":
                    return chunk.model_copy(update={
                        "validation_status": "validated",
                        "epistemic_state": "validated",
                        "judge_feedback": reason
                    })
                else:
                    return chunk.model_copy(update={
                        "validation_status": "rejected",
                        "epistemic_state": "contradicted",
                        "judge_feedback": reason
                    })
            except json.JSONDecodeError:
                logger.error(f"Le Juge n'a pas renvoyé de JSON valide: {response}")
                return chunk.model_copy(update={
                    "validation_status": "rejected",
                    "epistemic_state": "uncertain",
                    "judge_feedback": "Erreur de format du Juge LLM."
                })
        except Exception as e:
            logger.error(f"Erreur lors de l'appel LLM du Juge: {e}")
            return chunk.model_copy(update={
                "validation_status": "rejected",
                "epistemic_state": "uncertain",
                "judge_feedback": f"Erreur technique du Juge: {e}"
            })
            
    def evaluate_project_chunks(self, chunks: list[AtomicChunk]) -> list[AtomicChunk]:
        """Évalue une liste de chunks."""
        # TODO: Faire en parallèle (async/ThreadPoolExecutor) si la latence est trop élevée
        return [self.evaluate_chunk(chunk) for chunk in chunks]
