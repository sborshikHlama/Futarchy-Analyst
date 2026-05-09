"""
Apify Telegram scraper — utils/ingest/apify_telegram.py
X402 payment-first, APIFY_TOKEN fallback, mock for demo mode.

Payment priority:
  1. X402 via `mcpc x402 sign` (no token needed if accepted)
  2. APIFY_TOKEN from environment (classic bearer auth)
  3. Mock data (if neither is available or mock=True)
"""
import json
import logging
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

log = logging.getLogger(__name__)

_ACTOR_ID  = "apify~telegram-scraper"
_APIFY_RUN = "https://api.apify.com/v2/acts/{actor}/runs"
_APIFY_DS  = "https://api.apify.com/v2/datasets/{ds_id}/items"

_PAYMENT_LOG_TEMPLATE: dict = {
    "paid":     False,
    "protocol": "x402",
    "chain":    "Base",
    "currency": "USDC",
}


# ── X402 helpers ──────────────────────────────────────────────────────────────

def _mcpc_available() -> bool:
    """Return True if the mcpc CLI is on PATH."""
    return shutil.which("mcpc") is not None


def _x402_sign(payment_required_header: str) -> Optional[str]:
    """
    Run `mcpc x402 sign <header>` and return the signature string,
    or None on any failure.
    """
    try:
        result = subprocess.run(
            ["mcpc", "x402", "sign", payment_required_header],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            sig = result.stdout.strip()
            log.info("[X402] Payment signed successfully")
            return sig
        log.warning(f"[X402] mcpc sign failed (rc={result.returncode}): {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        log.warning("[X402] mcpc sign timed out")
    except Exception as exc:
        log.warning(f"[X402] mcpc sign error: {exc}")
    return None


def _post_actor_x402(run_input: dict) -> Optional[dict]:
    """
    POST to Apify actor run endpoint with X402 protocol header.
    Handles the 402 challenge→sign→retry flow.

    Returns the parsed run dict on success, None on failure.
    """
    import requests  # lazy import — not in base stdlib

    url = _APIFY_RUN.format(actor=_ACTOR_ID)
    headers = {
        "Content-Type":              "application/json",
        "X-APIFY-PAYMENT-PROTOCOL":  "X402",
    }

    try:
        # Step 1 — announce X402 intent
        resp = requests.post(url, json=run_input, headers=headers, timeout=30)

        if resp.status_code == 402:
            payment_required = resp.headers.get("Payment-Required", "")
            if not payment_required:
                log.warning("[X402] 402 received but no Payment-Required header")
                return None

            log.info(f"[X402] 402 received — signing payment challenge")
            signature = _x402_sign(payment_required)
            if not signature:
                return None

            # Step 3 — resend with payment signature
            signed_headers = {**headers, "Payment-Signature": signature}
            resp = requests.post(url, json=run_input, headers=signed_headers, timeout=30)

            payment_log = {**_PAYMENT_LOG_TEMPLATE, "paid": True}
            log.info(f"[X402] Payment sent | {json.dumps(payment_log)}")

        if resp.status_code in (200, 201):
            return resp.json()

        log.warning(f"[X402] Actor run failed: HTTP {resp.status_code} — {resp.text[:200]}")

    except Exception as exc:
        log.warning(f"[X402] Request error: {exc}")

    return None


def _post_actor_token(run_input: dict) -> Optional[dict]:
    """Classic APIFY_TOKEN bearer auth fallback."""
    import requests

    token = os.getenv("APIFY_TOKEN", "")
    if not token:
        return None

    url = _APIFY_RUN.format(actor=_ACTOR_ID)
    params = {"token": token}
    try:
        resp = requests.post(url, json=run_input, params=params, timeout=30)
        if resp.status_code in (200, 201):
            log.info("[Telegram] Actor started via APIFY_TOKEN fallback")
            return resp.json()
        log.warning(f"[Telegram] Token auth failed: HTTP {resp.status_code}")
    except Exception as exc:
        log.warning(f"[Telegram] Token request error: {exc}")
    return None


def _poll_dataset(dataset_id: str, token: Optional[str] = None, timeout: int = 120) -> list[dict]:
    """
    Poll an Apify dataset until the run finishes, then return all items.
    Falls back to empty list on timeout.
    """
    import requests

    ds_url = _APIFY_DS.format(ds_id=dataset_id)
    params = {"token": token} if token else {}
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            resp = requests.get(ds_url, params=params, timeout=15)
            if resp.status_code == 200:
                items = resp.json()
                if isinstance(items, list) and items:
                    return items
        except Exception:
            pass
        time.sleep(5)

    log.warning(f"[Telegram] Dataset poll timed out after {timeout}s")
    return []


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_telegram(channel: str, days: int = 7, mock: bool = False) -> list[dict]:
    """
    Fetch messages from a Telegram channel for the last N days.

    Payment waterfall:
      X402 (mcpc) → APIFY_TOKEN → mock

    Args:
        channel: Telegram channel username or URL (e.g. "@metadao_official")
        days:    How many days back to look
        mock:    Force mock data regardless of environment

    Returns:
        list of {text, date, views, forwards}
    """
    use_mock = mock or (
        not _mcpc_available() and not os.getenv("APIFY_TOKEN")
    )
    if use_mock:
        log.info(f"[Telegram] Mock mode | channel={channel}")
        return _mock_messages(channel, days)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    run_input = {
        "channels":      [channel],
        "limitMessages": 100,
        "startUrls":     [],
    }

    run_data: Optional[dict] = None
    used_token: Optional[str] = None

    # --- Payment waterfall ---
    if _mcpc_available():
        run_data = _post_actor_x402(run_input)

    if run_data is None:
        log.info("[Telegram] X402 unavailable/failed — falling back to APIFY_TOKEN")
        payment_log = {**_PAYMENT_LOG_TEMPLATE, "paid": False}
        log.info(f"[X402] Payment skipped | {json.dumps(payment_log)}")
        used_token = os.getenv("APIFY_TOKEN")
        run_data = _post_actor_token(run_input)

    if run_data is None:
        log.warning("[Telegram] Both payment methods failed — returning mock")
        return _mock_messages(channel, days)

    # --- Retrieve dataset ---
    dataset_id = (
        run_data.get("data", {}).get("defaultDatasetId")
        or run_data.get("defaultDatasetId", "")
    )
    if not dataset_id:
        log.warning("[Telegram] No dataset ID in run response — returning mock")
        return _mock_messages(channel, days)

    items = _poll_dataset(dataset_id, token=used_token)

    messages = []
    for item in items:
        msg_date = item.get("date", "")
        if msg_date >= cutoff:
            messages.append({
                "text":     item.get("text", ""),
                "date":     msg_date,
                "views":    item.get("views", 0),
                "forwards": item.get("forwards", 0),
            })

    log.info(f"[Telegram] Fetched {len(messages)} messages | channel={channel}")
    return messages if messages else _mock_messages(channel, days)


# ── Mock ──────────────────────────────────────────────────────────────────────

def _mock_messages(channel: str, days: int) -> list[dict]:
    base = datetime.now(timezone.utc).isoformat()
    return [
        {"text": f"[MOCK] {channel}: Major update shipping next week!", "date": base, "views": 1200, "forwards": 45},
        {"text": f"[MOCK] {channel}: Dev team working hard on v2.",      "date": base, "views": 850,  "forwards": 12},
        {"text": f"[MOCK] {channel}: Community AMA tomorrow at 3pm UTC.","date": base, "views": 600,  "forwards": 8},
    ]
