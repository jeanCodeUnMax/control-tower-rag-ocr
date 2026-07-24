import asyncio
import sys
import json
from pathlib import Path

# Setup path
RAG_PATH = Path(".agent/rag")
if str(RAG_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_PATH))

try:
    from embedder import ZvecEmbedder
    from utils.env_loader import merge_config_with_env
except ImportError as e:
    print(f"❌ Erreur : {e}")
    sys.exit(1)

async def check_data():
    config_path = RAG_PATH / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        full_config = json.load(f)
    
    zvec_config = merge_config_with_env(full_config).get("embedding", {}).get("zvec", {})
    embedder = ZvecEmbedder(zvec_config)
    
    collection = "jiminy_personality_vector_base"
    print(f"🔍 Diagnostic profond de '{collection}'...\n")
    
    # On cherche TOUT (requête vide ou générique) avec une limite haute
    results = await embedder.search(collection=collection, query="EXPERT", limit=83)
    
    if not results:
        print("❌ Toujours aucun résultat. Vérifions si la collection existe au moins sur le serveur.")
        import httpx
        url = f"{zvec_config.get('url', 'http://localhost:8001')}/collections"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            print(f"Collections sur le serveur : {resp.json()}")
        return

    print(f"✅ {len(results)} vecteurs trouvés !\n")
    
    for i, res in enumerate(results[:5]): # On regarde les 5 premiers
        print(f"--- Vecteur {i+1} ---")
        print(f"Score: {res.get('score')}")
        print(f"Structure complète: {json.dumps(res, indent=2, ensure_ascii=False)[:500]}...")
        print("\n")

if __name__ == "__main__":
    asyncio.run(check_data())
