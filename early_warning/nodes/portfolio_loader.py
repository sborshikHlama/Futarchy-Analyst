# DETERMINISTIC
"""
Live Watch — Market Loader — early_warning/nodes/portfolio_loader.py
Loads open decision markets for signal monitoring.
"""
import json
import logging
import os
from pathlib import Path

from utils.audit import _audit

log = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "markets"


def load_open_markets(state: dict) -> dict:
    """
    Loads open decision markets.
    Demo: reads data/markets/*/raw_mock.json where resolved_outcome is null.
    Production: would call Umia/Polymarket API.
    """
    env = os.getenv("UMIA_ENV", "demo")
    log.info(f"[MarketLoader] Loading open markets | env={env}")

    open_markets: list[dict] = []
    market_signals: dict = {}

    if env != "production":
        if _DATA_DIR.exists():
            for mock_file in sorted(_DATA_DIR.glob("*/raw_mock.json")):
                try:
                    with mock_file.open("r", encoding="utf-8") as f:
                        bundle = json.load(f)
                    meta = bundle.get("metadata", {})
                    market_id = mock_file.parent.name
                    if meta.get("resolved_outcome") is None:
                        open_markets.append({**meta, "market_id": market_id})
                        market_signals[market_id] = bundle.get("signals", {})
                except Exception as exc:
                    log.warning(f"[MarketLoader] Failed to load {mock_file}: {exc}")
    else:
        log.info("[MarketLoader] Production: live market list not yet implemented")

    log.info(f"[MarketLoader] Found {len(open_markets)} open markets")
    audit = _audit(state, node="MarketLoader", action="markets_loaded",
                   result=f"{len(open_markets)}_markets",
                   metadata={"env": env, "open_markets": len(open_markets)})
    return {**state, "open_markets": open_markets,
            "market_signals": market_signals, "audit_trail": audit}
