"""
Live Memo Watch — ui/page_live_watch.py
Monitor open decision markets for signal changes. Replaces page_early_warning.py.
"""

import streamlit as st
from ui.styles import page_header, ew_badge_html


def render_live_watch_page():
    st.markdown(page_header("👁️", "Live Memo Watch",
                             "Monitor open markets for signal changes in real time"),
                unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        run_btn = st.button("Run Watch Scan", type="primary", use_container_width=True)

    if run_btn or "watch_result" not in st.session_state:
        with st.spinner("Scanning open markets..."):
            try:
                from early_warning.graph import run_live_watch
                result = run_live_watch("on_demand")
                st.session_state["watch_result"] = result
            except Exception as exc:
                st.error(f"Watch scan failed: {exc}")
                return

    result = st.session_state.get("watch_result", {})
    summary = result.get("summary", {})
    open_markets = result.get("open_markets", [])
    watch_alerts = result.get("watch_alerts", [])
    scores = result.get("metrics_computed", {})

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Open Markets",  summary.get("total_markets", 0))
    k2.metric("High Signal",   summary.get("high_signal", 0))
    k3.metric("Medium Signal", summary.get("medium_signal", 0))
    k4.metric("Low Signal",    summary.get("low_signal", 0))

    st.markdown("---")

    # Alerts
    if watch_alerts:
        st.markdown("### Signal Alerts")
        for alert in watch_alerts:
            level = alert.get("signal_level", "LOW")
            level_color = {"HIGH": "#DC2626", "MEDIUM": "#D97706", "LOW": "#16A34A"}.get(level, "#6B7280")
            st.markdown(f"""
            <div class="client-row" style="border-left:4px solid {level_color}">
                <span style="color:{level_color};font-weight:700">[{level}]</span>
                &nbsp;<span style="font-weight:600">{alert.get('title','')}</span><br>
                <span style="font-size:0.84rem;color:#4B5563">{alert.get('description','')}</span><br>
                <span style="font-size:0.82rem;color:#6B7280">
                    Action: {alert.get('recommended_action','')}
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Open Markets")

    if not open_markets:
        st.info("No open markets found. All demo markets have been resolved.")
        return

    for market in open_markets:
        mid   = market.get("market_id", "")
        score = scores.get(mid, {})
        level = score.get("signal_level", "LOW")
        hours = score.get("hours_to_close")
        level_color = {"HIGH": "#DC2626", "MEDIUM": "#D97706", "LOW": "#16A34A"}.get(level, "#6B7280")

        with st.expander(f"**{market.get('title','')[:80]}** — {level} signal"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Signal Level", level)
            c2.metric("Sources",      score.get("source_count", 0))
            if hours is not None:
                c3.metric("Hours to Close", f"{hours:.0f}h")

            st.markdown(f"""
            - GitHub: {'✅' if score.get('has_github') else '❌'}
            - On-chain: {'✅' if score.get('has_onchain') else '❌'}
            - Social: {'✅' if score.get('has_social') else '❌'}
            """)

            if st.button("Generate Memo", key=f"gen_{mid}"):
                st.session_state["selected_market"] = mid
                st.session_state["page"] = "memo_detail"
                st.rerun()
