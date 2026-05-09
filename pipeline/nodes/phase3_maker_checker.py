# AI + DETERMINISTIC
"""
Phase 3 — Position + Self-Review Loop — pipeline/nodes/phase3_maker_checker.py

Nodes:
  - position_agent       (AI)  — decides YES/NO/ABSTAIN, size_pct, confidence
  - self_reviewer        (AI)  — argues against own memo, may reduce confidence
  - position_rules_engine (DET) — enforces hard rules (confidence cap, size cap)

Retry loop: max MAX_POSITION_ITERATIONS (3).
API failure → ProcessStatus.FROZEN.
"""

import json
import logging
import re
import time

from pipeline.state import ProcessStatus
from skills import registry
from utils.audit import _audit
from utils.source_rules import (
    API_RETRY_COUNT,
    API_RETRY_DELAY_SEC,
    MAX_POSITION_ITERATIONS,
    MIN_CITATION_COVERAGE,
    check_position_rules,
)

log = logging.getLogger(__name__)


# AI
def position_agent(state: dict) -> dict:
    """
    Given bull_case, bear_case, manipulation_flags → produces position.
    Output: {side, size_pct, rationale, confidence}.

    Re-iteration: if reviewer_verdict == "fail", re-runs with self_review feedback.
    """
    market_id = state.get("market_id", "UNKNOWN")
    iteration = state.get("position_iteration", 0) + 1
    log.info(f"[PositionAgent] Starting | market_id={market_id} iteration={iteration}")

    if iteration > MAX_POSITION_ITERATIONS:
        audit = _audit(state, node="PositionAgent", action="max_iterations_reached",
                       result="escalated",
                       metadata={"market_id": market_id, "iteration": iteration})
        return {**state, "status": ProcessStatus.ESCALATED,
                "escalation_reason": f"Position agent exceeded {MAX_POSITION_ITERATIONS} iterations",
                "position_iteration": iteration, "audit_trail": audit}

    skill = registry.get("position_skill")
    prompt = skill["prompt"]
    skill_version = skill["version"]

    re_iter_section = ""
    if iteration > 1 and state.get("self_review"):
        sr = state["self_review"]
        re_iter_section = (
            f"\n\nRE-ITERATION {iteration} — address these self-review findings:\n"
            f"Weaknesses:\n" + "\n".join(f"- {w}" for w in sr.get("weaknesses", []))
            + f"\nCounter-arguments:\n"
            + "\n".join(f"- {c}" for c in sr.get("counter_arguments", []))
        )

    user_message = (
        f"Market: {state.get('market_metadata', {}).get('title', market_id)}\n"
        f"Proposal: {state.get('market_metadata', {}).get('proposal', '')}\n\n"
        f"BULL CASE:\n{state.get('bull_case', 'N/A')}\n\n"
        f"BEAR CASE:\n{state.get('bear_case', 'N/A')}\n\n"
        f"MANIPULATION FLAGS:\n"
        + "\n".join(f"- {f}" for f in state.get("manipulation_flags", []))
        + f"\n\nSOURCE WEIGHTS SUMMARY:\n"
        + "\n".join(
            f"  {src}: {sw.get('class_')} weight={sw.get('weight'):.2f}"
            for src, sw in state.get("source_weights", {}).items()
        )
        + re_iter_section
        + "\n\nReturn JSON: {\"side\": \"YES|NO|ABSTAIN\", \"size_pct\": 0.0-7.0, "
          "\"rationale\": \"...\", \"confidence\": 0.0-1.0}"
    )

    last_error: str | None = None
    for attempt in range(1, API_RETRY_COUNT + 1):
        try:
            from utils.llm_factory import get_llm
            api_client = get_llm()
            response = api_client.complete(
                system=prompt, user_message=user_message, max_tokens=1024)
            parsed = json.loads(_extract_json(response.text))

            side       = parsed.get("side", "ABSTAIN")
            size_pct   = float(parsed.get("size_pct", 0.0))
            rationale  = parsed.get("rationale", "")
            confidence = float(parsed.get("confidence", 0.0))

            log.info(f"[PositionAgent] Done | market_id={market_id} "
                     f"side={side} size={size_pct:.1f}% conf={confidence:.2f} "
                     f"tokens={response.tokens_used}")

            audit = _audit(state, node="PositionAgent", action="position_taken",
                           result="success", prompt=prompt, prompt_version=skill_version,
                           tokens_used=response.tokens_used,
                           metadata={"market_id": market_id, "iteration": iteration,
                                     "side": side, "size_pct": size_pct,
                                     "confidence": confidence})
            return {**state,
                    "position": {"side": side, "size_pct": size_pct, "rationale": rationale},
                    "confidence": confidence,
                    "position_iteration": iteration,
                    "audit_trail": audit}

        except Exception as exc:
            last_error = str(exc)
            log.warning(f"[PositionAgent] Attempt {attempt}/{API_RETRY_COUNT} failed: {last_error}")
            if attempt < API_RETRY_COUNT:
                time.sleep(API_RETRY_DELAY_SEC)

    audit = _audit(state, node="PositionAgent", action="position_failed",
                   result="process_freeze", prompt=prompt, prompt_version=skill_version,
                   metadata={"market_id": market_id, "last_error": last_error})
    return {**state, "status": ProcessStatus.FROZEN,
            "fallback_reason": f"PositionAgent API failed after {API_RETRY_COUNT} attempts: {last_error}",
            "position_iteration": iteration, "audit_trail": audit}


