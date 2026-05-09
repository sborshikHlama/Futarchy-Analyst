# Umia Analyst Agent

**The first autonomous research analyst for futarchic decision markets.**  
It reads the signals. It takes positions. It tracks its own PnL.

Built for the **Umia Protocol Hackathon 2026** · "Best Agentic Venture" bounty.

---

## What it does

Umia Analyst Agent monitors decision markets (MetaDAO, Polymarket, Umia) and:

1. **Ingests** signals from Telegram, Twitter, GitHub commit activity, and on-chain wallet flows
2. **Classifies** each source as `verifiable / partial / manipulable` with weight caps
3. **Synthesizes** a bull case and bear case, flagging manipulation attempts
4. **Takes a position** — YES / NO / ABSTAIN — scaled by confidence (max 7% treasury)
5. **Publishes a trading memo** with full audit trail and prompt hashes
6. **Tracks realized PnL** as markets resolve

---

## Architecture

```
Signal Ingestion (Apify / GitHub / Etherscan)
          │
          ▼
Phase 1: Source Classifier Agent (AI)
          │  Classification Validator (DET)
          │
          ▼
Phase 2: Memo Context Builder (DET)
          │  Synthesizer Agent (AI) — bull/bear cases
          │
          ▼
Phase 3: Position Agent (AI)
          │  Self-Reviewer (AI) — adversarial check
          │  Position Rules Engine (DET) — hard caps
          │
          ▼
Phase 4: Publish Node (DET) → data/markets/<id>/memo.json
          │
          ▼
      Audit Trail (immutable, sha256 prompt hashes)
```

**Skills registry** — every AI prompt is versioned in YAML (`skills/`) with a sha256 audit hash. Deterministic nodes are clearly marked `# DETERMINISTIC`.

---

## Quickstart

```bash
git clone <repo>
cd umia-analyst-agent

pip install -r requirements.txt

# Demo mode — no API keys needed
UMIA_ENV=demo streamlit run app.py

# Run pipeline on a single market (CLI)
UMIA_ENV=demo python -m agent.run --market metadao_001

# Backtest all 3 demo markets
UMIA_ENV=demo python -m agent.run --all-backtest

# Show track record
python -m agent.run --track-record
```

---

## Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `UMIA_ENV` | `demo` | `demo` = mock signals; `production` = live APIs |
| `LLM_PROVIDER` | `anthropic` | `anthropic` or `openai` |
| `ANTHROPIC_API_KEY` | — | Claude API key |
| `APIFY_TOKEN` | — | Telegram + Twitter scraping (production only) |
| `GITHUB_TOKEN` | — | GitHub REST API (production only) |
| `ETHERSCAN_API_KEY` | — | On-chain wallet activity (production only) |
| `HF_TOKEN` | — | HuggingFace Inference API token (Read, Inference Providers only) |

---

## Signal sources & models

| Signal | Source | Model / API | Weight class |
|--------|--------|-------------|--------------|
| Telegram posts | Apify telegram-scraper | ElKulako/cryptobert | manipulable 0.3 |
| Financial tweets | Apify / Grok X Search | StephanAkkerman/FinTwitBERT-sentiment | manipulable 0.3 |
| News snippets | Apify google-search-scraper | ProsusAI/finbert | partial 0.6 |
| Twitter fallback | cardiffnlp/twitter-roberta | Used if Grok API unavailable | manipulable 0.3 |
| GitHub commits | GitHub REST API | Deterministic | verifiable 1.0 |
| On-chain flows | Etherscan API | Deterministic | verifiable 1.0 |
| Market TWAP | Contract read (web3.py) | Deterministic | verifiable 1.0 |

All HuggingFace models are called via **Inference API** — no local downloads, no GPU required.
Setup: `HF_TOKEN=hf_xxx` in `.env` (Read token, Inference Providers permission only).
Demo mode (`UMIA_ENV=demo`) uses deterministic mock scores — no API keys needed.

---

## Demo markets

Three backtested MetaDAO governance proposals:

| Market ID | Title | Resolution |
|-----------|-------|------------|
| `metadao_001` | SOL/USDC Perpetuals Integration | YES (strong GitHub + on-chain) |
| `metadao_002` | Double Developer Grant Pool | NO (weak activity, skeptical Twitter) |
| `metadao_003` | Jito LST Treasury Staking | OPEN |

