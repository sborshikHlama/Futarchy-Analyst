"""
Umia Analyst Agent CLI runner — agent/run.py

Usage:
    UMIA_ENV=demo python -m agent.run --market metadao_001
    UMIA_ENV=demo python -m agent.run --market metadao_001 --resolve YES
    UMIA_ENV=demo python -m agent.run --all-backtest
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("agent.run")


def run_market(market_id: str) -> dict:
    from dotenv import load_dotenv
    load_dotenv()

    from pipeline.graph import run_pipeline
    log.info(f"Running pipeline | market_id={market_id}")
    result = run_pipeline(market_id)
    return result


def resolve_market(market_id: str, outcome: str) -> None:
    from utils.pnl import attach_outcome_to_memo
    ok = attach_outcome_to_memo(market_id, outcome)
    if ok:
        print(f"Outcome recorded: {market_id} → {outcome}")
    else:
        print(f"No memo found for {market_id} — run the pipeline first")


def run_all_backtest() -> None:
    from utils.mock_markets import MARKET_CONFIGS
    for market_id, config in MARKET_CONFIGS.items():
        meta = config.get("metadata", {})
        resolved = meta.get("resolved_outcome")
        print(f"\n{'='*60}")
        print(f"Market: {meta.get('title', market_id)}")
        result = run_market(market_id)
        status = result.get("status")
        pos    = result.get("position") or {}
        print(f"Status:     {status}")
        print(f"Position:   {pos.get('side')} @ {pos.get('size_pct', 0):.1f}%")
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        print(f"Resolved:   {resolved or '(open)'}")

        if resolved and status and "completed" in str(status):
            resolve_market(market_id, resolved)


def print_track_record() -> None:
    from utils.pnl import aggregate_track_record
    record = aggregate_track_record()
    print(f"\n{'='*40}")
    print(f"UMIA ANALYST AGENT — TRACK RECORD")
    print(f"{'='*40}")
    print(f"Memos generated: {record['total_memos']}")
    print(f"Resolved:        {record['resolved']}")
    print(f"Unresolved:      {record['unresolved']}")
    print(f"Win rate:        {record['win_rate']:.1f}%")
    print(f"Total PnL:       {record['total_pnl_pct']:+.2f}%")
    print(f"W/L/A:           {record['win_count']}/{record['loss_count']}/{record['abstain_count']}")


def main():
    parser = argparse.ArgumentParser(description="Umia Analyst Agent runner")
    parser.add_argument("--market",       help="Market ID to run (e.g. metadao_001)")
    parser.add_argument("--resolve",      help="Resolve outcome: YES or NO")
    parser.add_argument("--all-backtest", action="store_true",
                        help="Run pipeline for all backtest markets")
    parser.add_argument("--track-record", action="store_true",
                        help="Print aggregated track record")
    args = parser.parse_args()

    if args.all_backtest:
        run_all_backtest()
        print_track_record()
        return

    if args.track_record:
        print_track_record()
        return

    if not args.market:
        parser.print_help()
        sys.exit(1)

    market_id = args.market

    if args.resolve:
        if args.resolve not in ("YES", "NO"):
            print("--resolve must be YES or NO")
            sys.exit(1)
        resolve_market(market_id, args.resolve)
        return

    result = run_market(market_id)

    print(f"\n{'='*60}")
    print(f"Market:     {result.get('market_metadata', {}).get('title', market_id)}")
    print(f"Status:     {result.get('status')}")
    pos = result.get("position") or {}
    print(f"Position:   {pos.get('side')} @ {pos.get('size_pct', 0):.1f}%")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    print(f"Flags:      {len(result.get('manipulation_flags', []))}")
    print(f"Audit events: {len(result.get('audit_trail', []))}")

    if result.get("bull_case"):
        print(f"\nBULL CASE:\n{result['bull_case'][:300]}")
    if result.get("bear_case"):
        print(f"\nBEAR CASE:\n{result['bear_case'][:300]}")


if __name__ == "__main__":
    main()
