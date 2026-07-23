from __future__ import annotations

from pathlib import Path
from typing import Protocol

from control_tower.config import OCRConfig
from control_tower.ocr.models import ExtractionResult


class OCRProvider(Protocol):
    accepted: set[str]

    def extract(self, source: Path, config: OCRConfig) -> ExtractionResult: ...
