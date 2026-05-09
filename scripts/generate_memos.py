"""Generate pre-baked memo.json files for the three demo markets."""
import json

# ── Proposal 3: Passed YES ────────────────────────────────────────────────────
memo_p3 = {
    "market_id": "metadao_p3",
    "request_id": "req_backtest_p3",
    "market_metadata": {
        "title": "MetaDAO Proposal 3: Fundraise & Launch META/USDC Spot Market",
        "proposal": (
            "Raise ~$75k USDC via token sale and deploy a META/USDC liquidity pool on Meteora AMM. "
            "Creates a spot market to separate intrinsic-value speculation from proposal outcomes. "
            "Pass price: $24.2 vs Fail price: $18.9."
        ),
        "venue": "MetaDAO",
        "opens_at": "2024-02-07T00:00:00Z",
        "closes_at": "2024-02-11T00:00:00Z",
        "resolved_outcome": "YES",
    },
    "source_weights": {
        "github_futarchy": {
            "class_": "verifiable",
            "weight": 0.72,
            "reasoning": (
                "Steady 8.4 commits/week for a 3-month-old protocol is strong for stage. "
                "Meteora LP integration PR is directly on-topic — team is executing the "
                "proposal deliverable before it passes."
            ),
        },
        "onchain_treasury": {
            "class_": "verifiable",
            "weight": 0.88,
            "reasoning": (
                "Pre-positioned META in staging multisig and Meteora test transactions on Feb 10 "
                "are a clear operational signal. The team is ready to execute immediately on resolution."
            ),
        },
        "telegram_metadao": {
            "class_": "manipulable",
            "weight": 0.18,
            "reasoning": (
                "Founder (proph3t) is publicly arguing AGAINST the proposal via this channel — "
                "the opposite of typical founder-channel manipulation. This reduces but does not "
                "eliminate the manipulable classification, as channel is still founder-controlled."
            ),
        },
        "twitter_community": {
            "class_": "partial",
            "weight": 0.51,
            "reasoning": (
                "Community and independent traders citing on-chain evidence and GitHub corroborate "
                "the verifiable signals. Founder opposition publicly noted and priced in by commentators."
            ),
        },
    },
    "classification_attempts": 1,
    "bull_case": (
        "Strong verifiable signals support a YES outcome. [CITATION:onchain_treasury] "
        "The MetaDAO treasury staged ~4,200 META into a Meteora LP multisig on February 10 "
        "and completed test transactions — the team is operationally ready to execute the moment "
        "the proposal passes. [CITATION:github_futarchy] The futarchy repository shows a Meteora "
        "CLMM integration PR already merged, confirming the technical work is complete ahead of "
        "the vote. [CITATION:twitter_community] Independent traders observing the pMETA/fMETA "
        "spread ($24.2 pass vs $18.9 fail) note the market is pricing a $5.3/META value-add "
        "from the spot launch — a meaningful signal for a $75k investment. "
        "Critically, the pass market price reflects intrinsic-value expectations, not social momentum."
    ),
    "bear_case": (
        "The most credible bear signal is the founder himself. [CITATION:telegram_metadao] "
        "Proph3t publicly stated he believes MetaDAO is too early for a spot market and that "
        "thin liquidity will undermine price discovery rather than improve it. "
        "This is not typical founder-channel noise — it is an informed insider view. "
        "[CITATION:twitter_community] Some community members echo this concern: a $75k raise "
        "at a discount dilutes existing holders for a liquidity pool that may see under $10k "
        "daily volume in early months. If the spot market fails to attract organic trading "
        "volume, the futarchy signal it was supposed to provide becomes worthless."
    ),
    "manipulation_flags": [
        "Founder (proph3t) publicly opposing his own proposal via official Telegram. "
        "Note: this is ANTI-manipulation (founder arguing against YES), not pro-manipulation. "
        "Reduces weight on telegram_metadao to 0.18."
    ],
    "confidence": 0.74,
    "position": {
        "side": "YES",
        "size_pct": 5.0,
        "rationale": (
            "Verifiable on-chain and GitHub signals dominate. The team has pre-executed the "
            "technical deliverable and staged treasury funds — costly-to-fake actions that "
            "strongly predict follow-through on resolution. Founder opposition is a legitimate "
            "bear signal and has been weighted accordingly, reducing confidence from ~0.82 to 0.74. "
            "At 0.74 confidence: 5.0% treasury. Pass market at $24.2 vs fail at $18.9 implies "
            "~56% pass probability — our 0.74 confidence is meaningfully above consensus."
        ),
    },
    "self_review": {
        "weaknesses": [
            "Founder has more context on treasury health and product readiness than any external analyst",
            "Meteora LP with thin initial liquidity could generate adverse selection and impermanent loss",
            "Our on-chain signal (pre-positioned META) could reflect team optimism rather than certainty",
        ],
        "counter_arguments": [
            "If Meteora pool attracts under $5k daily volume, the spot market becomes a liability",
            "A failed spot market launch could damage MetaDAO credibility more than not having one",
            "The $75k raise at discount is real dilution — if META rises post-launch it looks worse",
        ],
    },
    "position_iteration": 1,
    "reviewer_verdict": "APPROVE",
    "outcome": {"resolved_side": "YES", "pnl_pct": 3.33},
    "status": "completed",
    "audit_events": 9,
    "generated_at": "2024-02-09T11:22:04Z",
    "published_at": "2024-02-09T11:23:17Z",
}

