from pathlib import Path

from PIL import Image

from control_tower.config import VisionProviderConfig
from control_tower.processing.models import PageProfile, RenderedPage
from control_tower.processing.providers import GeminiPageProvider, OpenAICompatiblePageProvider


def page_fixture(tmp_path: Path):
    image = tmp_path / "page.png"
    Image.new("RGB", (40, 40), "white").save(image)
    page = RenderedPage(page_number=7, image_path=image, native_text="Texte source")
    profile = PageProfile(
        page_number=7,
        native_characters=12,
        image_count=1,
        drawing_count=1,
        estimated_context_units=3000,
        requires_visual_analysis=True,
    )
    return page, profile


def analysis_payload(provider: str):
    return {
        "page_number": 7,
        "provider": provider,
        "summary": "Schéma analysé",
        "confidence": 0.9,
    }


def test_openai_compatible_contract_contains_image_schema_and_router_options(
    tmp_path: Path, monkeypatch
):
    page, profile = page_fixture(tmp_path)
    captured = {}

    def fake_post(endpoint, payload, headers, timeout):
        captured.update(
            endpoint=endpoint,
            payload=payload,
            headers=headers,
            timeout=timeout,
        )
        import json

        return {"choices": [{"message": {"content": json.dumps(analysis_payload("raw"))}}]}

    monkeypatch.setattr("control_tower.processing.providers._post_json", fake_post)
    config = VisionProviderConfig(
        name="openrouter_test",
        enabled=True,
        model="qwen/qwen3-vl-32b-instruct",
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        provider_options={"sort": "throughput", "allow_fallbacks": True},
    )
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    result = OpenAICompatiblePageProvider(config).analyze(page, profile)

    content = captured["payload"]["messages"][0]["content"]
    assert captured["endpoint"].endswith("/chat/completions")
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert captured["payload"]["response_format"]["type"] == "json_schema"
    assert captured["payload"]["provider"]["sort"] == "throughput"
    assert result.provider == "openrouter_test"
    assert result.page_number == 7


def test_gemini_contract_contains_inline_image_and_response_schema(tmp_path: Path, monkeypatch):
    page, profile = page_fixture(tmp_path)
    captured = {}

    def fake_post(endpoint, payload, headers, timeout):
        captured.update(endpoint=endpoint, payload=payload, headers=headers, timeout=timeout)
        import json

        return {
            "candidates": [
                {"content": {"parts": [{"text": json.dumps(analysis_payload("raw"))}]}}
            ]
        }

    monkeypatch.setattr("control_tower.processing.providers._post_json", fake_post)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    config = VisionProviderConfig(
        name="gemini_test",
        kind="gemini",
        enabled=True,
        model="gemini-test",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        api_key_env="GEMINI_API_KEY",
    )

    result = GeminiPageProvider(config).analyze(page, profile)

    parts = captured["payload"]["contents"][0]["parts"]
    assert captured["endpoint"].endswith("/models/gemini-test:generateContent")
    assert parts[1]["inlineData"]["mimeType"] == "image/png"
    assert captured["payload"]["generationConfig"]["responseMimeType"] == "application/json"
    assert "responseJsonSchema" in captured["payload"]["generationConfig"]
    assert captured["headers"]["x-goog-api-key"] == "test-key"
    assert result.provider == "gemini_test"
