# Umia Analyst Agent · CLAUDE.md
## Developer Context for Claude Code

---

## Project

**Umia Analyst Agent** is an autonomous research analyst for futarchic decision markets.
LangGraph + Claude/GPT-4o + Streamlit + Apify/GitHub/Etherscan.

Built for Umia Protocol Hackathon 2026 — "Best Agentic Venture" bounty.

---

## File architecture

```
app.py                              ← Streamlit entry point (7-page nav)
agent/
  run.py                            ← CLI: --market, --all-backtest, --track-record

pipeline/
  state.py                          ← AgentState, ProcessStatus (TypedDict)
  graph.py                          ← LangGraph StateGraph (build_graph, run_pipeline)
  routing.py                        ← Conditional edges (DETERMINISTIC)
  nodes/
    phase1_extraction.py            ← AI: SourceClassifierAgent + DET: ClassificationValidator
    phase2_analysis.py              ← DET: MemoContextBuilder + AI: Synthesizer
    phase3_maker_checker.py         ← AI: PositionAgent + SelfReviewer
                                       DET: PositionRulesEngine (hard caps)
    phase4_human_audit.py           ← DET: PublishNode + RecordPublishDecision

early_warning/
  graph.py                          ← Live Watch LangGraph pipeline (run_live_watch)
  state.py                          ← make_initial_watch_state()
  nodes/
    portfolio_loader.py             ← DET: load_open_markets
    metrics_calculator.py           ← DET: calculate_market_signal_scores
    anomaly_detector.py             ← DET: detect_market_anomalies + AI text
    alert_generator.py              ← DET: generate_watch_alerts
    alert_dispatcher.py             ← DET: dispatch_watch_alerts

skills/
  __init__.py                       ← SkillsRegistry singleton
  classifier_skill.yaml             ← SourceClassifier v1.0
  synthesizer_skill.yaml            ← Synthesizer v1.0
  position_skill.yaml               ← PositionAgent v1.0
  reviewer_skill.yaml               ← SelfReviewer v1.0

utils/
  source_rules.py                   ← SOURCE_CLASS_MAX_WEIGHT, position caps,
                                       check_position_rules(), classify_signal_level()
  pnl.py                            ← compute_pnl(), attach_outcome_to_memo(),
                                       aggregate_track_record()
  mock_markets.py                   ← MARKET_CONFIGS (3 MetaDAO markets),
                                       get_mock_bundle(), get_portfolio(), get_market()
  ingest/
    __init__.py                     ← gather_signals(market_id, mock)
    apify_telegram.py               ← fetch_telegram(channel, days, mock)
    apify_twitter.py                ← fetch_tweets(query, days, max_items, mock)
    github_activity.py              ← fetch_github_activity(repo, weeks, mock)
    onchain.py                      ← fetch_wallet_activity(addresses, days, mock)
  audit.py                          ← _audit(state, node, action, result, prompt, ...)
                                       → immutable append-only, sha256[:12] for AI nodes
  llm_factory.py                    ← get_llm() → LLMClient(provider, model)
  chunking.py                       ← semantic_chunk()

ui/
  styles.py                         ← Manrope font, ACCENT=#5B5BD6, TEXT_MAIN=#0B0F17
                                       GLOBAL_CSS, page_header(), ew_badge_html(),
                                       fmt_pct(), fmt_usd()
  page_landing.py                   ← Hero, how-it-works, track record, roadmap
  page_memo_archive.py              ← All memos with positions and PnL
  page_memo_detail.py               ← Market selector + pipeline runner + 4-tab memo view
  page_live_watch.py                ← Open market monitoring (run_live_watch)
  page_track_record.py              ← KPIs + running PnL chart + memo table
  page_settings.py                  ← Skills Library + Skills Management + Env Config
  page_audit_trail.py               ← Immutable pipeline audit log

data/markets/
  metadao_001/                      ← raw_mock.json + memo.json (after pipeline run)
  metadao_002/
  metadao_003/
```

---

## Invariant rules (NEVER break)

### 1. Deterministic vs. AI split

- `# DETERMINISTIC` — pure Python, no LLM
- `# AI` — calls Claude/GPT via `utils/llm_factory.py`
- **LLM NEVER does math** — all scoring via `utils/source_rules.py`
- Every AI node reads its prompt from the skills registry (versioned YAML)

### 2. Audit Trail

- `_audit()` from `utils/audit.py` must be called in every node
- Audit trail is **append-only** — never mutate existing events
- AI nodes: `prompt=skill["prompt"]` → auto-hashed sha256[:12]
- DET nodes: `prompt=None` → `prompt_hash=None` in log

### 3. API Failure → Process Freeze

- On Claude/GPT API failure: `status = ProcessStatus.FROZEN`
- **NEVER** fallback silently to stale data
- Max retries: `API_RETRY_COUNT = 3`, delay: `API_RETRY_DELAY_SEC = 30`

