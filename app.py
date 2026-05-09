"""
Umia Analyst Agent — app.py
Autonomous research analyst for futarchic decision markets.

Pages:
  1. Landing       — hero, how it works, track record, roadmap
  2. Memo Archive  — all generated memos with positions and PnL
  3. Memo Detail   — run pipeline or view existing memo
  4. Live Watch    — open market signal monitoring
  5. Track Record  — aggregated PnL and performance history
  6. Settings      — skills library and environment config
  7. Audit Trail   — immutable pipeline audit log

Run:
    UMIA_ENV=demo streamlit run app.py
"""

import logging
import sys

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

st.set_page_config(
    page_title="Umia Analyst Agent",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.styles import ACCENT, GLOBAL_CSS
from ui.page_landing import render_landing_page
from ui.page_memo_archive import render_memo_archive_page
from ui.page_memo_detail import render_memo_detail_page
from ui.page_live_watch import render_live_watch_page
from ui.page_track_record import render_track_record_page
from ui.page_settings import render_settings_page
from ui.page_audit_trail import render_audit_trail_page

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

PAGES = {
    "landing":       "🏠 Home",
    "memo_archive":  "📚 Memo Archive",
    "memo_detail":   "📄 Memo Detail",
    "live_watch":    "👁️ Live Watch",
    "track_record":  "📈 Track Record",
    "settings":      "⚙️ Settings",
    "audit_trail":   "🔍 Audit Trail",
}


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            f"""
            <div style="background:{ACCENT};color:white;padding:1rem 1.2rem;
                 border-radius:10px;margin-bottom:1.2rem;text-align:center">
                <div style="font-size:2rem">🔮</div>
                <div style="font-weight:700;font-size:1rem;margin-top:0.2rem">Umia Analyst Agent</div>
                <div style="font-size:0.72rem;opacity:0.8;margin-top:0.1rem">
                    Autonomous · Futarchic · On-chain track record
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Navigation")

        if "page" not in st.session_state:
            st.session_state["page"] = "landing"

        for key, label in PAGES.items():
            active = st.session_state.get("page") == key
            btn_type = "primary" if active else "secondary"
            if st.button(label, key=f"nav_{key}", type=btn_type, use_container_width=True):
                st.session_state["page"] = key
                st.rerun()

        st.markdown("---")

        # Active market info
        selected = st.session_state.get("selected_market")
        if selected:
            try:
                from utils.mock_markets import MARKET_CONFIGS
                cfg = MARKET_CONFIGS.get(selected, {})
                title = cfg.get("metadata", {}).get("title", selected)
                st.markdown(
                    f"<div style='font-size:0.82rem;color:#4B5563'>"
                    f"<b>Active market:</b><br>{title[:50]}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")
            except Exception:
                pass

        import os
        umia_env = os.getenv("UMIA_ENV", "demo").lower()
        env_color = "#D97706" if umia_env == "demo" else "#16A34A"
        st.markdown(
            f"<div style='font-size:0.75rem;color:#9CA3AF'>"
            f"Umia Analyst Agent v0.1<br>"
            f"LangGraph + Claude API<br>"
            f"Audit Trail: immutable<br>"
            f"<span style='color:{env_color};font-weight:600'>{umia_env.upper()} mode</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    return st.session_state.get("page", "landing")


def main() -> None:
    page = render_sidebar()

    log.debug(f"[App] Rendering page: {page}")

    if page == "landing":
        render_landing_page()
    elif page == "memo_archive":
        render_memo_archive_page()
    elif page == "memo_detail":
        render_memo_detail_page()
    elif page == "live_watch":
        render_live_watch_page()
    elif page == "track_record":
        render_track_record_page()
    elif page == "settings":
        render_settings_page()
    elif page == "audit_trail":
        render_audit_trail_page()
    else:
        st.error(f"Unknown page: {page}")


if __name__ == "__main__":
    main()
