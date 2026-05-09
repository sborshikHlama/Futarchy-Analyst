"""
Track Record — ui/page_track_record.py
Aggregated PnL and performance history. Replaces page_cases_log.py.
"""

import streamlit as st
from ui.styles import page_header


def render_track_record_page():
    st.markdown(page_header("📈", "Track Record",
                             "Aggregated realized PnL across all resolved markets"),
                unsafe_allow_html=True)

    from utils.pnl import aggregate_track_record
    record = aggregate_track_record()

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Memos",  record["total_memos"])
    k2.metric("Resolved",     record["resolved"])
    k3.metric("Win Rate",     f"{record['win_rate']:.0f}%")
    k4.metric("Total PnL",    f"{record['total_pnl_pct']:+.1f}%")
    k5.metric("W / L / A",   f"{record['win_count']} / {record['loss_count']} / {record['abstain_count']}")

    st.markdown("---")

    memos = record.get("memos", [])
    if not memos:
        st.info("No memos generated yet.")
        return

    # Running PnL chart
    resolved_memos = [m for m in memos if m.get("outcome")]
    if resolved_memos:
        st.markdown("### Running PnL")
        import pandas as pd
        rows = []
        running = 0.0
        for m in resolved_memos:
            out = m.get("outcome", {})
            pnl = out.get("pnl_pct", 0)
            running += pnl
            rows.append({
                "Market": m.get("market_metadata", {}).get("title", m.get("market_id",""))[:40],
                "PnL":    pnl,
                "Running PnL": running,
            })
        df = pd.DataFrame(rows)
        st.line_chart(df.set_index("Market")[["Running PnL"]])

    st.markdown("---")
    st.markdown("### All Memos")

    for memo in memos:
        meta  = memo.get("market_metadata") or {}
        pos   = memo.get("position") or {}
        out   = memo.get("outcome") or {}
        conf  = memo.get("confidence", 0)
        side  = pos.get("side", "ABSTAIN")
        pnl   = out.get("pnl_pct")

        side_color = {"YES": "#16A34A", "NO": "#DC2626", "ABSTAIN": "#6B7280"}.get(side, "#6B7280")
        pnl_str    = f"{pnl:+.1f}%" if pnl is not None else "Open"
        pnl_color  = "#16A34A" if pnl and pnl > 0 else ("#DC2626" if pnl and pnl < 0 else "#6B7280")

        c1, c2, c3, c4, c5 = st.columns([3, 1.5, 1, 1.5, 1])
        with c1:
            st.markdown(f"**{meta.get('title','')[:70]}**")
            st.caption(f"{meta.get('venue','?')} · {memo.get('published_at','?')[:10]}")
        with c2:
            st.markdown(f"<span style='color:{side_color};font-weight:700'>"
                        f"{side} @ {pos.get('size_pct',0):.1f}%</span>",
                        unsafe_allow_html=True)
        with c3:
            st.markdown(f"Conf: **{conf:.2f}**" if conf else "—")
        with c4:
            st.markdown(f"<span style='color:{pnl_color};font-weight:700'>{pnl_str}</span>"
                        f" ({out.get('resolved_side','Open')})",
                        unsafe_allow_html=True)
        with c5:
            if st.button("View", key=f"tr_{memo.get('market_id','')}"):
                st.session_state["selected_market"] = memo.get("market_id")
                st.session_state["page"] = "memo_detail"
                st.rerun()
        st.markdown("---")
