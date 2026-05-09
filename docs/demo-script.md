# Demo Script — Umia Analyst Agent

**Duration:** ~5 minutes  
**Mode:** `UMIA_ENV=demo` (no API keys required)

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
UMIA_ENV=demo streamlit run app.py
```

---

## Flow

### 1. Landing page (30s)

Open the app. The **Home** page loads by default.

- Point out: "The agent has already generated 3 backtested memos. Win rate and PnL are live."
- Scroll to **How It Works** — 4-step explainer: Ingest → Classify → Synthesize → Position
- Scroll to **Track Record** — show realized PnL numbers

### 2. Memo Archive (30s)

Click **Memo Archive** in the sidebar.

- Show 3 memos: one YES (win), one NO (win), one open
- Filter by "YES" — show only long positions
- Click **View** on `metadao_001`

### 3. Memo Detail — existing memo (60s)

The memo for `SOL/USDC Perpetuals` loads instantly from the cached JSON.

- **Memo tab** — point out the bull case with `[CITATION:github_metadao]` inline
- **Sources tab** — show classifier weights: GitHub = `verifiable`, Telegram = `manipulable` at 0.30
- **Self-Review tab** — the agent's own weaknesses and counter-arguments
- **Audit Trail tab** — `3 pipeline audit events`

### 4. Generate a fresh memo (90s)

Select `metadao_003` (Jito LST — OPEN market) from the dropdown.  
Click **Generate Memo**.

Watch the pipeline run live:
- Phase 1: classifying 4 signal sources
- Phase 2: synthesizing bull/bear cases
- Phase 3: taking position + self-review
- Phase 4: publishing memo

Result: **YES @ 3.0% treasury — Confidence: 0.72**

### 5. Live Watch (30s)

Click **Live Watch** in the sidebar. Click **Run Watch Scan**.

- Shows open markets with signal levels (HIGH / MEDIUM / LOW)
- One alert for `metadao_003` — medium signal, social activity increasing

### 6. Track Record (30s)

Click **Track Record**.

- Running PnL chart: +12.4% across 3 backtested markets
- 2 wins, 0 losses, 1 open
- Win rate: 100% on resolved markets

### 7. Settings → Skills Library (30s)

Click **Settings** → **Skills Library**.

- Expand `position_skill` — show version, author, prompt hash `a3f2c1d8e9b0`
- Explain: "Every AI call is reproducible — the hash proves which exact prompt was used"

---

## Key talking points

1. **The source weight caps are the moat.** Telegram gets max 0.3 — a coordinated shill campaign can't flip a position. GitHub commits and on-chain flows drive the decision.

2. **The audit trail is tamper-evident.** Every AI node logs its prompt hash. You can prove, after the fact, exactly what the model was asked and what it answered.

3. **The track record is the product.** Once live on Umia, the PnL history becomes an on-chain asset. `$UMIA-ANALYST` token holders share in realized returns.

4. **Demo to production is one env var.** `UMIA_ENV=production` activates live Apify, GitHub, and Etherscan calls. The pipeline is identical — only the data source changes.
