"""
AgentState + data models — pipeline/state.py
TypedDict definitions for the Umia Analyst Agent LangGraph pipeline.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


# ── Enums ─────────────────────────────────────────────────────────────────────


class ProcessStatus(str, Enum):
    RUNNING           = "running"
    FROZEN            = "frozen"            # data-fetch failure → no silent fallback
    ESCALATED         = "escalated"         # max iterations or critical error
    AWAITING_PUBLISH  = "awaiting_publish"  # ready for human publish gate (optional)
    COMPLETED         = "completed"         # memo published
    FAILED            = "failed"


# ── Data models ───────────────────────────────────────────────────────────────


class AuditEvent(dict):
    """Immutable audit event. Keys: timestamp, node, action, result,
    prompt_hash, prompt_version, tokens_used, metadata."""
    pass


class AgentState(dict):
    """Central LangGraph pipeline state.
    All nodes read from and write to this dict.
    audit_trail is append-only — never overwrite existing events.
    """
    pass


# ── Initial state factory ─────────────────────────────────────────────────────


def make_initial_state(market_id: str, request_id: str) -> AgentState:
    from datetime import datetime, timezone
    return AgentState(
        # Identity
        market_id=market_id,
        request_id=request_id,
        generated_at=datetime.now(timezone.utc).isoformat(),

        # Market metadata (populated in phase 1)
        market_metadata=None,

        # Phase 1 — SourceClassifier
        raw_signals={},
        source_weights={},     # dict[source_id → {class_, weight, reasoning}]
        classification_attempts=0,

        # Phase 2 — Synthesizer
        bull_case=None,
        bear_case=None,
        manipulation_flags=[],

        # Phase 3 — Position + Self-Review loop
        confidence=None,
        position=None,         # {side, size_pct, rationale}
        self_review=None,      # {weaknesses, counter_arguments}
        position_iteration=0,
        reviewer_verdict=None,

        # Phase 4 — Publish
        requires_human_approval=False,
        published_at=None,

        # Outcome (post-resolution, filled externally)
        outcome=None,          # {resolved_side, pnl_pct}

        # Pipeline control
        status=ProcessStatus.RUNNING,
        escalation_reason=None,
        fallback_reason=None,

        # Audit trail — immutable append-only
        audit_trail=[],
    )


if __name__ == "__main__":
    state = make_initial_state("metadao_001", "REQ-001")
    assert state["market_id"] == "metadao_001"
    assert state["status"] == ProcessStatus.RUNNING
    assert state["audit_trail"] == []
    print("OK — state.py smoke test passed")
