from __future__ import annotations

from control_tower.config import BatchConfig
from control_tower.processing.models import PageBatch, PageProfile


class AdaptiveBatchPlanner:
    """Crée des lots contigus et bornés par pages + charge estimée.

    La taille n'est jamais supposée fixe. Une page lourde peut être seule ;
    plusieurs pages simples peuvent partager un lot jusqu'à max_pages.
    """

    def __init__(self, config: BatchConfig) -> None:
        self.config = config

    def plan(self, profiles: list[PageProfile]) -> list[PageBatch]:
        if not profiles:
            return []
        profiles = sorted(profiles, key=lambda item: item.page_number)
        batches: list[PageBatch] = []
        current_pages: list[int] = []
        current_units = 0

        for profile in profiles:
            page_units = max(1, profile.estimated_context_units)
            would_exceed_pages = len(current_pages) >= self.config.max_pages
            would_exceed_units = (
                bool(current_pages)
                and current_units + page_units > self.config.max_context_units
                and len(current_pages) >= self.config.min_pages
            )
            if would_exceed_pages or would_exceed_units:
                batches.append(
                    PageBatch(
                        page_numbers=current_pages,
                        estimated_context_units=current_units,
                    )
                )
                current_pages = []
                current_units = 0

            current_pages.append(profile.page_number)
            current_units += page_units

            # Une page isolée dépassant le budget est tout de même traitée seule.
            if page_units > self.config.max_context_units:
                batches.append(
                    PageBatch(
                        page_numbers=current_pages,
                        estimated_context_units=current_units,
                    )
                )
                current_pages = []
                current_units = 0

        if current_pages:
            batches.append(
                PageBatch(
                    page_numbers=current_pages,
                    estimated_context_units=current_units,
                )
            )
        return batches

    @staticmethod
    def split(batch: PageBatch) -> tuple[PageBatch, PageBatch] | None:
        if len(batch.page_numbers) <= 1:
            return None
        midpoint = len(batch.page_numbers) // 2
        left_pages = batch.page_numbers[:midpoint]
        right_pages = batch.page_numbers[midpoint:]
        left_ratio = len(left_pages) / len(batch.page_numbers)
        left_units = max(1, round(batch.estimated_context_units * left_ratio))
        right_units = max(1, batch.estimated_context_units - left_units)
        return (
            PageBatch(
                page_numbers=left_pages,
                estimated_context_units=left_units,
                attempt=batch.attempt + 1,
                parent_batch_id=batch.id,
            ),
            PageBatch(
                page_numbers=right_pages,
                estimated_context_units=right_units,
                attempt=batch.attempt + 1,
                parent_batch_id=batch.id,
            ),
        )
