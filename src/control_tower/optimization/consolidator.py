from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher

from control_tower.config import ConsolidationConfig
from control_tower.domain.models import AtomicChunk, DuplicateKind, EvidenceOccurrence
from control_tower.optimization.embeddings import EmbeddingProvider, OpenAIEmbeddingProvider
from control_tower.processing.assets import hamming_distance
from control_tower.processing.models import ConsolidationReport, VisualAsset
from control_tower.storage.sqlite import SQLiteStore


def _normalized(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[\wÀ-ÖØ-öø-ÿ]+", _normalized(text), flags=re.UNICODE)
        if len(token) > 2
    }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def _minhash_buckets(tokens: set[str]) -> list[str]:
    if not tokens:
        return []
    hashes = sorted(hashlib.sha1(token.encode("utf-8")).hexdigest() for token in tokens)
    return hashes[:4]


def _vector_bands(vector: list[float], band_count: int = 8) -> list[tuple[int, int]]:
    if not vector:
        return []
    bits: list[int] = []
    projection_count = band_count * 8
    for projection in range(projection_count):
        total = 0.0
        for index in range(projection, len(vector), projection_count):
            total += vector[index]
        bits.append(1 if total >= 0 else 0)
    bands: list[tuple[int, int]] = []
    for band in range(band_count):
        value = 0
        for bit in bits[band * 8 : (band + 1) * 8]:
            value = (value << 1) | bit
        bands.append((band, value))
    return bands


