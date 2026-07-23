from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from control_tower.service import ControlTowerService

app = FastAPI(title="Control Tower RAG", version="0.5.0")
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
