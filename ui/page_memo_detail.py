"""
Memo Detail — ui/page_memo_detail.py
Runs the pipeline for a market and displays the full memo.
Replaces page_credit_memo.py.
"""

import json
import os
import streamlit as st
from pathlib import Path
from ui.styles import ACCENT, page_header, highlight_citations, fmt_pct

_DATA_DIR = Path(__file__).parent.parent / "data" / "markets"


def render_memo_detail_page():
    st.markdown(page_header("📄", "Trading Memo",
                             "Generate or view an analysis memo for a decision market"),
                unsafe_allow_html=True)

    from utils.mock_markets import MARKET_CONFIGS

    # Market selector
    market_options = {mid: cfg["metadata"]["title"] for mid, cfg in MARKET_CONFIGS.items()}
    selected_mid = st.session_state.get("selected_market")

    col1, col2 = st.columns([3, 1])
    with col1:
        market_id = st.selectbox(
            "Select market",
            options=list(market_options.keys()),
            format_func=lambda x: market_options.get(x, x),
            index=list(market_options.keys()).index(selected_mid)
            if selected_mid in market_options else 0,
        )
    with col2:
        run_btn = st.button("Generate Memo", type="primary", use_container_width=True)

    if run_btn:
        st.session_state["selected_market"] = market_id
        _run_pipeline(market_id)
        return

    # Try to load existing memo
    memo = _load_memo(market_id)
    if memo is None:
        st.info("No memo generated yet for this market. Click **Generate Memo** to run the pipeline.")
        return

    _render_memo(memo)


def _run_pipeline(market_id: str):
    from pipeline.graph import run_pipeline
    from pipeline.state import ProcessStatus

    with st.status("Running Umia Analyst Agent pipeline...", expanded=True) as status:
        st.write("Phase 1: Classifying signal sources...")
        st.write("Phase 2: Synthesizing bull/bear cases...")
        st.write("Phase 3: Taking position + self-review...")
        st.write("Phase 4: Publishing memo...")
        try:
            result = run_pipeline(market_id)
            if str(result.get("status")) in ("ProcessStatus.COMPLETED", "completed"):
                status.update(label="Memo published!", state="complete")
                st.success(f"Position: **{result.get('position', {}).get('side')}** "
                           f"@ {result.get('position', {}).get('size_pct', 0):.1f}% — "
                           f"Confidence: {result.get('confidence', 0):.2f}")
            else:
                status.update(label=f"Pipeline status: {result.get('status')}", state="error")
                if result.get("fallback_reason"):
                    st.warning(f"Reason: {result['fallback_reason']}")
        except Exception as exc:
            status.update(label="Pipeline error", state="error")
            st.error(str(exc))
        st.rerun()


def _load_memo(market_id: str) -> dict | None:
    memo_path = _DATA_DIR / market_id / "memo.json"
    if not memo_path.exists():
        return None
    with memo_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _render_memo(memo: dict):
    meta = memo.get("market_metadata") or {}
    pos  = memo.get("position") or {}
    sr   = memo.get("self_review") or {}
    out  = memo.get("outcome") or {}
    conf = memo.get("confidence", 0)
    flags = memo.get("manipulation_flags", [])
    source_weights = memo.get("source_weights", {})

    # Header
    side = pos.get("side", "ABSTAIN")
    side_color = {"YES": "#16A34A", "NO": "#DC2626", "ABSTAIN": "#6B7280"}.get(side, "#6B7280")
    pnl = out.get("pnl_pct")
    pnl_str   = f"{pnl:+.1f}%" if pnl is not None else "Open"

    st.markdown(f"""
    <div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:10px;
                padding:1.2rem 1.5rem;margin-bottom:1rem">
        <div style="font-size:1.1rem;font-weight:700">{meta.get('title','')}</div>
        <div style="font-size:0.85rem;color:#4B5563;margin-top:0.3rem">
            {meta.get('proposal','')}
        </div>
        <div style="margin-top:0.8rem;display:flex;gap:1.5rem;align-items:center">
            <span style="font-size:1.3rem;font-weight:800;color:{side_color}">{side}</span>
            <span style="color:#4B5563">@ {pos.get('size_pct',0):.1f}% treasury</span>
            <span style="color:#4B5563">Confidence: {conf:.0%}</span>
            <span style="color:#4B5563">PnL: <b>{pnl_str}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Memo", "Sources", "Self-Review", "Audit Trail"])

    with tab1:
        # Bull case
        st.markdown("### Bull Case")
        bull = memo.get("bull_case", "")
        st.markdown(highlight_citations(bull) if bull else "_No bull case generated_",
                    unsafe_allow_html=True)

        # Bear case
        st.markdown("### Bear Case")
        bear = memo.get("bear_case", "")
        st.markdown(highlight_citations(bear) if bear else "_No bear case generated_",
                    unsafe_allow_html=True)

        # Position rationale
        st.markdown("### Position Rationale")
        st.markdown(pos.get("rationale", "—"))

        # Manipulation flags
        if flags:
            st.markdown("### Manipulation Flags")
            for flag in flags:
                st.warning(flag)

        # Outcome
        if out:
            st.markdown("### Outcome")
            resolved = out.get("resolved_side", "—")
            pnl_v    = out.get("pnl_pct", 0)
            color    = "#16A34A" if pnl_v > 0 else "#DC2626" if pnl_v < 0 else "#6B7280"
            st.markdown(f"Resolved: **{resolved}** · PnL: "
                        f"<span style='color:{color};font-weight:700'>{pnl_v:+.1f}%</span>",
                        unsafe_allow_html=True)

    with tab2:
        if not source_weights:
            st.info("No source weights recorded.")
        else:
            for src_id, sw in source_weights.items():
                cls   = sw.get("class_", "unknown")
                w     = sw.get("weight", 0)
                rsn   = sw.get("reasoning", "")
                cls_color = {"verifiable": "#16A34A", "partial": "#D97706",
                             "manipulable": "#DC2626"}.get(cls, "#6B7280")
                st.markdown(f"""
                <div class="client-row">
                    <span style="font-weight:600">{src_id}</span>
                    &nbsp;
                    <span style="color:{cls_color};font-size:0.8rem">[{cls}]</span>
                    &nbsp; weight=<b>{w:.2f}</b>
                    <br><span style="font-size:0.82rem;color:#4B5563">{rsn}</span>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        if not sr:
            st.info("No self-review recorded.")
        else:
            st.markdown("**Weaknesses**")
            for w in sr.get("weaknesses", []):
                st.markdown(f"- {w}")
            st.markdown("**Counter-arguments**")
            for ca in sr.get("counter_arguments", []):
                st.markdown(f"- {ca}")

    with tab4:
        audit_events = memo.get("audit_events", 0)
        st.markdown(f"This memo was generated with **{audit_events}** pipeline audit events.")
        st.markdown(f"Published: `{memo.get('published_at','—')}`")
        st.markdown(f"Generated: `{memo.get('generated_at','—')}`")
        st.info("Full audit trail available in the Audit Trail page.")
