# AI + DETERMINISTIC
"""
Phase 1 — Source Classification — pipeline/nodes/phase1_extraction.py

Nodes:
  - source_classifier_agent   (AI) — classifies each signal source by manipulability
  - classification_validator  (DET) — checks every source has class + weight in [0,1]

On API failure → ProcessStatus.FROZEN (no silent fallback).
"""

import json
import logging
import re
import time

from pipeline.state import ProcessStatus
from skills import registry
from utils.audit import _audit
from utils.source_rules import API_RETRY_COUNT, API_RETRY_DELAY_SEC

log = logging.getLogger(__name__)


# AI
def source_classifier_agent(state: dict) -> dict:
    """
    Classifies each raw signal source by manipulability.
    Reads state["raw_signals"] and writes state["source_weights"].

    source_weights: dict[source_id → {class_, weight, reasoning}]
    class_: "verifiable" | "partial" | "manipulable"
    """
    market_id = state.get("market_id", "UNKNOWN")
    log.info(f"[SourceClassifier] Starting | market_id={market_id}")

    raw_signals: dict = state.get("raw_signals", {})
    if not raw_signals:
        audit = _audit(state, node="SourceClassifier", action="no_signals",
                       result="frozen", metadata={"market_id": market_id})
        return {**state, "status": ProcessStatus.FROZEN,
                "fallback_reason": "No raw signals to classify",
                "audit_trail": audit}

    from utils.sentiment import analyze_batch

    telegram_posts = state.get("telegram_signals", [])
    news_snippets  = state.get("news_signals", [])

    telegram_sentiment = analyze_batch(telegram_posts, source_type="social")
    news_sentiment     = analyze_batch(news_snippets,  source_type="news")

    state = {**state, "sentiment": {
        "telegram": telegram_sentiment,
        "news":     news_sentiment,
    }}

    skill = registry.get("classifier_skill")
    prompt = skill["prompt"]
    skill_version = skill["version"]

    market_meta = state.get("market_metadata") or {}
    user_message = (
        f"Market ID: {market_id}\n"
        f"Title: {market_meta.get('title', 'Unknown')}\n"
        f"Proposal: {market_meta.get('proposal', 'Unknown')}\n\n"
        f"RAW SIGNALS TO CLASSIFY:\n"
        + json.dumps(raw_signals, indent=2, ensure_ascii=False)
        + "\n\nReturn JSON: {\"source_weights\": {\"<source_id>\": "
          "{\"class_\": \"verifiable|partial|manipulable\", "
          "\"weight\": 0.0-1.0, \"reasoning\": \"...\"}, ...}}"
    )

    last_error: str | None = None
    attempts = state.get("classification_attempts", 0)

    for attempt in range(1, API_RETRY_COUNT + 1):
        attempts += 1
        try:
            from utils.llm_factory import get_llm
            api_client = get_llm()
            response = api_client.complete(
                system=prompt, user_message=user_message, max_tokens=1024)
            raw_text = response.text
            tokens_used = response.tokens_used

            parsed = json.loads(_extract_json(raw_text))
            source_weights = parsed.get("source_weights", {})

            log.info(f"[SourceClassifier] Done | market_id={market_id} "
                     f"sources={len(source_weights)} tokens={tokens_used}")

            audit = _audit(state, node="SourceClassifier",
                           action="classification_done", result="success",
                           prompt=prompt, prompt_version=skill_version,
                           tokens_used=tokens_used,
                           metadata={"market_id": market_id,
                                     "sources_classified": len(source_weights)})
            return {**state, "source_weights": source_weights,
                    "classification_attempts": attempts, "audit_trail": audit}

        except Exception as exc:
            last_error = str(exc)
            log.warning(f"[SourceClassifier] Attempt {attempt}/{API_RETRY_COUNT} failed: {last_error}")
            if attempt < API_RETRY_COUNT:
                time.sleep(API_RETRY_DELAY_SEC)

    audit = _audit(state, node="SourceClassifier", action="classification_failed",
                   result="process_freeze", prompt=prompt, prompt_version=skill_version,
                   metadata={"market_id": market_id, "last_error": last_error})
    return {**state, "status": ProcessStatus.FROZEN,
            "fallback_reason": f"Classifier API failed after {API_RETRY_COUNT} attempts: {last_error}",
            "classification_attempts": attempts, "audit_trail": audit}


