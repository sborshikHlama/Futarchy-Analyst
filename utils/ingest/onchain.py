"""
On-chain activity fetcher — utils/ingest/onchain.py
Queries a block explorer (Etherscan-compatible) for dev wallet activity.
Falls back to mock data for hackathon demo.
"""
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests

log = logging.getLogger(__name__)

_ETHERSCAN_API = "https://api.etherscan.io/api"
_TIMEOUT       = 10


def fetch_wallet_activity(addresses: list[str], days: int = 14,
                           mock: bool = False) -> dict:
    """
    Fetch on-chain transaction activity for dev wallet addresses.

    Args:
        addresses: list of EVM wallet addresses
        days:      How many days back to look
        mock:      If True, return mock data

    Returns:
        {addresses, total_tx_7d, total_tx_30d, active_wallets,
         recent_transfers, last_activity}
    """
    if mock or not os.getenv("ETHERSCAN_API_KEY"):
        log.info(f"[OnChain] Mock mode | addresses={len(addresses)}")
        return _mock_activity(addresses)

    api_key = os.environ["ETHERSCAN_API_KEY"]
    cutoff  = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())

    total_tx   = 0
    active     = 0
    transfers  = []
    last_ts    = 0

    for addr in addresses:
        try:
            r = requests.get(_ETHERSCAN_API, timeout=_TIMEOUT, params={
                "module":     "account",
                "action":     "txlist",
                "address":    addr,
                "startblock": 0,
                "endblock":   "latest",
                "sort":       "desc",
                "apikey":     api_key,
            })
            data = r.json()
            if data.get("status") == "1":
                txs = [t for t in data.get("result", [])
                       if int(t.get("timeStamp", 0)) >= cutoff]
                total_tx += len(txs)
                if txs:
                    active += 1
                    ts = int(txs[0].get("timeStamp", 0))
                    if ts > last_ts:
                        last_ts = ts
                    for tx in txs[:3]:
                        transfers.append({
                            "hash":  tx.get("hash", ""),
                            "value": int(tx.get("value", 0)) / 1e18,
                            "to":    tx.get("to", ""),
                            "ts":    tx.get("timeStamp", ""),
                        })
        except Exception as exc:
            log.warning(f"[OnChain] Failed for {addr}: {exc}")

    last_activity = datetime.fromtimestamp(last_ts, tz=timezone.utc).isoformat() if last_ts else None

    return {
        "addresses":       addresses,
        "total_tx":        total_tx,
        "active_wallets":  active,
        "recent_transfers": transfers[:10],
        "last_activity":   last_activity,
        "days_observed":   days,
    }


def _mock_activity(addresses: list[str]) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "addresses":       addresses,
        "total_tx":        23,
        "active_wallets":  len(addresses),
        "recent_transfers": [
            {"hash": "0xabc123", "value": 0.5, "to": "0xDEFcontract", "ts": now},
            {"hash": "0xdef456", "value": 1.2, "to": "0xGHIwallet",   "ts": now},
        ],
        "last_activity":   now,
        "days_observed":   14,
    }
