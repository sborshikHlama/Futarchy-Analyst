# Umia Analyst Agent · CLAUDE.md
## Developer Context for Claude Code

---

## Project

**Umia Analyst Agent** is an autonomous research analyst for futarchic decision markets.
LangGraph + Claude/Grok/GPT-4o + Next.js + Streamlit + Apify/GitHub/Etherscan + HuggingFace.

Built for Umia Protocol Hackathon 2026 — "Best Agentic Venture" bounty.

---

## Current project stage (as of 2026-05-10)

### What is fully working
- **Python pipeline** — all 4 phases run end-to-end in demo mode (`UMIA_ENV=demo`)
- **3 demo markets** — `metadao_p3`, `metadao_p6`, `metadao_p7` (real MetaDAO historical proposals)
- **Next.js web frontend** (`web/`) — Home, Memos, Memo Detail, Live Watch, Track Record, Pricing pages
- **UI overhaul** — dark Bloomberg-style theme, Mochifi logo with blinking mascot eyes, mobile-responsive with burger menu, framer-motion animations, footer with social links
- **Sentiment analysis** — HuggingFace Inference API wired into Phase 1; demo mode returns deterministic mock scores
- **Source links** — every source in the weights table links to its origin (GitHub, Telegram, on-chain explorer, Twitter/X)
- **PnL tracking** — two resolved memos (+3.33%, +3.00%); one open (`metadao_p7`)
- **Multi-provider LLM** — `anthropic` (Claude Opus 4.6), `openai` (GPT-4o), `grok` (Grok-3) via `utils/llm_factory.py`
- **Immutable audit trail** — sha256-hashed prompts, append-only events in every node
- **Auth infrastructure** — NextAuth v4 + Prisma (SQLite) + Google OAuth wired end-to-end; Twitter/X OAuth configured; MetaMask SIWE backend ready
- **Stripe infrastructure** — checkout, portal, webhook API routes implemented; pricing page with Free/Pro toggle built

### Known gaps / not yet wired
- **Production ingest** — `UMIA_ENV=production` code paths exist but are untested end-to-end; Apify, GitHub, Etherscan calls need live keys
- **More than 3 markets** — adding a market requires a new entry in `MARKET_CONFIGS` + `_signals_for()` branch in `mock_markets.py`; the web frontend picks up any `data/markets/*/memo.json` automatically
- **Streamlit UI** — `app.py` is functional but `web/` is the primary user-facing frontend; Streamlit is secondary/admin
- **On-chain publishing** — memos are JSON on disk; on-chain anchoring is roadmap only
- **`$UMIA-ANALYST` token mechanics** — described in README, not implemented

### ⚠️ Auth & Stripe — what the developer still needs to do manually

