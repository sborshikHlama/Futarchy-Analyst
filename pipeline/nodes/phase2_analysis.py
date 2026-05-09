"""
Phase 2 — Synthesis — pipeline/nodes/phase2_analysis.py

Nodes:
  - memo_context_builder  (DET) — assembles classified sources into structured prompt context
  - synthesizer           (AI)  — produces bull_case, bear_case, manipulation_flags

DETERMINISTIC context builder, AI synthesis.
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


# DETERMINISTIC
def memo_context_builder(state: dict) -> dict:
    """
    Assembles classified sources into a structured context dict
    for the synthesizer agent. Pure Python — no LLM.
    """
    market_id = state.get("market_id", "UNKNOWN")
    log.info(f"[MemoContextBuilder] Building context | market_id={market_id}")

    raw_signals: dict = state.get("raw_signals", {})
    source_weights: dict = state.get("source_weights", {})
    market_meta: dict = state.get("market_metadata") or {}

    # Group sources by class for easy synthesis
    by_class: dict[str, list[dict]] = {
        "verifiable": [], "partial": [], "manipulable": []
    }
    for src_id, sw in source_weights.items():
        cls = sw.get("class_", "partial")
        by_class.setdefault(cls, []).append({
            "source_id": src_id,
            "weight": sw.get("weight", 0.0),
            "reasoning": sw.get("reasoning", ""),
            "signals": raw_signals.get(src_id, []),
        })

    context = {
        "market_id":   market_id,
        "title":       market_meta.get("title", "Unknown"),
        "proposal":    market_meta.get("proposal", "Unknown"),
        "venue":       market_meta.get("venue", "Unknown"),
        "closes_at":   market_meta.get("closes_at", "Unknown"),
        "sources_by_class": by_class,
        "source_count": {cls: len(srcs) for cls, srcs in by_class.items()},
    }

    total_verifiable_weight = sum(
        s["weight"] for s in by_class.get("verifiable", [])
    )
    manipulation_source_count = len(by_class.get("manipulable", []))

    log.info(f"[MemoContextBuilder] Context built | market_id={market_id} "
             f"verifiable_weight={total_verifiable_weight:.2f} "
             f"manipulable_sources={manipulation_source_count}")

    audit = _audit(state, node="MemoContextBuilder", action="context_built",
                   result="success",
                   metadata={"market_id": market_id,
                              "total_sources": len(source_weights),
                              "verifiable_weight": round(total_verifiable_weight, 3),
                              "source_count_by_class": context["source_count"]})

    return {**state, "memo_context": context, "audit_trail": audit}


# AI
def synthesizer(state: dict) -> dict:
    """
    Given classified sources, writes bull_case, bear_case, manipulation_flags.
    Uses synthesizer_skill.yaml prompt. All claims must cite source_ids.
    """
    market_id = state.get("market_id", "UNKNOWN")
    log.info(f"[Synthesizer] Starting | market_id={market_id}")

    memo_context = state.get("memo_context")
    if not memo_context:
        audit = _audit(state, node="Synthesizer", action="synthesis_failed",
                       result="missing_context", metadata={"market_id": market_id})
        return {**state, "audit_trail": audit}

    skill = registry.get("synthesizer_skill")
    prompt = skill["prompt"]
    skill_version = skill["version"]

    source_ids = list(state.get("source_weights", {}).keys())
    user_message = (
        f"MARKET CONTEXT:\n{json.dumps(memo_context, indent=2, ensure_ascii=False)}\n\n"
        f"VALID SOURCE IDs FOR CITATIONS: {source_ids}\n\n"
        f"Return JSON:\n"
        f'{{"bull_case": "markdown bullets...", '
        f'"bear_case": "markdown bullets...", '
        f'"manipulation_flags": ["flag1", "flag2"]}}'
    )

    last_error: str | None = None
    for attempt in range(1, API_RETRY_COUNT + 1):
        try:
            from utils.llm_factory import get_llm
            api_client = get_llm()
            response = api_client.complete(
                system=prompt, user_message=user_message, max_tokens=2048)
            raw_text = response.text
            tokens_used = response.tokens_used

            parsed = json.loads(_extract_json(raw_text))
            bull_case          = parsed.get("bull_case", "")
            bear_case          = parsed.get("bear_case", "")
            manipulation_flags = parsed.get("manipulation_flags", [])

            log.info(f"[Synthesizer] Done | market_id={market_id} tokens={tokens_used} "
                     f"flags={len(manipulation_flags)}")

            audit = _audit(state, node="Synthesizer", action="synthesis_done",
                           result="success", prompt=prompt, prompt_version=skill_version,
                           tokens_used=tokens_used,
                           metadata={"market_id": market_id,
                                     "manipulation_flags": len(manipulation_flags)})
            return {**state, "bull_case": bull_case, "bear_case": bear_case,
                    "manipulation_flags": manipulation_flags, "audit_trail": audit}

        except Exception as exc:
            last_error = str(exc)
            log.warning(f"[Synthesizer] Attempt {attempt}/{API_RETRY_COUNT} failed: {last_error}")
            if attempt < API_RETRY_COUNT:
                time.sleep(API_RETRY_DELAY_SEC)

    audit = _audit(state, node="Synthesizer", action="synthesis_failed",
                   result="process_freeze", prompt=prompt, prompt_version=skill_version,
                   metadata={"market_id": market_id, "last_error": last_error})
    return {**state, "status": ProcessStatus.FROZEN,
            "fallback_reason": f"Synthesizer API failed after {API_RETRY_COUNT} attempts: {last_error}",
            "audit_trail": audit}


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
    import os
    from pipeline.state import make_initial_state, ProcessStatus

    state = make_initial_state("metadao_001", "REQ-SMOKE-P2")
    state["raw_signals"] = {
        "github_commits":   {"commits_last_week": 12},
        "telegram_founder": ["Big announcement coming!"],
    }
    state["source_weights"] = {
        "github_commits":   {"class_": "verifiable",  "weight": 0.85, "reasoning": "on-chain"},
        "telegram_founder": {"class_": "manipulable", "weight": 0.25, "reasoning": "founder-controlled"},
    }
    state["market_metadata"] = {
        "title":    "MetaDAO Proposal: Expand Developer Grants",
        "proposal": "Allocate 500k USDC to developer grants",
        "venue":    "MetaDAO",
        "closes_at": "2026-05-15",
    }

    state = memo_context_builder(state)
    assert state.get("memo_context") is not None
    assert state["memo_context"]["source_count"]["verifiable"] == 1
    print(f"  Context sources: {state['memo_context']['source_count']}")

    if not os.getenv("ANTHROPIC_API_KEY"):
        state["bull_case"] = "- Strong GitHub activity [CITATION:github_commits]"
        state["bear_case"] = "- Founder hype without verifiable delivery [CITATION:telegram_founder]"
        state["manipulation_flags"] = ["Founder Telegram claims unverified by on-chain data"]
        print("  Skipping live LLM call (no API key) — mock bull/bear injected")
    else:
        state = synthesizer(state)
        assert state.get("bull_case"), "bull_case missing"
        assert state.get("bear_case"), "bear_case missing"

    print(f"  Manipulation flags: {len(state.get('manipulation_flags', []))}")
    print("OK — phase2_analysis.py smoke test passed")
