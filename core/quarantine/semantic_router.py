import os
import json
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Ajout du RAG au path
RAG_PATH = Path(".agent/rag")
if str(RAG_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_PATH))

try:
    from embedder import ZvecEmbedder
    from utils.env_loader import merge_config_with_env
except ImportError as e:
    print(f"❌ Erreur critique : Impossible de charger les composants RAG : {e}")
    sys.exit(1)

class JiminySemanticRouter:
    """
    Router MoE (Mixture of Experts) optimisé pour Jiminy.
    Interroge directement Zvec sans charger tout le pipeline RAG.
    """
    
    def __init__(self, threshold: float = 0.3, max_experts: int = 5):
        # Chargement config minimale
        config_path = RAG_PATH / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            full_config = json.load(f)
        
        zvec_config = merge_config_with_env(full_config).get("embedding", {}).get("zvec", {})
        self.embedder = ZvecEmbedder(zvec_config)
        
        self.threshold = threshold
        self.max_experts = max_experts
        self.base_experts_dir = Path("core/features/jiminy_pipeline_enrichi/prompts_base")
        self.collection_name = "jiminy_personality_vector_base"

    async def route_task(self, user_query: str) -> Dict[str, Any]:
        """
        Analyse la tâche et sélectionne les experts les plus pertinents.
        """
        print(f"🔍 Recherche sémantique flash : '{user_query}'...")
        
        # 1. Recherche directe dans la collection d'experts
        # On évite search_dual et les boucles inutiles
        results = await self.embedder.search(
            collection=self.collection_name,
            query=user_query,
            limit=15
        )
        
        experts_scores = {}
        for res in results:
            metadata = res.get('metadata', {})
            mode = metadata.get('mode')
            score = res.get('score', 0)
            
            if mode and score >= self.threshold:
                experts_scores[mode] = max(score, experts_scores.get(mode, 0))

        # 2. Tri et sélection du top-K
        sorted_experts = sorted(experts_scores.items(), key=lambda x: x[1], reverse=True)[:self.max_experts]
        
        if not sorted_experts:
            return await self._build_composite_persona([("assistant", 1.0)], user_query)

        print(f"🧠 Experts activés : {', '.join([f'{m} ({s:.2f})' for m, s in sorted_experts])}")
        return await self._build_composite_persona(sorted_experts, user_query)

    async def _build_composite_persona(self, selected_experts: List[tuple], user_query: str) -> Dict[str, Any]:
        """
        Fusionne les fragments neuronaux des experts sélectionnés.
        """
        composite = {
            "query": user_query,
            "experts": [],
            "combined_prompt": "",
            "active_clusters": set(),
            "fusion_metadata": {
                "total_resonance": sum([s for m, s in selected_experts]),
                "top_expert": selected_experts[0][0]
            }
        }

        combined_mission = []
        combined_principles = []
        combined_questions = []

        for mode, score in selected_experts:
            data = await self._load_expert_data(mode)
            if data:
                composite["experts"].append({
                    "mode": mode,
                    "resonance": score,
                    "shrink": data["identity"]["shrink"],
                    "cluster": data["neuron_map"]["moe_cluster"]
                })
                composite["active_clusters"].add(data["neuron_map"]["moe_cluster"])
                
                # Extraction intelligente du raw_prompt (après le header MISSION)
                raw = data["raw_prompt"]
                parts = raw.split("MISSION")
                if len(parts) > 1:
                    mission_part = parts[1].split("PRINCIPE")[0].strip()
                    combined_mission.append(f"[{mode.upper()}]: {mission_part}")
                
                if "PRINCIPE" in raw:
                    principe_part = raw.split("PRINCIPE")[1].split("CONTEXTE")[0].strip()
                    combined_principles.append(f"--- Principes {mode.upper()} ---\n{principe_part}")

                if "QUESTIONS" in raw:
                    question_part = raw.split("QUESTIONS")[1].strip()
                    combined_questions.append(f"--- Questions {mode.upper()} ---\n{question_part}")

        # Assemblage du Super-Prompt Jiminy
        composite["combined_prompt"] = (
            f"Tu es Jiminy Cricket, une conscience multi-dimensionnelle fusionnant {len(selected_experts)} experts.\n\n"
            f"MISSION COMPOSITE\n" + "\n".join(combined_mission) + "\n\n"
            f"SYNERGIE DES PRINCIPES\n" + "\n".join(combined_principles) + "\n\n"
            f"ANALYSE MULTI-CRITÈRES\n" + "\n".join(combined_questions)
        )
        
        composite["active_clusters"] = list(composite["active_clusters"])
        return composite

    async def _load_expert_data(self, mode: str) -> Optional[Dict]:
        file_path = self.base_experts_dir / f"{mode}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

if __name__ == "__main__":
    # Test rapide si lancé en direct
    async def test():
        router = JiminySemanticRouter()
        result = await router.route_task("J'ai un bug critique de performance sur ma base de données de production")
        print("\n--- PROMPT GÉNÉRÉ ---")
        print(result["combined_prompt"])
        
    asyncio.run(test())