#### Google OAuth (15 min)
1. Go to [console.cloud.google.com](https://console.cloud.google.com) → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Authorized JavaScript origins: `http://localhost:3000`
4. Authorized redirect URIs: `http://localhost:3000/api/auth/callback/google`
5. Copy Client ID + Secret → `web/.env.local`: `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
6. Generate `NEXTAUTH_SECRET`: run `openssl rand -base64 32` in terminal

#### Twitter / X OAuth (20 min)
1. Go to [developer.twitter.com](https://developer.twitter.com) → Projects → Create App
2. App Settings → Authentication Settings → OAuth 2.0 → ON
3. Type: Web App; Callback URL: `http://localhost:3000/api/auth/callback/twitter`
4. Copy Client ID + Secret → `web/.env.local`: `TWITTER_CLIENT_ID` / `TWITTER_CLIENT_SECRET`

#### MetaMask (0 setup — works immediately once app runs)
- Install MetaMask browser extension
- Click "Connect MetaMask" on `/auth/signin` — signs SIWE message, creates wallet-linked user in DB
- Test on Ethereum Sepolia testnet (signing is free, no real ETH needed)

#### Stripe (30 min)
1. Go to [dashboard.stripe.com](https://dashboard.stripe.com) → Products → Add Product
2. Name: "Mochifi Pro" → Add two prices:
   - Monthly: $9.00 / month → copy Price ID → `STRIPE_PRICE_MONTHLY=price_...`
   - Yearly: $79.00 / year → copy Price ID → `STRIPE_PRICE_YEARLY=price_...`
3. Copy Secret Key → `STRIPE_SECRET_KEY=sk_test_...`
4. For local webhook testing, install [Stripe CLI](https://stripe.com/docs/stripe-cli) then run:
   ```bash
   stripe listen --forward-to localhost:3000/api/stripe/webhook
   ```
   Copy the `whsec_...` secret → `STRIPE_WEBHOOK_SECRET`
5. Enable Customer Portal in Stripe Dashboard → Settings → Billing → Customer Portal

#### Final `.env.local` template
```
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<openssl rand -base64 32>

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=

DATABASE_URL=file:./dev.db

STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_MONTHLY=price_...
STRIPE_PRICE_YEARLY=price_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Demo data state
| Market ID | Position | Confidence | Outcome | PnL |
|-----------|----------|------------|---------|-----|
| `metadao_p3` | YES @ 5.0% | 0.74 | YES ✓ | +3.33% |
| `metadao_p6` | NO @ 3.0% | 0.60 | NO ✓ | +3.00% |
| `metadao_p7` | NO @ 3.0% | 0.60 | OPEN | — |

All three memos have: sentiment scores, source URLs, manipulation flags, self-review, full audit trail.

---

## File architecture

```
app.py                              ← Streamlit entry point (7-page nav, secondary UI)
agent/
  run.py                            ← CLI: --market, --all-backtest, --track-record

pipeline/
  state.py                          ← AgentState, ProcessStatus (TypedDict)
  graph.py                          ← LangGraph StateGraph (build_graph, run_pipeline)
  routing.py                        ← Conditional edges (DETERMINISTIC)
  nodes/
    phase1_extraction.py            ← AI: SourceClassifierAgent + DET: ClassificationValidator
                                       + HF sentiment via analyze_batch() before classifier
    phase2_analysis.py              ← DET: MemoContextBuilder + AI: Synthesizer
    phase3_maker_checker.py         ← AI: PositionAgent + SelfReviewer
                                       DET: PositionRulesEngine (hard caps)
    phase4_human_audit.py           ← DET: PublishNode + RecordPublishDecision
                                       Persists sentiment + preserves resolved outcome on re-run

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
  sentiment.py                      ← analyze_batch(texts, source_type) → HF Inference API
                                       Demo mode returns deterministic mock scores (no token needed)
                                       Models: cryptobert / FinTwitBERT / finbert / twitter-roberta
  ingest/
    __init__.py                     ← gather_signals(market_id, mock)
    apify_telegram.py               ← fetch_telegram(channel, days, mock)
                                       Payment waterfall: X402 (mcpc) → APIFY_TOKEN → mock
    apify_twitter.py                ← fetch_tweets(query, days, max_items, mock)
    github_activity.py              ← fetch_github_activity(repo, weeks, mock)
    onchain.py                      ← fetch_wallet_activity(addresses, days, mock)
  audit.py                          ← _audit(state, node, action, result, prompt, ...)
                                       → immutable append-only, sha256[:12] for AI nodes
  llm_factory.py                    ← get_llm() → LLMClient(provider, model)
                                       Providers: anthropic | openai | grok
  chunking.py                       ← semantic_chunk()

web/                                ← Next.js 14 frontend (PRIMARY user-facing UI)
  app/
    page.tsx                        ← Home / hero
    memos/page.tsx                  ← Memo archive with track record strip
    memos/[id]/page.tsx             ← Memo detail (server component, reads memo.json)
    memos/[id]/MemoDetailClient.tsx ← Client component: all memo sections
    live/page.tsx                   ← Live Watch
    track/page.tsx                  ← Track Record
  components/memo/
    MemoHeader.tsx                  ← Title, proposal, venue/dates
    VerdictBar.tsx                  ← POSITION / CONFIDENCE / SIZE / STATUS (LIVE or RESOLVED+PnL)
    ExecutiveSummary.tsx
    ManipulationFlags.tsx
    BullBearGrid.tsx                ← Citation buttons scroll to SourceWeightsTable
    SourceWeightsTable.tsx          ← Sortable, expandable, source link icons (↗)
    SentimentAnalysis.tsx           ← HF sentiment scores by source
    SelfReview.tsx
    PositionRationale.tsx
    Provenance.tsx
  lib/
    memos.ts                        ← getAllMemos(), getMemo(), getTrackRecord() — reads disk
    types.ts                        ← Memo, SourceWeight (+ url?), Sentiment, SentimentResult, etc.

ui/                                 ← Streamlit UI (secondary, admin/debug use)
  styles.py / page_*.py

data/markets/
  metadao_p3/                       ← raw_mock.json + memo.json
  metadao_p6/                       ← raw_mock.json + memo.json
  metadao_p7/                       ← raw_mock.json + memo.json
```

---

## Memo JSON schema (current)

Every `data/markets/*/memo.json` contains:

```json
{
  "market_id": "metadao_p6",
  "generated_at": "...",
  "published_at": "...",
  "market_metadata": { "title", "proposal", "venue", "opens_at", "closes_at", "resolved_outcome" },
  "source_weights": {
    "<source_id>": { "class_": "verifiable|partial|manipulable", "weight": 0.0-1.0, "reasoning": "...", "url": "..." }
  },
  "bull_case": "... [CITATION:source_id] ...",
  "bear_case": "... [CITATION:source_id] ...",
  "manipulation_flags": ["..."],
  "confidence": 0.0-1.0,
  "position": { "side": "YES|NO|ABSTAIN", "size_pct": 0.0-7.0, "rationale": "..." },
  "self_review": { "weaknesses": [...], "counter_arguments": [...] },
  "sentiment": {
    "telegram": { "score": -1.0–1.0, "label": "bullish|neutral|bearish", "confidence": 0-1, "sample_size": n, "model": "..." },
    "news":     { ... }
  },
  "outcome": { "resolved_side": "YES|NO", "pnl_pct": float } | null,
  "audit_events": n
}
```

**Critical invariant**: `publish_node` preserves an existing `outcome` from disk on re-run — a new pipeline run must not wipe a resolved outcome.

---

## Invariant rules (NEVER break)

### 1. Deterministic vs. AI split
- `# DETERMINISTIC` — pure Python, no LLM
- `# AI` — calls Claude/GPT/Grok via `utils/llm_factory.py`
- **LLM NEVER does math** — all scoring via `utils/source_rules.py`
- Every AI node reads its prompt from the skills registry (versioned YAML)

### 2. Audit Trail
- `_audit()` from `utils/audit.py` must be called in every node
- Audit trail is **append-only** — never mutate existing events
- AI nodes: `prompt=skill["prompt"]` → auto-hashed sha256[:12]
- DET nodes: `prompt=None` → `prompt_hash=None` in log

### 3. API Failure → Process Freeze
- On LLM API failure: `status = ProcessStatus.FROZEN`
- **NEVER** fallback silently to stale data
- Max retries: `API_RETRY_COUNT = 3`, delay: `API_RETRY_DELAY_SEC = 30`

### 4. Position iteration cap
- Max iterations: `MAX_POSITION_ITERATIONS = 3` (guard in `source_rules.py`)
- On exceeded: `status = ProcessStatus.ESCALATED`
- Self-reviewer checks only citations and hallucinations — not math

### 5. Source weight caps
```python
SOURCE_CLASS_MAX_WEIGHT = {
    "verifiable":  1.0,   # GitHub commits, on-chain txns
    "partial":     0.6,   # Forum posts with evidence
    "manipulable": 0.3,   # Telegram, Twitter
}
```

### 6. Demo / Production mode
- `UMIA_ENV=demo` → reads `data/markets/*/raw_mock.json`; no external API calls; HF sentiment returns mock scores
- `UMIA_ENV=production` → calls Apify (X402 → APIFY_TOKEN), GitHub REST, Etherscan, HF Inference API
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
Font:            Manrope (Google Fonts)
Primary color:   #5B5BD6 (ACCENT)
Hover color:     #4A4ABF (ACCENT_DARK)
Main text:       #0B0F17 (TEXT_MAIN)
Secondary text:  #4B5563 (TEXT_SEC)
Background:      #FFFFFF (BG) — Streamlit / #0A0A0A dark — Next.js
```

---

## LLM Factory

```python
from utils.llm_factory import get_llm

llm = get_llm()   # reads LLM_PROVIDER + LLM_MODEL from env
resp = llm.complete(system=skill["prompt"], user_message=context_json, max_tokens=2048)
text   = resp.text
tokens = resp.tokens_used
```

Default models: `anthropic` → `claude-opus-4-6` · `openai` → `gpt-4o` · `grok` → `grok-3`

---

## Telegram ingest

Payment waterfall in `utils/ingest/apify_telegram.py`:
1. **X402** — `mcpc x402 sign` (pay-per-use micropayment, no token needed)
2. **APIFY_TOKEN** — classic bearer auth fallback
3. **Mock** — if neither available or `UMIA_ENV=demo`

Actor: `apify~telegram-scraper` · Returns `[{text, date, views, forwards}]`

---

## Source rules
```python
MAX_POSITION_SIZE_PCT   = 7.0
MIN_CONFIDENCE_TO_BET   = 0.6
MIN_CITATION_COVERAGE   = 0.85
MAX_POSITION_ITERATIONS = 3
API_RETRY_COUNT         = 3
API_RETRY_DELAY_SEC     = 30
```

---

## Run

```bash
# Next.js web UI (primary)
cd web && npm install && npm run dev   # → http://localhost:3000

# Streamlit UI (secondary)
UMIA_ENV=demo streamlit run app.py

# CLI single market
UMIA_ENV=demo python -m agent.run --market metadao_p6

# CLI backtest all 3 markets
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
| 2026-05-09 | Add Grok (xAI) provider to LLM factory | Complete |
| 2026-05-09 | Next.js web frontend (`web/`) — full memo detail UI | Complete |
| 2026-05-09 | Replace generic demo markets with real MetaDAO proposals (p3/p6/p7) | Complete |
| 2026-05-09 | HuggingFace sentiment analysis wired into Phase 1 + web UI | Complete |
| 2026-05-09 | Source links in SourceWeightsTable (GitHub/Telegram/Twitter/on-chain) | Complete |
| 2026-05-09 | Fix: publish_node preserved resolved outcome across re-runs | Complete |
| 2026-05-10 | UI overhaul — Mochifi logo, blinking mascot eyes, dark Bloomberg theme | Complete |
| 2026-05-10 | Mobile responsive — burger menu, hero layout, memo cards, 2×2 stats grid | Complete |
| 2026-05-10 | Animations — typing headline, framer-motion fade-in, count-up stats, dot grid | Complete |
| 2026-05-10 | Footer — 3-col with nav + social links (X, GitHub, Telegram) | Complete |
| 2026-05-10 | Auth — NextAuth v4 + Prisma SQLite + Google + Twitter/X + MetaMask SIWE | Complete (needs env keys) |
| 2026-05-10 | Stripe — checkout + portal + webhook API routes + pricing page | Complete (needs Stripe keys) |
