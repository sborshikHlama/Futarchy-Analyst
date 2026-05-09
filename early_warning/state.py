"""
Live Memo Watch state — early_warning/state.py
Tracks currently open decision markets being monitored for signal changes.
"""

from __future__ import annotations


class WatchAlert(dict):
    """A watch alert for a live market.
    Keys: market_id, title, signal_level (HIGH/MEDIUM/LOW),
          trigger, description, recommended_action, detected_at.
    """
    pass


def make_initial_watch_state(run_id: str, run_type: str = "on_demand") -> dict:
    from datetime import datetime, timezone
    return {
        "run_id":         run_id,
        "run_type":       run_type,        # "on_demand" | "scheduled"
        "triggered_at":   datetime.now(timezone.utc).isoformat(),
        "open_markets":   [],              # list of market metadata dicts
        "market_signals": {},              # market_id → raw signal dict
        "watch_alerts":   [],              # list[WatchAlert]
        "summary":        {},              # {total, high_signal, medium_signal, low_signal}
        "status":         "running",
        "audit_trail":    [],
    }
