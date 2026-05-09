"""
Settings — ui/page_settings.py
Skills Library · Skills Management · Environment Config
"""
import os
import re
import datetime

import streamlit as st

from ui.styles import ACCENT, TEXT_SEC, page_header


def render_settings_page() -> None:
    st.markdown(page_header("⚙️", "Settings",
                             "Skills Library · Skills Management · Environment Config"),
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "🧠 Skills Library",
        "➕ Skills Management",
        "🌐 Environment",
    ])

    with tab1:
        _render_skills_library()

    with tab2:
        _render_skills_management()

    with tab3:
        _render_env_tab()


# ── Skills Library ──────────────────────────────────────────────────────────────

def _render_skills_library() -> None:
    st.markdown("### Skills Library")
    st.markdown(
        "YAML skill files with versioned prompts and audit hashes. "
        "Every skill is audited and carries an immutable `prompt_hash`."
    )
    st.markdown("---")

    try:
        from skills import registry
        skills = registry.get_all_skills()

        if not skills:
            st.info("No skills found.")
            return

        col_h1, col_h2, col_h3, col_h4 = st.columns([3, 1, 2, 3])
        col_h1.markdown("**Skill**")
        col_h2.markdown("**Version**")
        col_h3.markdown("**Type**")
        col_h4.markdown("**Hash / Approved by**")
        st.markdown(
            "<hr style='border:none;border-top:1px solid #E5E7EB;margin:0.3rem 0'>",
            unsafe_allow_html=True,
        )

        for skill in skills:
            node_icon = "🤖" if skill.get("node_type") == "AI" else "⚙️"
            with st.expander(
                f"{node_icon} **{skill['name']}** (`{skill['skill_key']}`) · v{skill['version']}",
                expanded=False,
            ):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Type:** {skill.get('node_type', 'N/A')}")
                    st.markdown(f"**Author:** {skill.get('author', 'N/A')}")
                with c2:
                    st.markdown(f"**Approved by:** {skill.get('approved_by', 'N/A')}")
                    st.markdown(f"**Approved at:** {skill.get('approved_at', 'N/A')}")
                with c3:
                    st.markdown(f"**Hash:** `{skill['prompt_hash']}`")

                constraints = skill.get("constraints", [])
                if constraints:
                    st.markdown("**Constraints:**")
                    for c in constraints:
                        st.markdown(f"  - {c}")

    except Exception as exc:
        st.error(f"Cannot load Skills: {exc}")


# ── Skills Management ───────────────────────────────────────────────────────────

