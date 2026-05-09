"""
Landing page — ui/page_landing.py
Pitch page for judges. Hero + 3-step explainer + track record + token mechanics.
"""

import streamlit as st
from ui.styles import ACCENT, GLOBAL_CSS, page_header


def render_landing_page():
    st.markdown("""
    <div class="hero-section">
        <h1>Umia Analyst Agent</h1>
        <p>The first autonomous research analyst for futarchic decision markets.<br>
        It reads the signals. It takes positions. It tracks its own PnL.</p>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("View Memo Archive", type="primary", use_container_width=True):
            st.session_state["page"] = "memo_archive"
            st.rerun()
    with col2:
        if st.button("Live Watch", type="secondary", use_container_width=True):
            st.session_state["page"] = "live_watch"
            st.rerun()
    with col3:
        if st.button("Track Record", type="secondary", use_container_width=True):
            st.session_state["page"] = "track_record"
            st.rerun()

    st.markdown("---")

    # The Problem
    st.markdown("## The Problem")
    st.markdown("""
    Futarchic markets reward voters who can distinguish signal from noise.
    But the signal is adversarial:

    - **Founder-controlled channels** (Telegram, Twitter) are designed to push YES
    - **GitHub and on-chain data** are harder to fake but harder to read
    - Most traders can't process all three simultaneously at prediction-market speed

    The result: markets are dominated by insiders and narrative traders, not analysts.
    """)

    st.markdown("---")

    # How it works
    st.markdown("## How It Works")
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("1. Ingest", "Telegram · Twitter · GitHub · On-chain wallets"),
        ("2. Classify", "Verifiable / Partial / Manipulable — weighted credibility"),
        ("3. Synthesize", "Bull case · Bear case · Manipulation flags"),
        ("4. Position", "YES / NO / ABSTAIN with confidence-scaled size"),
    ]
    for col, (title, desc) in zip([c1, c2, c3, c4], steps):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">{title}</div>
                <div style="font-size:0.88rem;color:#4B5563;margin-top:0.4rem">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Track record summary
    st.markdown("## Track Record (Backtested)")
    from utils.pnl import aggregate_track_record
    record = aggregate_track_record()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Memos Generated", record["total_memos"])
    m2.metric("Win Rate", f"{record['win_rate']:.0f}%")
    m3.metric("Total PnL", f"{record['total_pnl_pct']:+.1f}%")
    m4.metric("Unresolved", record["unresolved"])

    if record["memos"]:
        st.markdown("#### Recent Memos")
        for memo in record["memos"][:3]:
            meta = memo.get("market_metadata") or {}
            pos  = memo.get("position") or {}
            out  = memo.get("outcome") or {}
            side = pos.get("side", "ABSTAIN")
            side_color = {"YES": "#16A34A", "NO": "#DC2626", "ABSTAIN": "#6B7280"}.get(side, "#6B7280")
            pnl  = out.get("pnl_pct")
            pnl_str = f"{pnl:+.1f}%" if pnl is not None else "Open"
            pnl_color = "#16A34A" if pnl and pnl > 0 else ("#DC2626" if pnl and pnl < 0 else "#6B7280")

            st.markdown(f"""
            <div class="client-row">
                <span style="font-weight:700">{meta.get('title','Unknown')[:70]}</span>
                &nbsp;&nbsp;
                <span style="color:{side_color};font-weight:600">{side} @ {pos.get('size_pct',0):.1f}%</span>
                &nbsp;&nbsp;
                <span style="color:{pnl_color};font-weight:700">{pnl_str}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Why it's a venture
    st.markdown("## Why This Is a Venture, Not a Tool")
    st.markdown("""
    The agent builds a **public, on-chain track record**. That track record is an asset.

    **Token mechanics (v1):**
    - Investors mint `$UMIA-ANALYST` tokens proportional to their capital contribution
    - The agent's trading book is the underlying asset
    - Token holders share in realized PnL from confirmed market resolutions
    - New memos are published on-chain — full transparency, no black box

    **Why this is fundable on Umia:**
    The protocol rewards agents with demonstrable edge. Backtested PnL + reproducible
    methodology = launchable with a credible track record from day one.
    """)

    st.markdown("---")

    # Roadmap
    st.markdown("## Roadmap")
    r1, r2, r3, r4 = st.columns(4)
    phases = [
        ("Phase 1 — Now", "Backtest on 3 MetaDAO markets. Publish memos. Prove the model."),
        ("Phase 2 — Q3 2026", "Live trading on Umia + Polymarket. Real capital deployment."),
        ("Phase 3 — Q4 2026", "Token launch on Umia. Crowdfunded trading book."),
        ("Phase 4 — 2027", "Multi-chain. Cosmos governance. DAO proposal monitoring."),
    ]
    for col, (title, desc) in zip([r1, r2, r3, r4], phases):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">{title}</div>
                <div style="font-size:0.82rem;color:#4B5563;margin-top:0.4rem">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Tech stack
    st.markdown("## Tech Stack")
    st.markdown("""
    | Layer | Technology |
    |-------|-----------|
    | Agent pipeline | LangGraph (multi-step, conditional routing) |
    | LLM | Claude Opus 4.7 (Anthropic) |
    | Signal ingestion | Apify (Telegram, Twitter) · GitHub REST API · Etherscan |
    | Skills | YAML-versioned prompts with sha256 audit hashes |
    | Audit trail | Append-only, immutable, prompt-hashed |
    | UI | Streamlit |
    | Storage | JSON files (demo) → on-chain (production) |
    """)

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#9CA3AF;font-size:0.8rem'>"
        "Umia Analyst Agent · Built for Umia Protocol Hackathon · 2026"
        "</div>",
        unsafe_allow_html=True
    )