---

## Source classification

| Class | Max weight | Examples |
|-------|-----------|---------|
| `verifiable` | 1.0 | GitHub commits, on-chain txns, smart contract state |
| `partial` | 0.6 | Forum posts with linked evidence, timestamped docs |
| `manipulable` | 0.3 | Telegram, Twitter, founder announcements |

The position rules engine enforces hard caps — no single manipulable source can drive a position.

---

## Position sizing

| Confidence | Max size |
|-----------|---------|
| ≥ 0.85 | 7.0% treasury |
| ≥ 0.70 | 5.0% treasury |
| ≥ 0.60 | 3.0% treasury |
| < 0.60 | ABSTAIN |

---

## PnL model

Binary market resolution:

- **WIN (YES, resolves YES):** `((1 - p) / p) × size_pct`
- **WIN (NO, resolves NO):** `((1 - p) / p) × size_pct` (using NO price)
- **LOSS:** `-size_pct`
- **ABSTAIN:** `0`

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Agent pipeline | LangGraph (multi-step, conditional routing) |
| LLM | Claude Opus 4.7 (Anthropic) |
| Signal ingestion | Apify (Telegram, Twitter) · GitHub REST API · Etherscan |
| Sentiment models | HuggingFace Inference API (ElKulako/cryptobert · FinTwitBERT-sentiment · ProsusAI/finbert · cardiffnlp/twitter-roberta) |
| Skills | YAML-versioned prompts with sha256 audit hashes |
| Audit trail | Append-only, immutable, prompt-hashed |
| UI | Streamlit |
| Storage | JSON files (demo) → on-chain (production) |

---

## File structure

```
app.py                          ← Streamlit entry point (7-page nav)
agent/run.py                    ← CLI: --market, --all-backtest, --track-record

pipeline/
  state.py                      ← AgentState, ProcessStatus
  graph.py                      ← LangGraph StateGraph + run_pipeline()
  routing.py                    ← Conditional edges (deterministic)
  nodes/
    phase1_extraction.py        ← AI: SourceClassifierAgent + DET: ClassificationValidator
    phase2_analysis.py          ← DET: MemoContextBuilder + AI: Synthesizer
    phase3_maker_checker.py     ← AI: PositionAgent + SelfReviewer + DET: PositionRulesEngine
    phase4_human_audit.py       ← DET: PublishNode

early_warning/
  graph.py                      ← Live Watch LangGraph pipeline + run_live_watch()
  nodes/                        ← Load → Score → Detect → Generate → Dispatch

skills/
  classifier_skill.yaml         ← Source credibility classification v1.0
  synthesizer_skill.yaml        ← Bull/bear synthesis v1.0
  position_skill.yaml           ← YES/NO/ABSTAIN positioning v1.0
  reviewer_skill.yaml           ← Adversarial self-review v1.0

utils/
  source_rules.py               ← Weight caps, position sizing limits
  pnl.py                        ← compute_pnl(), aggregate_track_record()
  mock_markets.py               ← 3 demo MetaDAO markets + MARKET_CONFIGS
  ingest/                       ← Apify, GitHub, Etherscan, gather_signals()
  audit.py                      ← Append-only audit trail
  llm_factory.py                ← Model-agnostic LLM client

data/markets/
  metadao_001/raw_mock.json     ← Demo signals
  metadao_002/raw_mock.json
  metadao_003/raw_mock.json
  */memo.json                   ← Generated after pipeline run

ui/
  page_landing.py               ← Hero + explainer + track record preview
  page_memo_archive.py          ← All memos with PnL
  page_memo_detail.py           ← Pipeline runner + 4-tab memo view
  page_live_watch.py            ← Open market signal monitoring
  page_track_record.py          ← Aggregated PnL + running chart
  page_settings.py              ← Skills Library + Environment Config
  page_audit_trail.py           ← Immutable pipeline audit log
```

---

## Why this is a venture

The agent builds a **public, on-chain track record**. That track record is an asset.

**Token mechanics (v1):**
- Investors mint `$UMIA-ANALYST` tokens proportional to capital contribution
- The agent's trading book is the underlying asset
- Token holders share in realized PnL from confirmed market resolutions
- New memos are published on-chain — full transparency, no black box

---

*Built for Umia Protocol Hackathon 2026 · Team 7*
