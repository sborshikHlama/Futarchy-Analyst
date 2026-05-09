# Umia Analyst Agent

**The first autonomous research analyst for futarchic decision markets.**  
It reads the signals. It takes positions. It tracks its own PnL.

Built for the **Umia Protocol Hackathon 2026** · "Best Agentic Venture" bounty.

---

## What it does

Umia Analyst Agent monitors decision markets (MetaDAO, Polymarket, Umia) and:

1. **Ingests** signals from Telegram (Apify X402), News (Google Search), GitHub commit activity, and on-chain wallet flows
2. **Classifies** each source as `verifiable / partial / manipulable` with weight caps
3. **Synthesizes** a bull case and bear case, flagging manipulation attempts
4. **Takes a position** — YES / NO / ABSTAIN — scaled by confidence (max 7% treasury)
5. **Publishes a trading memo** with full audit trail and prompt hashes
6. **Tracks realized PnL** as markets resolve

---

## Architecture

```
Signal Ingestion
  ├── Apify X402  → Telegram posts   (manipulable 0.3)
  ├── Apify X402  → News snippets    (partial 0.6)
  ├── GitHub REST → Commit cadence   (verifiable 1.0)
  └── Etherscan   → On-chain flows   (verifiable 1.0)
          │
          ▼  gather_signals() → raw_signals{}
Phase 1: HuggingFace Sentiment (cryptobert / finbert) — pre-compute scores
          │  Source Classifier Agent (AI) — classifies + weights each source
          │  Classification Validator (DET) — enforces weight caps
          │
          ▼
Phase 2: Memo Context Builder (DET)
          │  Synthesizer Agent (AI) — bull/bear cases with citations
          │
          ▼
Phase 3: Position Agent (AI) — YES / NO / ABSTAIN
          │  Self-Reviewer (AI) — adversarial check
          │  Position Rules Engine (DET) — confidence + size hard caps
          │
          ▼
Phase 4: Publish Node (DET) → data/markets/<id>/memo.json
          │
          ▼
      Audit Trail (immutable · sha256 prompt hashes · X402 payment log)
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
| `APIFY_TOKEN` | — | Telegram scraping — X402 (mcpc) → token fallback (production only) |
| `GROK_API_KEY` | — | xAI Grok X Search for Twitter signals (production only) |
| `GITHUB_TOKEN` | — | GitHub REST API (production only) |
| `ETHERSCAN_API_KEY` | — | On-chain wallet activity (production only) |
| `HF_TOKEN` | — | HuggingFace Inference API token (Read, Inference Providers only) |

---

## Apify integration

### What Apify does in this project

Apify runs cloud-hosted scrapers ("Actors") so we never manage browser infrastructure ourselves. We use two Actors:

| Actor | What it scrapes | Source class | Weight |
|-------|----------------|--------------|--------|
| `apify/telegram-scraper` | Channel posts (last 7 days) | manipulable | 0.3 |
| `apify/google-search-scraper` | News snippets for a query | partial | 0.6 |

Twitter/X was previously scraped via Apify (`apidojo~tweet-scraper`) but has been replaced by **Grok X Search** — see Task 1 below.

---

### X402 payment flow

X402 is an HTTP micropayment protocol. Instead of a monthly API subscription, each Actor run is paid per-call in USDC on Base mainnet. The flow:

```
1. POST /v2/acts/{actor}/run-sync-get-dataset-items
   + header: X-APIFY-PAYMENT-PROTOCOL: X402

2. Apify responds 402 Payment Required
   + header: PAYMENT-REQUIRED: <payment instruction>

3. mcpc CLI signs the payment:
   $ mcpc x402 sign "<PAYMENT-REQUIRED value>"
   → returns PAYMENT-SIGNATURE

4. Resend original POST
   + header: PAYMENT-SIGNATURE: <signature>

5. Apify runs Actor, returns JSON dataset items
   Payment settles on Base (USDC, ~$0.001 per run)
```

Every payment is logged to `data/x402_payments.jsonl` (append-only, immutable).

---

### Payment fallback order

```
UMIA_ENV=demo        →  mock data, zero network calls (default)
mcpc on PATH         →  X402 USDC payment on Base
mcpc missing         →  APIFY_TOKEN bearer auth (classic Apify account)
neither available    →  empty result, logs error
```

This means **demo always works** without any keys or CLI tools installed.

---

### Setup for production

**Option A — X402 (hackathon track, preferred)**

```bash
# 1. Install mcpc CLI
npm install -g @mcpc/cli        # or: brew install mcpc

# 2. Create + fund a wallet
mcpc wallet create
mcpc wallet fund --chain base --amount 5   # 5 USDC ≈ ~5000 Actor runs

# 3. Verify
mcpc x402 info                 # should show wallet address + balance

# 4. Set env
UMIA_ENV=production            # in .env
# APIFY_TOKEN= leave empty (X402 doesn't need it)
```

**Option B — Classic APIFY_TOKEN (fallback)**

```bash
# 1. Sign up at https://apify.com → free tier available
# 2. Settings → Integrations → API token
# 3. Set in .env:
APIFY_TOKEN=apify_api_xxxx
UMIA_ENV=production
```

---

### What is connected right now

| Component | Status | Notes |
|-----------|--------|-------|
| `utils/ingest/apify.py` | ✅ Done | X402 core: `scrape_telegram()` + `scrape_news()` |
| `utils/ingest/__init__.py` `gather_signals()` | ✅ Done | Routes Telegram + News through `apify.py`, X402 payments logged |
| Phase 1 extraction | ✅ Done | Calls `scrape_telegram` + `scrape_news` before sentiment + Claude |
| X402 audit log | ✅ Done | `data/x402_payments.jsonl` — append-only JSONL |
| `utils/ingest/apify_telegram.py` | ⚠️ Legacy | Kept as reference; no longer called by the pipeline |
| Twitter / `apify_twitter.py` | ❌ Deprecated | Replaced by Grok X Search — not yet implemented |

**One thing remaining:** Grok X Search (Twitter signals). Until implemented, `twitter_queries` in `MARKET_CONFIGS` are defined but skipped at runtime — no Twitter data is passed to Claude. All other Apify sources are fully wired.

---

### Checking payments

```bash
# See all X402 payment events
cat data/x402_payments.jsonl | python -m json.tool

# Filter to paid-only runs
python -c "
import json
for line in open('data/x402_payments.jsonl'):
    e = json.loads(line)
    if e['paid']:
        print(e['timestamp'], e['actor'], e['items_received'], 'items')
"
```

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
| Signal ingestion | Apify (Telegram) · Grok X Search (Twitter) · GitHub REST API · Etherscan |
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
