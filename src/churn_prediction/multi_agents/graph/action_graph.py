# graphs/action_graph.py
from langgraph.graph import StateGraph, END
from ..state.graph_state import ActionState, ReportState
from ..agents.action_agent import ActionAgent

# Nếu bạn chưa có ActionState, tôi gợi ý dùng ReportState hoặc tạo mới.
# Ở đây tôi giả định bạn có ActionState hoặc dùng ReportState.

action_agent = ActionAgent()

def node_action_only(state: ReportState) -> ReportState:
    """
    Node chỉ thực hiện action recommendation (không tạo report).
    """
    try:
        action_plan = action_agent.recommend(
            sentiment_summary=state.get("sentiment_summary", {}),
            churn_summary=state.get("churn_summary", {}),
            report=state.get("report", "")  # có thể để trống
        )
        return {**state, "action_plan": action_plan}
    except Exception as e:
        return {**state, "error": f"ActionAgent: {e}"}

def build_action_pipeline():
    graph = StateGraph(ReportState)  # hoặc ActionState
    graph.add_node("action", node_action_only)
    graph.set_entry_point("action")
    graph.add_edge("action", END)
    return graph.compile()

action_pipeline = build_action_pipeline()