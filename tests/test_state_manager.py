from pathlib import Path

from control_tower.state.manager import KnowledgeStateManager
from control_tower.storage.sqlite import SQLiteStore


def test_targeted_invalidation(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "knowledge.db")
    with store._connect() as conn:  # test fixture minimal
        conn.executemany(
            "INSERT INTO node_state(node_id, version, status) VALUES (?, 1, 'fresh')",
            [("a",), ("b",), ("c",), ("x",)],
        )
    manager = KnowledgeStateManager(store)
    manager.link("a", "b")
    manager.link("b", "c")
    impacted = manager.invalidate("a")
    assert set(impacted) == {"a", "b", "c"}
    assert store.state("x")["status"] == "fresh"
    assert store.state("c")["status"] == "stale"
