"""
Apify Twitter scraper — utils/ingest/apify_twitter.py
Fetches recent tweets for a search query via Apify actor.
"""
import logging
import os
from datetime import datetime, timezone, timedelta

log = logging.getLogger(__name__)

_ACTOR_ID = "apidojo~tweet-scraper"   # placeholder — swap for real actor


def fetch_tweets(query: str, days: int = 7, max_items: int = 50, mock: bool = False) -> list[dict]:
    """
    Fetch tweets matching query for the last N days.

    Args:
        query:     Twitter search query (e.g. "MetaDAO proposal")
        days:      Days back to look
        max_items: Max tweets to return
        mock:      If True, return hardcoded mock data

    Returns:
        list of {text, date, likes, retweets, author_followers}
    """
    if mock or not os.getenv("APIFY_TOKEN"):
        log.info(f"[Twitter] Mock mode | query={query}")
        return _mock_tweets(query)

    try:
        from apify_client import ApifyClient  # type: ignore
        client = ApifyClient(os.environ["APIFY_TOKEN"])

        run_input = {
            "searchTerms": [query],
            "maxItems": max_items,
            "sort": "Latest",
            "tweetLanguage": "en",
        }
        run = client.actor(_ACTOR_ID).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        cutoff_dt = datetime.now(timezone.utc) - timedelta(days=days)
        tweets = []
        for item in items:
            created = item.get("created_at", "")
            try:
                ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if ts < cutoff_dt:
                    continue
            except Exception:
                pass
            tweets.append({
                "text":             item.get("full_text", item.get("text", "")),
                "date":             created,
                "likes":            item.get("favorite_count", 0),
                "retweets":         item.get("retweet_count", 0),
                "author_followers": item.get("user", {}).get("followers_count", 0),
            })
        log.info(f"[Twitter] Fetched {len(tweets)} tweets | query={query}")
        return tweets

    except Exception as exc:
        log.warning(f"[Twitter] Fetch failed: {exc} — returning mock")
        return _mock_tweets(query)


def _mock_tweets(query: str) -> list[dict]:
    from datetime import datetime, timezone
    base = datetime.now(timezone.utc).isoformat()
    return [
        {"text": f"[MOCK] {query} — bullish signals from the team!", "date": base,
         "likes": 340, "retweets": 45, "author_followers": 12000},
        {"text": f"[MOCK] Not sure about {query}, seems overhyped", "date": base,
         "likes": 89, "retweets": 12, "author_followers": 500},
        {"text": f"[MOCK] {query} devs shipped 3 PRs this week", "date": base,
         "likes": 210, "retweets": 28, "author_followers": 3200},
    ]
