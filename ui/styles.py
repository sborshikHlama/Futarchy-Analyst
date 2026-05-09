"""
UI Styles & Constants — ui/styles.py
Design system: Mochifi — Outfit font, Mochi Mint #3DE0A5, Deep Space Navy #151B2B.
Dark mode default (Web3-native). Pill buttons, 24px card radius, mint glows.
"""

# ── Brand / Design-system colors ──────────────────────────────────────────────

ACCENT       = "#3DE0A5"   # Mochi Mint — primary accent, buttons, highlights
ACCENT_DARK  = "#2BB887"   # Hover / pressed state
ACCENT_GLOW  = "rgba(61, 224, 165, 0.18)"  # soft glow behind active elements

BG           = "#151B2B"   # Deep Space Navy — main background
SURFACE      = "#1E2638"   # card / panel background
SURFACE_2    = "#252E42"   # elevated surface (nested cards)
BORDER       = "rgba(255, 255, 255, 0.06)"  # subtle card borders

TEXT_MAIN    = "#F8FAFC"   # primary text
TEXT_SEC     = "#94A3B8"   # secondary / muted text
DIVIDER      = "rgba(255, 255, 255, 0.08)"

# Signal / market watch colors
EW_COLORS: dict[str, str] = {
    "GREEN": "#3DE0A5",   # use mint for positive
    "AMBER": "#F59E0B",
    "RED":   "#F87171",
}

STATUS_COLORS: dict[str, str] = {
    "running":          "#60A5FA",
    "frozen":           "#64748B",
    "escalated":        "#F59E0B",
    "awaiting_publish": ACCENT,
    "completed":        "#3DE0A5",
    "failed":           "#F87171",
}

STATUS_LABELS: dict[str, str] = {
    "running":          "Running",
    "frozen":           "Frozen",
    "escalated":        "Escalated",
    "awaiting_publish": "Awaiting Publish",
    "completed":        "Published",
    "failed":           "Failed",
}


