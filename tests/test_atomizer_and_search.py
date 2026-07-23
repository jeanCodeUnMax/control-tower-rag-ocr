import re
from pathlib import Path

from control_tower.ingestion.atomizer import AtomicChunker
from control_tower.service import ControlTowerService


def test_overlap_never_starts_inside_a_word() -> None:
    source_text = (
        "Les fragments atomiques conservent le contexte utile. "
        "Le deuxième fragment doit commencer sur une frontière de mot."
    )
    chunks = AtomicChunker(max_chars=70, overlap_chars=25).split("demo", "doc", source_text)
    assert len(chunks) >= 2
    source_words = set(re.findall(r"[\wÀ-ÖØ-öø-ÿ]+", source_text.casefold()))
    first_word = re.match(r"[\wÀ-ÖØ-öø-ÿ]+", chunks[1].text.casefold())
    assert first_word is not None
    assert first_word.group(0) in source_words


def test_lexical_search_normalizes_punctuation(tmp_path: Path) -> None:
    service = ControlTowerService(tmp_path / "projects")
    service.init_project("demo")
    source = tmp_path / "doc.txt"
    source.write_text("Le projet documentaire possède son propre espace.", encoding="utf-8")
    service.ingest("demo", source)
    response = service.query("demo", "projet, documentaire !")
    assert response["hits"]
    assert response["hits"][0]["score"] == 1.0