# ── Proposal 6: Failed NO ─────────────────────────────────────────────────────
memo_p6 = {
    "market_id": "metadao_p6",
    "request_id": "req_backtest_p6",
    "market_metadata": {
        "title": "MetaDAO Proposal 6: Ben Hawkins META Discount Purchase",
        "proposal": (
            "Ben Hawkins (Head of Staking Ecosystem, Solana Foundation) proposes to purchase "
            "1,500 META (~10% of supply) from treasury at $33.33/META — a ~38% discount to "
            "spot price of ~$55. Treasury receives $50,000 USDC."
        ),
        "venue": "MetaDAO",
        "opens_at": "2024-02-13T00:00:00Z",
        "closes_at": "2024-02-17T00:00:00Z",
        "resolved_outcome": "NO",
    },
    "source_weights": {
        "github_futarchy": {
            "class_": "verifiable",
            "weight": 0.12,
            "reasoning": (
                "GitHub is nearly irrelevant here. Proposal 6 is a token sale, not a development "
                "initiative. Commits continue at normal cadence — no signal either way."
            ),
        },
        "onchain_treasury": {
            "class_": "verifiable",
            "weight": 0.97,
            "reasoning": (
                "CRITICAL SIGNAL. On-chain shows a single wallet depositing >180k USDC into pMETA "
                "(pass) market and simultaneously selling META into fMETA (fail) market — a textbook "
                "manipulation attempt. Peak: 330k USDC + 4,200 META across both sides from "
                "concentrated sources. Three arbitrageur wallets responded within 48h. "
                "This is the clearest on-chain manipulation signature in MetaDAO history."
            ),
        },
        "telegram_metadao": {
            "class_": "manipulable",
            "weight": 0.21,
            "reasoning": (
                "Ben Hawkins posting in MetaDAO channels to justify his position — classic conflict "
                "of interest where the proposer is also the largest market participant. Community "
                "members independently identifying the on-chain manipulation corroborate verifiable signals."
            ),
        },
        "twitter_community": {
            "class_": "partial",
            "weight": 0.58,
            "reasoning": (
                "Independent analysts (Barrett, 7Layer) calculating Ben's on-chain exposure in real "
                "time and publicly calling the manipulation. Their analysis is consistent with "
                "verifiable on-chain data — unusually high signal quality for a Twitter source."
            ),
        },
    },
    "classification_attempts": 1,
    "bull_case": (
        "The proposal does offer the DAO $50,000 USDC in immediate liquidity. "
        "[CITATION:twitter_community] Ben Hawkins' supporters argue he is a credible figure "
        "(Head of Staking at Solana Foundation) whose involvement could attract further "
        "institutional interest in MetaDAO. [CITATION:telegram_metadao] Ben himself frames "
        "the 38% discount as fair compensation for taking on illiquid-token risk, "
        "citing standard VC discount norms for early-stage protocols. "
        "If META's intrinsic value is below $33.33, the DAO is actually receiving fair value."
    ),
    "bear_case": (
        "[CITATION:onchain_treasury] On-chain evidence is unambiguous: a single wallet has "
        "deposited >180,000 USDC into the pass (pMETA) market and simultaneously sold META "
        "into the fail (fMETA) market to suppress the fail price. Total Ben-linked market "
        "exposure exceeds $250,000 — 5x the proposed $50k USDC purchase price. "
        "This is not conviction investing; this is an attempt to manufacture consent in a "
        "mechanism designed to prevent exactly this. [CITATION:twitter_community] "
        "Independent trader 7Layer has publicly disclosed active arbitrage: selling overpriced "
        "pMETA and buying underpriced fMETA, which directly corrects the manipulation. "
        "[CITATION:onchain_treasury] META spot at $55 means a $33.33 purchase yields an "
        "instant 65% gain on resolution — the discount is value extraction, not a liquidity premium."
    ),
    "manipulation_flags": [
        "CONFIRMED MARKET MANIPULATION: Single wallet (Ben Hawkins) deposited >180k USDC into "
        "pass market and sold META into fail market to artificially inflate pass probability. "
        "Total exposure >$250k.",
        "Proposer is simultaneously the largest market participant — severe conflict of interest.",
        "On-chain shows coordinated sell pressure on fMETA from 3 wallets in a 4-hour window "
        "on Feb 15 — possible coordination.",
        "Arbitrageurs (7Layer, Barrett) have publicly disclosed counter-positions, confirming "
        "informed market participants are actively correcting the manipulation.",
    ],
    "confidence": 0.87,
    "position": {
        "side": "NO",
        "size_pct": 5.0,
        "rationale": (
            "Confidence 0.87 — highest in this backtest set. On-chain manipulation is unambiguous "
            "and verifiable, not inferential. The proposer spent 5x the proposal value attempting "
            "to manipulate the market, which is itself proof that terms are highly favorable to him. "
            "Arbitrageurs are actively correcting — the mechanism is working. "
            "TWAP resolution over 4 days will price in the arbitrage correction. "
            "Position: NO at 5.0% treasury (confidence >= 0.85 tier)."
        ),
    },
    "self_review": {
        "weaknesses": [
            "Ben Hawkins is genuinely credible — Solana Foundation affiliation is not nothing",
            "If MetaDAO truly needs liquidity and no other buyers exist, the $50k USDC has real option value",
            "We cannot rule out that Ben's market position represents genuine conviction, not manipulation",
        ],
        "counter_arguments": [
            "If arbitrageurs are wrong and pass market prevails via TWAP, our NO position loses 5%",
            "Reputation cost from failing a Solana Foundation-affiliated proposal could outweigh economic case",
            "Our on-chain interpretation assumes Ben's wallet identity — mis-attribution invalidates the flag",
        ],
    },
    "position_iteration": 1,
    "reviewer_verdict": "APPROVE",
    "outcome": {"resolved_side": "NO", "pnl_pct": 2.14},
    "status": "completed",
    "audit_events": 12,
    "generated_at": "2024-02-14T08:45:33Z",
    "published_at": "2024-02-14T08:46:51Z",
}

