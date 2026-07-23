from __future__ import annotations

import hashlib
import json
from io import BytesIO
from pathlib import Path
from typing import Any

import fitz
from PIL import Image

from control_tower.processing.models import AssetKind, VisualAsset


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dhash(image: Image.Image) -> str:
    gray = image.convert("L").resize((9, 8))
    pixels = list(gray.getdata())
    bits: list[int] = []
    for row in range(8):
        offset = row * 9
        for column in range(8):
            bits.append(1 if pixels[offset + column] > pixels[offset + column + 1] else 0)
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return f"{value:016x}"


def hamming_distance(hash_a: str, hash_b: str) -> int:
    return (int(hash_a, 16) ^ int(hash_b, 16)).bit_count()


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in sorted(value.items(), key=lambda x: str(x[0]))}
    if hasattr(value, "x") and hasattr(value, "y"):
        return {"x": round(float(value.x), 4), "y": round(float(value.y), 4)}
    if hasattr(value, "x0") and hasattr(value, "y0") and hasattr(value, "x1") and hasattr(value, "y1"):
        return {
            "x0": round(float(value.x0), 4),
            "y0": round(float(value.y0), 4),
            "x1": round(float(value.x1), 4),
            "y1": round(float(value.y1), 4),
        }
    return repr(value)


def extract_visual_assets(
    source: Path,
    document_id: str,
    page_numbers: list[int],
    output_dir: Path,
) -> list[VisualAsset]:
    output_dir.mkdir(parents=True, exist_ok=True)
    assets: list[VisualAsset] = []
    with fitz.open(source) as document:
        for page_number in sorted(set(page_numbers)):
            page = document.load_page(page_number - 1)
            for image_index, image_info in enumerate(page.get_images(full=True), start=1):
                xref = image_info[0]
                extracted = document.extract_image(xref)
                data = extracted["image"]
                extension = extracted.get("ext", "bin")
                asset_path = output_dir / f"page_{page_number:05d}_image_{image_index:03d}.{extension}"
                asset_path.write_bytes(data)
                perceptual_hash: str | None = None
                width = extracted.get("width")
                height = extracted.get("height")
                try:
                    with Image.open(BytesIO(data)) as image:
                        perceptual_hash = _dhash(image)
                        width, height = image.size
                except Exception:
                    pass
                assets.append(
                    VisualAsset(
                        document_id=document_id,
                        page_number=page_number,
                        kind=AssetKind.EMBEDDED_IMAGE,
                        exact_hash=_sha256(data),
                        perceptual_hash=perceptual_hash,
                        file_path=str(asset_path),
                        metadata={
                            "xref": xref,
                            "width": width,
                            "height": height,
                            "extension": extension,
                        },
                    )
                )

            for drawing_index, drawing in enumerate(page.get_drawings(), start=1):
                normalized = _jsonable(drawing)
                payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True).encode("utf-8")
                asset_path = output_dir / f"page_{page_number:05d}_drawing_{drawing_index:03d}.json"
                asset_path.write_text(
                    json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True),
                    encoding="utf-8",
                )
                assets.append(
                    VisualAsset(
                        document_id=document_id,
                        page_number=page_number,
                        kind=AssetKind.VECTOR_DRAWING,
                        exact_hash=_sha256(payload),
                        file_path=str(asset_path),
                        metadata={"drawing_index": drawing_index},
                    )
                )
    return assets
