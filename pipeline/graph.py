"""
Umia Analyst Agent — LangGraph Pipeline — pipeline/graph.py

Graph topology:
  START
    → source_classifier_agent
    → classification_validator
    ─[freeze]─→ END
    ─[synthesize]─→ memo_context_builder
    → synthesizer
    → position_agent
    → self_reviewer
    ─[freeze / escalate]─→ END
    ─[retry_position]─→ position_agent   (loop, max 3×)
    ─[rules]─→ position_rules_engine
    → publish_node
    → END

Demo mode: reads from data/markets/<market_id>/raw_mock.json
Production mode: hits live Apify / GitHub / on-chain APIs.
"""

import logging

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import END, START, StateGraph

from pipeline.nodes.phase1_extraction import (
    classification_validator,
    source_classifier_agent,
)
from pipeline.nodes.phase2_analysis import memo_context_builder, synthesizer
from pipeline.nodes.phase3_maker_checker import (
    position_agent,
    position_rules_engine,
    self_reviewer,
)
from pipeline.nodes.phase4_human_audit import publish_node
from pipeline.routing import (
    route_after_classification,
    route_after_reviewer,
    route_after_rules,
)
from pipeline.state import AgentState, make_initial_state

log = logging.getLogger(__name__)


def build_graph() -> StateGraph:
    graph = StateGraph(dict)

    graph.add_node("source_classifier_agent",  source_classifier_agent)
    graph.add_node("classification_validator", classification_validator)
    graph.add_node("memo_context_builder",     memo_context_builder)
    graph.add_node("synthesizer",              synthesizer)
    graph.add_node("position_agent",           position_agent)
    graph.add_node("self_reviewer",            self_reviewer)
    graph.add_node("position_rules_engine",    position_rules_engine)
    graph.add_node("publish_node",             publish_node)

    graph.add_edge(START,                        "source_classifier_agent")
    graph.add_edge("source_classifier_agent",    "classification_validator")

    graph.add_conditional_edges(
        "classification_validator",
        route_after_classification,
        {"freeze": END, "synthesize": "memo_context_builder"},
    )

    graph.add_edge("memo_context_builder", "synthesizer")
    graph.add_edge("synthesizer",          "position_agent")
    graph.add_edge("position_agent",       "self_reviewer")

    graph.add_conditional_edges(
        "self_reviewer",
        route_after_reviewer,
        {
            "freeze":          END,
            "escalate":        END,
            "retry_position":  "position_agent",
            "rules":           "position_rules_engine",
        },
    )

    graph.add_conditional_edges(
        "position_rules_engine",
        route_after_rules,
        {"publish": "publish_node"},
    )

    graph.add_edge("publish_node", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        log.info("[Graph] Compiling Umia Analyst Agent pipeline")
        _compiled_graph = build_graph()
        log.info("[Graph] Pipeline compiled")
    return _compiled_graph


def run_pipeline(market_id: str, request_id: str | None = None) -> dict:
    """
    Run the full pipeline for a given market_id.

    Demo mode (UMIA_ENV=demo): reads raw_signals from
    data/markets/<market_id>/raw_mock.json.
    Production mode: calls live ingest APIs.
    """
    import os, uuid
    if request_id is None:
        request_id = f"REQ-{market_id[:8]}-{uuid.uuid4().hex[:6].upper()}"

    initial_state = make_initial_state(market_id, request_id)

    # Load signals + metadata
    env = os.getenv("UMIA_ENV", "demo")
    if env == "demo":
        initial_state = _load_demo_signals(initial_state, market_id)
    else:
        from utils.ingest import gather_signals
        signals_bundle = gather_signals(market_id)
        initial_state["raw_signals"]    = signals_bundle.get("signals", {})
        initial_state["market_metadata"] = signals_bundle.get("metadata", {})

    log.info(f"[Graph] Starting pipeline | market_id={market_id} env={env} request_id={request_id}")
    graph = get_graph()
    final_state = graph.invoke(initial_state)
    log.info(f"[Graph] Pipeline done | market_id={market_id} "
             f"status={final_state.get('status')} "
             f"side={final_state.get('position', {}).get('side')} "
             f"audit_events={len(final_state.get('audit_trail', []))}")
    return final_state


def _load_demo_signals(state: dict, market_id: str) -> dict:
    """Load raw_mock.json and market metadata for demo mode."""
    import json
    from pathlib import Path
    mock_path = Path(__file__).parent.parent / "data" / "markets" / market_id / "raw_mock.json"
    if mock_path.exists():
        with mock_path.open("r", encoding="utf-8") as f:
            bundle = json.load(f)
        state["raw_signals"]    = bundle.get("signals", {})
        state["market_metadata"] = bundle.get("metadata", {})
        log.info(f"[Graph] Demo signals loaded | market_id={market_id} "
                 f"sources={len(state['raw_signals'])}")
    else:
        log.warning(f"[Graph] No mock data found at {mock_path} — using empty signals")
        state["raw_signals"]    = {}
        state["market_metadata"] = {"title": market_id, "proposal": "Unknown", "venue": "Unknown"}
    return state


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    market_id = sys.argv[1] if len(sys.argv) > 1 else "metadao_001"
    print(f"\nRunning pipeline for market: {market_id}")
    print("=" * 60)

    result = run_pipeline(market_id)

    print(f"\nStatus:    {result.get('status')}")
    print(f"Market:    {result.get('market_metadata', {}).get('title', 'N/A')}")
    print(f"Position:  {result.get('position', {}).get('side')} "
          f"@ {result.get('position', {}).get('size_pct', 0):.1f}%")
    print(f"Confidence:{result.get('confidence', 0):.2f}")
    print(f"Flags:     {len(result.get('manipulation_flags', []))}")
    print(f"Audit events: {len(result.get('audit_trail', []))}")
    print("\nOK — graph.py smoke test passed")
