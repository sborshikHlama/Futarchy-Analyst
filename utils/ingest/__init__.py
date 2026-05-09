"""
Signal ingestion layer — utils/ingest/__init__.py
Exposes gather_signals(market_id) → unified raw-data bundle.
"""
import logging
import os

log = logging.getLogger(__name__)


def gather_signals(market_id: str, mock: bool = False) -> dict:
    """
    Gather all signals for a decision market.

    Demo/mock mode: returns minimal bundle based on market_id prefix.
    Production mode: calls live Apify, GitHub, and on-chain APIs.

    Returns:
        {
          "metadata": {title, proposal, venue, ...},
          "signals":  {source_id → data},
        }
    """
    env  = os.getenv("UMIA_ENV", "demo")
    use_mock = mock or (env != "production")

    # Each market configures its own sources via a market_config lookup.
    # For production this would come from a market registry API.
    config = _get_market_config(market_id)
    if not config:
        log.warning(f"[Ingest] No config for market_id={market_id}, using empty signals")
        return {"metadata": {"title": market_id, "proposal": ""}, "signals": {}}

    signals: dict = {}

    # Telegram
    for ch_id, channel in config.get("telegram_channels", {}).items():
        from utils.ingest.apify_telegram import fetch_telegram
        signals[ch_id] = fetch_telegram(channel, mock=use_mock)

    # Twitter
    for q_id, query in config.get("twitter_queries", {}).items():
        from utils.ingest.apify_twitter import fetch_tweets
        signals[q_id] = fetch_tweets(query, mock=use_mock)

    # GitHub
    for repo_id, repo in config.get("github_repos", {}).items():
        from utils.ingest.github_activity import fetch_github_activity
        signals[repo_id] = fetch_github_activity(repo, mock=use_mock)

    # On-chain
    wallets = config.get("dev_wallets", [])
    if wallets:
        from utils.ingest.onchain import fetch_wallet_activity
        signals["onchain_dev_wallets"] = fetch_wallet_activity(wallets, mock=use_mock)

    log.info(f"[Ingest] Gathered {len(signals)} signal sources | market_id={market_id}")
    return {"metadata": config.get("metadata", {}), "signals": signals}


def _get_market_config(market_id: str) -> dict | None:
    """
    Returns ingestion config for a known market.
    In production, this would query a market registry API.
    """
    from utils.mock_markets import MARKET_CONFIGS
    return MARKET_CONFIGS.get(market_id)
