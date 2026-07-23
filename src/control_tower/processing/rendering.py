from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image

from control_tower.processing.models import PageProfile, RenderedPage


def render_pdf_pages(
    source: Path,
    page_numbers: list[int],
    output_dir: Path,
    *,
    dpi: int = 144,
    profiles: dict[int, PageProfile] | None = None,
) -> list[RenderedPage]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[RenderedPage] = []
    zoom = dpi / 72
    with fitz.open(source) as document:
        for page_number in sorted(set(page_numbers)):
            page = document.load_page(page_number - 1)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            image_path = output_dir / f"page_{page_number:05d}.png"
            image.save(image_path, format="PNG", optimize=True)
            profile = profiles.get(page_number) if profiles else None
            rendered.append(
                RenderedPage(
                    page_number=page_number,
                    image_path=image_path,
                    native_text=page.get_text("text", sort=True).strip(),
                    image_count=profile.image_count if profile else len(page.get_images(full=True)),
                    drawing_count=profile.drawing_count if profile else len(page.get_drawings()),
                )
            )
    return rendered
