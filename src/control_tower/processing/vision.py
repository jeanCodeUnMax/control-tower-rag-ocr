from __future__ import annotations

import base64
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Protocol

from control_tower.config import VisionConfig
from control_tower.processing.models import (
    BatchAnalysis,
    PageAnalysis,
    PageProfile,
    RenderedPage,
    VisualElement,
)
from control_tower.semantics.pseudocode import PseudocodeAnalyzer


class VisionAnalyzer(Protocol):
    provider_name: str

    def analyze_batch(
        self,
        pages: list[RenderedPage],
        profiles: dict[int, PageProfile],
    ) -> list[PageAnalysis]: ...


class LocalVisionAnalyzer:
    """Mode sans API.

    Il inventorie les éléments visuels détectés par PyMuPDF et applique des
    heuristiques au texte. Il ne prétend pas comprendre un graphe ou un manuscrit.
    """

    provider_name = "local"
    _symbol_pattern = re.compile(r"[→←↑↓↔⇒⇔≠≤≥≈±∞∑∏√∆ΔΩµαβγλπσ∫∂%‰§©®™]")
    _word_pattern = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][\wÀ-ÖØ-öø-ÿ-]{3,}")
    _stopwords = {
        "avec", "dans", "pour", "mais", "plus", "cette", "comme", "tout", "tous",
        "une", "des", "les", "est", "sont", "sur", "par", "que", "qui", "donc",
        "the", "and", "with", "from", "this", "that", "into", "page", "document",
    }

    def __init__(self, startup_warnings: list[str] | None = None) -> None:
        self.pseudocode = PseudocodeAnalyzer()
        self.startup_warnings = startup_warnings or []

    def analyze_batch(
        self,
        pages: list[RenderedPage],
        profiles: dict[int, PageProfile],
    ) -> list[PageAnalysis]:
        analyses: list[PageAnalysis] = []
        for page in pages:
            profile = profiles[page.page_number]
            visual_elements: list[VisualElement] = []
            if profile.image_count:
                visual_elements.append(
                    VisualElement(
                        type="embedded_images",
                        description=(
                            f"{profile.image_count} image(s) embarquée(s) détectée(s). "
                            "Le mode local ne décrit pas leur sens."
                        ),
                    )
                )
            if profile.drawing_count:
                visual_elements.append(
                    VisualElement(
                        type="vector_drawings",
                        description=(
                            f"{profile.drawing_count} élément(s) vectoriel(s) détecté(s). "
                            "Le mode local ne déduit pas leur rôle."
                        ),
                    )
                )
            text = page.native_text.strip()
            symbols = sorted(set(self._symbol_pattern.findall(text)))
            concepts = self._concepts(text)
            warnings: list[str] = list(self.startup_warnings)
            needs_review = bool(profile.requires_visual_analysis or profile.requires_ocr)
            if needs_review:
                warnings.append(
                    "Analyse locale limitée: activer vision.provider=router ou openai pour comprendre "
                    "graphes, symboles visuels et manuscrit."
                )
            analyses.append(
                PageAnalysis(
                    page_number=page.page_number,
                    provider=self.provider_name,
                    summary=self._summary(text),
                    extracted_text=text,
                    visual_elements=visual_elements,
                    symbols=symbols,
                    pseudocode=self.pseudocode.analyze_text(text),
                    concepts=concepts,
                    maieutic_questions=[
                        "Quelle hypothèse implicite porte cette page ?",
                        "Quel élément visuel ou textuel manque pour vérifier son interprétation ?",
                    ],
                    kant_tensions=self._kant_tensions(text),
                    confidence=0.55 if text else 0.2,
                    needs_multimodal_review=needs_review,
                    warnings=warnings,
                    raw={
                        "image_count": profile.image_count,
                        "drawing_count": profile.drawing_count,
                        "text_block_count": profile.text_block_count,
                    },
                )
            )
        return analyses

    @classmethod
    def _summary(cls, text: str) -> str:
        compact = " ".join(text.split())
        if not compact:
            return "Page sans texte natif exploitable."
        return compact[:600]

    @classmethod
    def _concepts(cls, text: str) -> list[str]:
        words = [word.casefold() for word in cls._word_pattern.findall(text)]
        counts = Counter(word for word in words if word not in cls._stopwords)
        return [word for word, _ in counts.most_common(12)]

    @staticmethod
    def _kant_tensions(text: str) -> list[str]:
        lower = text.casefold()
        tensions = ["facts_vs_interpretations"] if text.strip() else []
        if any(item in lower for item in ("afin", "pour ", "objectif", "but")):
            tensions.append("means_vs_ends")
        if any(item in lower for item in ("donc", "parce", "cause", "entraîne")):
            tensions.append("causation_vs_correlation")
        if any(item in lower for item in ("toujours", "chaque", "jamais", "tous")):
            tensions.append("universalization")
        return sorted(set(tensions))