def _render_skills_management() -> None:
    from skills import registry

    st.markdown("### Skills Management")
    st.markdown(
        "Register a new skill YAML for use in the agent pipeline. "
        "The system generates the YAML, registers it under the skills registry, "
        "and makes it immediately available to any LangGraph node."
    )
    st.markdown("---")

    # Existing custom skills
    skills = registry.get_all_skills()
    core_keys = {"classifier_skill", "synthesizer_skill", "position_skill", "reviewer_skill"}
    custom_skills = [s for s in skills if s["skill_key"] not in core_keys]

    if custom_skills:
        st.markdown("#### Custom skills")
        for s in custom_skills:
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.markdown(f"**{s['name']}** (`{s['skill_key']}`) — v{s['version']} · {s.get('author', '—')}")
            node_icon = "🤖" if s.get("node_type") == "AI" else "⚙️"
            c2.markdown(f"{node_icon} {s.get('node_type', 'N/A')} · `{s['prompt_hash']}`")
            if c3.button("🗑️", key=f"del_{s['skill_key']}", help="Delete skill"):
                registry.delete_skill(s["skill_key"])
                st.success(f"Skill `{s['skill_key']}` deleted.")
                st.rerun()
        st.markdown("---")

    st.markdown("#### Add new skill")

    with st.form("add_skill_form", clear_on_submit=True):
        st.markdown("##### Identity")
        fc1, fc2 = st.columns(2)
        with fc1:
            skill_key = st.text_input(
                "File key *",
                placeholder="my_signal_extractor",
                help="Unique identifier (a-z, 0-9, _). Used as the YAML filename.",
            )
            skill_name = st.text_input(
                "Skill name *",
                placeholder="My Signal Extractor",
            )
        with fc2:
            skill_version = st.text_input("Version *", value="1.0")
            skill_author  = st.text_input("Author / team", placeholder="team_x")

        st.markdown("##### Configuration")
        fc3, fc4 = st.columns(2)
        with fc3:
            node_type = st.selectbox(
                "Node type *",
                options=["AI", "DETERMINISTIC"],
                help="AI = calls Claude API. DETERMINISTIC = pure Python, no LLM.",
            )
            language = st.selectbox("Prompt language", options=["en", "cs"])
        with fc4:
            approved_by = st.text_input("Approved by", placeholder="risk_mgmt")
            approved_at = st.date_input("Approval date", value=datetime.date.today())

        st.markdown("##### Prompt")
        prompt_text = st.text_area(
            "Prompt text *",
            height=220,
            placeholder=(
                "You are a signal extractor for market X. Your task is...\n\n"
                "RULES:\n"
                "1. NEVER invent sources — only cite provided source_ids.\n"
                "2. Every claim must have [CITATION:source_id].\n"
                "3. Return JSON only.\n"
            ),
        )

        st.markdown("##### Constraints (optional)")
        constraints_raw = st.text_area(
            "One constraint per line",
            height=100,
            placeholder=(
                "NEVER invent sources\n"
                "Every claim must have [CITATION:source_id]\n"
                "Return JSON only"
            ),
        )

        st.markdown("##### Data sources (optional)")
        data_sources_raw = st.text_area(
            "One source_id per line",
            height=80,
            placeholder="github\ntelegram\nonchain",
        )

        submitted = st.form_submit_button(
            "Save skill and register", type="primary", use_container_width=True
        )

    if submitted:
        errors = []
        if not skill_key.strip():
            errors.append("File key is required.")
        elif not re.match(r"^[a-z0-9_]+$", skill_key.strip()):
            errors.append("File key may only contain a-z, 0-9 and _.")
        if not skill_name.strip():
            errors.append("Skill name is required.")
        if not skill_version.strip():
            errors.append("Version is required.")
        if not prompt_text.strip():
            errors.append("Prompt text is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            skill_data = {
                "name":                  skill_name.strip(),
                "version":               skill_version.strip(),
                "author":                skill_author.strip() or "custom_team",
                "approved_by":           approved_by.strip() or "pending",
                "approved_at":           str(approved_at),
                "node_type":             node_type,
                "language":              language,
                "constraints":           [l.strip() for l in constraints_raw.splitlines() if l.strip()],
                "data_sources_required": [l.strip() for l in data_sources_raw.splitlines() if l.strip()],
                "prompt":                prompt_text.strip(),
            }
            try:
                saved_path = registry.save_skill(skill_key.strip(), skill_data)
                import hashlib
                ph = hashlib.sha256(prompt_text.strip().encode()).hexdigest()[:12]
                st.success(
                    f"Skill **{skill_name}** (`{skill_key}`) saved.  \n"
                    f"File: `{saved_path.name}` · Prompt hash: `{ph}`  \n"
                    "Skill is immediately available in Skills Library and pipeline nodes."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Save error: {exc}")

    with st.expander("How to use a registered skill in the pipeline", expanded=False):
        st.markdown(
            """
**1. Direct Python call:**
```python
from skills import registry

skill = registry.get("my_signal_extractor")
prompt = skill["prompt"]
# → pass to LLM via utils.llm_factory.get_llm()
```

**2. In a LangGraph AI node:**
```python
from skills import registry
from utils.audit import _audit
from utils.llm_factory import get_llm

def my_node(state):
    skill = registry.get("my_signal_extractor")
    llm = get_llm()
    resp = llm.complete(system=skill["prompt"], user_message=state["raw_signals_json"])
    _audit(state, "my_node", "extract", "ok", prompt=skill["prompt"])
    return {**state, "my_result": resp.text}
```

The YAML file is stored in `skills/<key>.yaml` and auto-loaded by `SkillsRegistry`.
"""
        )


# ── Environment Config ──────────────────────────────────────────────────────────

def _render_env_tab() -> None:
    st.markdown("### Environment Config")
    st.markdown("---")

    umia_env = os.getenv("UMIA_ENV", "demo").lower()
    is_demo  = umia_env != "production"

    if is_demo:
        st.warning("**Demo mode** — mock signals loaded from `data/markets/*/raw_mock.json`; no external APIs called")
    else:
        st.success("**Production mode** — live Apify, GitHub, and Etherscan calls enabled")

    st.markdown("---")
    st.markdown("#### Runtime variables")

    vars_display = [
        ("UMIA_ENV",           os.getenv("UMIA_ENV",           "demo"),     "demo | production"),
        ("LLM_PROVIDER",       os.getenv("LLM_PROVIDER",       "anthropic"), "anthropic | openai"),
        ("LLM_MODEL",          os.getenv("LLM_MODEL",          "(default)"), "claude-opus-4-6 / gpt-4o"),
        ("APIFY_TOKEN",        _mask(os.getenv("APIFY_TOKEN")),              "Apify Actor token (Telegram + Twitter)"),
        ("GITHUB_TOKEN",       _mask(os.getenv("GITHUB_TOKEN")),             "GitHub REST API token"),
        ("ETHERSCAN_API_KEY",  _mask(os.getenv("ETHERSCAN_API_KEY")),        "Etherscan API key (on-chain)"),
        ("ANTHROPIC_API_KEY",  _mask(os.getenv("ANTHROPIC_API_KEY")),        "Claude API key"),
        ("OPENAI_API_KEY",     _mask(os.getenv("OPENAI_API_KEY")),           "OpenAI API key (optional)"),
    ]

    for name, val, desc in vars_display:
        c1, c2, c3 = st.columns([2, 2, 3])
        c1.markdown(f"`{name}`")
        c2.markdown(f"**{val}**")
        c3.markdown(f"<span style='color:{TEXT_SEC};font-size:0.82rem'>{desc}</span>",
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### `.env.example`")
    st.code(
        """UMIA_ENV=demo
LLM_PROVIDER=anthropic
LLM_MODEL=claude-opus-4-6

# Production API keys (leave blank for demo mode)
APIFY_TOKEN=
GITHUB_TOKEN=
ETHERSCAN_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
""",
        language="bash",
    )


def _mask(val: str | None) -> str:
    if not val:
        return "_(not set)_"
    if len(val) <= 8:
        return "••••••••"
    return val[:4] + "••••" + val[-4:]