class Consolidator:
    """Consolide sans supprimer les preuves.

    Tous les chunks restent stockés. Seuls les canoniques sont indexables ; les
    répétitions deviennent des occurrences rattachées au canonique.
    """

    def __init__(
        self,
        store: SQLiteStore | None = None,
        *,
        config: ConsolidationConfig | None = None,
        embedder: EmbeddingProvider | None = None,
    ) -> None:
        self.store = store
        self.config = config or ConsolidationConfig()
        self.embedder = embedder

    def consolidate(
        self,
        chunks: list[AtomicChunk],
        assets: list[VisualAsset] | None = None,
    ) -> tuple[list[AtomicChunk], list[VisualAsset], ConsolidationReport]:
        assets = list(assets or [])
        if not self.config.enabled:
            self._attach_self_occurrences(chunks)
            return chunks, assets, ConsolidationReport(
                raw_chunks=len(chunks),
                canonical_chunks=len(chunks),
                exact_duplicates=0,
                near_duplicates=0,
                semantic_duplicates=0,
                raw_assets=len(assets),
                canonical_assets=len(assets),
                duplicate_assets=0,
                semantic_stage="disabled",
            )

        working = [chunk.model_copy(deep=True) for chunk in chunks]
        exact = self._exact_text(working) if self.config.exact_text else 0
        near = self._near_text(working) if self.config.near_text else 0
        semantic = 0
        semantic_stage = "disabled"
        warnings: list[str] = []
        if self.config.semantic_embeddings:
            try:
                embedder = self.embedder or OpenAIEmbeddingProvider(self.config)
                semantic = self._semantic_text(working, embedder)
                semantic_stage = embedder.name
            except Exception as exc:
                semantic_stage = "skipped"
                warnings.append(f"Consolidation sémantique ignorée: {exc}")

        self._attach_occurrences(working)
        consolidated_assets, duplicate_assets = self._assets(assets)
        canonical_chunks = sum(1 for chunk in working if chunk.indexable)
        canonical_assets = sum(1 for asset in consolidated_assets if asset.indexable)
        report = ConsolidationReport(
            raw_chunks=len(working),
            canonical_chunks=canonical_chunks,
            exact_duplicates=exact,
            near_duplicates=near,
            semantic_duplicates=semantic,
            raw_assets=len(consolidated_assets),
            canonical_assets=canonical_assets,
            duplicate_assets=duplicate_assets,
            semantic_stage=semantic_stage,
            warnings=warnings,
        )
        return working, consolidated_assets, report

    def propose(self) -> list[dict]:
        if self.store is None:
            return []
        by_hash: dict[str, list[str]] = {}
        for chunk in self.store.all_chunks():
            by_hash.setdefault(chunk.content_hash, []).append(chunk.id)
        return [
            {"type": "duplicate_chunks", "chunk_ids": ids, "action": "review_merge"}
            for ids in by_hash.values()
            if len(ids) > 1
        ]

    def _exact_text(self, chunks: list[AtomicChunk]) -> int:
        canonical_by_hash: dict[str, AtomicChunk] = {}
        duplicates = 0
        for chunk in sorted(chunks, key=lambda item: item.ordinal):
            if not chunk.indexable or len(chunk.text.strip()) < self.config.minimum_text_chars:
                continue
            digest = hashlib.sha256(_normalized(chunk.text).encode("utf-8")).hexdigest()
            canonical = canonical_by_hash.get(digest)
            if canonical is None:
                canonical_by_hash[digest] = chunk
                continue
            self._mark_duplicate(chunk, canonical, DuplicateKind.EXACT, 1.0)
            duplicates += 1
        return duplicates

    def _near_text(self, chunks: list[AtomicChunk]) -> int:
        buckets: dict[str, list[AtomicChunk]] = defaultdict(list)
        token_cache: dict[str, set[str]] = {}
        duplicates = 0
        for chunk in sorted(chunks, key=lambda item: item.ordinal):
            if not chunk.indexable or len(chunk.text.strip()) < self.config.minimum_text_chars:
                continue
            tokens = _tokens(chunk.text)
            token_cache[chunk.id] = tokens
            candidate_map: dict[str, AtomicChunk] = {}
            for bucket in _minhash_buckets(tokens):
                for candidate in buckets[bucket]:
                    if candidate.indexable:
                        candidate_map[candidate.id] = candidate
            best: tuple[AtomicChunk, float] | None = None
            for candidate in candidate_map.values():
                token_score = _jaccard(tokens, token_cache[candidate.id])
                if token_score < self.config.near_duplicate_threshold - 0.12:
                    continue
                sequence_score = SequenceMatcher(
                    None, _normalized(chunk.text), _normalized(candidate.text), autojunk=False
                ).ratio()
                score = max(token_score, sequence_score)
                if score >= self.config.near_duplicate_threshold and (
                    best is None or score > best[1]
                ):
                    best = (candidate, score)
            if best:
                canonical = self._choose_canonical(best[0], chunk)
                duplicate = chunk if canonical.id == best[0].id else best[0]
                self._mark_duplicate(duplicate, canonical, DuplicateKind.NEAR, best[1])
                duplicates += 1
            if chunk.indexable:
                for bucket in _minhash_buckets(tokens):
                    buckets[bucket].append(chunk)
        return duplicates

    def _semantic_text(
        self,
        chunks: list[AtomicChunk],
        embedder: EmbeddingProvider,
    ) -> int:
        candidates = [
            chunk
            for chunk in chunks
            if chunk.indexable and len(chunk.text.strip()) >= self.config.minimum_text_chars
        ]
        vectors = embedder.embed([chunk.text for chunk in candidates])
        bands: dict[tuple[int, int], list[int]] = defaultdict(list)
        duplicates = 0
        for index, (chunk, vector) in enumerate(zip(candidates, vectors, strict=True)):
            possible: set[int] = set()
            for band in _vector_bands(vector):
                possible.update(bands[band])
            best: tuple[int, float] | None = None
            for candidate_index in possible:
                candidate = candidates[candidate_index]
                if not candidate.indexable:
                    continue
                score = _cosine(vector, vectors[candidate_index])
                if score >= self.config.semantic_duplicate_threshold and (
                    best is None or score > best[1]
                ):
                    best = (candidate_index, score)
            if best:
                candidate = candidates[best[0]]
                canonical = self._choose_canonical(candidate, chunk)
                duplicate = chunk if canonical.id == candidate.id else candidate
                self._mark_duplicate(duplicate, canonical, DuplicateKind.SEMANTIC, best[1])
                duplicates += 1
            if chunk.indexable:
                for band in _vector_bands(vector):
                    bands[band].append(index)
        return duplicates

    def _assets(self, assets: list[VisualAsset]) -> tuple[list[VisualAsset], int]:
        if not assets or not self.config.image_deduplication:
            return assets, 0
        exact_map: dict[tuple[str, str], VisualAsset] = {}
        perceptual_canonicals: list[VisualAsset] = []
        result: list[VisualAsset] = []
        duplicates = 0
        for source in assets:
            asset = source.model_copy(deep=True)
            exact_key = (asset.kind.value, asset.exact_hash)
            canonical = exact_map.get(exact_key)
            if canonical:
                asset.canonical_asset_id = canonical.id
                asset.duplicate_kind = "exact_duplicate"
                asset.duplicate_score = 1.0
                duplicates += 1
                result.append(asset)
                continue
            if asset.perceptual_hash:
                for candidate in perceptual_canonicals:
                    if not candidate.perceptual_hash or candidate.kind != asset.kind:
                        continue
                    distance = hamming_distance(asset.perceptual_hash, candidate.perceptual_hash)
                    if distance <= self.config.image_phash_distance:
                        asset.canonical_asset_id = candidate.id
                        asset.duplicate_kind = "near_duplicate"
                        asset.duplicate_score = 1 - distance / 64
                        duplicates += 1
                        break
            if asset.canonical_asset_id is None:
                exact_map[exact_key] = asset
                if asset.perceptual_hash:
                    perceptual_canonicals.append(asset)
            result.append(asset)
        return result, duplicates

    def _choose_canonical(self, first: AtomicChunk, second: AtomicChunk) -> AtomicChunk:
        if self.config.canonical_policy == "longest" and len(second.text) > len(first.text):
            return second
        return first

    @staticmethod
    def _mark_duplicate(
        duplicate: AtomicChunk,
        canonical: AtomicChunk,
        kind: DuplicateKind,
        score: float,
    ) -> None:
        duplicate.duplicate_kind = kind
        duplicate.canonical_id = canonical.id
        duplicate.duplicate_score = score
        duplicate.indexable = False

    @staticmethod
    def _attach_self_occurrences(chunks: list[AtomicChunk]) -> None:
        for chunk in chunks:
            chunk.evidence_occurrences = [
                EvidenceOccurrence(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    source_pages=chunk.source_pages,
                )
            ]

    @staticmethod
    def _attach_occurrences(chunks: list[AtomicChunk]) -> None:
        by_id = {chunk.id: chunk for chunk in chunks}
        for chunk in chunks:
            if chunk.indexable:
                chunk.evidence_occurrences = [
                    EvidenceOccurrence(
                        document_id=chunk.document_id,
                        chunk_id=chunk.id,
                        source_pages=chunk.source_pages,
                    )
                ]
        for duplicate in chunks:
            if duplicate.indexable or not duplicate.canonical_id:
                continue
            canonical = by_id.get(duplicate.canonical_id)
            if canonical is None:
                continue
            canonical.evidence_occurrences.append(
                EvidenceOccurrence(
                    document_id=duplicate.document_id,
                    chunk_id=duplicate.id,
                    source_pages=duplicate.source_pages,
                    duplicate_kind=duplicate.duplicate_kind,
                    score=duplicate.duplicate_score,
                )
            )