# AI
def self_reviewer(state: dict) -> dict:
    """
    Argues against the memo. Produces weaknesses and counter_arguments.
    Recommends confidence delta if counter-arguments are strong.
    """
    market_id = state.get("market_id", "UNKNOWN")
    iteration = state.get("position_iteration", 1)
    log.info(f"[SelfReviewer] Starting | market_id={market_id} iteration={iteration}")

    position = state.get("position")
    if not position:
        audit = _audit(state, node="SelfReviewer", action="review_failed",
                       result="missing_position", metadata={"market_id": market_id})
        return {**state, "reviewer_verdict": "fail", "audit_trail": audit}

    skill = registry.get("reviewer_skill")
    prompt = skill["prompt"]
    skill_version = skill["version"]

    user_message = (
        f"Market: {state.get('market_metadata', {}).get('title', market_id)}\n\n"
        f"BULL CASE:\n{state.get('bull_case', '')}\n\n"
        f"BEAR CASE:\n{state.get('bear_case', '')}\n\n"
        f"POSITION TAKEN: {position.get('side')} @ {position.get('size_pct')}%\n"
        f"RATIONALE: {position.get('rationale')}\n"
        f"CONFIDENCE: {state.get('confidence', 0):.2f}\n\n"
        f"MANIPULATION FLAGS: {state.get('manipulation_flags', [])}\n\n"
        f"Return JSON: {{\"weaknesses\": [...], \"counter_arguments\": [...], "
        f"\"confidence_delta\": 0.0, \"verdict\": \"pass|fail\"}}"
    )

    last_error: str | None = None
    for attempt in range(1, API_RETRY_COUNT + 1):
        try:
            from utils.llm_factory import get_llm
            api_client = get_llm()
            response = api_client.complete(
                system=prompt, user_message=user_message, max_tokens=1024)
            parsed = json.loads(_extract_json(response.text))

            weaknesses       = parsed.get("weaknesses", [])
            counter_args     = parsed.get("counter_arguments", [])
            confidence_delta = float(parsed.get("confidence_delta", 0.0))
            verdict          = parsed.get("verdict", "pass")

            # Apply confidence reduction if recommended
            new_confidence = state.get("confidence", 0.5)
            if confidence_delta > 0:
                new_confidence = max(0.0, new_confidence - confidence_delta)
                log.info(f"[SelfReviewer] Confidence reduced by {confidence_delta:.2f} "
                         f"→ {new_confidence:.2f}")

            self_review = {"weaknesses": weaknesses, "counter_arguments": counter_args}

            log.info(f"[SelfReviewer] Done | market_id={market_id} verdict={verdict} "
                     f"weaknesses={len(weaknesses)} tokens={response.tokens_used}")

            audit = _audit(state, node="SelfReviewer", action="self_review_done",
                           result=verdict, prompt=prompt, prompt_version=skill_version,
                           tokens_used=response.tokens_used,
                           metadata={"market_id": market_id, "iteration": iteration,
                                     "verdict": verdict, "confidence_delta": confidence_delta,
                                     "weaknesses_count": len(weaknesses)})
            return {**state, "self_review": self_review,
                    "reviewer_verdict": verdict,
                    "confidence": new_confidence,
                    "audit_trail": audit}

        except Exception as exc:
            last_error = str(exc)
            log.warning(f"[SelfReviewer] Attempt {attempt}/{API_RETRY_COUNT} failed: {last_error}")
            if attempt < API_RETRY_COUNT:
                time.sleep(API_RETRY_DELAY_SEC)

    audit = _audit(state, node="SelfReviewer", action="review_failed",
                   result="process_freeze", prompt=prompt, prompt_version=skill_version,
                   metadata={"market_id": market_id, "last_error": last_error})
    return {**state, "status": ProcessStatus.FROZEN,
            "fallback_reason": f"SelfReviewer API failed after {API_RETRY_COUNT} attempts: {last_error}",
            "reviewer_verdict": "fail", "audit_trail": audit}


