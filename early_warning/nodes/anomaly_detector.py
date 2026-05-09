# DETERMINISTIC
"""
Live Watch — Anomaly Detector — early_warning/nodes/anomaly_detector.py
Detects unusual signal patterns in open markets.
DETERMINISTIC rules + optional AI text for recommended_action.
"""
import logging
import os
from datetime import datetime, timezone

from utils.audit import _audit
from utils.source_rules import WATCH_THRESHOLDS

log = logging.getLogger(__name__)


def detect_market_anomalies(state: dict) -> dict:
    """
    Applies signal rules to each open market.
    Optionally enriches alerts with AI recommended_action.
    """
    open_markets: list[dict] = state.get("open_markets", [])
    scores: dict = state.get("metrics_computed", {})
    watch_alerts: list[dict] = []

    for market in open_markets:
        mid = market.get("market_id", "")
        score = scores.get(mid, {})
        alerts = _apply_watch_rules(market, score)
        watch_alerts.extend(alerts)

    # Sort HIGH → MEDIUM → LOW
    level_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    watch_alerts.sort(key=lambda a: level_order.get(a.get("signal_level", "LOW"), 3))

    audit = _audit(state, node="AnomalyDetector", action="anomalies_detected",
                   result="success",
                   metadata={
                       "total_alerts": len(watch_alerts),
                       "high":   sum(1 for a in watch_alerts if a["signal_level"] == "HIGH"),
                       "medium": sum(1 for a in watch_alerts if a["signal_level"] == "MEDIUM"),
                   })
    log.info(f"[AnomalyDetector] Done | total_alerts={len(watch_alerts)}")
    return {**state, "watch_alerts": watch_alerts, "audit_trail": audit}


def _apply_watch_rules(market: dict, score: dict) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    alerts: list[dict] = []
    mid   = market.get("market_id", "")
    title = market.get("title", mid)
    level = score.get("signal_level", "LOW")
    hours = score.get("hours_to_close")

    # High-signal market without a published memo → flag for analysis
    if level == "HIGH":
        trigger = "High verifiable signal weight detected"
        alerts.append({
            "market_id":   mid,
            "title":       title,
            "signal_level": "HIGH",
            "trigger":     trigger,
            "description": (
                f"Market '{title}' has strong verifiable signals "
                f"(GitHub + on-chain). Recommend generating a fresh memo."
            ),
            "recommended_action": "Run full pipeline analysis on this market.",
            "detected_at": now,
        })

    # Market closing soon with medium signal → remind
    if level == "MEDIUM" and hours is not None and 0 < hours < 24:
        alerts.append({
            "market_id":   mid,
            "title":       title,
            "signal_level": "MEDIUM",
            "trigger":     f"Market closes in {hours:.0f}h with medium signal",
            "description":  f"'{title}' closes soon. Partial signals available — review memo.",
            "recommended_action": "Review existing memo or run synthesis with current signals.",
            "detected_at": now,
        })

    return alerts
