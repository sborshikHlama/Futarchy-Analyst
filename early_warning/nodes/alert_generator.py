# DETERMINISTIC
"""
Live Watch — Alert Generator — early_warning/nodes/alert_generator.py
Assembles summary of the Live Memo Watch run.
"""
import logging
from datetime import datetime, timezone

from utils.audit import _audit

log = logging.getLogger(__name__)


def generate_watch_alerts(state: dict) -> dict:
    """Builds summary of signal alerts across all open markets."""
    watch_alerts: list[dict] = state.get("watch_alerts", [])
    open_markets: list[dict] = state.get("open_markets", [])

    high   = [a for a in watch_alerts if a.get("signal_level") == "HIGH"]
    medium = [a for a in watch_alerts if a.get("signal_level") == "MEDIUM"]
    low    = [a for a in watch_alerts if a.get("signal_level") == "LOW"]

    summary = {
        "run_id":         state.get("run_id", ""),
        "run_type":       state.get("run_type", "on_demand"),
        "total_markets":  len(open_markets),
        "high_signal":    len(high),
        "medium_signal":  len(medium),
        "low_signal":     len(low),
        "top_alerts":     high[:5],
        "generated_at":   datetime.now(timezone.utc).isoformat(),
    }

    log.info(f"[AlertGenerator] Summary | HIGH={len(high)} MEDIUM={len(medium)} LOW={len(low)}")
    audit = _audit(state, node="AlertGenerator", action="summary_generated",
                   result="success",
                   metadata={"high": len(high), "medium": len(medium), "low": len(low)})
    return {**state, "summary": summary, "audit_trail": audit}
