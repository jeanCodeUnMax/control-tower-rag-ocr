from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)
            
        result = service.ingest(project_id, tmp_path)
        
        # Clean up
        try:
            tmp_path.unlink()
        except:
            pass
            
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/ingest")
def ingest(request: IngestRequest) -> dict:
    try:
        return service.ingest(request.project_id, Path(request.source_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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


@app.get("/projects/{project_id}/inspect")
def inspect_project(project_id: str) -> dict:
    try:
        return service.inspect_project(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