### 4. Position iteration cap

- Max iterations: `MAX_POSITION_ITERATIONS = 3` (guard in `source_rules.py`)
- On exceeded: `status = ProcessStatus.ESCALATED`
- Self-reviewer checks only citations and hallucinations — not math

### 5. Source weight caps

```python
SOURCE_CLASS_MAX_WEIGHT = {
    "verifiable":  1.0,
    "partial":     0.6,
    "manipulable": 0.3,
}
```

No manipulable source may exceed weight 0.3.

### 6. Demo / Production mode

- `UMIA_ENV=demo` → reads from `data/markets/*/raw_mock.json`; no external API calls
- `UMIA_ENV=production` → calls Apify, GitHub REST, Etherscan via `utils/ingest/`
- If demo file missing → `ProcessStatus.FROZEN` (no silent fallback)

### 7. PnL model

```
WIN  (YES @ p, resolves YES): ((1-p)/p) * size_pct
WIN  (NO  @ p, resolves NO ): ((1-p)/p) * size_pct  (p = NO price)
LOSS: -size_pct
ABSTAIN: 0
```

---

## Branding

```
Product name:    Umia Analyst Agent
Protocol:        Umia Protocol
Font:            Manrope (Google Fonts)
Primary color:   #5B5BD6 (ACCENT)
Hover color:     #4A4ABF (ACCENT_DARK)
Main text:       #0B0F17 (TEXT_MAIN)
Secondary text:  #4B5563 (TEXT_SEC)
Divider:         #E5E7EB (DIVIDER)
Surface / cards: #F9FAFB (SURFACE)
Background:      #FFFFFF (BG)
```

---

## UI Navigation (app.py)

```python
PAGES = {
    "landing":      "🏠 Home",
    "memo_archive": "📚 Memo Archive",
    "memo_detail":  "📄 Memo Detail",
    "live_watch":   "👁️ Live Watch",
    "track_record": "📈 Track Record",
    "settings":     "⚙️ Settings",
    "audit_trail":  "🔍 Audit Trail",
}
```

Default page: `landing`.

---

## LLM Factory

```python
from utils.llm_factory import get_llm

llm = get_llm()   # reads LLM_PROVIDER + LLM_MODEL from env
resp = llm.complete(
    system=skill["prompt"],
    user_message=context_json,
    max_tokens=2048,
)
text   = resp.text
tokens = resp.tokens_used
```

Default models:
- `anthropic` → `claude-opus-4-6`
- `openai` → `gpt-4o`

---

## Skills Management

```python
from skills import registry

skill = registry.get("position_skill")
prompt = skill["prompt"]
ph = registry.get_prompt_hash("position_skill")  # sha256[:12]

path = registry.save_skill("my_skill", {
    "name": "My Signal Agent",
    "version": "1.0",
    "author": "team_x",
    "node_type": "AI",
    "language": "en",
    "approved_by": "risk_mgmt",
    "approved_at": "2026-05-01",
    "constraints": ["NEVER invent sources"],
    "data_sources_required": ["github", "telegram"],
    "prompt": "You are a signal analyst...",
})

registry.delete_skill("my_skill")
```

---

## Source rules

```python
SOURCE_CLASS_MAX_WEIGHT = {
    "verifiable":  1.0,   # GitHub commits, on-chain txns
    "partial":     0.6,   # Forum posts with evidence
    "manipulable": 0.3,   # Telegram, Twitter
}

MAX_POSITION_SIZE_PCT   = 7.0
MIN_CONFIDENCE_TO_BET   = 0.6
MIN_CITATION_COVERAGE   = 0.85
MAX_POSITION_ITERATIONS = 3
API_RETRY_COUNT         = 3
API_RETRY_DELAY_SEC     = 30
```

---

## Demo markets

| Market ID | Title | Resolved |
|-----------|-------|---------|
| `metadao_001` | SOL/USDC Perpetuals | YES |
| `metadao_002` | Double Developer Grant Pool | NO |
| `metadao_003` | Jito LST Treasury Staking | OPEN |

---

## Run

```bash
# Demo UI
UMIA_ENV=demo streamlit run app.py

# CLI single market
UMIA_ENV=demo python -m agent.run --market metadao_001

# CLI backtest all
UMIA_ENV=demo python -m agent.run --all-backtest

# Smoke tests
python -m utils.source_rules
python -m utils.pnl
python -m utils.mock_markets
python -m utils.ingest
python -m utils.audit
python -m utils.llm_factory
python -m pipeline.nodes.phase2_analysis
python -m pipeline.nodes.phase3_maker_checker
python -m pipeline.nodes.phase4_human_audit
python -m early_warning.graph
```

---

## Audit log

| Date | What | Result |
|------|------|--------|
| 2026-05-09 | Domain transformation: Horizon Bank → Umia Analyst Agent | Complete |
