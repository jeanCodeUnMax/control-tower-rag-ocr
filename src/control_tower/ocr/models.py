from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, computed_field


class ExtractionMethod(StrEnum):
    TEXT = "text"
    NATIVE_PDF = "native_pdf"
    TESSERACT_PDF = "tesseract_pdf"
    TESSERACT_IMAGE = "tesseract_image"


from control_tower.ocr.layout import LayoutBlock

class ExtractedPage(BaseModel):
    page_number: int = Field(ge=1)
    text: str
    method: ExtractionMethod
    width: int | None = None
    height: int | None = None
    warnings: list[str] = Field(default_factory=list)
    supplemental_methods: list[str] = Field(default_factory=list)
    blocks: list[LayoutBlock] = Field(default_factory=list)

    @computed_field
    @property
    def char_count(self) -> int:
        return len(self.text)


class ExtractionResult(BaseModel):
    source_path: str
    source_type: str
    pages: list[ExtractedPage]
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    contract_version: str = "1.0"

    @property
    def text(self) -> str:
        sections = [page.text.strip() for page in self.pages if page.text.strip()]
        return "\n\n".join(sections)

    @property
    def character_count(self) -> int:
        return sum(page.char_count for page in self.pages)

    @property
    def methods(self) -> list[str]:
        return sorted({page.method.value for page in self.pages})

    def artifact_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json")
        payload["summary"] = {
            "page_count": len(self.pages),
            "character_count": self.character_count,
            "methods": self.methods,
        }
        return payload

    @classmethod
    def for_text(cls, source: Path, text: str) -> "ExtractionResult":
        return cls(
            source_path=str(source),
            source_type=source.suffix.lower().lstrip("."),
            pages=[ExtractedPage(page_number=1, text=text, method=ExtractionMethod.TEXT)],
        )
