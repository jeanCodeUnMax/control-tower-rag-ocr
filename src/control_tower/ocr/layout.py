from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Représente les coordonnées d'une boîte englobante (x0, y0, x1, y1)."""
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def width(self) -> int:
        return max(0, self.x1 - self.x0)

    @property
    def height(self) -> int:
        return max(0, self.y1 - self.y0)


class LayoutBlock(BaseModel):
    """Un bloc d'information structuré détecté par l'OCR."""
    type: Literal["text", "title", "table", "image", "list", "figure"] = "text"
    text: str
    box: BoundingBox
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
