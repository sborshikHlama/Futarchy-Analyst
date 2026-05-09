# DETERMINISTIC
"""
Live Watch — Alert Dispatcher — early_warning/nodes/alert_dispatcher.py
Demo: logs results. Production: would push to notification endpoint.
"""
import logging
import os

from utils.audit import _audit

log = logging.getLogger(__name__)


def dispatch_watch_alerts(state: dict) -> dict:
    """Demo: logs summary. Production: push to Umia notification endpoint."""
    summary = state.get("summary", {})
    env = os.getenv("UMIA_ENV", "demo")

    log.info(
        f"[AlertDispatcher] Watch run {state.get('run_id', '')} done | "
        f"HIGH={summary.get('high_signal', 0)} "
        f"MEDIUM={summary.get('medium_signal', 0)} "
        f"LOW={summary.get('low_signal', 0)} mode={env}"
    )

    if env == "production":
        # TODO: POST to Umia notification webhook
        pass

    audit = _audit(state, node="AlertDispatcher", action="dispatch",
                   result="success",
                   metadata={**summary, "mode": env})
    return {**state, "status": "completed", "audit_trail": audit}
