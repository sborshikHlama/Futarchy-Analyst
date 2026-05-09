"""
Apify Telegram scraper — utils/ingest/apify_telegram.py
Fetches recent messages from a Telegram channel via Apify actor.
Falls back to mock data if APIFY_TOKEN not set or --mock flag used.
"""
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

log = logging.getLogger(__name__)

_ACTOR_ID = "johndoe~telegram-scraper"   # placeholder — swap for real Apify actor ID


def fetch_telegram(channel: str, days: int = 7, mock: bool = False) -> list[dict]:
    """
    Fetch messages from a Telegram channel for the last N days.

    Args:
        channel: Telegram channel username or URL (e.g. "@metadao_official")
        days:    How many days back to look
        mock:    If True, return hardcoded mock data

    Returns:
        list of {text, date, views, forwards}
    """
    if mock or not os.getenv("APIFY_TOKEN"):
        log.info(f"[Telegram] Mock mode | channel={channel}")
        return _mock_messages(channel, days)

    try:
        from apify_client import ApifyClient  # type: ignore
        client = ApifyClient(os.environ["APIFY_TOKEN"])
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        run_input = {
            "channels": [channel],
            "limitMessages": 100,
            "startUrls": [],
        }
        run = client.actor(_ACTOR_ID).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

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
        return messages

    except Exception as exc:
        log.warning(f"[Telegram] Fetch failed: {exc} — returning mock")
        return _mock_messages(channel, days)


def _mock_messages(channel: str, days: int) -> list[dict]:
    from datetime import datetime, timezone
    base = datetime.now(timezone.utc).isoformat()
    return [
        {"text": f"[MOCK] {channel}: Major update shipping next week!", "date": base, "views": 1200, "forwards": 45},
        {"text": f"[MOCK] {channel}: Dev team working hard on v2.", "date": base, "views": 850, "forwards": 12},
        {"text": f"[MOCK] {channel}: Community AMA tomorrow at 3pm UTC.", "date": base, "views": 600, "forwards": 8},
    ]