# ── Proposal 7: Failed NO ─────────────────────────────────────────────────────
memo_p7 = {
    "market_id": "metadao_p7",
    "request_id": "req_backtest_p7",
    "market_metadata": {
        "title": "MetaDAO Proposal 7: Pantera Capital META Token Purchase",
        "proposal": (
            "Pantera Capital proposes to purchase META tokens from the treasury for $50,000 USDC, "
            "capped at $100/META (or prevailing TWAP). Framed as VC validation of futarchy. "
            "Filed immediately after Proposal 6."
        ),
        "venue": "MetaDAO",
        "opens_at": "2024-02-17T00:00:00Z",
        "closes_at": "2024-02-21T00:00:00Z",
        "resolved_outcome": "NO",
    },
    "source_weights": {
        "github_futarchy": {
            "class_": "verifiable",
            "weight": 0.31,
            "reasoning": (
                "Post-P6 commits (TWAP hardening, manipulation resistance) show a healthy team. "
                "Indirectly bullish for protocol credibility but does not speak to whether "
                "the $100 cap is fair at current prices."
            ),
        },
        "onchain_treasury": {
            "class_": "verifiable",
            "weight": 0.79,
            "reasoning": (
                "META spot price on Meteora (post-P3 LP) is $87 at proposal open and trending upward. "
                "TWAP over a 4-day window starting at $87 will almost certainly resolve above $100. "
                "On-chain fMETA accumulation starting day 2 confirms market participants reaching "
                "the same conclusion independently."
            ),
        },
        "telegram_metadao": {
            "class_": "manipulable",
            "weight": 0.29,
            "reasoning": (
                "Proph3t neutrally explaining the cap mechanics. Community analyzing cap vs TWAP math "
                "independently. No obvious manipulation — channel signal is informational."
            ),
        },
        "twitter_community": {
            "class_": "partial",
            "weight": 0.55,
            "reasoning": (
                "Pantera official announcement confirms legitimacy of proposal. Independent analysts "
                "applying correct TWAP logic. Community correctly distinguishing between VC credibility "
                "(positive) and specific cap terms (unfavorable at current META price)."
            ),
        },
    },
    "classification_attempts": 1,
    "bull_case": (
        "[CITATION:twitter_community] Pantera Capital is a top-tier crypto VC whose engagement "
        "with MetaDAO governance is meaningful external validation of the futarchy model. "
        "[CITATION:github_futarchy] Active post-P6 development shows a team that strengthens "
        "the protocol under stress — exactly what a VC performs due diligence on. "
        "If META retraces below $100 before close, the cap becomes fair and the DAO receives "
        "$50k USDC at a reasonable rate. [CITATION:twitter_community] Proph3t noted that "
        "institutional interest despite a failed resolution is credibility, not failure."
    ),
    "bear_case": (
        "[CITATION:onchain_treasury] META spot opened at $87 on February 17 and traded to "
        "$94 by day 2 of the proposal window. The $100 cap was set when META was ~$70 — "
        "terms are already stale at proposal open. A TWAP calculated over 4 days from $87 "
        "upward will almost certainly resolve above $100. [CITATION:onchain_treasury] "
        "On-chain fMETA accumulation beginning February 19 confirms market participants have "
        "independently reached this conclusion. [CITATION:twitter_community] Barrett's analysis "
        "is correct: if TWAP resolves above $100, Pantera gets 0 META and the DAO spent 4 days "
        "of governance overhead for zero economic outcome. The proposal is not bad in principle — "
        "the cap is simply expired."
    ),
    "manipulation_flags": [],
    "confidence": 0.76,
    "position": {
        "side": "NO",
        "size_pct": 5.0,
        "rationale": (
            "Pantera's proposal is legitimate — no manipulation flags. The NO position is purely "
            "economic: META at $87 trending upward makes a $100 TWAP cap almost certain to resolve "
            "out-of-the-money for Pantera. On-chain price data is the primary signal and is "
            "unambiguous. Confidence 0.76 -> 5% position (0.70-0.85 tier). "
            "Lower confidence than P6 because there is no manipulation — just mispriced terms — "
            "and META could theoretically reverse below $100."
        ),
    },
    "self_review": {
        "weaknesses": [
            "META could retrace below $100 if broader Solana market corrects during the 4-day window",
            "Pantera may have private information justifying $100 as a ceiling, not a floor",
            "We are extrapolating a short-term price trend — TWAP is sensitive to intra-day volatility",
        ],
        "counter_arguments": [
            "A Pantera deal at any price could unlock institutional pipeline the market has not priced in",
            "If Pantera withdraws or renegotiates, the market dynamic changes entirely",
            "The post-P3 Meteora pool may have thin liquidity susceptible to third-party price manipulation",
        ],
    },
    "position_iteration": 2,
    "reviewer_verdict": "APPROVE",
    "outcome": {"resolved_side": "NO", "pnl_pct": 2.69},
    "status": "completed",
    "audit_events": 11,
    "generated_at": "2024-02-18T16:03:22Z",
    "published_at": "2024-02-18T16:04:44Z",
}

for mid, memo in [("metadao_p3", memo_p3), ("metadao_p6", memo_p6), ("metadao_p7", memo_p7)]:
    with open(f"data/markets/{mid}/memo.json", "w") as f:
        json.dump(memo, f, indent=2)
    print(f"  {mid}: {memo['position']['side']} @ {memo['position']['size_pct']}% "
          f"-> PnL {memo['outcome']['pnl_pct']:+.2f}%")
