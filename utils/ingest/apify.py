"""
Apify signal ingestion via X402 payment protocol.

Two Actors:
  apify/telegram-scraper       → Telegram channel posts (manipulable, weight 0.3)
  apify/google-search-scraper  → News snippets for context (partial, weight 0.6)

Payment: USDC on Base via mcpc CLI (x402 protocol).
Fallback order:
  1. UMIA_ENV=demo → mock data, no network calls
  2. mcpc not installed → APIFY_TOKEN from env (standard auth)
  3. Both available → X402 payment flow
"""

import os
import subprocess
import logging
import requests

log = logging.getLogger(__name__)

APIFY_BASE  = "https://api.apify.com/v2/acts"

# ── Mock data for demo mode ───────────────────────────────────────────────────

MOCK_TELEGRAM = [
    "MetaDAO proposal looks solid, strong dev activity on GitHub 🔥",
    "Not convinced by this governance vote, team has been quiet for weeks",
    "Treasury allocation seems reasonable, YES from me",
    "Bearish on this one — competitor launched same feature yesterday",
    "Smart money is accumulating before the vote closes 👀",
]

MOCK_NEWS = [
    "MetaDAO records highest governance participation in Q1 2026",
    "Futarchy-based DAOs outperform traditional voting by 34% in study",
    "On-chain analytics show whale accumulation ahead of proposal deadline",
]

# ── X402 payment core ─────────────────────────────────────────────────────────

def _is_mcpc_available() -> bool:
    """Check if mcpc CLI is installed."""
    try:
        result = subprocess.run(
            ["mcpc", "x402", "info"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _sign_payment(payment_required: str) -> str | None:
    """Sign X402 payment via mcpc CLI. Returns signature or None on failure."""
    try:
        result = subprocess.run(
            ["mcpc", "x402", "sign", payment_required],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return result.stdout.strip()
        log.error(f"mcpc sign failed: {result.stderr}")
        return None
    except Exception as e:
        log.error(f"mcpc sign error: {e}")
        return None


def _call_actor_x402(actor_id: str, run_input: dict) -> dict:
    """
    Call Apify Actor via X402 payment protocol.

    Returns:
        {
          "items":    list[dict],   ← raw Actor output
          "paid":     bool,
          "protocol": str,          ← "x402" | "token" | "mock" | "none"
          "actor":    str,
        }
    """
    if os.getenv("UMIA_ENV", "demo") == "demo":
        log.info(f"[x402] DEMO mode — skipping {actor_id}")
        return {"items": [], "paid": False, "protocol": "mock", "actor": actor_id}

    actor_slug = actor_id.replace("/", "~")
    url = f"{APIFY_BASE}/{actor_slug}/run-sync-get-dataset-items"

    # Step 1 — probe with X402 header
    log.info(f"[x402] → POST {actor_id}")
    try:
        r1 = requests.post(
            url,
            headers={"X-APIFY-PAYMENT-PROTOCOL": "X402", "Content-Type": "application/json"},
            json=run_input,
            timeout=15,
        )
    except requests.RequestException as exc:
        log.error(f"[x402] Initial request failed: {exc}")
        return {"items": [], "paid": False, "protocol": "none", "actor": actor_id}

    # X402 flow — 402 received and mcpc is available
    if r1.status_code == 402 and _is_mcpc_available():
        payment_required = r1.headers.get("PAYMENT-REQUIRED", "")
        log.info("[x402] ← 402 Payment Required")
        log.info("[x402] → Signing USDC payment on Base...")

        signature = _sign_payment(payment_required)

        if signature:
            log.info("[x402] → Sending payment + request")
            try:
                r2 = requests.post(
                    url,
                    headers={
                        "X-APIFY-PAYMENT-PROTOCOL": "X402",
                        "PAYMENT-SIGNATURE":         signature,
                        "Content-Type":              "application/json",
                    },
                    json=run_input,
                    timeout=60,
                )
                r2.raise_for_status()
                items = r2.json() if isinstance(r2.json(), list) else []
                log.info(f"[x402] ← Payment settled · {len(items)} items received")
                return {"items": items, "paid": True, "protocol": "x402", "actor": actor_id}
            except requests.RequestException as exc:
                log.error(f"[x402] Signed request failed: {exc}")

    # Fallback — standard APIFY_TOKEN bearer auth
    apify_token = os.getenv("APIFY_TOKEN", "")
    if apify_token:
        log.warning("[x402] mcpc unavailable or signing failed — falling back to APIFY_TOKEN")
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {apify_token}", "Content-Type": "application/json"},
                json=run_input,
                timeout=60,
            )
            r.raise_for_status()
            items = r.json() if isinstance(r.json(), list) else []
            log.info(f"[apify] ← {len(items)} items (token auth)")
            return {"items": items, "paid": False, "protocol": "token", "actor": actor_id}
        except requests.RequestException as exc:
            log.error(f"[apify] Token auth failed: {exc}")

    log.error("[x402] No payment method available (mcpc not installed, no APIFY_TOKEN)")
    return {"items": [], "paid": False, "protocol": "none", "actor": actor_id}


# ── Public ingestion functions ────────────────────────────────────────────────

def scrape_telegram(channel: str, max_messages: int = 50) -> dict:
    """
    Scrape Telegram channel posts via X402.
    source_class: manipulable, weight: 0.3

    Returns:
        {
          "texts":   list[str],
          "payment": {"paid": bool, "protocol": str},
          "source":  "telegram",
          "channel": str,
        }
    """
    if os.getenv("UMIA_ENV", "demo") == "demo":
        log.info(f"[telegram] DEMO — returning mock posts for #{channel}")
        return {
            "texts":   MOCK_TELEGRAM,
            "payment": {"paid": False, "protocol": "mock"},
            "source":  "telegram",
            "channel": channel,
        }

    result = _call_actor_x402(
        actor_id="apify/telegram-scraper",
        run_input={"channelUsernames": [channel], "maxMessages": max_messages},
    )

    texts = [
        item.get("text") or item.get("message", "")
        for item in result["items"]
        if item.get("text") or item.get("message")
    ]

    return {
        "texts":   texts,
        "payment": {"paid": result["paid"], "protocol": result["protocol"]},
        "source":  "telegram",
        "channel": channel,
    }


def scrape_news(query: str, max_results: int = 10) -> dict:
    """
    Scrape news snippets via Apify Google Search + X402.
    source_class: partial, weight: 0.6

    Returns:
        {
          "texts":   list[str],   ← "title: snippet" strings
          "payment": {"paid": bool, "protocol": str},
          "source":  "news",
          "query":   str,
        }
    """
    if os.getenv("UMIA_ENV", "demo") == "demo":
        log.info(f"[news] DEMO — returning mock news for '{query}'")
        return {
            "texts":   MOCK_NEWS,
            "payment": {"paid": False, "protocol": "mock"},
            "source":  "news",
            "query":   query,
        }

    result = _call_actor_x402(
        actor_id="apify/google-search-scraper",
        run_input={
            "queries":           query,
            "maxResultsPerPage": max_results,
            "outputFormats":     ["captions"],
        },
    )

    texts = [
        f"{item.get('title', '')}: {item.get('description', '')}"
        for item in result["items"]
        if item.get("description")
    ]

    return {
        "texts":   texts,
        "payment": {"paid": result["paid"], "protocol": result["protocol"]},
        "source":  "news",
        "query":   query,
    }
