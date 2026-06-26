# graphs/churn_graph.py
from langgraph.graph import StateGraph, END
from ..state.graph_state import ChurnState
from ..agents.churn_agent import ChurnAgent
from ..builders.churn_feature_builder import ChurnFeatureBuilder
from churn_prediction.paths import CHURN_MODEL_PATH

# ── Khởi tạo agent ────────────────────────────────────────────────────────────
churn_agent = ChurnAgent(str(CHURN_MODEL_PATH))
churn_feature_builder = ChurnFeatureBuilder()

def node_churn(state: ChurnState) -> ChurnState:
    print("=" * 50)
    print("STATE IN churn")
    print(state.keys())
    print(state.get("customer_profile"))
    print("=" * 50)
    try:
        features = state.get("features")
        
        # Nếu chưa có features truyền vào từ bên ngoài, tự động build từ profile
        if not features:
            profile = state.get("customer_profile")
            if profile:
                features = churn_feature_builder.build(profile)
            
        if not features or all(v == 0 for v in features.values()):
            raise ValueError("Không có features hoặc không thể build features từ profile")
        
        result = churn_agent.predict(features)
        return {**state, "features": features, "churn_result": result}
    except Exception as e:
        return {**state, "error": f"ChurnAgent: {e}"}

def build_churn_pipeline():
    graph = StateGraph(ChurnState)
    graph.add_node("churn", node_churn)
    graph.set_entry_point("churn")
    graph.add_edge("churn", END)
    return graph.compile()

# ── Compile sẵn để import ──────────────────────────────────────────────────────
churn_pipeline = build_churn_pipeline()