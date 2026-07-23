from pathlib import Path

from PIL import Image

from control_tower.config import VisionConfig, VisionProviderConfig
from control_tower.processing.models import PageAnalysis, PageProfile, RenderedPage
from control_tower.processing.providers import ProviderHTTPError
from control_tower.processing.routing import RoutedVisionAnalyzer, plan_routes, route_page


class FakeProvider:
    def __init__(self, name: str, *, failures: int = 0, cost: float = 0.0) -> None:
        self.name = name
        self.estimated_cost_per_page_usd = cost
        self.failures = failures
        self.calls = 0

    def analyze(self, page: RenderedPage, profile: PageProfile) -> PageAnalysis:
        self.calls += 1
        if self.calls <= self.failures:
            raise ProviderHTTPError("limite artificielle", status_code=429, retry_after=0.0)
        return PageAnalysis(
            page_number=page.page_number,
            provider=self.name,
            summary=f"Analyse par {self.name}",
            confidence=0.9,
        )


def provider_config(name: str, *, cost: float = 0.0, retries: int = 0) -> VisionProviderConfig:
    return VisionProviderConfig(
        name=name,
        enabled=True,
        model="fake-model",
        base_url="https://example.invalid/v1",
        allow_missing_api_key=True,
        max_retries=retries,
        backoff_base_seconds=0,
        backoff_max_seconds=0.1,
        estimated_cost_per_page_usd=cost,
    )


def page_fixture(tmp_path: Path):
    image = tmp_path / "page.png"
    Image.new("RGB", (32, 32), "white").save(image)
    rendered = RenderedPage(page_number=1, image_path=image, native_text="Texte")
    profile = PageProfile(
        page_number=1,
        native_characters=5,
        image_count=1,
        drawing_count=0,
        estimated_context_units=2000,
        requires_visual_analysis=True,
    )
    return rendered, profile


def test_local_fast_defers_complex_pages_without_cloud_call(tmp_path: Path):
    rendered, profile = page_fixture(tmp_path)
    fake = FakeProvider("cloud")
    config = VisionConfig(
        provider="router",
        profile="local_fast",
        provider_order=["cloud"],
        providers=[provider_config("cloud")],
    )
    analyzer = RoutedVisionAnalyzer(config, providers={"cloud": fake})

    result = analyzer.analyze_batch([rendered], {1: profile})[0]

    assert fake.calls == 0
    assert result.provider == "local"
    assert result.needs_multimodal_review is True
    assert analyzer.report()["deferred_pages"] == [1]


def test_cloud_cascade_uses_second_provider_after_rate_limit(tmp_path: Path):
    rendered, profile = page_fixture(tmp_path)
    first = FakeProvider("first", failures=1)
    second = FakeProvider("second")
    config = VisionConfig(
        provider="router",
        profile="cloud_turbo",
        provider_order=["first", "second"],
        providers=[provider_config("first"), provider_config("second")],
        max_workers=2,
    )
    analyzer = RoutedVisionAnalyzer(
        config,
        providers={"first": first, "second": second},
    )

    result = analyzer.analyze_batch([rendered], {1: profile})[0]

    assert first.calls == 1
    assert second.calls == 1
    assert result.provider == "second"
    assert result.raw["routing"]["selected_provider"] == "second"
    assert result.raw["routing"]["fallback_errors"]


def test_budget_limit_falls_back_to_local(tmp_path: Path):
    rendered, profile = page_fixture(tmp_path)
    expensive = FakeProvider("expensive", cost=2.0)
    config = VisionConfig(
        provider="router",
        profile="cloud_turbo",
        provider_order=["expensive"],
        providers=[provider_config("expensive", cost=2.0)],
        max_cost_per_document_usd=1.0,
    )
    analyzer = RoutedVisionAnalyzer(config, providers={"expensive": expensive})

    result = analyzer.analyze_batch([rendered], {1: profile})[0]

    assert expensive.calls == 0
    assert result.provider == "local"
    assert result.needs_multimodal_review is True
    assert "budget insuffisant" in " ".join(result.warnings)


def test_route_plan_distinguishes_local_cloud_and_deferred():
    simple = PageProfile(
        page_number=1,
        native_characters=1000,
        image_count=0,
        drawing_count=0,
        estimated_context_units=300,
    )
    complex_page = PageProfile(
        page_number=2,
        native_characters=20,
        image_count=1,
        drawing_count=2,
        estimated_context_units=3000,
        requires_visual_analysis=True,
    )

    fast = VisionConfig(profile="local_fast")
    turbo = VisionConfig(profile="cloud_turbo")

    assert route_page(simple, fast) == "local"
    assert route_page(complex_page, fast) == "deferred"
    assert route_page(complex_page, turbo) == "cloud"
    assert plan_routes([simple, complex_page], fast)["counts"] == {
        "local": 1,
        "cloud": 0,
        "deferred": 1,
    }


def test_provider_runtime_retries_rate_limits_before_success(tmp_path: Path):
    rendered, profile = page_fixture(tmp_path)
    flaky = FakeProvider("flaky", failures=2)
    config = VisionConfig(
        provider="router",
        profile="cloud_turbo",
        provider_order=["flaky"],
        providers=[provider_config("flaky", retries=2)],
    )
    analyzer = RoutedVisionAnalyzer(config, providers={"flaky": flaky})

    result = analyzer.analyze_batch([rendered], {1: profile})[0]
    report = analyzer.report()["providers"][0]["stats"]

    assert result.provider == "flaky"
    assert flaky.calls == 3
    assert report["retries"] == 2
    assert report["successes"] == 1
