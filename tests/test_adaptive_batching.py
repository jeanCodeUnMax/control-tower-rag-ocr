from control_tower.config import BatchConfig
from control_tower.processing.batching import AdaptiveBatchPlanner
from control_tower.processing.models import PageProfile


def profile(page: int, units: int) -> PageProfile:
    return PageProfile(
        page_number=page,
        native_characters=100,
        image_count=0,
        drawing_count=0,
        estimated_context_units=units,
    )


def test_planner_uses_context_budget_instead_of_fixed_five_pages():
    planner = AdaptiveBatchPlanner(
        BatchConfig(min_pages=1, max_pages=5, max_context_units=1000)
    )
    batches = planner.plan(
        [profile(1, 200), profile(2, 200), profile(3, 900), profile(4, 100), profile(5, 100)]
    )

    assert [batch.page_numbers for batch in batches] == [[1, 2], [3, 4], [5]]
    assert all(len(batch.page_numbers) <= 5 for batch in batches)
