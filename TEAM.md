# Team 7 — Umia Analyst Agent

**Hackathon:** Umia Protocol Hackathon 2026  
**Bounty:** Best Agentic Venture  
**Project:** Umia Analyst Agent

---

## Team members

| Name | Role |
|------|------|
| sborshikHlama | Lead Engineer — LangGraph pipeline, skills registry, audit trail |

---

## Tech choices

| Decision | Rationale |
|----------|-----------|
| LangGraph | Explicit state machine — every edge is deterministic or clearly AI. Auditable. |
| YAML skills registry | Versioned prompts with sha256 hashes — reproducible and auditable across runs |
| Source classification | Manipulable sources capped at 0.3 weight — no Telegram post can swing a position |
| Binary PnL model | `((1-p)/p) × size` matches actual prediction market payoff structure |
| Demo / production dual mode | Zero-friction demo without API keys; clean path to production |
| Append-only audit trail | Every node action logged with prompt hash — tamper-evident by construction |

---

## Contact

GitHub: sborshikHlama
