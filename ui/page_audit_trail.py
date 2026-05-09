"""
Audit Trail Viewer — ui/page_audit_trail.py
Immutable pipeline audit log with AI/DET node distinction.
"""

import json
import streamlit as st
from pathlib import Path

from ui.styles import ACCENT, page_header

_DATA_DIR = Path(__file__).parent.parent / "data" / "markets"


def render_audit_trail_page() -> None:
    st.markdown(page_header("🔍", "Audit Trail",
                             "Immutable log of every pipeline action · AI nodes with prompt hash · DET nodes without LLM"),
                unsafe_allow_html=True)

    from utils.mock_markets import MARKET_CONFIGS
    market_options = {mid: cfg["metadata"]["title"] for mid, cfg in MARKET_CONFIGS.items()}

    preselected = st.session_state.get("audit_market") or st.session_state.get("selected_market")
    default_idx = 0
    if preselected and preselected in market_options:
        default_idx = list(market_options.keys()).index(preselected)

    market_id = st.selectbox(
        "Select market",
        options=list(market_options.keys()),
        format_func=lambda x: market_options.get(x, x),
        index=default_idx,
        key="audit_market_select",
    )

    memo = _load_memo(market_id)
    if memo is None:
        st.info("No memo generated for this market. Run the pipeline on the **Memo Detail** page first.")
        if st.button("Go to Memo Detail", type="primary"):
            st.session_state["selected_market"] = market_id
            st.session_state["page"] = "memo_detail"
            st.rerun()
        return

    audit_trail = memo.get("audit_trail", [])
    audit_events = memo.get("audit_events", 0)

    if audit_trail:
        _render_full_trail(audit_trail, memo, market_id)
    else:
        _render_summary_only(audit_events, memo, market_id)


def _load_memo(market_id: str) -> dict | None:
    memo_path = _DATA_DIR / market_id / "memo.json"
    if not memo_path.exists():
        return None
    with memo_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _render_summary_only(audit_events: int, memo: dict, market_id: str) -> None:
    st.info(f"This memo was generated with **{audit_events}** pipeline audit events. "
            "Full event log is available when the pipeline runs in the current session.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Audit Events", audit_events)
    col2.metric("Published", memo.get("published_at", "—")[:10] if memo.get("published_at") else "—")
    col3.metric("Generated", memo.get("generated_at", "—")[:10] if memo.get("generated_at") else "—")

    st.markdown("---")
    st.markdown("### Memo metadata")
    st.markdown(f"- **Market ID:** `{market_id}`")
    st.markdown(f"- **Published at:** `{memo.get('published_at', '—')}`")
    st.markdown(f"- **Generated at:** `{memo.get('generated_at', '—')}`")
    pos = memo.get("position") or {}
    st.markdown(f"- **Position:** {pos.get('side', '—')} @ {pos.get('size_pct', 0):.1f}%")
    st.markdown(f"- **Confidence:** {memo.get('confidence', 0):.2f}")
    st.markdown(f"- **Position iteration:** {memo.get('position_iteration', 0)}")


def _render_full_trail(audit_trail: list, memo: dict, market_id: str) -> None:
    ai_events  = [e for e in audit_trail if e.get("prompt_hash")]
    det_events = [e for e in audit_trail if not e.get("prompt_hash")]
    total_tokens = sum(e.get("tokens_used") or 0 for e in audit_trail)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", len(audit_trail))
    col2.metric("AI Nodes", len(ai_events))
    col3.metric("DET Nodes", len(det_events))
    col4.metric("Total Tokens", f"{total_tokens:,}")

    filter_type = st.radio(
        "Filter nodes",
        options=["All", "AI Nodes", "DET Nodes"],
        horizontal=True,
        key="audit_filter",
    )

    filtered = audit_trail
    if filter_type == "AI Nodes":
        filtered = ai_events
    elif filter_type == "DET Nodes":
        filtered = det_events

    st.markdown(f"**{len(filtered)} events** ({filter_type})")
    st.markdown("---")

    for i, event in enumerate(filtered, 1):
        _render_event(i, event)

    st.markdown("---")

    with st.expander("Export Audit Trail"):
        json_str = json.dumps(audit_trail, ensure_ascii=False, indent=2)
        st.download_button(
            "Download audit trail (.json)",
            data=json_str,
            file_name=f"audit_trail_{market_id}.json",
            mime="application/json",
        )

        lines = []
        for e in audit_trail:
            ph = f" [hash:{e['prompt_hash']}]" if e.get("prompt_hash") else " [DET]"
            tok = f" tokens={e['tokens_used']}" if e.get("tokens_used") else ""
            lines.append(f"{e.get('timestamp','')[:19]} | {e.get('node','?')} | "
                         f"{e.get('action','?')} → {e.get('result','?')}{ph}{tok}")
        txt = "\n".join(lines)
        st.download_button(
            "Download audit trail (.txt)",
            data=txt,
            file_name=f"audit_trail_{market_id}.txt",
            mime="text/plain",
        )


def _render_event(index: int, event: dict) -> None:
    node         = event.get("node", "N/A")
    action       = event.get("action", "N/A")
    result       = event.get("result", "N/A")
    timestamp    = event.get("timestamp", "")
    prompt_hash  = event.get("prompt_hash")
    prompt_ver   = event.get("prompt_version")
    tokens       = event.get("tokens_used")
    metadata     = event.get("metadata", {})

    is_ai = bool(prompt_hash)
    border_color = ACCENT if is_ai else "#9CA3AF"
    bg_color = "#EEF2FF" if is_ai else "#F9FAFB"
    badge = "🤖 AI" if is_ai else "⚙️ DET"

    result_str = str(result).lower()
    if any(kw in result_str for kw in ("fail", "freeze", "error", "breach")):
        result_color = "#DC2626"
    elif any(kw in result_str for kw in ("pass", "success", "ok", "completed", "published")):
        result_color = "#16A34A"
    else:
        result_color = "#D97706"

    details = []
    if prompt_hash:
        details.append(f"hash:`{prompt_hash}`")
    if prompt_ver:
        details.append(f"v{prompt_ver}")
    if tokens:
        details.append(f"{tokens:,} tokens")
    if metadata:
        meta_str = " · ".join(
            f"{k}={v}" for k, v in metadata.items()
            if v is not None and v != [] and v != {}
        )
        if meta_str:
            details.append(meta_str)

    detail_str = " · ".join(details)

    st.markdown(
        f"""
        <div style="border-left:4px solid {border_color};background:{bg_color};
             padding:0.6rem 0.9rem;margin:0.4rem 0;border-radius:0 8px 8px 0">
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span><strong>{index:02d}. {node}</strong>
                    <span style="margin-left:0.4rem;font-size:0.8rem;color:#6B7280">{badge}</span>
                </span>
                <span style="font-size:0.78rem;color:#9CA3AF">{timestamp[:19]}</span>
            </div>
            <div style="margin-top:0.2rem">
                <code style="background:#E5E7EB;padding:0.1rem 0.3rem;border-radius:3px;
                             font-size:0.82rem">{action}</code>
                → <span style="color:{result_color};font-weight:600;font-size:0.85rem">{result}</span>
            </div>
            {f'<div style="font-size:0.78rem;color:#6B7280;margin-top:0.2rem">{detail_str}</div>' if detail_str else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
