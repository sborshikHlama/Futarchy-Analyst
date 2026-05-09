"""
Mock decision markets — utils/mock_markets.py

Three real MetaDAO proposals from early 2024 — chosen for maximum demo impact:
  - metadao_p3: Proposal 3 — Fundraise + META/USDC Spot Market (PASSED, Feb 2024)
  - metadao_p6: Proposal 6 — Ben Hawkins Discount Purchase (FAILED, manipulation caught)
  - metadao_p7: Proposal 7 — Pantera Capital Token Purchase (FAILED, cap unfavorable)

Sources: MetaDAO blog, @metaproph3t, @MetaDAOProject, Helius on-chain data, Discord.
"""

from __future__ import annotations

# ── Market configs (used by utils/ingest/__init__.py) ─────────────────────────

MARKET_CONFIGS: dict[str, dict] = {

    # ── Proposal 3: Fundraise / Spot Market ───────────────────────────────────
    "metadao_p3": {
        "metadata": {
            "title":            "MetaDAO Proposal 3: Fundraise & Launch META/USDC Spot Market",
            "proposal":         "Raise ~$75k USDC via token sale and deploy a META/USDC liquidity "
                                "pool on Meteora AMM. Creates a spot market to separate intrinsic-value "
                                "speculation from proposal outcomes. Pass price: $24.2 · Fail price: $18.9.",
            "venue":            "MetaDAO",
            "opens_at":         "2024-02-07T00:00:00Z",
            "closes_at":        "2024-02-11T00:00:00Z",
            "resolved_outcome": "YES",
        },
        "telegram_channels": {"telegram_metadao": "@metadao_official"},
        "twitter_queries":   {"twitter_community": "MetaDAO Proposal 3 fundraise spot market META"},
        "github_repos":      {"github_futarchy": "metadaoproject/futarchy"},
        "dev_wallets":       ["6Mj5JMkFqvmTEikGBMu4eFsYgzANFyFQgCRpSMVDPcn"],
    },

    # ── Proposal 6: Ben Hawkins Discount Purchase ─────────────────────────────
    "metadao_p6": {
        "metadata": {
            "title":            "MetaDAO Proposal 6: Ben Hawkins META Discount Purchase",
            "proposal":         "Ben Hawkins (Head of Staking Ecosystem, Solana Foundation) proposes "
                                "to purchase 1,500 META (~10% of supply) from treasury at $33.33/META — "
                                "a ~38% discount to spot price of ~$55. Treasury receives $50,000 USDC.",
            "venue":            "MetaDAO",
            "opens_at":         "2024-02-13T00:00:00Z",
            "closes_at":        "2024-02-17T00:00:00Z",
            "resolved_outcome": "NO",
        },
        "telegram_channels": {"telegram_metadao": "@metadao_official"},
        "twitter_queries":   {"twitter_community": "MetaDAO Proposal 6 Ben Hawkins META discount"},
        "github_repos":      {"github_futarchy": "metadaoproject/futarchy"},
        "dev_wallets":       [
            "6Mj5JMkFqvmTEikGBMu4eFsYgzANFyFQgCRpSMVDPcn",  # MetaDAO treasury
            "BenHawkinsWalletPlaceholder111111111111111111",   # Ben's wallet (observed)
        ],
    },

    # ── Proposal 7: Pantera Capital Token Purchase ────────────────────────────
    "metadao_p7": {
        "metadata": {
            "title":            "MetaDAO Proposal 7: Pantera Capital META Token Purchase",
            "proposal":         "Pantera Capital proposes to purchase META tokens from the treasury "
                                "for $50,000 USDC, capped at $100/META (or prevailing TWAP). "
                                "Framed as VC validation of futarchy. Filed immediately after Proposal 6.",
            "venue":            "MetaDAO",
            "opens_at":         "2024-02-17T00:00:00Z",
            "closes_at":        "2024-02-21T00:00:00Z",
            "resolved_outcome": "NO",
        },
        "telegram_channels": {"telegram_metadao": "@metadao_official"},
        "twitter_queries":   {"twitter_community": "MetaDAO Pantera Capital META proposal futarchy"},
        "github_repos":      {"github_futarchy": "metadaoproject/futarchy"},
        "dev_wallets":       ["6Mj5JMkFqvmTEikGBMu4eFsYgzANFyFQgCRpSMVDPcn"],
    },
}


