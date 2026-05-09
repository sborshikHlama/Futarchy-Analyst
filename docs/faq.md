# FAQ — Umia Analyst Agent

## General

**Q: What is a futarchic decision market?**  
A: A prediction market used to make governance decisions. If a proposal passes, one token pays out; if it fails, the other pays out. Voters reveal their beliefs through prices, not just votes. MetaDAO and Umia Protocol are the leading examples.

**Q: How is this different from a regular prediction market bot?**  
A: Three things: (1) it classifies *source credibility* — not all signals are equal, and it enforces that mathematically; (2) it writes a *structured memo* explaining its reasoning, with citations; (3) it maintains an *on-chain track record* — the agent's past calls are public and auditable.

---

## Technical

**Q: Why LangGraph instead of a simple prompt chain?**  
A: The pipeline has conditional branching — if the self-reviewer drops confidence below the betting threshold, the position agent retries. If the API fails, the pipeline freezes rather than silently returning stale data. LangGraph makes these state transitions explicit and auditable.

**Q: What does "prompt hash" mean?**  
A: Every AI node reads its prompt from a versioned YAML file. The sha256 hash of that prompt is logged in the audit trail. This means you can prove, after the fact, that the agent used a specific, unmodified prompt when it generated a given memo.

**Q: Why are manipulable sources capped at 0.3 weight?**  
A: Telegram and Twitter are the primary vectors for coordinated shilling in crypto governance. Even if 10 Telegram messages all say "YES," their combined maximum influence on the position is capped below what a single verifiable GitHub signal provides. This is a hard rule, not a suggestion to the LLM.

**Q: What happens if the Claude API fails?**  
A: The pipeline sets `status = ProcessStatus.FROZEN` and returns immediately. There is no fallback to cached or stale data. The audit trail logs the failure. This is intentional — a frozen pipeline is visible; a silent fallback would be dangerous.

---

## Business

**Q: What is the token mechanic?**  
A: `$UMIA-ANALYST` tokens represent a proportional claim on the agent's trading book. As markets resolve, PnL is calculated and distributed to token holders. New memos are published on-chain — every position is public before it resolves.

**Q: Why would anyone trust an agent's track record?**  
A: Because it's tamper-evident. Memos are published before markets resolve. The prompt hashes prove the reasoning wasn't changed after the fact. The PnL calculation is deterministic from public market data. There is no black box.

**Q: What's the path from demo to production?**  
A: Set `UMIA_ENV=production`, add your `APIFY_TOKEN`, `GITHUB_TOKEN`, and `ETHERSCAN_API_KEY` to `.env`. The pipeline is identical — only the data source changes from mock JSON to live API calls.
