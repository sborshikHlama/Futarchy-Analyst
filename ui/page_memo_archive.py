"""
Memo Archive — ui/page_memo_archive.py
Lists all generated memos with positions and PnL. Replaces page_portfolio.py.
"""

import streamlit as st
from ui.styles import ACCENT, page_header, fmt_pct, ew_badge_html


def render_memo_archive_page():
    st.markdown(page_header("📚", "Memo Archive",
                             "All generated Trading Memos with positions and outcomes"),
                unsafe_allow_html=True)

    from utils.pnl import aggregate_track_record
    record = aggregate_track_record()
    memos  = record.get("memos", [])

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Memos", record["total_memos"])
    k2.metric("Resolved",    record["resolved"])
    k3.metric("Win Rate",    f"{record['win_rate']:.0f}%")
    k4.metric("Total PnL",   f"{record['total_pnl_pct']:+.1f}%")

    st.markdown("---")

    if not memos:
        st.info("No memos generated yet. Run the pipeline on a market to generate the first memo.")
        if st.button("Run Demo Pipeline", type="primary"):
            st.session_state["page"] = "memo_detail"
            st.rerun()
        return

    # Filter
    side_filter = st.radio("Filter by position", ["All", "YES", "NO", "ABSTAIN"],
                            horizontal=True, index=0)

    for memo in memos:
        meta = memo.get("market_metadata") or {}
        pos  = memo.get("position") or {}
        out  = memo.get("outcome") or {}
        conf = memo.get("confidence")

        side = pos.get("side", "ABSTAIN")
        if side_filter != "All" and side != side_filter:
            continue

        side_color = {"YES": "#16A34A", "NO": "#DC2626", "ABSTAIN": "#6B7280"}.get(side, "#6B7280")
        pnl = out.get("pnl_pct")
        pnl_str   = f"{pnl:+.1f}%" if pnl is not None else "Open"
        pnl_color = "#16A34A" if pnl and pnl > 0 else ("#DC2626" if pnl and pnl < 0 else "#6B7280")
        resolved  = out.get("resolved_side", "—")

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([4, 1.5, 1.5, 1.5, 1])
            with col1:
                title = meta.get("title", memo.get("market_id", "Unknown"))
                st.markdown(f"**{title[:80]}**")
                st.caption(f"Venue: {meta.get('venue','?')} · "
                           f"Published: {memo.get('published_at','?')[:10]}")
            with col2:
                st.markdown(f"<span style='color:{side_color};font-weight:700'>"
                            f"{side} @ {pos.get('size_pct',0):.1f}%</span>",
                            unsafe_allow_html=True)
            with col3:
                st.markdown(f"Conf: **{conf:.2f}**" if conf else "Conf: —")
            with col4:
                st.markdown(f"<span style='color:{pnl_color};font-weight:700'>{pnl_str}</span>"
                            f" (resolved: {resolved})",
                            unsafe_allow_html=True)
            with col5:
                if st.button("View", key=f"view_{memo.get('market_id','')}"):
                    st.session_state["selected_market"] = memo.get("market_id")
                    st.session_state["page"] = "memo_detail"
                    st.rerun()
            st.markdown("---")