# ── Mock signal bundles ────────────────────────────────────────────────────────

def get_mock_bundle(market_id: str) -> dict:
    config = MARKET_CONFIGS.get(market_id)
    if not config:
        return {}
    return {"metadata": config["metadata"], "signals": _signals_for(market_id)}


def _signals_for(market_id: str) -> dict:

    if market_id == "metadao_p3":
        return {
            "github_futarchy": {
                "type":                "github",
                "repo":                "metadaoproject/futarchy",
                "avg_commits_per_week": 8.4,
                "contributors":        5,
                "open_prs":            3,
                "stars":               312,
                "is_active":           True,
                "recent_prs": [
                    "feat: add Meteora CLMM liquidity pool integration",
                    "docs: META/USDC spot market architecture spec",
                    "fix: TWAP oracle edge case on low-volume markets",
                ],
                "note": "Early-stage repo (Nov 2023 launch). Steady cadence for a 3-month-old project.",
            },
            "onchain_treasury": {
                "type":              "onchain",
                "total_tx":          9,
                "active_wallets":    2,
                "last_activity":     "2024-02-10T21:14:00Z",
                "notable_transfers": [
                    "~4,200 META transferred from treasury to LP staging multisig (Feb 10)",
                    "Meteora pool creation transaction signed by 2/3 multisig (Feb 11 preparation)",
                    "Test liquidity add/remove on devnet — confirmed working",
                ],
                "note": "On-chain shows pre-positioned META ahead of LP launch — team executing.",
            },
            "telegram_metadao": [
                "proph3t: I'm going to be honest — I think Proposal 3 overestimates how much a spot "
                "market helps us right now. We're too early. The liquidity will be thin and we're giving "
                "away META at a discount. I'll vote against but I respect whatever the market decides.",
                "proph3t: The futarchy mechanism exists exactly for this — if the market thinks the spot "
                "liquidity creates more long-term value than I do, they should win. Let's see.",
                "Community mod: Reminder that pass market is at $24.2, fail at $18.9. Gap is widening.",
                "Anonymous trader: The spot market is exactly what MetaDAO needs to grow. Separating "
                "governance value from speculation is fundamental to futarchy working at scale.",
            ],
            "twitter_community": [
                "@metaproph3t: Proposal 3 is live. I disagree with it — I think we're too early for a "
                "spot market and the $75k raise dilutes holders. But that's what markets are for. "
                "Let the mechanism decide. #MetaDAO #futarchy",
                "@trader_7layer: Wild that the founder is publicly campaigning against his own DAO's "
                "proposal. But this is futarchy working as intended — no veto power, just price signals.",
                "@Barrett_DeFi: Checked the MetaDAO GitHub — devs already have Meteora integration "
                "drafted. The team wants this to happen regardless of proph3t's public stance.",
                "@solana_anon: pass pMETA at $24.2 vs fail fMETA at $18.9. Market is saying the spot "
                "launch adds $5.3 per META in long-term value. That's a strong signal.",
                "@metadao_community: Founder opposition to his own proposal is actually a BULLISH "
                "signal for futarchy — proves the mechanism is credibly neutral.",
            ],
        }

    if market_id == "metadao_p6":
        return {
            "github_futarchy": {
                "type":                "github",
                "repo":                "metadaoproject/futarchy",
                "avg_commits_per_week": 6.1,
                "contributors":        5,
                "open_prs":            2,
                "stars":               389,
                "is_active":           True,
                "recent_prs": [
                    "chore: minor UI updates",
                    "docs: add proposal lifecycle documentation",
                ],
                "note": "No commits related to Proposal 6. This is a treasury token sale, not a "
                        "development initiative. GitHub signal is irrelevant to the core question.",
            },
            "onchain_treasury": {
                "type":              "onchain",
                "total_tx":          47,
                "active_wallets":    6,
                "last_activity":     "2024-02-16T23:58:00Z",
                "peak_deposits_usdc": 330000,
                "peak_meta_deposited": 4200,
                "manipulation_wallet": "BenHawkinsWalletPlaceholder111111111111111111",
                "notable_transfers": [
                    "Feb 13: Ben wallet deposits 180k USDC into pMETA (pass) market",
                    "Feb 13: Ben wallet sells 1,800 META into fMETA (fail) market — drives fail price down",
                    "Feb 14: Additional 90k USDC from Ben wallet → pMETA. Total Ben exposure: ~$250k+",
                    "Feb 14: Arbitrageur 1 (7Layer wallet) sells pMETA, buys fMETA — correcting spread",
                    "Feb 15: Arbitrageur 2 dumps 800 META into pass market — 'this proposal is bad for holders'",
                    "Feb 15: 3 new wallets buying fMETA in coordinated 4-hour window",
                    "Feb 16: Peak — 330k USDC + 4,200 META deposited across both sides",
                    "Feb 17: fMETA price recovers above pMETA — fail market wins",
                ],
                "note": "Clear manipulation signature: one wallet (Ben) spent >$250k attempting to "
                        "artificially inflate pass market. Arbitrageurs responded and corrected within 48h. "
                        "This is the largest single-wallet manipulation attempt in MetaDAO history.",
            },
            "telegram_metadao": [
                "Ben Hawkins: I believe deeply in MetaDAO and in futarchy. This purchase is at a fair "
                "discount given the liquidity risk the DAO takes on an illiquid token. I'm putting my "
                "money where my mouth is — I've taken a significant position in the pass market.",
                "Community member: Checked on-chain. Ben has deposited >180k USDC into pMETA in the "
                "last 6 hours. That's not investing — that's trying to buy the vote.",
                "proph3t: I want to be clear — I have not and will not coordinate with any party to "
                "influence this market. The mechanism should resolve this. Watch the arbitrage.",
                "Mod: For context, Ben Hawkins is Head of Staking Ecosystem at Solana Foundation. "
                "He is proposing this in a personal capacity, not on behalf of Solana Foundation.",
                "Community member: The fail market is being suppressed by large META sells. "
                "Someone is trying to make failure look cheap. Classic manipulation.",
                "7Layer: I've been arbing this since hour 1. The spread is artificial. "
                "Pass market is overpriced relative to intrinsic value at $33.33/META.",
            ],
            "twitter_community": [
                "@BenHawkins_SF: I'm proposing to buy 1,500 META at $33.33 from @MetaDAOProject treasury. "
                "$50k USDC. I believe in the team and this is fair value for an illiquid token. "
                "Let the market decide. #futarchy #MetaDAO",
                "@BenHawkins_SF: Update: I've taken a position in the pass market. I'm not just proposing "
                "— I'm putting capital behind my conviction. This is how futarchy should work.",
                "@Barrett_DeFi: On-chain shows Ben has spent over $200k trying to push the pass market. "
                "At $33.33/META vs spot $55, he would make 65% instantly on resolution. "
                "This isn't conviction — this is a trade.",
                "@trader_7layer: Spent the last 3 hours arbing Proposal 6. Pass market is artificially "
                "inflated. Selling pMETA, buying fMETA. The mechanism is working — price will correct.",
                "@solana_defi_anon: MetaDAO is getting stress-tested in real time. Someone with "
                "deep pockets is trying to buy a $55 asset at $33. The question is whether "
                "arbitrageurs can outgun them. So far: yes.",
                "@MetaDAOProject: The futarchy mechanism is functioning as designed. Large deposits "
                "from any single party create arbitrage opportunities for other participants. "
                "We are monitoring and will update the community.",
                "@metaproph3t: This is exactly why TWAP-based resolution matters. "
                "Flash deposits don't win. Time-weighted truth wins.",
            ],
        }

    if market_id == "metadao_p7":
        return {
            "github_futarchy": {
                "type":                "github",
                "repo":                "metadaoproject/futarchy",
                "avg_commits_per_week": 7.2,
                "contributors":        6,
                "open_prs":            4,
                "stars":               421,
                "is_active":           True,
                "recent_prs": [
                    "feat: TWAP resolution improvements post-P6 stress test",
                    "docs: update manipulation resistance documentation",
                    "fix: arbitrage cooldown mechanism",
                ],
                "note": "Active development continues. Post-P6 commits show team hardening the "
                        "mechanism — positive signal for protocol credibility but not directly "
                        "relevant to whether Pantera's cap terms are fair.",
            },
            "onchain_treasury": {
                "type":              "onchain",
                "total_tx":          14,
                "active_wallets":    4,
                "last_activity":     "2024-02-20T18:30:00Z",
                "notable_transfers": [
                    "Pantera-linked wallet tests $500 USDC → pMETA (likely technical validation)",
                    "3 community arbitrage wallets active from P6 now monitoring P7",
                    "META spot price on Meteora (post-P3 LP): $87 as of Feb 18, already above $100 cap",
                    "fMETA accumulation starting Feb 19 — market pricing in fail from day 2",
                ],
                "note": "META spot is already at $87 at proposal open, trending toward $100 cap. "
                        "At $100 cap, Pantera gets META at a discount only if price stays below $100 — "
                        "but TWAP over 4 days likely resolves above cap. DAO gets no premium for the risk.",
            },
            "telegram_metadao": [
                "Community member: Pantera is a top-tier VC. Even a failed proposal proves they're "
                "watching MetaDAO. This is validation.",
                "proph3t: The cap at $100 was reasonable when Pantera wrote this. META was at ~$70. "
                "It's now at $87 and rising. The market is pricing in whether the cap stays attractive.",
                "Analyst: At $100 cap, Pantera would get META at a discount IF resolved before price "
                "crosses. But TWAP over 4 days... META could easily resolve above $100. Then what? "
                "Pantera gets nothing and DAO gave up 4 days of market clarity for free.",
                "Community member: Proposal 7 is interesting but the terms are already stale. "
                "META outran the cap. Voting NO isn't anti-Pantera — it's protecting holder value.",
                "Mod: Remember that P7 was submitted hours after P6 resolved. This feels like "
                "a legitimate VC testing the water after watching P6's drama.",
            ],
            "twitter_community": [
                "@PanteraCapital: We're submitting a proposal to purchase META tokens from @MetaDAOProject. "
                "$50,000 USDC, capped at $100/META. We believe in futarchy as a governance primitive "
                "and want skin in the game. Let the market decide. 🔮",
                "@metaproph3t: Honored that @PanteraCapital is engaging with MetaDAO. "
                "The $100 cap was set when META was ~$70. Community will decide if the terms "
                "still make sense. This is exactly how futarchy should work.",
                "@Barrett_DeFi: Pantera's $100 cap was reasonable 4 days ago. META is now $87 "
                "and trending. TWAP resolution over 4 days likely puts average above $100. "
                "If so: Pantera gets 0 META, DAO got nothing for the governance overhead. Voting NO.",
                "@trader_7layer: Proposal 7 is a legitimate proposal with stale terms. Not a manipulation. "
                "But 'not manipulation' ≠ 'good for META holders.' Fail market looks right here.",
                "@solana_defi_anon: The subtext of P7: Pantera is bullish on futarchy and wants "
                "to be an early holder. That's credibility. But the specific terms expired. "
                "A renegotiated cap above $100 could easily pass — this one won't.",
                "@crypto_research_: MetaDAO has now run two token-purchase proposals in one week. "
                "Both failed. The market is saying: we don't sell META at a discount, "
                "even to credible buyers. That's a strong signal for protocol confidence.",
            ],
        }

    return {}


def get_portfolio() -> list[dict]:
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
        print(f"  {mid}: {bundle['metadata']['title'][:70]} — "
              f"{len(bundle['signals'])} sources")
    print("OK — mock_markets.py smoke test passed")