# ── CSS ────────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@400;500;600&display=swap');

    /* ── Base reset ── */
    html, body, [class*="css"], .stApp, .stMarkdown {
        font-family: 'Inter', sans-serif !important;
        color: #F8FAFC;
    }

    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700;
        color: #F8FAFC;
    }

    /* ── App shell ── */
    .stApp {
        background-color: #151B2B !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #1E2638 !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* ── Page header card ── */
    .icm-header {
        background: linear-gradient(135deg, #1E2638 0%, #252E42 100%);
        border: 1px solid rgba(61, 224, 165, 0.2);
        box-shadow: 0 0 24px rgba(61, 224, 165, 0.08);
        color: #F8FAFC;
        padding: 1.25rem 1.75rem;
        border-radius: 24px;
        margin-bottom: 1.5rem;
    }
    .icm-header h2 {
        margin: 0;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: -0.3px;
        color: #F8FAFC;
    }
    .icm-header p {
        margin: 0.25rem 0 0;
        font-size: 0.83rem;
        color: #94A3B8;
    }

    /* ── Cards ── */
    .metric-card {
        background: #1E2638;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 24px;
        padding: 1.1rem 1.3rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .metric-card:hover {
        border-color: rgba(61, 224, 165, 0.3);
        box-shadow: 0 0 16px rgba(61, 224, 165, 0.08);
    }
    .metric-card .label {
        font-size: 0.72rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 0.3rem;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
    }
    .metric-card .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'Outfit', sans-serif;
    }

    /* ── Streamlit native metrics ── */
    [data-testid="metric-container"] {
        background: #1E2638;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px;
        padding: 0.9rem 1.1rem;
    }
    [data-testid="metric-container"] label {
        font-size: 0.73rem !important;
        color: #94A3B8 !important;
        font-weight: 600;
        font-family: 'Outfit', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 9999px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: #3DE0A5 !important;
        border: none !important;
        color: #151B2B !important;
        box-shadow: 0 8px 24px -4px rgba(61, 224, 165, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #2BB887 !important;
        box-shadow: 0 12px 28px -4px rgba(61, 224, 165, 0.45) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #F8FAFC !important;
        background: #252E42 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: rgba(61, 224, 165, 0.4) !important;
        color: #3DE0A5 !important;
        background: rgba(61, 224, 165, 0.06) !important;
    }

    /* Sidebar nav buttons */
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 12px !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(61, 224, 165, 0.15) !important;
        color: #3DE0A5 !important;
        box-shadow: none !important;
        border: 1px solid rgba(61, 224, 165, 0.25) !important;
    }

    /* ── Dividers ── */
    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 1.2rem 0;
    }

    /* ── Badges ── */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Outfit', sans-serif;
        letter-spacing: 0.3px;
    }

    .ew-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
    }

    /* ── Row items ── */
    .client-row {
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.5rem;
        background: #1E2638;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .client-row:hover {
        border-color: rgba(61, 224, 165, 0.3);
        box-shadow: 0 0 16px rgba(61, 224, 165, 0.06);
    }

    /* ── Memo container ── */
    .memo-container {
        background: #1E2638;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 24px;
        padding: 1.75rem 2rem;
        line-height: 1.8;
        font-family: 'Inter', sans-serif;
        color: #F8FAFC;
    }

    /* ── Citation highlight ── */
    .citation {
        background: rgba(61, 224, 165, 0.12);
        color: #3DE0A5;
        padding: 0 4px;
        border-radius: 4px;
        font-size: 0.8em;
        font-family: monospace;
    }

    /* ── Audit events ── */
    .audit-event {
        border-left: 3px solid #3DE0A5;
        padding: 0.5rem 0.9rem;
        margin: 0.4rem 0;
        background: #1E2638;
        border-radius: 0 12px 12px 0;
        font-size: 0.83rem;
        color: #F8FAFC;
    }
    .audit-event.det { border-left-color: #475569; }
    .audit-event.ai  { border-left-color: #3DE0A5; }

    /* ── Section title ── */
    .section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 1.4rem 0 0.7rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        color: #F8FAFC !important;
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 16px !important;
        background: #1E2638 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-family: 'Outfit', sans-serif;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        color: #3DE0A5 !important;
        border-bottom-color: #3DE0A5 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
    }

    /* ── Inputs ── */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        background: #252E42 !important;
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3DE0A5 !important;
        box-shadow: 0 0 0 2px rgba(61, 224, 165, 0.15) !important;
    }
    .stSelectbox [data-baseweb="select"] {
        border-radius: 12px !important;
        background: #252E42 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* ── Misc ── */
    .scroll-box { max-height: 500px; overflow-y: auto; padding-right: 0.5rem; }

    .rule-row-pass { background-color: rgba(61, 224, 165, 0.08); border-radius: 8px; }
    .rule-row-fail { background-color: rgba(248, 113, 113, 0.08); border-radius: 8px; }

    .decision-panel {
        background: #1E2638;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px;
        padding: 1.4rem 1.75rem;
        margin-top: 1rem;
    }

    .stAlert {
        border-radius: 16px !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Landing hero ── */
    .hero-section {
        background: linear-gradient(135deg, #1E2638 0%, #252E42 100%);
        border: 1px solid rgba(61, 224, 165, 0.2);
        box-shadow: 0 0 60px rgba(61, 224, 165, 0.07);
        color: #F8FAFC;
        padding: 3.5rem 2.5rem;
        border-radius: 32px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .hero-section h1 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0 0 0.5rem;
        background: linear-gradient(90deg, #3DE0A5, #60A5FA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-section p {
        font-size: 1.05rem;
        color: #94A3B8;
        margin: 0;
    }

    /* ── Dataframes ── */
    .stDataFrame { border-radius: 16px !important; overflow: hidden; }
    [data-testid="stDataFrameResizable"] {
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 16px !important;
    }

    /* ── Code blocks ── */
    code, pre {
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
        background: #252E42 !important;
        border-radius: 8px !important;
        color: #3DE0A5 !important;
    }
</style>
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def page_header(icon: str, title: str, subtitle: str = "") -> str:
    sub = (f"<p style='margin:0.3rem 0 0;font-size:0.83rem;color:#94A3B8'>"
           f"{subtitle}</p>") if subtitle else ""
    return f"<div class='icm-header'><h2>{icon} {title}</h2>{sub}</div>"


def ew_badge_html(level: str) -> str:
    color = EW_COLORS.get(level, TEXT_SEC)
    icons = {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴"}
    icon  = icons.get(level, "⚪")
    return (f'<span class="ew-badge" style="background:rgba(61,224,165,0.12);'
            f'color:{color};border:1px solid {color}40">{icon} {level}</span>')


def status_badge_html(status: str) -> str:
    key   = status.replace("ProcessStatus.", "").lower()
    color = STATUS_COLORS.get(key, TEXT_SEC)
    label = STATUS_LABELS.get(key, key.upper())
    return (f'<span class="status-badge" '
            f'style="background:{color}22;color:{color};border:1px solid {color}44">'
            f'{label}</span>')


def rule_icon(passed) -> str:
    if passed is True:
        return "✅"
    if passed is False:
        return "❌"
    return "⏭️"


def fmt_usd(value: float | None) -> str:
    if value is None:
        return "N/A"
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return str(value)


def highlight_citations(memo_text: str) -> str:
    import re
    return re.sub(
        r"\[CITATION:([^\]]+)\]",
        r'<span class="citation">[CITATION:\1]</span>',
        memo_text,
    )


def node_type_badge(prompt_hash: str | None) -> str:
    return "🤖 AI" if prompt_hash else "⚙️ DET"
