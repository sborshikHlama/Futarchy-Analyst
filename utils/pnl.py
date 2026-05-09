"""
PnL Calculator — utils/pnl.py
Computes realized PnL for memo positions and aggregates track record.
DETERMINISTIC — no LLM.

Model:
  A binary prediction market resolves YES at 1.0 or NO at 0.0.
  Implied market price at time of bet is stored in memo["position"]["implied_price"]
  (default 0.5 if absent — 50/50 market assumption for demos).

  If you bet YES at price p and YES resolves:
    pnl_pct = ((1.0 - p) / p) * size_pct   (win: you bought at p, resolved at 1)
  If you bet YES and NO resolves:
    pnl_pct = -size_pct                      (loss: position goes to 0)
  If ABSTAIN: pnl_pct = 0.
"""

import logging
import json
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data" / "markets"


def compute_pnl(memo: dict, resolved_outcome: str) -> float:
    """
    Compute PnL percentage for a single memo given the resolved outcome.

    Args:
        memo:             memo dict with position.{side, size_pct, implied_price}
        resolved_outcome: "YES" or "NO"

    Returns:
        pnl_pct: realized profit/loss as fraction of treasury (e.g. +5.2 or -3.0)
    """
    position = memo.get("position") or {}
    side     = position.get("side", "ABSTAIN")
    size_pct = float(position.get("size_pct", 0.0))
    # Default to 0.5 (50/50 market) when implied price not recorded
    implied_price = float(position.get("implied_price", 0.5))

    if side == "ABSTAIN" or size_pct == 0:
        return 0.0

    implied_price = max(0.01, min(0.99, implied_price))

    if side == resolved_outcome:
        # Win: bought at implied_price, resolved at 1.0 (YES) or 0.0 (NO)
        if resolved_outcome == "YES":
            return round(((1.0 - implied_price) / implied_price) * size_pct, 2)
        else:
            return round(((implied_price - 0.0) / (1.0 - implied_price)) * size_pct, 2)
    else:
        # Loss: full position size lost
        return round(-size_pct, 2)


def attach_outcome_to_memo(market_id: str, resolved_outcome: str) -> bool:
    """
    Load the memo JSON for a market, compute PnL, and write it back with outcome.

    Returns True if memo exists and was updated.
    """
    memo_path = _DATA_DIR / market_id / "memo.json"
    if not memo_path.exists():
        log.warning(f"[PnL] No memo found for {market_id}")
        return False

    with memo_path.open("r", encoding="utf-8") as f:
        memo = json.load(f)

    pnl = compute_pnl(memo, resolved_outcome)
    memo["outcome"] = {
        "resolved_side": resolved_outcome,
        "pnl_pct":       pnl,
    }

    with memo_path.open("w", encoding="utf-8") as f:
        json.dump(memo, f, indent=2, ensure_ascii=False)

    log.info(f"[PnL] Outcome recorded | market={market_id} "
             f"resolved={resolved_outcome} pnl={pnl:+.2f}%")
    return True


def aggregate_track_record(data_dir: Path | None = None) -> dict:
    """
    Walk data/markets/*/memo.json and aggregate realized PnL.

    Returns:
        {total_memos, resolved, unresolved, total_pnl_pct,
         win_count, loss_count, abstain_count, memos: list[dict]}
    """
    if data_dir is None:
        data_dir = _DATA_DIR

    memos: list[dict] = []
    total_pnl = 0.0
    resolved = wins = losses = abstains = 0

    for memo_file in sorted(data_dir.glob("*/memo.json")):
        try:
            with memo_file.open("r", encoding="utf-8") as f:
                memo = json.load(f)
            memos.append(memo)

            outcome = memo.get("outcome")
            if outcome:
                resolved += 1
                pnl = float(outcome.get("pnl_pct", 0.0))
                total_pnl += pnl
                if pnl > 0:
                    wins += 1
                elif pnl < 0:
                    losses += 1
                else:
                    abstains += 1
        except Exception as exc:
            log.warning(f"[PnL] Failed to read {memo_file}: {exc}")

    unresolved = len(memos) - resolved

    return {
        "total_memos":   len(memos),
        "resolved":      resolved,
        "unresolved":    unresolved,
        "total_pnl_pct": round(total_pnl, 2),
        "win_count":     wins,
        "loss_count":    losses,
        "abstain_count": abstains,
        "win_rate":      round(wins / resolved * 100, 1) if resolved > 0 else 0.0,
        "memos":         memos,
    }


if __name__ == "__main__":
    # Smoke test
    mock_memo = {
        "position": {"side": "YES", "size_pct": 5.0, "implied_price": 0.42}
    }
    pnl_win  = compute_pnl(mock_memo, "YES")
    pnl_loss = compute_pnl(mock_memo, "NO")
    assert pnl_win > 0, f"Expected positive PnL on win, got {pnl_win}"
    assert pnl_loss == -5.0, f"Expected -5.0 on loss, got {pnl_loss}"
    print(f"  YES@0.42 bet 5% → WIN: +{pnl_win:.2f}% | LOSS: {pnl_loss:.2f}%")

    abstain_memo = {"position": {"side": "ABSTAIN", "size_pct": 0.0}}
    assert compute_pnl(abstain_memo, "YES") == 0.0
    print(f"  ABSTAIN: {compute_pnl(abstain_memo, 'YES'):.2f}%")

    record = aggregate_track_record()
    print(f"  Track record: {record['total_memos']} memos, "
          f"{record['resolved']} resolved, total_pnl={record['total_pnl_pct']:+.2f}%")
    print("OK — pnl.py smoke test passed")
