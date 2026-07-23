from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evaluation:
    evaluator: str
    confidence: float
    evidence_count: int
    blockers: tuple[str, ...] = ()


class ConsensusLessValidator:
    """Conserve les désaccords au lieu de les écraser par un vote majoritaire."""

    def assess(self, evaluations: list[Evaluation]) -> dict:
        if not evaluations:
            return {"decision": "insufficient_evidence", "confidence": 0.0, "evaluations": []}
        blockers = sorted({b for e in evaluations for b in e.blockers})
        weighted = sum(e.confidence * max(e.evidence_count, 1) for e in evaluations)
        weight = sum(max(e.evidence_count, 1) for e in evaluations)
        confidence = weighted / weight
        decision = "blocked" if blockers else "proceed_with_trace"
        return {
            "decision": decision,
            "confidence": round(confidence, 4),
            "blockers": blockers,
            "evaluations": [e.__dict__ for e in evaluations],
        }