class OpenAIVisionAnalyzer:
    """Analyse multimodale structurée via l'API Responses.

    Le client peut être injecté dans les tests. Sans injection, le paquet optionnel
    `openai` et la variable définie dans VisionConfig.api_key_env sont nécessaires.
    """

    provider_name = "openai"

    def __init__(self, config: VisionConfig, client: object | None = None) -> None:
        self.config = config
        self.client = client or self._build_client()

    def _build_client(self) -> object:
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Clé API absente: définir {self.config.api_key_env} ou utiliser vision.provider=local."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "Le provider OpenAI nécessite l'option d'installation: pip install -e '.[vision]'."
            ) from exc
        return OpenAI(api_key=api_key, timeout=self.config.timeout_seconds)

    def analyze_batch(
        self,
        pages: list[RenderedPage],
        profiles: dict[int, PageProfile],
    ) -> list[PageAnalysis]:
        if not pages:
            return []
        content: list[dict[str, str]] = [
            {
                "type": "input_text",
                "text": self._prompt(pages, profiles),
            }
        ]
        for page in pages:
            content.append(
                {
                    "type": "input_text",
                    "text": f"PAGE {page.page_number}",
                }
            )
            content.append(
                {
                    "type": "input_image",
                    "image_url": self._data_url(page.image_path),
                    "detail": self.config.detail,
                }
            )
        response = self.client.responses.parse(
            model=self.config.model,
            input=[{"role": "user", "content": content}],
            text_format=BatchAnalysis,
            store=False,
        )
        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            output_text = getattr(response, "output_text", "")
            if not output_text:
                raise RuntimeError("Le provider multimodal n'a retourné aucune analyse structurée.")
            parsed = BatchAnalysis.model_validate_json(output_text)
        analyses = parsed.pages if isinstance(parsed, BatchAnalysis) else parsed["pages"]
        by_number = {item.page_number: item for item in analyses}
        expected = {page.page_number for page in pages}
        if set(by_number) != expected:
            raise RuntimeError(
                "Réponse multimodale incomplète: "
                f"attendu={sorted(expected)}, reçu={sorted(by_number)}"
            )
        return [by_number[number] for number in sorted(expected)]

    def _prompt(
        self,
        pages: list[RenderedPage],
        profiles: dict[int, PageProfile],
    ) -> str:
        page_descriptions: list[str] = []
        for page in pages:
            profile = profiles[page.page_number]
            native = page.native_text[:8000] if self.config.include_native_text_in_prompt else ""
            page_descriptions.append(
                f"PAGE {page.page_number}: images={profile.image_count}, "
                f"dessins={profile.drawing_count}, OCR_requis={profile.requires_ocr}.\n"
                f"Texte natif éventuel:\n{native}"
            )
        return (
            "Analyse séparément chaque page fournie. Ne fusionne jamais deux pages. "
            "Lis le texte imprimé et manuscrit, décris les dessins, diagrammes, graphes, "
            "axes, légendes, flèches, tableaux et symboles. Extrais les concepts, les "
            "étapes de pseudocode réellement présentes ou clairement implicites, puis "
            "produis des questions maïeutiques et des tensions de type kantien. "
            "N'invente aucune donnée de graphe illisible. Signale l'incertitude dans warnings. "
            "Retourne exactement une PageAnalysis par numéro de page.\n\n"
            + "\n\n".join(page_descriptions)
        )

    @staticmethod
    def _data_url(path: Path) -> str:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"


class ResilientVisionAnalyzer:
    provider_name = "openai_with_local_fallback"

    def __init__(self, primary: VisionAnalyzer, fallback: LocalVisionAnalyzer) -> None:
        self.primary = primary
        self.fallback = fallback

    def analyze_batch(
        self,
        pages: list[RenderedPage],
        profiles: dict[int, PageProfile],
    ) -> list[PageAnalysis]:
        try:
            return self.primary.analyze_batch(pages, profiles)
        except Exception as exc:
            fallback = LocalVisionAnalyzer(
                [f"Analyse multimodale échouée, repli local: {exc}"]
            )
            return fallback.analyze_batch(pages, profiles)


def build_vision_analyzer(config: VisionConfig, client: object | None = None) -> VisionAnalyzer:
    if not config.enabled:
        return LocalVisionAnalyzer(["Analyse visuelle désactivée par configuration."])
    if config.provider == "router":
        # Import tardif pour éviter une dépendance circulaire: routing utilise
        # LocalVisionAnalyzer comme repli déterministe.
        from control_tower.processing.routing import RoutedVisionAnalyzer

        return RoutedVisionAnalyzer(config)
    if config.provider == "openai":
        try:
            primary = OpenAIVisionAnalyzer(config, client=client)
        except Exception as exc:
            if config.require_provider_success:
                raise
            return LocalVisionAnalyzer([f"Provider OpenAI indisponible, repli local: {exc}"])
        if config.require_provider_success:
            return primary
        return ResilientVisionAnalyzer(primary, LocalVisionAnalyzer())
    return LocalVisionAnalyzer()
