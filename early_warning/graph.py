"""
Live Memo Watch — LangGraph Pipeline — early_warning/graph.py
Monitors open decision markets for signal changes.

Graph:
  START → load_open_markets → calculate_market_signal_scores
        → detect_market_anomalies → generate_watch_alerts
        → dispatch_watch_alerts → END
"""
import logging
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import END, START, StateGraph

from early_warning.nodes.alert_dispatcher import dispatch_watch_alerts
from early_warning.nodes.alert_generator import generate_watch_alerts
from early_warning.nodes.anomaly_detector import detect_market_anomalies
from early_warning.nodes.metrics_calculator import calculate_market_signal_scores
from early_warning.nodes.portfolio_loader import load_open_markets
from early_warning.state import make_initial_watch_state

log = logging.getLogger(__name__)


def build_watch_graph() -> StateGraph:
    builder = StateGraph(dict)

    builder.add_node("load_open_markets",             load_open_markets)
    builder.add_node("calculate_market_signal_scores", calculate_market_signal_scores)
    builder.add_node("detect_market_anomalies",       detect_market_anomalies)
    builder.add_node("generate_watch_alerts",         generate_watch_alerts)
    builder.add_node("dispatch_watch_alerts",         dispatch_watch_alerts)

    builder.add_edge(START,                              "load_open_markets")
    builder.add_edge("load_open_markets",               "calculate_market_signal_scores")
    builder.add_edge("calculate_market_signal_scores",  "detect_market_anomalies")
    builder.add_edge("detect_market_anomalies",         "generate_watch_alerts")
    builder.add_edge("generate_watch_alerts",           "dispatch_watch_alerts")
    builder.add_edge("dispatch_watch_alerts",           END)

    return builder.compile()


_compiled_graph = None


def get_watch_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_watch_graph()
    return _compiled_graph


def run_live_watch(run_type: str = "on_demand") -> dict:
    """Run the Live Memo Watch pipeline."""
    initial_state = make_initial_watch_state(
        run_id=str(uuid.uuid4()),
        run_type=run_type,
    )
    log.info(f"[WatchGraph] Starting | run_type={run_type}")
    graph = get_watch_graph()
    result = graph.invoke(initial_state)
    s = result.get("summary", {})
    log.info(f"[WatchGraph] Done | HIGH={s.get('high_signal',0)} "
             f"MEDIUM={s.get('medium_signal',0)}")
    return result


if __name__ == "__main__":
    import logging as _logging
    _logging.basicConfig(level=_logging.INFO)

    result = run_live_watch("on_demand")
    s = result["summary"]
    print(f"\nLive Watch OK")
    print(f"  Run ID:  {result['run_id']}")
    print(f"  Markets: {s.get('total_markets', 0)}")
    print(f"  HIGH:    {s.get('high_signal', 0)}")
    print(f"  MEDIUM:  {s.get('medium_signal', 0)}")
    print(f"  LOW:     {s.get('low_signal', 0)}")
    print("\nOK — early_warning/graph.py smoke test passed")
