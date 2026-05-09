"""
Source classification rules and position limits — utils/source_rules.py
Replaces wcr_rules.py. All constants for Umia Analyst Agent.
DETERMINISTIC — no LLM.
"""

# ── Source class weight caps ───────────────────────────────────────────────────

SOURCE_CLASS_MAX_WEIGHT: dict[str, float] = {
    "verifiable":  1.0,   # on-chain txs, GitHub commits, third-party audits
    "partial":     0.6,   # independent news, public forums, analytics
    "manipulable": 0.3,   # founder Telegram, official Twitter, project blog
}

# ── Position hard limits ───────────────────────────────────────────────────────

MAX_POSITION_SIZE_PCT    = 7.0    # hard cap on any single position
MIN_CONFIDENCE_TO_BET    = 0.6    # below this → ABSTAIN
MIN_CITATION_COVERAGE    = 0.85   # 85% of claims must cite a source_id
MAX_POSITION_ITERATIONS  = 3      # Position + Self-Review retry cap

# ── API retry ─────────────────────────────────────────────────────────────────

API_RETRY_COUNT     = 3
API_RETRY_DELAY_SEC = 30

# ── Signal watch thresholds ───────────────────────────────────────────────────

WATCH_THRESHOLDS: dict[str, float] = {
    "high_signal_weight_sum":   1.5,   # sum of verifiable source weights → HIGH
    "medium_signal_weight_sum": 0.8,
    "manipulation_flag_high":   3,     # ≥ N flags → HIGH manipulation risk
    "manipulation_flag_medium": 1,
}


def classify_signal_level(source_weights: dict) -> str:
    """Return HIGH / MEDIUM / LOW based on total verifiable signal weight."""
    total = sum(
        sw.get("weight", 0)
        for sw in source_weights.values()
        if sw.get("class_") in ("verifiable", "partial")
    )
    if total >= WATCH_THRESHOLDS["high_signal_weight_sum"]:
        return "HIGH"
    if total >= WATCH_THRESHOLDS["medium_signal_weight_sum"]:
        return "MEDIUM"
    return "LOW"


def check_position_rules(confidence: float, side: str, size_pct: float) -> dict:
    """
    Deterministic position rule engine.
    Returns {passed: bool, overrides: list[str], final_side, final_size_pct}.
    """
    overrides: list[str] = []

    if confidence < MIN_CONFIDENCE_TO_BET:
        overrides.append(f"confidence {confidence:.2f} < {MIN_CONFIDENCE_TO_BET} → ABSTAIN")
        side     = "ABSTAIN"
        size_pct = 0.0

    if size_pct > MAX_POSITION_SIZE_PCT:
        overrides.append(f"size_pct {size_pct:.1f} capped to {MAX_POSITION_SIZE_PCT}")
        size_pct = MAX_POSITION_SIZE_PCT

    if side == "ABSTAIN":
        size_pct = 0.0

    return {
        "passed":         len(overrides) == 0,
        "overrides":      overrides,
        "final_side":     side,
        "final_size_pct": size_pct,
    }


if __name__ == "__main__":
    assert check_position_rules(0.5, "YES", 5.0)["final_side"] == "ABSTAIN"
    assert check_position_rules(0.8, "YES", 10.0)["final_size_pct"] == 7.0
    assert check_position_rules(0.75, "NO", 5.0)["passed"] is True
    print("OK — source_rules.py smoke test passed")
