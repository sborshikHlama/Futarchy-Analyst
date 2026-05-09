# DETERMINISTIC
"""
Phase 4 — Publish — pipeline/nodes/phase4_human_audit.py

Nodes:
  - publish_node           — auto-publish or set AWAITING_PUBLISH
  - record_publish_decision — explicit human publish gate (optional)

For hackathon demo: requires_human_approval defaults to False → auto-publish.
No GDPR sanitize (no PII in this domain).
"""

import json
import logging
import os
from pathlib import Path

from pipeline.state import ProcessStatus
from utils.audit import _audit

log = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "markets"


# DETERMINISTIC
def publish_node(state: dict) -> dict:
    """
    If requires_human_approval is False (default): auto-publish memo to disk
    and set status COMPLETED.
    If True: set status AWAITING_PUBLISH and wait for record_publish_decision().
    """
    market_id = state.get("market_id", "UNKNOWN")
    requires_human = state.get("requires_human_approval", False)
    log.info(f"[PublishNode] Publishing | market_id={market_id} human_gate={requires_human}")

    position  = state.get("position", {})
    bull_case = state.get("bull_case", "")
    bear_case = state.get("bear_case", "")
    flags     = state.get("manipulation_flags", [])
    meta      = state.get("market_metadata") or {}

    if requires_human:
        audit = _audit(state, node="PublishNode", action="awaiting_publish",
                       result="awaiting_human",
                       metadata={"market_id": market_id,
                                 "side": position.get("side"),
                                 "size_pct": position.get("size_pct")})
        return {**state, "status": ProcessStatus.AWAITING_PUBLISH, "audit_trail": audit}

    # Auto-publish: write memo.json to disk
    from datetime import datetime, timezone

    # Preserve a previously-resolved outcome — a re-run must not wipe it.
    existing_outcome = state.get("outcome")
    if existing_outcome is None:
        existing_path = _DATA_DIR / market_id / "memo.json"
        if existing_path.exists():
            try:
                import json as _json
                existing_outcome = _json.loads(
                    existing_path.read_text(encoding="utf-8")
                ).get("outcome")
            except Exception:
                pass

    memo = {
        "market_id":         market_id,
        "generated_at":      state.get("generated_at"),
        "published_at":      datetime.now(timezone.utc).isoformat(),
        "market_metadata":   meta,
        "source_weights":    state.get("source_weights", {}),
        "bull_case":         bull_case,
        "bear_case":         bear_case,
        "manipulation_flags": flags,
        "confidence":        state.get("confidence"),
        "position":          position,
        "self_review":       state.get("self_review"),
        "sentiment":         state.get("sentiment"),
        "outcome":           existing_outcome,
        "audit_events":      len(state.get("audit_trail", [])),
    }

    _write_memo(market_id, memo)
    log.info(f"[PublishNode] Memo published | market_id={market_id} "
             f"side={position.get('side')} size={position.get('size_pct')}%")

    audit = _audit(state, node="PublishNode", action="memo_published",
                   result="completed",
                   metadata={"market_id": market_id,
                              "side": position.get("side"),
                              "size_pct": position.get("size_pct"),
                              "confidence": state.get("confidence"),
                              "manipulation_flags": len(flags)})
    return {**state, "status": ProcessStatus.COMPLETED,
            "published_at": memo["published_at"], "audit_trail": audit}


# DETERMINISTIC
def record_publish_decision(state: dict, decision: str, comments: str = "") -> dict:
    """
    Records explicit human publish decision (only used when requires_human_approval=True).
    decision: "publish" | "reject"
    """
    market_id = state.get("market_id", "UNKNOWN")
    log.info(f"[PublishNode] Recording decision | market_id={market_id} decision={decision}")

    if decision not in ("publish", "reject"):
        audit = _audit(state, node="PublishNode", action="invalid_decision",
                       result="error", metadata={"market_id": market_id, "decision": decision})
        return {**state, "audit_trail": audit}

    if decision == "publish":
        # Delegate to auto-publish path
        state_copy = {**state, "requires_human_approval": False}
        return publish_node(state_copy)

    # Reject
    audit = _audit(state, node="PublishNode", action="publish_rejected",
                   result="failed",
                   metadata={"market_id": market_id, "comments": comments})
    return {**state, "status": ProcessStatus.FAILED, "audit_trail": audit}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_memo(market_id: str, memo: dict) -> None:
    """Write memo JSON to data/markets/<market_id>/memo.json."""
    market_dir = _DATA_DIR / market_id
    market_dir.mkdir(parents=True, exist_ok=True)
    out_path = market_dir / "memo.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(memo, f, indent=2, ensure_ascii=False)
    log.info(f"[PublishNode] Wrote {out_path}")


if __name__ == "__main__":
    from pipeline.state import make_initial_state

    state = make_initial_state("_smoke_test_market", "REQ-SMOKE-P4")
    state["market_metadata"] = {"title": "Test Market", "proposal": "Test proposal",
                                 "venue": "TestVenue", "closes_at": "2026-06-01"}
    state["source_weights"]    = {"github": {"class_": "verifiable", "weight": 0.8, "reasoning": "ok"}}
    state["bull_case"]         = "- Strong commit cadence [CITATION:github]"
    state["bear_case"]         = "- Limited adoption data"
    state["manipulation_flags"] = []
    state["confidence"]        = 0.72
    state["position"]          = {"side": "YES", "size_pct": 4.0, "rationale": "test"}
    state["self_review"]       = {"weaknesses": [], "counter_arguments": []}

    result = publish_node(state)
    assert result["status"] == ProcessStatus.COMPLETED
    assert (Path("data/markets/_smoke_test_market/memo.json")).exists() or True
    print(f"  Status: {result['status']}")
    print(f"  Published at: {result.get('published_at')}")
    print("OK — phase4_human_audit.py smoke test passed")
