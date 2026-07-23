from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def event(event_type: str, **payload: Any) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "timestamp": datetime.now(UTC).isoformat(),
        **payload,
    }
