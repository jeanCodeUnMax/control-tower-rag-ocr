from __future__ import annotations

import base64
import json
import os
import re
import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Protocol

from control_tower.config import VisionProviderConfig
from control_tower.processing.models import PageAnalysis, PageProfile, RenderedPage


class PageVisionProvider(Protocol):
    name: str
    estimated_cost_per_page_usd: float

    def analyze(self, page: RenderedPage, profile: PageProfile) -> PageAnalysis: ...


class ProviderHTTPError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after

    @property
    def retryable(self) -> bool:
        return self.status_code in {408, 409, 425, 429} or (
            self.status_code is not None and self.status_code >= 500
        )


class OpenAICompatiblePageProvider:
    """Provider vision compatible Chat Completions.

    Fonctionne avec OpenRouter, Ollama local et Ollama Cloud. Les appels sont
    volontairement faits avec la bibliothèque standard pour garder le cœur léger.
    """

    def __init__(self, config: VisionProviderConfig) -> None:
        self.config = config
        self.name = config.name
        self.estimated_cost_per_page_usd = config.estimated_cost_per_page_usd

    def analyze(self, page: RenderedPage, profile: PageProfile) -> PageAnalysis:
        api_key = self._api_key()
        endpoint = self.config.base_url.rstrip("/") + "/chat/completions"
        schema = PageAnalysis.model_json_schema()
        response_format: dict[str, Any]
        if self.config.strict_json_schema:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "page_analysis",
                    "strict": True,
                    "schema": schema,
                },
            }
        else:
            response_format = {"type": "json_object"}

        payload: dict[str, Any] = {
            "model": self.config.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _page_prompt(page, profile)},
                        {
                            "type": "image_url",
                            "image_url": {"url": _data_url(page.image_path)},
                        },
                    ],
                }
            ],
            "response_format": response_format,
        }
        if self.config.provider_options:
            payload["provider"] = self.config.provider_options

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            **self.config.headers,
        }
        raw = _post_json(endpoint, payload, headers, self.config.timeout_seconds)
        try:
            content = raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Réponse {self.name} sans contenu exploitable: {raw}") from exc
        text = _content_to_text(content)
        result = _parse_page_analysis(text, page.page_number, self.name)
        result.raw.update(
            {
                "provider": self.name,
                "model": self.config.model,
                "endpoint": endpoint,
            }
        )
        return result

    def _api_key(self) -> str:
        if self.config.api_key_env:
            value = os.getenv(self.config.api_key_env)
            if value:
                return value
        if self.config.allow_missing_api_key:
            return "ollama"
        raise RuntimeError(
            f"Provider {self.name}: définir la variable {self.config.api_key_env}."
        )


class GeminiPageProvider:
    """Provider Gemini REST natif avec image inline et sortie JSON structurée."""

    def __init__(self, config: VisionProviderConfig) -> None:
        self.config = config
        self.name = config.name
        self.estimated_cost_per_page_usd = config.estimated_cost_per_page_usd

    def analyze(self, page: RenderedPage, profile: PageProfile) -> PageAnalysis:
        if not self.config.api_key_env or not os.getenv(self.config.api_key_env):
            raise RuntimeError(
                f"Provider {self.name}: définir la variable {self.config.api_key_env}."
            )
        api_key = os.environ[self.config.api_key_env]
        endpoint = (
            self.config.base_url.rstrip("/")
            + f"/models/{self.config.model}:generateContent"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": _page_prompt(page, profile)},
                        {
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": base64.b64encode(page.image_path.read_bytes()).decode("ascii"),
                            }
                        },
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
                "responseJsonSchema": PageAnalysis.model_json_schema(),
            },
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
            **self.config.headers,
        }
        raw = _post_json(endpoint, payload, headers, self.config.timeout_seconds)
        try:
            parts = raw["candidates"][0]["content"]["parts"]
            text = "\n".join(part.get("text", "") for part in parts if part.get("text"))
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Réponse {self.name} sans contenu exploitable: {raw}") from exc
        result = _parse_page_analysis(text, page.page_number, self.name)
        result.raw.update(
            {
                "provider": self.name,
                "model": self.config.model,
                "endpoint": endpoint,
            }
        )
        return result


def build_page_provider(config: VisionProviderConfig) -> PageVisionProvider:
    if config.kind == "gemini":
        return GeminiPageProvider(config)
    return OpenAICompatiblePageProvider(config)


def _page_prompt(page: RenderedPage, profile: PageProfile) -> str:
    native = page.native_text[:12_000]
    return (
        "Réponds uniquement avec un objet JSON conforme au schéma PageAnalysis. "
        f"La page_number doit être exactement {page.page_number}. "
        "Analyse la page sans inventer: texte imprimé, manuscrit, tableaux, équations, "
        "graphes, axes, légendes, flèches, dessins techniques, icônes et symboles. "
        "Décris les relations visuelles, extrais les concepts, le pseudocode réellement "
        "présent ou clairement implicite, deux questions maïeutiques utiles et les tensions "
        "kantiennes pertinentes. Mets les incertitudes dans warnings. "
        f"Profil détecté: images={profile.image_count}, dessins={profile.drawing_count}, "
        f"OCR_requis={profile.requires_ocr}, analyse_visuelle={profile.requires_visual_analysis}.\n"
        f"Texte natif/OCR déjà disponible:\n{native}"
    )


def _data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _post_json(
    endpoint: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: int,
) -> dict[str, Any]:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        retry_after_raw = exc.headers.get("Retry-After") if exc.headers else None
        try:
            retry_after = float(retry_after_raw) if retry_after_raw else None
        except ValueError:
            retry_after = None
        raise ProviderHTTPError(
            f"HTTP {exc.code} sur {endpoint}: {body[:1000]}",
            status_code=exc.code,
            retry_after=retry_after,
        ) from exc
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        raise ProviderHTTPError(f"Connexion impossible vers {endpoint}: {exc}") from exc


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        values: list[str] = []
        for item in content:
            if isinstance(item, str):
                values.append(item)
            elif isinstance(item, dict):
                value = item.get("text") or item.get("content")
                if isinstance(value, str):
                    values.append(value)
        return "\n".join(values)
    return str(content)


def _parse_page_analysis(text: str, page_number: int, provider: str) -> PageAnalysis:
    cleaned = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON invalide retourné par {provider}: {cleaned[:1000]}") from exc
    if isinstance(payload, dict) and "pages" in payload:
        pages = payload.get("pages") or []
        if len(pages) != 1:
            raise RuntimeError(f"{provider} a retourné {len(pages)} pages au lieu d'une.")
        payload = pages[0]
    if not isinstance(payload, dict):
        raise RuntimeError(f"{provider} n'a pas retourné un objet JSON.")
    payload["page_number"] = page_number
    payload["provider"] = provider
    return PageAnalysis.model_validate(payload)
