"""
Signal ingestion layer — utils/ingest/__init__.py
Exposes gather_signals(market_id) → unified raw-data bundle.

Source routing:
  Telegram  → utils/ingest/apify.py  scrape_telegram()  (X402 → APIFY_TOKEN → mock)
  News      → utils/ingest/apify.py  scrape_news()      (X402 → APIFY_TOKEN → mock)
  Twitter   → PENDING Grok X Search implementation (Task 1)
  GitHub    → utils/ingest/github_activity.py
  On-chain  → utils/ingest/onchain.py
"""
import logging
import os

log = logging.getLogger(__name__)


def gather_signals(market_id: str, mock: bool = False) -> dict:
    """
    Gather all signals for a decision market.

    Payment flow (production):
      Telegram + News → Apify via X402 (USDC on Base) → APIFY_TOKEN fallback
      GitHub          → REST API (GITHUB_TOKEN)
      On-chain        → Etherscan API (ETHERSCAN_API_KEY)

    Demo mode (UMIA_ENV=demo or mock=True):
      All sources return deterministic mock data. No network calls, no API keys.

    Returns:
        {
          "metadata": {title, proposal, venue, opens_at, closes_at, ...},
          "signals":  {source_id → data},
        }
    """
    env      = os.getenv("UMIA_ENV", "demo")
    use_mock = mock or (env != "production")

    config = _get_market_config(market_id)
    if not config:
        log.warning(f"[Ingest] No config for market_id={market_id}, using empty signals")
        return {"metadata": {"title": market_id, "proposal": ""}, "signals": {}}

    metadata = config.get("metadata", {})
    signals: dict = {}

    from utils.ingest.apify import scrape_telegram, scrape_news
    from utils.audit import log_x402_payment

    # ── Telegram (X402 → APIFY_TOKEN → mock) ─────────────────────────────────
    for ch_id, channel in config.get("telegram_channels", {}).items():
        result = scrape_telegram(channel)
        log_x402_payment(market_id, result["payment"], "apify/telegram-scraper",
                         len(result["texts"]))
        signals[ch_id] = result["texts"]
        log.info(f"[Ingest] Telegram {ch_id} | {len(result['texts'])} posts "
                 f"| protocol={result['payment']['protocol']}")

    # ── News (Google Search via X402) ────────────────────────────────────────
    title      = metadata.get("title", market_id)
    news_query = f"{title} governance"
    news = scrape_news(query=news_query)
    log_x402_payment(market_id, news["payment"], "apify/google-search-scraper",
                     len(news["texts"]))
    if news["texts"]:
        signals["news_search"] = news["texts"]
        log.info(f"[Ingest] News | {len(news['texts'])} snippets "
                 f"| protocol={news['payment']['protocol']}")

    # ── Twitter → Grok X Search (not yet implemented) ────────────────────────
    # twitter_queries in MARKET_CONFIGS kept for future Grok wiring.
    # Until Task 1 (Grok) is done, Twitter signals are absent from raw_signals.
    if config.get("twitter_queries") and env == "production":
        log.warning(f"[Ingest] Twitter queries configured for {market_id} but "
                    f"Grok X Search is not yet implemented — skipping")

    # ── GitHub ────────────────────────────────────────────────────────────────
    for repo_id, repo in config.get("github_repos", {}).items():
        from utils.ingest.github_activity import fetch_github_activity
        signals[repo_id] = fetch_github_activity(repo, mock=use_mock)
        log.info(f"[Ingest] GitHub {repo_id} | repo={repo}")

    # ── On-chain ──────────────────────────────────────────────────────────────
    wallets = config.get("dev_wallets", [])
    if wallets:
        from utils.ingest.onchain import fetch_wallet_activity
        signals["onchain_dev_wallets"] = fetch_wallet_activity(wallets, mock=use_mock)
        log.info(f"[Ingest] On-chain | {len(wallets)} wallets")

    log.info(f"[Ingest] Done | market_id={market_id} sources={len(signals)} env={env}")
    return {"metadata": metadata, "signals": signals}


def _get_market_config(market_id: str) -> dict | None:
    from utils.mock_markets import MARKET_CONFIGS
    return MARKET_CONFIGS.get(market_id)
