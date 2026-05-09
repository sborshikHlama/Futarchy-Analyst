"""
Mock decision markets — utils/mock_markets.py
3 historical MetaDAO proposals with known outcomes, used for backtesting.
Also defines MARKET_CONFIGS for the ingest layer.

Markets chosen: real MetaDAO proposals with clear narratives and known resolutions.
  - metadao_001: Proposal to add SOL/USDC cNFT market (passed, YES resolved)
  - metadao_002: Proposal to increase developer grant pool (failed, NO resolved)
  - metadao_003: Live / open market (unresolved — used for live demo)
"""

from __future__ import annotations

# ── Market configs (used by utils/ingest/__init__.py) ─────────────────────────

MARKET_CONFIGS: dict[str, dict] = {
    "metadao_001": {
        "metadata": {
            "title":            "MetaDAO: Launch SOL/USDC Perpetuals Market",
            "proposal":         "Deploy a SOL/USDC perpetuals market on MetaDAO exchange "
                                "using 200k USDC from the treasury as initial liquidity.",
            "venue":            "MetaDAO",
            "opens_at":         "2025-11-01T00:00:00Z",
            "closes_at":        "2025-11-08T00:00:00Z",
            "resolved_outcome": "YES",
        },
        "telegram_channels": {"telegram_founder": "@metadao_official"},
        "twitter_queries":   {"twitter_community": "MetaDAO perpetuals SOL"},
        "github_repos":      {"github_commits": "metadaoproject/futarchy"},
        "dev_wallets":       ["0xMETA_DEV_WALLET_PLACEHOLDER"],
    },
    "metadao_002": {
        "metadata": {
            "title":            "MetaDAO: Double Developer Grant Pool to 1M USDC",
            "proposal":         "Increase the annual developer grant pool from 500k to 1M USDC "
                                "by allocating additional treasury reserves.",
            "venue":            "MetaDAO",
            "opens_at":         "2025-12-01T00:00:00Z",
            "closes_at":        "2025-12-08T00:00:00Z",
            "resolved_outcome": "NO",
        },
        "telegram_channels": {"telegram_founder": "@metadao_official"},
        "twitter_queries":   {"twitter_community": "MetaDAO grants developer fund"},
        "github_repos":      {"github_commits": "metadaoproject/futarchy"},
        "dev_wallets":       ["0xMETA_DEV_WALLET_PLACEHOLDER"],
    },
    "metadao_003": {
        "metadata": {
            "title":            "MetaDAO: Integrate Jito Liquid Staking for Treasury",
            "proposal":         "Stake 30% of the USDC treasury into Jito liquid staking "
                                "to generate yield while maintaining liquidity.",
            "venue":            "MetaDAO",
            "opens_at":         "2026-05-07T00:00:00Z",
            "closes_at":        None,   # Open market — no close date yet
            "resolved_outcome": None,   # Unresolved
        },
        "telegram_channels": {"telegram_founder": "@metadao_official"},
        "twitter_queries":   {"twitter_community": "MetaDAO Jito staking treasury"},
        "github_repos":      {"github_commits": "metadaoproject/futarchy"},
        "dev_wallets":       ["0xMETA_DEV_WALLET_PLACEHOLDER"],
    },
}


# ── Mock signal bundles (written to data/markets/<id>/raw_mock.json) ──────────

def get_mock_bundle(market_id: str) -> dict:
    """Return the full mock bundle {metadata, signals} for a market."""
    config = MARKET_CONFIGS.get(market_id)
    if not config:
        return {}
    return {
        "metadata": config["metadata"],
        "signals":  _signals_for(market_id),
    }