# DETERMINISTIC
def position_rules_engine(state: dict) -> dict:
    """
    Enforces hard position rules:
    - confidence < 0.6 → ABSTAIN
    - size_pct capped at 7%
    - ABSTAIN → size_pct = 0

    Pure Python — no LLM.
    """
    market_id = state.get("market_id", "UNKNOWN")
    log.info(f"[PositionRulesEngine] Checking rules | market_id={market_id}")

    position   = state.get("position") or {}
    confidence = float(state.get("confidence", 0.0))
    side       = position.get("side", "ABSTAIN")
    size_pct   = float(position.get("size_pct", 0.0))

    result = check_position_rules(confidence, side, size_pct)

    final_position = {
        **position,
        "side":     result["final_side"],
        "size_pct": result["final_size_pct"],
    }

    log.info(f"[PositionRulesEngine] Done | market_id={market_id} "
             f"side={result['final_side']} size={result['final_size_pct']:.1f}% "
             f"overrides={len(result['overrides'])}")

    audit = _audit(state, node="PositionRulesEngine", action="rules_applied",
                   result="passed" if result["passed"] else "overridden",
                   metadata={"market_id": market_id,
                              "original_side": side,
                              "original_size_pct": size_pct,
                              "final_side": result["final_side"],
                              "final_size_pct": result["final_size_pct"],
                              "overrides": result["overrides"]})
    return {**state, "position": final_position, "audit_trail": audit}


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

    state = make_initial_state("metadao_001", "REQ-SMOKE-P3")
    state["position"] = {"side": "YES", "size_pct": 10.0, "rationale": "test"}
    state["confidence"] = 0.45   # below threshold

    state = position_rules_engine(state)
    assert state["position"]["side"] == "ABSTAIN", "Should ABSTAIN below threshold"
    assert state["position"]["size_pct"] == 0.0
    print(f"  Low confidence → side={state['position']['side']} size={state['position']['size_pct']}")

    state2 = make_initial_state("metadao_002", "REQ-SMOKE-P3B")
    state2["position"] = {"side": "NO", "size_pct": 12.0, "rationale": "test"}
    state2["confidence"] = 0.78

    state2 = position_rules_engine(state2)
    assert state2["position"]["side"] == "NO"
    assert state2["position"]["size_pct"] == 7.0
    print(f"  Size cap → side={state2['position']['side']} size={state2['position']['size_pct']}")

    print("OK — phase3_maker_checker.py smoke test passed")
