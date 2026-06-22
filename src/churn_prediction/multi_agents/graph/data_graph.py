# graphs/data_graph.py
from langgraph.graph import StateGraph, END
from ..state.graph_state import CustomerDataState
from ..agents.data_agent import CustomerDataAgent


# ── Khởi tạo agent ────────────────────────────────────────────────────────────
data_agent = CustomerDataAgent()

def node_data_processing(state: CustomerDataState) -> CustomerDataState:
    """
    Node xử lý dữ liệu đầu vào: chuẩn hóa, làm sạch, tìm kiếm, tạo profile.
    """
    try:
        order_input = state.get("order_input", {})
        customer_profile = data_agent.process(order_input)
        return {
            **state,
            "customer_profile": customer_profile,
        }
    except Exception as e:
        return {**state, "error": f"DataAgent: {e}"}

def build_data_pipeline():
    """
    Xây dựng pipeline xử lý dữ liệu.
    """
    graph = StateGraph(CustomerDataState)
    graph.add_node("data_processing", node_data_processing)
    graph.set_entry_point("data_processing")
    graph.add_edge("data_processing", END)
    return graph.compile()

# ── Compile sẵn để import ──────────────────────────────────────────────────────
data_pipeline = build_data_pipeline()