# DETERMINISTIC
def classification_validator(state: dict) -> dict:
    """
    Validates source_weights structure:
    - At least one source present
    - Every source has class_ ∈ {verifiable, partial, manipulable}
    - Every weight ∈ [0, 1]
    - manipulable sources capped at 0.3 (enforced, not just warned)
    """
    market_id = state.get("market_id", "UNKNOWN")
    log.info(f"[ClassificationValidator] Validating | market_id={market_id}")

    source_weights: dict = state.get("source_weights", {})
    valid_classes = {"verifiable", "partial", "manipulable"}

    from utils.source_rules import SOURCE_CLASS_MAX_WEIGHT

    issues: list[str] = []
    corrected = {}

    for src_id, sw in source_weights.items():
        cls = sw.get("class_", "")
        weight = sw.get("weight", 0.0)

        if cls not in valid_classes:
            issues.append(f"{src_id}: unknown class '{cls}' → defaulting to 'partial'")
            cls = "partial"

        cap = SOURCE_CLASS_MAX_WEIGHT.get(cls, 0.6)
        if weight > cap:
            issues.append(f"{src_id}: weight {weight:.2f} > cap {cap} for '{cls}' → capped")
            weight = cap
        if weight < 0:
            weight = 0.0

        corrected[src_id] = {**sw, "class_": cls, "weight": round(weight, 3)}

    if not corrected:
        audit = _audit(state, node="ClassificationValidator",
                       action="validation_failed", result="no_sources",
                       metadata={"market_id": market_id})
        return {**state, "status": ProcessStatus.FROZEN,
                "fallback_reason": "No classified sources — cannot synthesize memo",
                "audit_trail": audit}

    log.info(f"[ClassificationValidator] OK | market_id={market_id} "
             f"sources={len(corrected)} issues={len(issues)}")

    audit = _audit(state, node="ClassificationValidator",
                   action="validation_passed", result="passed",
                   metadata={"market_id": market_id,
                              "sources_count": len(corrected),
                              "corrections": issues})
    return {**state, "source_weights": corrected, "audit_trail": audit}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return m.group(1)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return m.group(0)
    return text


if __name__ == "__main__":
    from pipeline.state import make_initial_state

    state = make_initial_state("metadao_001", "REQ-SMOKE-P1")
    state["raw_signals"] = {
        "telegram_founder": ["We are shipping v2 this week!", "Team is working hard"],
        "github_commits":   {"commits_last_week": 12, "contributors": 5},
        "onchain_dev_wallet": {"tx_count_7d": 3, "last_tx": "2026-05-08"},
    }
    state["market_metadata"] = {
        "title": "Should MetaDAO adopt proposal X?",
        "proposal": "Allocate 500k USDC to expand developer grants",
    }

    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        # Inject mock source_weights to test validator without API
        state["source_weights"] = {
            "telegram_founder":   {"class_": "manipulable", "weight": 0.25, "reasoning": "founder-controlled"},
            "github_commits":     {"class_": "verifiable",  "weight": 0.85, "reasoning": "on-chain verifiable"},
            "onchain_dev_wallet": {"class_": "verifiable",  "weight": 0.90, "reasoning": "on-chain txs"},
        }
        print("  Skipping live LLM call (no API key) — testing validator only")
    else:
        state = source_classifier_agent(state)
        assert state.get("status") != ProcessStatus.FROZEN, state.get("fallback_reason")

    state = classification_validator(state)
    assert state.get("status") != ProcessStatus.FROZEN, state.get("fallback_reason")
    assert all(sw["weight"] <= 0.3 for src, sw in state["source_weights"].items()
               if sw["class_"] == "manipulable")
    print(f"  Sources classified: {len(state['source_weights'])}")
    for src, sw in state["source_weights"].items():
        print(f"  {src}: {sw['class_']} weight={sw['weight']:.2f}")
    print("OK — phase1_extraction.py smoke test passed")
