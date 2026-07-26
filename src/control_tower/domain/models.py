from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ResultStatus(StrEnum):
    OK = "ok"
    ERROR = "error"
    PARTIAL = "partial"
    BLOCKED = "blocked"


class ModuleResult(BaseModel):
    status: ResultStatus
    module: str
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    data: Any = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metrics: dict[str, float | int | str] = Field(default_factory=dict)
    contract_version: str = "1.1"


class PolicyEffect(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"


class PolicyDecision(BaseModel):
    effect: PolicyEffect
    rule_id: str
    reason: str
    obligations: list[str] = Field(default_factory=list)


class Project(BaseModel):
    id: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    schema_version: str = "1.1"


class DuplicateKind(StrEnum):
    CANONICAL = "canonical"
    EXACT = "exact_duplicate"
    NEAR = "near_duplicate"
    SEMANTIC = "semantic_duplicate"


class EvidenceOccurrence(BaseModel):
    document_id: str
    chunk_id: str
    source_pages: list[int] = Field(default_factory=list)
    duplicate_kind: DuplicateKind = DuplicateKind.CANONICAL
    score: float | None = None


class AtomicChunk(BaseModel):
    id: str
    project_id: str
    document_id: str
    ordinal: int
    text: str
    content_hash: str
    tags: list[str] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    pseudocode: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    tensions: list[str] = Field(default_factory=list)
    source_pages: list[int] = Field(default_factory=list)
    extraction_method: str | None = None
    visual_asset_ids: list[str] = Field(default_factory=list)
    duplicate_kind: DuplicateKind = DuplicateKind.CANONICAL
    canonical_id: str | None = None
    duplicate_score: float | None = None
    indexable: bool = True
    validation_status: str = "pending"
    epistemic_state: str = "extracted"
    judge_feedback: str | None = None
    web_enrichments: list[str] = Field(default_factory=list)
    web_sources: list[str] = Field(default_factory=list)
    evidence_occurrences: list[EvidenceOccurrence] = Field(default_factory=list)
    schema_version: str = "1.3"


class SearchHit(BaseModel):
    chunk: AtomicChunk
    score: float


class ExecutionStep(BaseModel):
    module: str
    action: str
    required: bool = True


class ExecutionPlan(BaseModel):
    project_id: str
    intent: str
    steps: list[ExecutionStep]
