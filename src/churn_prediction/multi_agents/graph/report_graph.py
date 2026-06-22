# graphs/report_graph.py
from langgraph.graph import StateGraph, END
from ..state.graph_state import ReportState
from ..agents.report_agent import ReportAgent
from ..agents.action_agent import ActionAgent

# ── Khởi tạo agents ────────────────────────────────────────────────────────────
report_agent = ReportAgent()
action_agent = ActionAgent()

def node_report(state: ReportState) -> ReportState:
    try:
        report = report_agent.generate(
            sentiment_summary=state.get("sentiment_summary", {}),
            churn_summary=state.get("churn_summary", {}),
        )
        return {**state, "report": report}
    except Exception as e:
        return {**state, "error": f"ReportAgent: {e}"}

def node_action(state: ReportState) -> ReportState:
    try:
        action_plan = action_agent.recommend(
            sentiment_summary=state.get("sentiment_summary", {}),
            churn_summary=state.get("churn_summary", {}),
            report=state.get("report", ""),
        )
        return {**state, "action_plan": action_plan}
    except Exception as e:
        return {**state, "error": f"ActionAgent: {e}"}

def should_continue(state: ReportState) -> str:
    return END if state.get("error") else "continue"

def build_report_pipeline():
    graph = StateGraph(ReportState)
    graph.add_node("report", node_report)
    graph.add_node("action", node_action)
    graph.set_entry_point("report")
    graph.add_conditional_edges(
        "report",
        should_continue,
        {"continue": "action", END: END}
    )
    graph.add_edge("action", END)
    return graph.compile()

# ── Compile sẵn để import ──────────────────────────────────────────────────────
report_pipeline = build_report_pipeline()