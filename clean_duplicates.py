import hashlib
import os
import glob
from pathlib import Path
from collections import defaultdict
import sqlite3

# Ajuster le chemin pour importer les modules du projet
import sys
sys.path.insert(0, str(Path(r"d:\DATA-WEBMAN\projet-DEV\control-tower-rag-ocr\src")))

from control_tower.storage.sqlite import SQLiteStore
from control_tower.storage.vector import QdrantVectorStore, ZvecRestStore

PROJECT_ID = "demo"
BASE_DIR = Path(r"d:\DATA-WEBMAN\projet-DEV\control-tower-rag-ocr\.control_tower\projects") / PROJECT_ID
DOCS_DIR = BASE_DIR / "documents"
DB_PATH = BASE_DIR / "state" / "knowledge.db"

def get_hash(filepath: Path):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def scan_and_clean():
    print("--- SCAN DES DOUBLONS ---")
    if not DOCS_DIR.exists():
        print("Dossier documents introuvable.")
        return
        
    hashes = defaultdict(list)
    
    # 1. Scanner les fichiers à la racine (anciens formats)
    for p in DOCS_DIR.iterdir():
        if p.is_file():
            hashes[get_hash(p)].append(p)
            
    # 2. Scanner les fichiers dans les sous-dossiers originaux (nouveaux formats)
    for p in DOCS_DIR.iterdir():
        if p.is_dir():
            orig_dir = p / "original"
            if orig_dir.exists():
                for orig_file in orig_dir.iterdir():
                    if orig_file.is_file():
                        hashes[get_hash(orig_file)].append(orig_file)

    to_delete = []
    for h, files in hashes.items():
        if len(files) > 1:
            print(f"\nGroupe de {len(files)} fichiers identiques (hash: {h[:8]}...) :")
            # Trier par date de modification (le plus récent en premier)
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # On garde le plus récent (index 0)
            keep = files[0]
            print(f"  [GARDER] {keep}")
            
            # Les autres vont à la poubelle
            for f in files[1:]:
                print(f"  [SUPPRIMER] {f}")
                to_delete.append(f)
                
    if not to_delete:
        print("\nAucun doublon trouvé ! Le système est propre.")
        return
        
    print(f"\n{len(to_delete)} fichiers obsolètes identifiés. Démarrage du nettoyage (fichiers + DB)...")
    
    try:
        store = SQLiteStore(DB_PATH)
    except Exception as e:
        print(f"Erreur connexion SQLite: {e}")
        store = None

    for f in to_delete:
        try:
            # 1. Identifier le document_id
            doc_id = None
            if f.parent.name == "original":
                # Impossible de déduire le UUID complet juste depuis les 8 premiers caractères du dossier,
                # mais dans notre cas les vieilles versions sont directement à la racine
                print(f"Attention: suppression d'un fichier dans le nouveau format {f}")
                pass
            else:
                # Fichier à la racine : le nom du fichier SANS l'extension EST le document_id
                doc_id = f.stem

            if doc_id and store:
                chunks = store.chunks_for_document(doc_id)
                chunk_ids = [c.id for c in chunks]
                if chunk_ids:
                    # Supprimer des bases vectorielles
                    for store_cls in (QdrantVectorStore, ZvecRestStore):
                        try:
                            # Tentative Qdrant local
                            if store_cls is QdrantVectorStore:
                                vs = store_cls(path=str(BASE_DIR / "state" / "qdrant_db"), url="local")
                            else:
                                vs = store_cls(url="http://localhost:8001")
                            vs.delete(PROJECT_ID, chunk_ids)
                        except Exception:
                            pass
                            
                # Supprimer de SQLite
                store.replace_document_chunks(doc_id, [])
                print(f"  -> Base de données nettoyée pour {doc_id}")
            
            # 2. Supprimer les fichiers
            if f.parent.name == "original":
                doc_folder = f.parent.parent
                import shutil
                shutil.rmtree(doc_folder, ignore_errors=True)
                print(f"  -> Dossier supprimé: {doc_folder}")
            else:
                f.unlink()
                print(f"  -> Fichier supprimé: {f}")
                
        except Exception as e:
            print(f"Erreur lors de la suppression de {f}: {e}")

    print("\nNettoyage terminé avec succès !")
    
if __name__ == "__main__":
    scan_and_clean()
