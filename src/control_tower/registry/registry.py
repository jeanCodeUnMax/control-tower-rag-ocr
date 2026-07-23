from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Capability:
    name: str
    version: str
    description: str
    status: str = "wired"
    factory: Callable | None = None


class Registry:
    def __init__(self) -> None:
        self._items: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        if capability.name in self._items:
            raise ValueError(f"Capacité déjà enregistrée: {capability.name}")
        self._items[capability.name] = capability

    def get(self, name: str) -> Capability:
        try:
            return self._items[name]
        except KeyError as exc:
            raise KeyError(f"Capacité inconnue: {name}") from exc

    def list(self) -> list[Capability]:
        return sorted(self._items.values(), key=lambda item: item.name)


def build_default_registry() -> Registry:
    registry = Registry()
    for capability in (
        Capability("policy", "0.2", "Contrôle l'ingestion selon la configuration du projet."),
        Capability("text_ocr", "0.3", "Extrait le texte des fichiers TXT et Markdown."),
        Capability("pdf_native_extraction", "0.3", "Extrait le texte natif page par page avec PyMuPDF."),
        Capability("pdf_image_ocr", "0.3", "OCR hybride PDF/image via Tesseract, piloté par projet."),
        Capability("atomizer", "0.2", "Découpe le texte selon max_chars et overlap_chars."),
        Capability("maieutic", "0.1", "Ajoute des questions heuristiques aux chunks."),
        Capability("kant_glove", "0.1", "Ajoute des tensions sémantiques heuristiques."),
        Capability("sqlite_store", "0.1", "Persiste chunks, dépendances et états."),
        Capability("lexical_search", "0.1", "Recherche locale par recouvrement de termes."),
        Capability("hydration", "0.2", "Construit un contexte borné par un budget de caractères."),
        Capability(
            "consensusless", "0.1", "Évaluateur disponible mais non relié au pipeline principal.", "available"
        ),
        Capability(
            "background_consolidation",
            "0.1",
            "Propose des doublons mais ne s'exécute pas automatiquement.",
            "available",
        ),
        Capability("vector_embeddings", "0.0", "Adaptateur non implémenté.", "not_implemented"),
        Capability("llm_answering", "0.0", "Adaptateur non implémenté.", "not_implemented"),
    ):
        registry.register(capability)
    return registry
