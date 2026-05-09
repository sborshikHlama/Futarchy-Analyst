# Umia Analyst Agent — User Manual

**Version:** 0.1  
**Last updated:** 2026-05-09

---

## Table of Contents

1. [Overview](#1-overview)
2. [Getting Started](#2-getting-started)
3. [Navigation](#3-navigation)
4. [Home Page](#4-home-page)
5. [Memo Archive](#5-memo-archive)
6. [Memo Detail](#6-memo-detail)
7. [Live Watch](#7-live-watch)
8. [Track Record](#8-track-record)
9. [Settings](#9-settings)
10. [Audit Trail](#10-audit-trail)
11. [CLI Reference](#11-cli-reference)
12. [Understanding the Agent's Decisions](#12-understanding-the-agents-decisions)
13. [Demo vs. Production Mode](#13-demo-vs-production-mode)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Overview

Umia Analyst Agent is an autonomous research analyst for futarchic decision markets. It monitors open governance proposals on platforms like MetaDAO, Polymarket, and Umia Protocol, ingests signals from multiple data sources, and publishes structured trading memos with explicit YES / NO / ABSTAIN positions.

**What the agent does:**

1. **Ingests signals** from Telegram channels, Twitter, GitHub commit history, and on-chain wallet activity
2. **Classifies each source** as `verifiable`, `partial`, or `manipulable` — with mathematically enforced weight caps
3. **Synthesizes a bull case and a bear case**, citing only classified sources
4. **Takes a position** (YES / NO / ABSTAIN) scaled by confidence — maximum 7% of treasury per bet
5. **Publishes a memo** with an immutable audit trail linking every AI decision to a versioned prompt hash
6. **Tracks realized PnL** as markets resolve

**What the agent does not do:**

- It does not take positions with confidence below 60% — it abstains instead
- It does not let manipulable sources (Telegram, Twitter) outweigh verifiable ones (GitHub, on-chain)
- It does not silently fall back to stale data if an API fails — the pipeline freezes
- It does not perform math with the LLM — all scoring is deterministic Python

---

## 2. Getting Started

### Requirements

- Python 3.11+
- Internet connection (demo mode: none required)

### Installation

```bash
git clone <repo-url>
cd umia-analyst-agent

pip install -r requirements.txt

cp .env.example .env
# Edit .env if needed — defaults work for demo mode
```

### Start the app

```bash
UMIA_ENV=demo streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

### First run

In demo mode, the app loads three pre-generated memos for MetaDAO backtests. No API keys are required. All signal data is read from `data/markets/*/raw_mock.json`.

---

## 3. Navigation

The sidebar on the left contains all navigation controls.

| Page | Icon | Purpose |
|------|------|---------|
| Home | 🏠 | Overview, how it works, track record summary |
| Memo Archive | 📚 | Browse all generated memos |
| Memo Detail | 📄 | Run the pipeline or view a specific memo |
| Live Watch | 👁️ | Scan open markets for signal changes |
| Track Record | 📈 | Aggregated PnL and performance history |
| Settings | ⚙️ | Skills library and environment config |
| Audit Trail | 🔍 | Immutable pipeline event log |

The **active market** is shown below the navigation buttons when one has been selected. Clicking **View** or **Generate Memo** on any page sets the active market.

The bottom of the sidebar shows the current mode (`DEMO` or `PRODUCTION`).

---

## 4. Home Page

The landing page gives judges and investors a complete picture of the product in one scroll.

### Sections

**Hero** — product name, one-line pitch, three quick-action buttons.

**The Problem** — explains why decision markets are dominated by insiders: most signal is adversarial (Telegram, Twitter) and most traders can't process verifiable signals (GitHub, on-chain) at prediction-market speed.

**How It Works** — four-step visual: Ingest → Classify → Synthesize → Position.

**Track Record (Backtested)** — live aggregated numbers pulled from generated memos:
- Memos Generated
- Win Rate
- Total PnL
- Recent memos list (last 3)

**Why This Is a Venture** — token mechanics explanation: `$UMIA-ANALYST` tokens, on-chain track record as asset, crowdfunded trading book.

**Roadmap** — four phases from current demo through multi-chain governance monitoring.

**Tech Stack** — table of technology choices.

### Quick actions

| Button | Navigates to |
|--------|-------------|
| View Memo Archive | Memo Archive page |
| Live Watch | Live Watch page |
| Track Record | Track Record page |

---

## 5. Memo Archive

Browse every memo the agent has generated, with position and PnL for each.

### KPI row

At the top: Total Memos, Resolved markets, Win Rate, Total PnL.

### Filtering

Use the **Filter by position** radio buttons to show only YES, NO, or ABSTAIN memos. Default is "All".

### Memo list

Each row shows:

| Column | Description |
|--------|-------------|
| Title + venue | Market name and platform |
| Position | Side and size — e.g. `YES @ 5.0%` |
| Confidence | Agent's stated confidence at memo time |
| PnL | Realized PnL if resolved; "Open" otherwise |
| View button | Opens the memo on the Memo Detail page |

### Empty state

If no memos exist yet, the page offers a **Run Demo Pipeline** button that navigates to Memo Detail.

---

## 6. Memo Detail

The core page. Select a market, run the pipeline, and read the full four-tab memo.

### Market selector

The dropdown lists all configured markets. If you navigated here by clicking **View** or **Generate Memo** from another page, the correct market is pre-selected.

### Generating a memo

Click **Generate Memo**. The pipeline runs in four visible phases:

```
Phase 1: Classifying signal sources...
Phase 2: Synthesizing bull/bear cases...
Phase 3: Taking position + self-review...
Phase 4: Publishing memo...
```

A green status bar appears when the pipeline completes. The result shows the position, size, and confidence inline.

If the pipeline fails, a red error bar appears with the reason. Common causes: missing API key in production mode, or the market's `raw_mock.json` file is missing in demo mode.

### Memo header

After generation or when loading an existing memo, the header shows:

- Market title and proposal text
- **Position** — YES / NO / ABSTAIN in color (green / red / grey)
- Size as % of treasury
- Confidence
- PnL (if resolved)

### Tab 1 — Memo

The full written analysis:

**Bull Case** — arguments for YES, with inline citations like `[CITATION:github_metadao]`. Each citation refers to a classified source.

**Bear Case** — arguments for NO, with citations.

**Position Rationale** — one paragraph explaining why the agent chose its side and size given the bull/bear cases.

**Manipulation Flags** *(if any)* — warnings about sources the agent identified as potentially coordinated or unreliable. Shown as amber warning boxes.

**Outcome** *(if resolved)* — the market's final resolution and the agent's PnL.

### Tab 2 — Sources

Each ingested source with its classification and weight:

| Field | Description |
|-------|-------------|
| Source ID | Internal identifier (e.g. `github_metadao`) |
| Class | `verifiable` / `partial` / `manipulable` |
| Weight | 0.0–1.0, capped by class |
| Reasoning | Why the classifier assigned this weight |

**Weight caps by class:**

| Class | Max weight | Typical sources |
|-------|-----------|----------------|
| verifiable | 1.0 | GitHub commits, on-chain transactions |
| partial | 0.6 | Forum posts with linked evidence |
| manipulable | 0.3 | Telegram, Twitter, founder announcements |

A manipulable source at weight 0.3 provides less than one-third the influence of a strong verifiable source at 1.0.

### Tab 3 — Self-Review

The agent's adversarial check of its own position:

**Weaknesses** — ways the bull case could be wrong, identified by the self-reviewer.

**Counter-arguments** — specific scenarios where the position would lose, even if the analysis is otherwise correct.

The self-reviewer can reduce the agent's stated confidence. If confidence drops below 0.60, the position agent retries (up to 3 iterations). If it cannot reach confidence ≥ 0.60 after 3 iterations, the pipeline escalates and the memo is not published.

### Tab 4 — Audit Trail

Shows how many pipeline events were logged and when the memo was generated and published. The full event-level audit trail is on the dedicated Audit Trail page.

---

## 7. Live Watch

Scans all open (unresolved) markets for signal changes and surface high-signal alerts.

### Running a scan

Click **Run Watch Scan**. The scanner runs the Live Watch pipeline:

1. Loads all open markets from `data/markets/`
2. Scores each market's signal diversity (GitHub, on-chain, social coverage)
3. Detects anomalies (low-data markets, approaching close times)
4. Generates alerts by signal level

The scan result is cached in the session. Clicking **Run Watch Scan** again refreshes it.

### KPI row

| Metric | Description |
|--------|-------------|
| Open Markets | Total markets with no resolved outcome |
| High Signal | Markets with strong multi-source coverage |
| Medium Signal | Markets with partial coverage |
| Low Signal | Markets with thin signal — abstain likely |

### Signal Alerts

Alerts are shown with a colored left border:

- **Red border** — HIGH signal: strong evidence, approaching close, immediate review recommended
- **Amber border** — MEDIUM signal: mixed evidence, monitor
- **Green border** — LOW signal: thin coverage, abstain likely

Each alert shows a title, description, and recommended action.

### Open Markets list

Each open market is shown as an expandable card:

- Signal level badge
- Source count, hours to close (if within 48h)
- Coverage indicators: GitHub ✅/❌, On-chain ✅/❌, Social ✅/❌
- **Generate Memo** button — runs the full pipeline and navigates to Memo Detail

---

## 8. Track Record

Aggregated historical performance across all generated memos.

### KPI row

| Metric | Description |
|--------|-------------|
| Total Memos | All memos ever generated |
| Resolved | Markets that have settled |
| Win Rate | % of resolved bets that were correct |
| Total PnL | Sum of realized PnL across all resolved memos |
| W / L / A | Win count / Loss count / Abstain count |

### Running PnL chart

A line chart showing cumulative PnL as each market resolved. X-axis is market title (in order of resolution), Y-axis is running PnL in percentage points.

### Memo table

Each row: market title, venue, publication date, position, confidence, PnL, resolved side, and a **View** button.

---

## 9. Settings

### Tab 1 — Skills Library

Lists all registered skill YAML files. Each skill is shown with:

- Name and version
- Node type: `AI` (calls the LLM) or `DETERMINISTIC` (pure Python)
- Author and approval metadata
- Prompt hash — a sha256[:12] fingerprint of the exact prompt text

Expand any skill to see its constraints. These are hard rules built into the prompt that the agent is expected to follow.

**Built-in skills:**

| Skill key | Role |
|-----------|------|
| `classifier_skill` | Classifies signal sources by credibility |
| `synthesizer_skill` | Writes bull/bear cases with citations |
| `position_skill` | Takes YES/NO/ABSTAIN position |
| `reviewer_skill` | Adversarial self-review |

### Tab 2 — Skills Management

Register a new skill YAML for use in the pipeline.

**Required fields:**
- **File key** — unique identifier, lowercase alphanumeric + underscores only (e.g. `my_signal_extractor`)
- **Skill name** — human-readable label shown in the library
- **Version** — semantic version string (e.g. `1.0`)
- **Node type** — `AI` or `DETERMINISTIC`
- **Prompt text** — the full system prompt; will be sha256-hashed on save

**Optional fields:**
- Author, approved by, approval date
- Constraints (one per line) — rules you want logged alongside the skill
- Data sources required (one per line) — documents which signal sources the skill expects

Once saved, the skill appears immediately in Skills Library and can be called from any pipeline node via `registry.get("your_skill_key")`.

To delete a custom skill, click the 🗑️ button next to it. Built-in skills cannot be deleted from the UI.

### Tab 3 — Environment

Shows the current values of all relevant environment variables, with secrets masked to `••••`.

Also shows the `.env.example` template for quick reference.

**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `UMIA_ENV` | `demo` or `production` |
| `LLM_PROVIDER` | `anthropic` or `openai` |
| `LLM_MODEL` | Override the default model |
| `ANTHROPIC_API_KEY` | Claude API key |
| `OPENAI_API_KEY` | OpenAI key (if using OpenAI) |
| `APIFY_TOKEN` | Telegram + Twitter scraping (production only) |
| `GITHUB_TOKEN` | GitHub REST API (production only) |
| `ETHERSCAN_API_KEY` | On-chain wallet activity (production only) |

---

## 10. Audit Trail

An immutable log of every action taken by every pipeline node, for a selected market.

### Market selector

Choose a market from the dropdown. If no memo has been generated yet, the page shows a prompt to run the pipeline first.

### Summary metrics

When a memo exists:

| Metric | Description |
|--------|-------------|
| Total Events | All logged pipeline actions |
| AI Nodes | Events from LLM-calling nodes (blue border) |
| DET Nodes | Events from deterministic nodes (grey border) |
| Total Tokens | Sum of LLM tokens consumed |

### Filtering

Use the **Filter nodes** radio to view All, only AI nodes, or only DET nodes.

### Event format

Each event shows:

```
01. source_classifier_agent   [🤖 AI]              2026-04-20T09:15:40
    classify_sources → classified_4_sources
    hash:`a3f2c1d8e9b0` · v1.0 · 1,204 tokens
```

- **Number** — sequential order within the pipeline run
- **Node name** — which function generated this event
- **Badge** — 🤖 AI (called the LLM) or ⚙️ DET (pure Python)
- **Timestamp** — UTC time of the action
- **Action → Result** — what was done and the outcome
- **Hash** — sha256[:12] of the prompt used (AI nodes only)
- **Version** — skill version (AI nodes only)
- **Tokens** — LLM tokens consumed (AI nodes only)

Blue-bordered events are AI nodes. Grey-bordered events are deterministic nodes.

### Export

Expand the **Export Audit Trail** section to download the full log as:
- **JSON** — structured, machine-readable
- **TXT** — one line per event, human-readable

---

## 11. CLI Reference

The CLI is useful for batch processing and integration into automated workflows.

```bash
# Run pipeline on a single market
UMIA_ENV=demo python -m agent.run --market metadao_001

# Run pipeline on all configured markets (backtest)
UMIA_ENV=demo python -m agent.run --all-backtest

# Mark a market as resolved and attach outcome
UMIA_ENV=demo python -m agent.run --market metadao_003 --resolve YES

# Print the track record summary
python -m agent.run --track-record
```

### Options

| Flag | Argument | Description |
|------|----------|-------------|
| `--market` | market ID | Run the full pipeline for one market |
| `--all-backtest` | — | Run pipeline on every market in `MARKET_CONFIGS` |
| `--resolve` | `YES` or `NO` | Attach a resolved outcome to the last memo for the selected market |
| `--track-record` | — | Print aggregated track record to stdout |

### Example: full backtest

```bash
UMIA_ENV=demo python -m agent.run --all-backtest
python -m agent.run --track-record
```

Output:
```
========================================
UMIA ANALYST AGENT — TRACK RECORD
========================================
Memos generated: 3
Resolved:        2
Unresolved:      1
Win rate:        100.0%
Total PnL:       +4.29%
W/L/A:           2/0/0
```

---

## 12. Understanding the Agent's Decisions

### Source classification

Every ingested signal is classified before it influences the memo:

- **Verifiable** — objective, hard to fake. Examples: GitHub commit history, on-chain transaction records, smart contract state. Maximum weight: **1.0**.
- **Partial** — has some evidence but is not independently verifiable. Examples: forum posts with linked sources, timestamped screenshots. Maximum weight: **0.6**.
- **Manipulable** — controlled by a single party or easily coordinated. Examples: Telegram, Twitter, founder blog posts. Maximum weight: **0.3**.

The weight cap is a hard constraint enforced by the `ClassificationValidator` node — it runs after the AI classifier and clips any weight that exceeds the class limit. The LLM cannot override this.

### Position sizing

Confidence level determines the maximum bet size:

| Confidence range | Position size |
|-----------------|--------------|
| ≥ 0.85 | Up to 7.0% treasury |
| ≥ 0.70 | Up to 5.0% treasury |
| ≥ 0.60 | Up to 3.0% treasury |
| < 0.60 | ABSTAIN (no position) |

These limits are also enforced deterministically by the `PositionRulesEngine` node, not by the LLM.

### Retry loop

The `PositionAgent` and `SelfReviewer` form a loop:

1. Position agent proposes YES / NO / ABSTAIN with confidence
2. Self-reviewer critiques the position and adjusts confidence
3. If confidence drops below 0.60, the position agent retries with the critique in context
4. Maximum 3 iterations; if confidence never reaches 0.60, status becomes ESCALATED and no memo is published

### Manipulation flags

If the classifier detects that a source is controlled by a directly interested party (grant recipient, project founder) and is the only source supporting one side, a manipulation flag is attached to the memo. These appear as amber warnings in the Memo tab and are visible in the Track Record for transparency.

### Abstaining

ABSTAIN is not a failure — it is the correct decision when evidence is too thin or contradictory to bet with conviction. An abstained market contributes 0% to the running PnL (neither positive nor negative).

---

## 13. Demo vs. Production Mode

### Demo mode (`UMIA_ENV=demo`)

Set by default. No API keys required.

- Signal data is read from `data/markets/<market_id>/raw_mock.json`
- LLM calls still require `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) — the demo bypasses external scraping but not the AI reasoning steps
- If a `raw_mock.json` is missing, the pipeline freezes with status `FROZEN`

### Production mode (`UMIA_ENV=production`)

Activates live signal ingestion:

- **Telegram** — scraped via Apify Actor (requires `APIFY_TOKEN`)
- **Twitter** — scraped via Apify Actor (requires `APIFY_TOKEN`)
- **GitHub** — queried via GitHub REST API (requires `GITHUB_TOKEN`)
- **On-chain** — queried via Etherscan API (requires `ETHERSCAN_API_KEY`)

No other changes to the pipeline — the same LangGraph graph, same skill prompts, same audit trail.

### Switching modes

Edit `.env`:

```bash
UMIA_ENV=production
APIFY_TOKEN=apify_api_xxxxx
GITHUB_TOKEN=github_pat_xxxxx
ETHERSCAN_API_KEY=xxxxx
```

Then restart the app:

```bash
streamlit run app.py
```

---

## 14. Troubleshooting

### "No memo generated yet for this market"

The pipeline has not been run for this market. Click **Generate Memo** on the Memo Detail page.

### Pipeline status: FROZEN

The pipeline stopped because a required data source was unavailable:
- In demo mode: the `raw_mock.json` file for this market is missing. Check `data/markets/<market_id>/raw_mock.json`.
- In production mode: an API call failed after 3 retries. Check your API keys in Settings → Environment.

### Pipeline status: ESCALATED

The self-reviewer could not raise confidence above 0.60 in 3 iterations. This usually means the market has deeply contradictory signals. No memo is published; this is the correct outcome.

### "Cannot load Skills"

The `skills/` directory is missing or contains invalid YAML. Run:

```bash
python3 -c "from skills import registry; print(registry.get_all_skills())"
```

If this fails, check that `pyyaml` is installed (`pip install pyyaml`) and that the YAML files in `skills/` are syntactically valid.

### Streamlit shows blank page or import error

Check that all dependencies are installed:

```bash
pip install -r requirements.txt
```

If a specific module is missing, install it individually:

```bash
pip install langgraph anthropic streamlit pyyaml python-dotenv pandas requests
```

### Track record shows 0 memos

No memo.json files have been generated yet. Run the pipeline on at least one market:

```bash
UMIA_ENV=demo python -m agent.run --market metadao_001
```

Or click **Generate Memo** on the Memo Detail page.

### LLM calls fail with authentication error

Verify your API key is set in `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx   # for anthropic
OPENAI_API_KEY=sk-xxxxx          # for openai
```

And that `LLM_PROVIDER` matches the key you've provided.
