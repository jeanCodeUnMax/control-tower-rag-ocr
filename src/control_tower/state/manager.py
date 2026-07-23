from __future__ import annotations

from control_tower.storage.sqlite import SQLiteStore


class KnowledgeStateManager:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def link(self, parent_id: str, child_id: str) -> None:
        self.store.add_dependency(parent_id, child_id)

    def invalidate(self, node_id: str) -> list[str]:
        impacted = [node_id, *self.store.descendants(node_id)]
        self.store.mark_stale(impacted)
        return impacted
