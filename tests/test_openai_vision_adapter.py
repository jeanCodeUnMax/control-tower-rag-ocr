from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from control_tower.config import VisionConfig
from control_tower.processing.models import BatchAnalysis, PageAnalysis, PageProfile, RenderedPage
from control_tower.processing.vision import OpenAIVisionAnalyzer


class FakeResponses:
    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.parsed, output_text="")


class FakeClient:
    def __init__(self, parsed):
        self.responses = FakeResponses(parsed)


def test_openai_adapter_requires_one_structured_result_per_page(tmp_path: Path):
    image_path = tmp_path / "page.png"
    Image.new("RGB", (32, 32), "white").save(image_path)
    parsed = BatchAnalysis(
        pages=[
            PageAnalysis(
                page_number=1,
                provider="openai",
                summary="Un graphe avec une flèche montante.",
                visual_elements=[],
                confidence=0.9,
            )
        ]
    )
    client = FakeClient(parsed)
    analyzer = OpenAIVisionAnalyzer(VisionConfig(provider="openai"), client=client)

    result = analyzer.analyze_batch(
        [RenderedPage(page_number=1, image_path=image_path, native_text="Texte")],
        {
            1: PageProfile(
                page_number=1,
                native_characters=5,
                image_count=1,
                drawing_count=0,
                estimated_context_units=2000,
                requires_visual_analysis=True,
            )
        },
    )

    assert result[0].summary.startswith("Un graphe")
    call = client.responses.calls[0]
    assert call["store"] is False
    assert call["text_format"] is BatchAnalysis
