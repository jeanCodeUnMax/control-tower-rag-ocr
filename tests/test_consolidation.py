from control_tower.config import ConsolidationConfig
from control_tower.domain.models import AtomicChunk, DuplicateKind
from control_tower.optimization.consolidator import Consolidator
from control_tower.processing.models import AssetKind, VisualAsset


def chunk(identifier: str, ordinal: int, text: str) -> AtomicChunk:
    return AtomicChunk(
        id=identifier,
        project_id="demo",
        document_id="doc",
        ordinal=ordinal,
        text=text,
        content_hash=identifier,
        source_pages=[ordinal + 1],
    )


class FakeSemanticEmbedder:
    name = "fake-semantic"

    def embed(self, texts):
        vectors = []
        for text in texts:
            if "urgence" in text or "immédiat" in text:
                vectors.append([1.0, 0.2, 0.1, 0.0])
            else:
                vectors.append([0.0, 1.0, 0.1, 0.2])
        return vectors


def test_exact_near_and_semantic_duplicates_keep_occurrences():
    config = ConsolidationConfig(
        near_duplicate_threshold=0.82,
        semantic_embeddings=True,
        semantic_duplicate_threshold=0.99,
        minimum_text_chars=10,
    )
    chunks = [
        chunk("a", 0, "Toujours arrêter la machine avant toute intervention de maintenance."),
        chunk("b", 1, "Toujours arrêter la machine avant toute intervention de maintenance."),
        chunk("c", 2, "Toujours arrêter la machine avant une intervention de maintenance."),
        chunk("d", 3, "Déclencher l'arrêt d'urgence de la machine."),
        chunk("e", 4, "Effectuer un arrêt immédiat de l'équipement."),
    ]

    consolidated, _, report = Consolidator(
        config=config,
        embedder=FakeSemanticEmbedder(),
    ).consolidate(chunks)

    assert report.exact_duplicates == 1
    assert report.near_duplicates >= 1
    assert report.semantic_duplicates >= 1
    canonical = [item for item in consolidated if item.indexable]
    duplicates = [item for item in consolidated if not item.indexable]
    assert len(canonical) + len(duplicates) == 5
    assert any(item.duplicate_kind == DuplicateKind.SEMANTIC for item in duplicates)
    assert sum(len(item.evidence_occurrences) for item in canonical) == 5


def test_repeated_visual_assets_are_canonicalized():
    assets = [
        VisualAsset(
            id="img-a",
            document_id="doc",
            page_number=1,
            kind=AssetKind.EMBEDDED_IMAGE,
            exact_hash="same",
            perceptual_hash="0000000000000000",
        ),
        VisualAsset(
            id="img-b",
            document_id="doc",
            page_number=20,
            kind=AssetKind.EMBEDDED_IMAGE,
            exact_hash="same",
            perceptual_hash="0000000000000000",
        ),
    ]

    _, consolidated_assets, report = Consolidator().consolidate([], assets)

    assert report.raw_assets == 2
    assert report.canonical_assets == 1
    assert report.duplicate_assets == 1
    assert consolidated_assets[1].canonical_asset_id == "img-a"
