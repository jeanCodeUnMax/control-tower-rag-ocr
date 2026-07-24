import os
import json
import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du pipeline RAG pour les imports
RAG_PATH = Path(".agent/rag")
if str(RAG_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_PATH))

try:
    from embedder import ZvecEmbedder
    from utils.env_loader import merge_config_with_env
except ImportError as e:
    print(f"❌ Impossible de charger les composants RAG : {e}")
    sys.exit(1)

# Configuration
PROMPTS_BASE_DIR = Path("core/features/jiminy_pipeline_enrichi/prompts_base")
COLLECTION_NAME = "jiminy_personality_vector_base"

async def sync_experts():
    print(f"🚀 Synchronisation DIRECTE des experts vers '{COLLECTION_NAME}'...")
    
    # 1. Charger la config Zvec
    config_path = RAG_PATH / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        full_config = json.load(f)
    
    zvec_config = merge_config_with_env(full_config).get("embedding", {}).get("zvec", {})
    embedder = ZvecEmbedder(zvec_config)
    
    # S'assurer que la collection existe
    await embedder.create_collection(COLLECTION_NAME)
    
    expert_files = list(PROMPTS_BASE_DIR.glob("*.json"))
    total = len(expert_files)
    
    success_count = 0
    
    for i, file_path in enumerate(expert_files, 1):
        if file_path.name == "all_prompts_enriched.json":
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            expert_data = json.load(f)
            
        mode = expert_data["mode"]
        print(f"[{i}/{total}] Embedding de l'expert : {mode}...")
        
        # On prépare le contenu enrichi
        content_to_index = (
            f"EXPERT: {mode}\n"
            f"SHRINK: {expert_data['identity']['shrink']}\n"
            f"SUMMARY: {expert_data['identity']['summary']}\n"
            f"TAGS: {', '.join(expert_data['identity']['tags'])}\n"
            f"CLUSTER: {expert_data['neuron_map']['moe_cluster']}\n"
            f"RESONANCE: {', '.join(expert_data['neuron_map']['resonance'])}\n"
            f"\nPROMPT BRUT:\n{expert_data['raw_prompt']}"
        )
        
        # 2. Stockage direct dans Zvec
        try:
            success = await embedder.store(
                collection=COLLECTION_NAME,
                chunk_id=f"expert_{mode}",
                content=content_to_index,
                metadata={
                    "mode": mode,
                    "type": "personality_expert",
                    "cluster": expert_data['neuron_map']['moe_cluster'],
                    "version": f"{expert_data['versioning_control']['v_major']}.{expert_data['versioning_control']['v_minor']}",
                    "is_personality_vector": True
                }
            )
            
            if success:
                success_count += 1
            else:
                print(f"⚠️ Échec stockage pour {mode}")
                
        except Exception as e:
            print(f"❌ Erreur pour {mode} : {e}")

    print(f"\n✅ Terminé. {success_count}/{total} experts indexés physiquement dans Zvec.")
    
    # Mise à jour du STATUS.json de la feature
    update_feature_status(success_count)

def update_feature_status(count):
    status_path = Path("core/features/jiminy_pipeline_enrichi/STATUS.json")
    if status_path.exists():
        with open(status_path, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        status["completed_steps"].append("zvec_sync_via_native_pipeline")
        status["current_step"] = "implementing_semantic_router"
        status["last_update"] = "2026-04-10T23:00:00"
        status["experts_indexed"] = count
        
        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(sync_experts())
