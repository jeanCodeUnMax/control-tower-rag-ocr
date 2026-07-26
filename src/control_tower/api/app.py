from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from pathlib import Path

# Chargement manuel du .env pour éviter la dépendance python-dotenv
env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            # Retirer les éventuels guillemets
            val = val.strip().strip('"').strip("'")
            if key not in os.environ:
                os.environ[key.strip()] = val

from control_tower.service import ControlTowerService

app = FastAPI(title="Control Tower RAG", version="0.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ControlTowerService()

_frontend_dir = Path(__file__).resolve().parents[3] / "frontend"
if _frontend_dir.exists():
    app.mount("/ui", StaticFiles(directory=_frontend_dir, html=True), name="ui")


class ProjectCreate(BaseModel):
    project_id: str
    name: str | None = None


class IngestRequest(BaseModel):
    project_id: str
    source_path: str


class QueryRequest(BaseModel):
    project_id: str
    text: str
    top_k: int | None = None


class SynthesizeRequest(BaseModel):
    project_id: str
    question: str
    top_k: int = 5
    use_web_search: bool = False
    paradigm: str = "executive"


class DocumentPlanRequest(BaseModel):
    project_id: str
    source_path: str


class VisionBenchmarkRequest(BaseModel):
    project_id: str
    source_path: str
    max_pages: int = 12


class EnrichRequest(BaseModel):
    project_id: str
    document_id: str
    profile: str = "cloud_turbo"


class ConfigUpdateRequest(BaseModel):
    key: str
    value: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.5.0"}


@app.post("/projects")
def create_project(request: ProjectCreate) -> dict:
    try:
        return service.init_project(request.project_id, request.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import tempfile
import shutil

@app.post("/projects/{project_id}/ingest")
async def ingest_upload(
    project_id: str,
    chunk_size: int = Form(1024),
    overlap: int = Form(256),
    advanced_ocr: bool = Form(False),
    orthogonal_rotation: bool = Form(False),
    tags: str = Form(""),
    force: bool = Form(False),
    file: UploadFile = File(...)
) -> dict:
    try:
        try:
            config = service.workspace.load_config(project_id)
        except Exception:
            service.workspace.create(project_id)
            config = service.workspace.load_config(project_id)
        config.atomizer.max_chars = chunk_size
        config.atomizer.overlap_chars = overlap
        if advanced_ocr:
            config.ocr.mode = "force_ocr"
        # Optional: Add tags logic or orthogonal_rotation logic directly in the document schema
        from control_tower.config import write_project_config
        write_project_config(service.workspace.config_path(project_id), config)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Sécuriser le nom du fichier
            safe_filename = Path(file.filename).name
            tmp_path = Path(tmpdir) / safe_filename
            with open(tmp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
                
            result = service.ingest(project_id, tmp_path, force=force)
            
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/projects/{project_id}/providers/{provider_name}/test")
def test_provider_connection(project_id: str, provider_name: str) -> dict:
    try:
        return service.test_provider_connection(project_id, provider_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/mcp/test")
def test_mcp_databases() -> dict:
    from control_tower.generation.mcp_client import MCPOrchestrator
    try:
        orch = MCPOrchestrator()
        # On va tester tous les serveurs définis dans le mcp_config.json
        results = {}
        for server_name in orch.servers.keys():
            try:
                # Si get_tools réussi, le serveur répond
                tools = orch.get_tools([server_name])
                results[server_name] = {"status": "ok", "tools_count": len(tools)}
            except Exception as e:
                results[server_name] = {"status": "error", "message": str(e)}
        return {"status": "success", "servers": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.get("/mcp/servers")
def get_mcp_servers() -> dict:
    import json
    from pathlib import Path
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        config_path = base_dir / "mcp_config.json"
        if not config_path.exists():
            return {"status": "success", "servers": []}
            
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        servers = list(data.get("mcpServers", {}).keys())
        return {"status": "success", "servers": servers}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.get("/models/{kind}")
def get_available_models(kind: str) -> dict:
    """Retourne la liste des modèles disponibles (ouverts/gratuits ou installés localement) pour un provider."""
    import httpx
    models = []
    try:
        if kind == "ollama":
            # Liste des modèles locaux (Forcer IPv4 car Ollama écoute souvent sur 127.0.0.1)
            resp = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5.0)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
        elif kind == "openrouter":
            # API publique OpenRouter, on filtre sur ceux qui sont gratuits
            resp = httpx.get("https://openrouter.ai/api/v1/models", timeout=10.0)
            if resp.status_code == 200:
                all_models = resp.json().get("data", [])
                models = [m["id"] for m in all_models if m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0"]
        elif kind == "gemini":
            models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-1.5-flash-8b"]
        elif kind == "mistral":
            models = ["mistral-large-latest", "mistral-small-latest", "open-mistral-nemo", "open-mixtral-8x22b", "ministral-8b-latest", "ministral-3b-latest", "pixtral-12b-2409"]
        elif kind == "huggingface":
            models = [
                "meta-llama/Llama-3.3-70B-Instruct", 
                "Qwen/Qwen2.5-72B-Instruct", 
                "Qwen/Qwen2.5-Coder-32B-Instruct",
                "mistralai/Mixtral-8x7B-Instruct-v0.1", 
                "microsoft/Phi-3.5-mini-instruct",
                "google/gemma-2-9b-it",
                "deepseek-ai/DeepSeek-V3",
                "CohereForAI/c4ai-command-r-plus-08-2024"
            ]
        elif kind == "llamacpp":
            import os
            models_dir = "D:/models"
            if os.path.exists(models_dir):
                models = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
        return {"status": "success", "models": models}
    except Exception as exc:
        # En cas d'erreur réseau (ex: Ollama non lancé), on retourne une liste vide sans planter
        return {"status": "error", "message": str(exc), "models": []}

@app.get("/providers/health")
def get_providers_health() -> dict:
    from control_tower.generation.llm import HealthMonitor
    try:
        return {"status": "success", "health": HealthMonitor.get_all()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

class BenchmarkRequest(BaseModel):
    prompt: str
    system_prompt: str = ""

@app.post("/projects/{project_id}/benchmark")
def run_benchmark(project_id: str, request: BenchmarkRequest) -> dict:
    from control_tower.config import LLMConfig
    from control_tower.generation.llm import get_llm_provider
    import time
    
    try:
        config_obj = service.workspace.load_config(project_id)
        enabled_providers = [p for p in config_obj.llm.providers if p.enabled]
        
        results = []
        for p in enabled_providers:
            # On crée un faux config LLM avec juste CE provider pour l'instancier avec les bons paramètres
            dummy_llm_config = LLMConfig(
                provider="router",
                provider_order=[p.name],
                providers=[p]
            )
            
            start_time = time.time()
            try:
                llm = get_llm_provider("router", dummy_llm_config)
                response = llm.generate(request.prompt, request.system_prompt)
                duration = time.time() - start_time
                results.append({
                    "name": p.name,
                    "kind": p.kind,
                    "model": p.model,
                    "duration_s": round(duration, 2),
                    "response": response,
                    "error": None
                })
            except Exception as e:
                duration = time.time() - start_time
                results.append({
                    "name": p.name,
                    "kind": p.kind,
                    "model": p.model,
                    "duration_s": round(duration, 2),
                    "response": None,
                    "error": str(e)
                })
                
        return {"status": "success", "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

class ChunkValidateRequest(BaseModel):
    new_text: str | None = None

@app.get("/projects/{project_id}/quarantine")
def get_quarantine(project_id: str) -> dict:
    try:
        return service.get_quarantined_chunks(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/projects/{project_id}/quarantine/{chunk_id}/validate")
def validate_chunk(project_id: str, chunk_id: str, request: ChunkValidateRequest) -> dict:
    try:
        return service.validate_chunk(project_id, chunk_id, new_text=request.new_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/projects/{project_id}/quarantine/{chunk_id}/discard")
def discard_chunk(project_id: str, chunk_id: str) -> dict:
    try:
        return service.discard_chunk(project_id, chunk_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/projects/{project_id}/vectorize")
def vectorize_project(project_id: str) -> dict:
    try:
        return service.vectorize_project(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/ingest")
def ingest(request: IngestRequest) -> dict:
    try:
        return service.ingest(request.project_id, Path(request.source_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/projects/{project_id}/consolidate")
def consolidate_api(project_id: str) -> dict:
    try:
        return service.consolidate_project(project_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/plan-document")
def plan_document(request: DocumentPlanRequest) -> dict:
    try:
        return service.plan_document(request.project_id, Path(request.source_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/benchmark-vision")
def benchmark_vision(request: VisionBenchmarkRequest) -> dict:
    try:
        return service.benchmark_vision(
            request.project_id, Path(request.source_path), request.max_pages
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/enrich-document")
def enrich_document(request: EnrichRequest) -> dict:
    try:
        return service.enrich_document(
            request.project_id, request.document_id, request.profile
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/query")
def query(request: QueryRequest) -> dict:
    try:
        return service.query(request.project_id, request.text, request.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/synthesize")
def synthesize(request: SynthesizeRequest) -> dict:
    try:
        # On ne passe pas output_file par défaut ici pour l'API, on utilise un nom par défaut.
        return service.synthesize_llms(
            project_id=request.project_id,
            question=request.question,
            top_k=request.top_k,
            use_web_search=request.use_web_search,
            paradigm=request.paradigm
        )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/projects/{project_id}/config")
def show_config(project_id: str) -> dict:
    try:
        return service.show_config(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/projects/{project_id}/providers")
def get_providers(project_id: str) -> dict:
    try:
        return service.get_providers(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.put("/projects/{project_id}/providers/{provider_name}")
def update_provider(project_id: str, provider_name: str, payload: dict) -> dict:
    try:
        return service.update_provider(project_id, provider_name, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.patch("/projects/{project_id}/config")
def update_config(project_id: str, request: ConfigUpdateRequest) -> dict:
    try:
        return service.set_config(project_id, request.key, request.value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{project_id}/documents")
def list_documents(project_id: str) -> dict:
    try:
        service.workspace.require(project_id)
        project_path = service.workspace.path_for(project_id)
        from control_tower.storage.sqlite import SQLiteStore
        store = SQLiteStore(project_path / "state" / "knowledge.db")
        with store._connect() as conn:
            docs = conn.execute("SELECT DISTINCT document_id FROM chunks").fetchall()
            return {"project_id": project_id, "documents": [row[0] for row in docs]}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/projects/{project_id}/documents/{document_id}")
def inspect_document(project_id: str, document_id: str) -> dict:
    try:
        return service.inspect_document(project_id, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.post("/projects/{project_id}/documents/{document_id}/open")
def open_document_folder(project_id: str, document_id: str) -> dict:
    try:
        service.workspace.require(project_id)
        docs_dir = service.workspace.path_for(project_id) / "documents"
        if not docs_dir.exists():
            raise HTTPException(status_code=404, detail="Dossier documents introuvable")
        
        target_path = None
        # 1. Chercher dans documents/ (fichiers originaux ou sous-dossiers anti-fragiles)
        if docs_dir.exists():
            for path in docs_dir.iterdir():
                if document_id in path.name:
                    target_path = path
                    break
                    
        # 2. Chercher dans artifacts/ (extractions JSON, assets) si pas trouvé dans documents/
        if not target_path:
            artifact_dir = service.workspace.path_for(project_id) / "artifacts" / document_id
            if artifact_dir.exists():
                target_path = artifact_dir

        if not target_path:
            raise HTTPException(status_code=404, detail="Dossier du document introuvable")
            
        import os
        import platform
        import subprocess
        
        if platform.system() == "Windows":
            if target_path.is_file():
                subprocess.Popen(['explorer', '/select,', str(target_path)])
            else:
                os.startfile(target_path)
        elif platform.system() == "Darwin":
            if target_path.is_file():
                subprocess.Popen(["open", "-R", str(target_path)])
            else:
                subprocess.Popen(["open", str(target_path)])
        else:
            if target_path.is_file():
                subprocess.Popen(["xdg-open", str(target_path.parent)])
            else:
                subprocess.Popen(["xdg-open", str(target_path)])
            
        return {"status": "ok", "path": str(target_path)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc



@app.get("/projects/{project_id}/inspect")
def inspect_project(project_id: str) -> dict:
    try:
        return service.inspect_project(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