def _signals_for(market_id: str) -> dict:
    if market_id == "metadao_001":
        return {
            "github_commits": {
                "type":                "github",
                "repo":                "metadaoproject/futarchy",
                "avg_commits_per_week": 14.2,
                "contributors":        9,
                "open_prs":            6,
                "stars":               1840,
                "is_active":           True,
                "recent_prs": [
                    "feat: add SOL/USDC perp market scaffolding",
                    "fix: liquidity pool rebalancing edge case",
                    "docs: perpetuals market specification v1.1",
                ],
            },
            "onchain_dev_wallets": {
                "type":              "onchain",
                "total_tx":          18,
                "active_wallets":    2,
                "last_activity":     "2025-11-06T14:22:00Z",
                "notable_transfers": [
                    "200k USDC moved to staging multisig",
                    "Test trade on devnet confirmed",
                ],
            },
            "telegram_founder": [
                "Perps market is live on devnet — public testnet next week! 🚀",
                "200k USDC liquidity provision approved internally. Waiting on governance.",
                "Team is 90% done with the smart contract audit. No critical issues found.",
            ],
            "twitter_community": [
                "MetaDAO perps are coming! Checked the GitHub — solid commit cadence",
                "Smart money is voting YES on the perps proposal. On-chain shows devs active",
                "MetaDAO founder says audit is clean. Bullish.",
            ],
        }

    if market_id == "metadao_002":
        return {
            "github_commits": {
                "type":                "github",
                "repo":                "metadaoproject/futarchy",
                "avg_commits_per_week": 3.1,
                "contributors":        4,
                "open_prs":            2,
                "stars":               1840,
                "is_active":           False,
                "recent_prs": [
                    "chore: bump deps",
                    "fix: minor UI typo",
                ],
            },
            "onchain_dev_wallets": {
                "type":              "onchain",
                "total_tx":          3,
                "active_wallets":    1,
                "last_activity":     "2025-11-20T09:10:00Z",
                "notable_transfers": [
                    "Small gas refill only — no significant treasury movement",
                ],
            },
            "telegram_founder": [
                "We need more developer grants to grow the ecosystem! Vote YES! 💪",
                "1M USDC would attract top builders to MetaDAO. This is essential.",
                "Grant expansion is critical for our roadmap. Community must support this.",
            ],
            "twitter_community": [
                "Treasury doesn't have enough runway for 1M grants. NO vote here.",
                "GitHub activity is down. Why increase grants if existing devs aren't building?",
                "Founder is pushing hard for YES but the numbers don't add up.",
                "MetaDAO treasury audit shows only 1.2M USDC liquid. 1M in grants is 83%!",
            ],
        }

    if market_id == "metadao_003":
        return {
            "github_commits": {
                "type":                "github",
                "repo":                "metadaoproject/futarchy",
                "avg_commits_per_week": 9.7,
                "contributors":        7,
                "open_prs":            5,
                "stars":               1920,
                "is_active":           True,
                "recent_prs": [
                    "feat: Jito LST integration research spike",
                    "docs: treasury yield strategy comparison",
                    "test: jito-sol redemption flow",
                ],
            },
            "onchain_dev_wallets": {
                "type":              "onchain",
                "total_tx":          11,
                "active_wallets":    2,
                "last_activity":     "2026-05-08T16:45:00Z",
                "notable_transfers": [
                    "Small Jito-SOL test stake (5k USDC equivalent)",
                    "Research wallet interacting with Jito staking contract",
                ],
            },
            "telegram_founder": [
                "Jito staking would generate ~8% APY on our idle USDC. Vote YES!",
                "30% staked = ~8M USDC still liquid. No liquidity risk.",
            ],
            "twitter_community": [
                "MetaDAO staking proposal looks interesting — Jito is solid protocol",
                "8% APY claim seems high for USDC-equivalent staking. Check the math.",
                "On-chain shows devs have tested Jito integration. Bullish signal.",
                "Is 30% really safe? What if we need emergency liquidity?",
            ],
        }

    return {}


def get_portfolio() -> list[dict]:
    """Return list of all markets as portfolio entries (for Live Watch UI)."""
    return [
        {**cfg["metadata"], "market_id": mid}
        for mid, cfg in MARKET_CONFIGS.items()
    ]


def get_market(market_id: str) -> dict | None:
    config = MARKET_CONFIGS.get(market_id)
    if not config:
        return None
    return {**config["metadata"], "market_id": market_id}


if __name__ == "__main__":
    import json
    for mid in MARKET_CONFIGS:
        bundle = get_mock_bundle(mid)
        assert bundle["metadata"]["title"]
        assert bundle["signals"]
        print(f"  {mid}: {bundle['metadata']['title'][:60]} — "
              f"{len(bundle['signals'])} sources")
    print("OK — mock_markets.py smoke test passed")
