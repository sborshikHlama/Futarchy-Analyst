# DETERMINISTIC
"""
Live Watch — Signal Scorer — early_warning/nodes/metrics_calculator.py
Scores each open market's signal quality. Pure Python — no LLM.
"""
import logging

from utils.audit import _audit
from utils.source_rules import classify_signal_level

log = logging.getLogger(__name__)


def calculate_market_signal_scores(state: dict) -> dict:
    """
    Computes signal strength score for each open market.
    Scores are based on source diversity and verifiable signal volume.
    """
    open_markets: list[dict] = state.get("open_markets", [])
    market_signals: dict = state.get("market_signals", {})
    scores: dict[str, dict] = {}

    for market in open_markets:
        mid = market.get("market_id", "")
        signals = market_signals.get(mid, {})
        score = _score_market(mid, market, signals)
        scores[mid] = score

    log.info(f"[SignalScorer] Scored {len(scores)} markets")
    audit = _audit(state, node="SignalScorer", action="scores_computed",
                   result="success", metadata={"markets_scored": len(scores)})
    return {**state, "metrics_computed": scores, "audit_trail": audit}


def _score_market(market_id: str, meta: dict, signals: dict) -> dict:
    """DETERMINISTIC — compute signal quality metrics for one market."""
    source_count    = len(signals)
    verifiable      = [k for k, v in signals.items() if isinstance(v, dict) and v.get("type") == "onchain"]
    has_github      = "github_commits" in signals or "github_activity" in signals
    has_onchain     = any("onchain" in k or "wallet" in k for k in signals)
    has_social      = any("telegram" in k or "twitter" in k for k in signals)
    signal_diversity = sum([has_github, has_onchain, has_social])

    # Simple heuristic: more verifiable sources → higher signal level
    mock_weights: dict = {}
    if has_onchain:
        mock_weights["onchain"] = {"class_": "verifiable", "weight": 0.8}
    if has_github:
        mock_weights["github"] = {"class_": "verifiable", "weight": 0.7}
    if has_social:
        mock_weights["social"] = {"class_": "manipulable", "weight": 0.25}

    signal_level = classify_signal_level(mock_weights) if mock_weights else "LOW"

    # Time to close
    from datetime import datetime, timezone
    closes_at = meta.get("closes_at", "")
    hours_to_close = None
    try:
        closes_dt = datetime.fromisoformat(closes_at.replace("Z", "+00:00"))
        delta = closes_dt - datetime.now(timezone.utc)
        hours_to_close = delta.total_seconds() / 3600
    except Exception:
        pass

    return {
        "market_id":      market_id,
        "signal_level":   signal_level,
        "source_count":   source_count,
        "has_github":     has_github,
        "has_onchain":    has_onchain,
        "has_social":     has_social,
        "signal_diversity": signal_diversity,
        "hours_to_close": hours_to_close,
    }
