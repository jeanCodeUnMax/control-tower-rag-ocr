from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field


class PageState(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PageProfile(BaseModel):
    page_number: int = Field(ge=1)
    native_characters: int = Field(ge=0)
    image_count: int = Field(ge=0)
    drawing_count: int = Field(ge=0)
    text_block_count: int = Field(default=0, ge=0)
    estimated_context_units: int = Field(ge=0)
    requires_ocr: bool = False
    requires_visual_analysis: bool = False


class PageBatch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    page_numbers: list[int]
    estimated_context_units: int
    attempt: int = 0
    parent_batch_id: str | None = None

    @computed_field
    @property
    def start_page(self) -> int:
        return min(self.page_numbers)

    @computed_field
    @property
    def end_page(self) -> int:
        return max(self.page_numbers)


class VisualElement(BaseModel):
    type: str
    description: str
    labels: list[str] = Field(default_factory=list)
    data_points: list[str] = Field(default_factory=list)
    asset_id: str | None = None
    canonical_asset_id: str | None = None


class PageAnalysis(BaseModel):
    page_number: int
    provider: str
    summary: str = ""
    extracted_text: str = ""
    handwriting_text: str = ""
    visual_elements: list[VisualElement] = Field(default_factory=list)
    symbols: list[str] = Field(default_factory=list)
    pseudocode: list[str] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    maieutic_questions: list[str] = Field(default_factory=list)
    kant_tensions: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    needs_multimodal_review: bool = False
    warnings: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class BatchAnalysis(BaseModel):
    pages: list[PageAnalysis]


class RenderedPage(BaseModel):
    page_number: int
    image_path: Path
    native_text: str = ""
    image_count: int = 0
    drawing_count: int = 0


class PageLedgerEntry(BaseModel):
    page_number: int
    state: PageState = PageState.PENDING
    attempts: int = 0
    batch_ids: list[str] = Field(default_factory=list)
    extraction_method: str | None = None
    artifact_path: str | None = None
    error: str | None = None


class IngestionLedger(BaseModel):
    document_id: str
    source_name: str
    total_pages: int
    entries: dict[int, PageLedgerEntry]
    planned_batches: list[PageBatch] = Field(default_factory=list)
    completed_batches: list[str] = Field(default_factory=list)
    failed_batches: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    schema_version: str = "1.0"

    @property
    def completed_pages(self) -> list[int]:
        return sorted(
            number for number, entry in self.entries.items() if entry.state == PageState.COMPLETED
        )

    @property
    def failed_pages(self) -> list[int]:
        return sorted(
            number for number, entry in self.entries.items() if entry.state == PageState.FAILED
        )

    @property
    def missing_pages(self) -> list[int]:
        expected = set(range(1, self.total_pages + 1))
        return sorted(expected - set(self.completed_pages) - set(self.failed_pages))

    @property
    def complete(self) -> bool:
        return (
            len(self.completed_pages) == self.total_pages
            and not self.failed_pages
            and not self.missing_pages
        )

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)

    def summary(self) -> dict[str, Any]:
        return {
            "total_pages": self.total_pages,
            "completed_pages": len(self.completed_pages),
            "completed_page_numbers": self.completed_pages,
            "failed_pages": self.failed_pages,
            "missing_pages": self.missing_pages,
            "complete": self.complete,
            "planned_batch_count": len(self.planned_batches),
            "completed_batch_count": len(self.completed_batches),
            "failed_batch_count": len(self.failed_batches),
        }


class AssetKind(StrEnum):
    EMBEDDED_IMAGE = "embedded_image"
    VECTOR_DRAWING = "vector_drawing"


class VisualAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    page_number: int
    kind: AssetKind
    exact_hash: str
    perceptual_hash: str | None = None
    canonical_asset_id: str | None = None
    duplicate_kind: str = "canonical"
    duplicate_score: float | None = None
    file_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def indexable(self) -> bool:
        return self.canonical_asset_id is None


class ConsolidationReport(BaseModel):
    raw_chunks: int
    canonical_chunks: int
    exact_duplicates: int
    near_duplicates: int
    semantic_duplicates: int
    raw_assets: int
    canonical_assets: int
    duplicate_assets: int
    semantic_stage: str
    warnings: list[str] = Field(default_factory=list)


class LongPDFResult(BaseModel):
    extraction: Any
    analyses: dict[int, PageAnalysis]
    assets: list[VisualAsset]
    ledger: IngestionLedger
    artifact_dir: str

    @property
    def complete(self) -> bool:
        return self.ledger.complete

    def page_analysis(self, page_number: int) -> PageAnalysis | None:
        return self.analyses.get(page_number)

    def extracted_page(self, page_number: int) -> Any | None:
        for page in self.extraction.pages:
            if page.page_number == page_number:
                return page
        return None
