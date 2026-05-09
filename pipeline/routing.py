# DETERMINISTIC
"""
Pipeline Routing — pipeline/routing.py
Conditional edges for the Umia Analyst Agent LangGraph.
No LLM — pure Python.
"""

import logging

from pipeline.state import ProcessStatus
from utils.source_rules import MAX_POSITION_ITERATIONS, MIN_CITATION_COVERAGE

log = logging.getLogger(__name__)


# DETERMINISTIC
def route_after_classification(state: dict) -> str:
    """After classification_validator → continue or freeze."""
    market_id = state.get("market_id", "UNKNOWN")
    status = state.get("status")
    if status == ProcessStatus.FROZEN:
        log.info(f"[Router] classification → freeze | market_id={market_id}")
        return "freeze"
    log.info(f"[Router] classification → synthesize | market_id={market_id}")
    return "synthesize"


# DETERMINISTIC
def route_after_reviewer(state: dict) -> str:
    """
    After self_reviewer → decides next step.

    - FROZEN / ESCALATED → end
    - reviewer_verdict == "pass" → position_rules_engine
    - reviewer_verdict == "fail" + iterations remaining → retry position_agent
    - max iterations → escalate
    """
    market_id   = state.get("market_id", "UNKNOWN")
    status      = state.get("status")
    verdict     = state.get("reviewer_verdict", "fail")
    iteration   = state.get("position_iteration", 1)

    if status == ProcessStatus.FROZEN:
        log.info(f"[Router] reviewer → freeze | market_id={market_id}")
        return "freeze"

    if status == ProcessStatus.ESCALATED:
        log.info(f"[Router] reviewer → escalate | market_id={market_id}")
        return "escalate"

    if verdict == "pass":
        log.info(f"[Router] reviewer → rules | market_id={market_id}")
        return "rules"

    if iteration < MAX_POSITION_ITERATIONS:
        log.info(f"[Router] reviewer → retry_position | market_id={market_id} "
                 f"iteration={iteration}/{MAX_POSITION_ITERATIONS}")
        return "retry_position"

    log.warning(f"[Router] reviewer → escalate (max iterations) | market_id={market_id}")
    return "escalate"


# DETERMINISTIC
def route_after_rules(state: dict) -> str:
    """After position_rules_engine → always publish."""
    market_id = state.get("market_id", "UNKNOWN")
    log.info(f"[Router] rules → publish | market_id={market_id}")
    return "publish"


if __name__ == "__main__":
    from pipeline.state import make_initial_state, ProcessStatus

    s = make_initial_state("x", "R1")
    s["status"] = ProcessStatus.FROZEN
    assert route_after_classification(s) == "freeze"

    s2 = make_initial_state("x", "R2")
    assert route_after_classification(s2) == "synthesize"

    s3 = make_initial_state("x", "R3")
    s3["reviewer_verdict"] = "pass"
    assert route_after_reviewer(s3) == "rules"

    s4 = make_initial_state("x", "R4")
    s4["reviewer_verdict"] = "fail"
    s4["position_iteration"] = 1
    assert route_after_reviewer(s4) == "retry_position"

    s5 = make_initial_state("x", "R5")
    s5["reviewer_verdict"] = "fail"
    s5["position_iteration"] = MAX_POSITION_ITERATIONS
    assert route_after_reviewer(s5) == "escalate"

    print("OK — routing.py smoke test passed")
